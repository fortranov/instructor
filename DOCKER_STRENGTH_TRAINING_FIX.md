# Docker: Исправление силовых тренировок

## Быстрое исправление для продакшена

### Шаг 1: Проверка базы данных

```bash
# Проверяем, что контейнер запущен
docker ps | grep backend

# Проверяем схему базы данных
docker exec backend python check_database_schema.py /app/data/triplan.db
```

**Ожидаемый результат:**
```
[SUCCESS] BAZA DANNYH GOTOVA K RABOTE
```

Если видите `[MISSING] has_strength_training - OTSUTSTVUET!` → переходите к Шагу 2

---

### Шаг 2: Миграция (если нужна)

#### 2.1. Создайте backup

```bash
# Backup внутри volume
docker exec backend cp /app/data/triplan.db /app/data/triplan.db.backup.$(date +%Y%m%d_%H%M%S)

# ИЛИ копируем на хост-машину (безопаснее)
docker cp backend:/app/data/triplan.db ./triplan.db.backup.$(date +%Y%m%d_%H%M%S)
```

#### 2.2. Примените миграцию

```bash
docker exec backend python migrate_add_strength_training.py /app/data/triplan.db
```

**Ожидаемый вывод:**
```
[SUCCESS] Pole has_strength_training uspeshno dobavleno
[VERIFIED] Migraciya primenyena uspeshno
```

#### 2.3. Перезапустите backend

```bash
docker-compose restart backend

# Проверьте логи
docker-compose logs -f backend
```

---

### Шаг 3: Проверка после миграции

```bash
# Проверяем еще раз схему
docker exec backend python check_database_schema.py /app/data/triplan.db

# Должны увидеть:
# [OK] has_strength_training - prisutstvuet
```

---

### Шаг 4: Пользователям - пересоздать планы

После миграции **каждому пользователю** нужно:

1. Войти в **Профиль**
2. Включить **"Включить силовые тренировки в план"** ✅
3. Нажать **"Изменить план тренировок"**

⚠️ **Важно:** План НЕ обновляется автоматически!

---

## Альтернативный способ: Прямой SQL

Если не работает Python скрипт:

```bash
# Backup
docker exec backend cp /app/data/triplan.db /app/data/triplan.db.backup

# Применяем SQL напрямую
docker exec backend sqlite3 /app/data/triplan.db \
  "ALTER TABLE users ADD COLUMN has_strength_training INTEGER DEFAULT 0;"

# Перезапуск
docker-compose restart backend
```

---

## Проверка силовых тренировок

```bash
# Проверяем, что настройка работает
docker exec backend python -c "
import sqlite3
conn = sqlite3.connect('/app/data/triplan.db')
cursor = conn.cursor()

# Пользователи с настройкой
cursor.execute('SELECT email, has_strength_training FROM users')
print('Пользователи:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {\"ON\" if row[1] == 1 else \"OFF\"}')

# Силовые тренировки в планах
cursor.execute('''
    SELECT COUNT(*) FROM workouts
    WHERE LOWER(sport_type) = \"strength\"
''')
count = cursor.fetchone()[0]
print(f'\nСиловых тренировок в базе: {count}')

conn.close()
"
```

---

## Откат изменений (если что-то не так)

```bash
# Остановите backend
docker-compose stop backend

# Восстановите backup
docker run --rm \
  -v triplan_data:/app/data \
  alpine \
  sh -c "cp /app/data/triplan.db.backup.XXXXXXXX_XXXXXX /app/data/triplan.db"

# Запустите backend
docker-compose up -d backend
```

---

## Структура

```
База данных: /app/data/triplan.db (внутри контейнера)
Docker volume: triplan_data
Контейнер: backend
Network: main-network (external)
```

---

## Частые проблемы

### Q: Не могу выполнить команду внутри контейнера

```bash
# Проверьте, что контейнер запущен
docker ps | grep backend

# Если не запущен:
docker-compose up -d backend
```

### Q: Файл миграции не найден

Миграционные скрипты должны быть в Docker image. Если их нет:

```bash
# Пересоберите образ
docker-compose build backend
docker-compose up -d backend
```

### Q: Ошибка "Permission denied"

```bash
# Проверьте права доступа к volume
docker volume inspect triplan_data

# Возможно нужно использовать sudo
sudo docker exec backend python migrate_add_strength_training.py /app/data/triplan.db
```

---

## Что ожидать после исправления

- **~1 силовая тренировка в неделю**
- Только в фазах **base** и **build** (первые ~8 недель)
- Для 12-недельного плана: **~9 силовых тренировок**
- Длительность: **50 минут каждая**

---

## Контрольный чеклист

- [ ] Создан backup базы данных
- [ ] Проверена схема БД (`check_database_schema.py`)
- [ ] Применена миграция (если требовалась)
- [ ] Backend перезапущен
- [ ] Логи проверены (нет ошибок)
- [ ] Пользователи уведомлены о пересоздании планов
- [ ] Силовые тренировки появились в новых планах

---

**Дата:** 4 ноября 2025

**Volume:** `triplan_data`
**DB Path:** `/app/data/triplan.db`
**Container:** `backend`
