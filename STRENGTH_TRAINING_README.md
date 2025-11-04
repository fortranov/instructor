# Силовые тренировки - Полное руководство

## Быстрый старт

### Для Docker (продакшен)

```bash
# Одна команда для проверки
bash check_strength_docker.sh

# Если нужна миграция:
docker exec backend cp /app/data/triplan.db /app/data/triplan.db.backup.$(date +%Y%m%d_%H%M%S)
docker exec backend python migrate_add_strength_training.py /app/data/triplan.db
docker-compose restart backend
```

### Для пользователей

1. **Профиль** → Включить "Силовые тренировки в план" ✅
2. **"Изменить план тренировок"**
3. Проверить план - должны появиться тренировки "Силовая"

---

## Документация

### 📋 Инструкции

| Файл | Описание | Когда использовать |
|------|----------|-------------------|
| **QUICK_FIX_STRENGTH_TRAINING.md** | Краткая шпаргалка | Первое место для старта |
| **DOCKER_STRENGTH_TRAINING_FIX.md** | Подробная инструкция для Docker | Продакшен в контейнерах ⭐ |
| **PRODUCTION_STRENGTH_TRAINING_FIX.md** | Инструкция для bare-metal | Продакшен без Docker |
| **STRENGTH_TRAINING_FIX.md** | Техническая документация | Понимание проблемы |

### 🛠 Скрипты

| Файл | Назначение | Пример использования |
|------|-----------|---------------------|
| `backend/check_database_schema.py` | Проверка БД | `docker exec backend python check_database_schema.py /app/data/triplan.db` |
| `backend/migrate_add_strength_training.py` | Миграция БД | `docker exec backend python migrate_add_strength_training.py /app/data/triplan.db` |
| `check_strength_docker.sh` | Быстрая диагностика Docker | `bash check_strength_docker.sh` |

---

## Проблема и решение

### Что случилось?

Силовые тренировки не отображаются в планах пользователей.

### Почему?

1. **На продакшене нет поля `has_strength_training`** (база данных не обновлена)
2. **План был создан до включения настройки** (план не обновляется автоматически)

### Как исправить?

#### Шаг 1: Миграция базы данных (один раз)

```bash
# Проверка
docker exec backend python check_database_schema.py /app/data/triplan.db

# Backup
docker exec backend cp /app/data/triplan.db /app/data/triplan.db.backup.$(date +%Y%m%d_%H%M%S)

# Миграция
docker exec backend python migrate_add_strength_training.py /app/data/triplan.db

# Перезапуск
docker-compose restart backend
```

#### Шаг 2: Пользователям - пересоздать планы

⚠️ **Каждому пользователю нужно:**

1. Профиль → Включить "Силовые тренировки"
2. "Изменить план тренировок"

---

## Что ожидать

После исправления в плане появятся:

- **~1 силовая тренировка в неделю**
- Только в фазах **base** и **build** (первые ~8 недель)
- Для 12-недельного плана: **~9 тренировок**
- Длительность: **50 минут**

---

## Техническая информация

### Структура Docker

```
Контейнер: backend
База данных: /app/data/triplan.db (внутри контейнера)
Docker volume: triplan_data
DB_PATH env: /app/data/triplan.db
```

### Логика работы

```python
# backend/plan_generator.py:126-132
if has_strength_training and phase in ['base', 'build']:
    strength_workout = self._add_strength_workout(...)
    if strength_workout:
        workouts.append(strength_workout)
```

### Схема базы данных

```sql
-- Таблица users
has_strength_training INTEGER DEFAULT 0  -- 0=выкл, 1=вкл

-- Тренировки
sport_type = 'STRENGTH'  -- силовая тренировка
workout_type = 'RECOVERY'
duration_minutes = 50
```

---

## Проверка работы

### На продакшене (Docker)

```bash
# Полная проверка
bash check_strength_docker.sh

# Или вручную:
docker exec backend python -c "
import sqlite3
conn = sqlite3.connect('/app/data/triplan.db')
cursor = conn.cursor()

# Проверяем поле
cursor.execute('PRAGMA table_info(users)')
columns = [col[1] for col in cursor.fetchall()]
print('has_strength_training:', 'has_strength_training' in columns)

# Считаем тренировки
cursor.execute('SELECT COUNT(*) FROM workouts WHERE LOWER(sport_type) = \"strength\"')
print('Силовых тренировок:', cursor.fetchone()[0])

conn.close()
"
```

### В локальной разработке

```bash
cd backend
python check_database_schema.py ./triplan.db
```

---

## Откат изменений

Если что-то пошло не так:

```bash
# Остановить контейнер
docker-compose stop backend

# Восстановить backup
docker run --rm \
  -v triplan_data:/app/data \
  alpine \
  sh -c "cp /app/data/triplan.db.backup.XXXXXXXX_XXXXXX /app/data/triplan.db"

# Запустить контейнер
docker-compose up -d backend
```

---

## FAQ

**Q: Как проверить, нужна ли миграция?**

```bash
docker exec backend python check_database_schema.py /app/data/triplan.db
```

Если видите `[MISSING] has_strength_training` - нужна миграция.

**Q: Миграция безопасна для повторного запуска?**

Да! Скрипт проверяет, существует ли поле, и не изменит базу если оно уже есть.

**Q: Силовые не появились после включения настройки?**

План нужно **пересоздать**. Зайдите в Профиль → "Изменить план тренировок".

**Q: Можно ли добавить силовые в существующий план?**

Нет, нужно пересоздать весь план. Это ограничение текущей архитектуры.

**Q: Где силовые тренировки в плане?**

Только в первых **~8 неделях** (фазы base и build). В фазах peak и taper их нет.

---

## Контакты и поддержка

- **GitHub Issues:** Для багов и вопросов
- **Документация:** См. файлы выше

---

## История изменений

### 4 ноября 2025

- ✅ Добавлена проверка базы данных
- ✅ Создана миграция для продакшена
- ✅ Добавлены предупреждения в UI
- ✅ Создана документация
- ✅ Добавлена поддержка Docker

---

**Версия документации:** 1.0
**Дата обновления:** 4 ноября 2025
