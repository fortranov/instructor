# Применение миграции в Docker окружении

База данных находится в Docker volume `triplan_data` и монтируется в контейнере по пути `/app/data/triplan.db`.

## Способ 1: Через docker exec (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Убедитесь, что контейнер запущен

```bash
docker ps | grep backend
```

### Шаг 2: Создайте backup базы данных

```bash
# Создаем backup прямо в volume
docker exec backend cp /app/data/triplan.db /app/data/triplan.db.backup.$(date +%Y%m%d_%H%M%S)

# ИЛИ копируем backup на хост
docker cp backend:/app/data/triplan.db ./triplan.db.backup.$(date +%Y%m%d_%H%M%S)
```

### Шаг 3: Примените миграцию

Миграционный скрипт уже находится в контейнере (копируется при сборке).

```bash
docker exec backend python migrate_add_strength_training.py /app/data/triplan.db
```

Ожидаемый вывод:
```
======================================================================
MIGRACIYA: Dobavlenie has_strength_training v tablicu users
======================================================================

Migraciya bazy dannyh: /app/data/triplan.db
  [SUCCESS] Pole has_strength_training uspeshno dobavleno
  [VERIFIED] Migraciya primenyena uspeshno

[SUCCESS] Migraciya zavershena uspeshno!
```

### Шаг 4: Перезапустите контейнер

```bash
docker-compose restart backend

# Проверьте логи
docker-compose logs -f backend
```

### Шаг 5: Проверьте работу

1. Откройте приложение в браузере
2. Попробуйте войти в систему
3. Создайте новый план тренировок

---

## Способ 2: Через docker-compose exec

Если используете docker-compose и контейнер уже запущен:

```bash
# Backup
docker-compose exec backend cp /app/data/triplan.db /app/data/triplan.db.backup

# Миграция
docker-compose exec backend python migrate_add_strength_training.py /app/data/triplan.db

# Перезапуск
docker-compose restart backend
```

---

## Способ 3: Пересборка с новым кодом (при деплое)

При обновлении кода на продакшене миграция может быть выполнена автоматически:

### Вариант 3.1: Добавить в entrypoint скрипт

Создайте файл `backend/entrypoint.sh`:

```bash
#!/bin/bash
set -e

# Применяем миграции при старте
python migrate_add_strength_training.py /app/data/triplan.db

# Запускаем основное приложение
exec "$@"
```

Обновите `Dockerfile`:

```dockerfile
# Копируем entrypoint скрипт
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Изменяем команду запуска
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Вариант 3.2: Выполнить миграцию вручную при деплое

```bash
# Обновляем код
git pull origin main

# Пересобираем контейнер
docker-compose build backend

# Останавливаем старый контейнер
docker-compose stop backend

# Выполняем миграцию на остановленном volume
docker run --rm \
  -v triplan_data:/app/data \
  backend:latest \
  python migrate_add_strength_training.py /app/data/triplan.db

# Запускаем новый контейнер
docker-compose up -d backend
```

---

## Способ 4: Прямой доступ к volume (если нужен)

Если нужно получить прямой доступ к файлу БД:

```bash
# Найти путь к volume на хосте
docker volume inspect triplan_data

# В выводе будет Mountpoint, например:
# "Mountpoint": "/var/lib/docker/volumes/triplan_data/_data"

# Выполнить миграцию напрямую (нужны права root)
sudo python migrate_add_strength_training.py /var/lib/docker/volumes/triplan_data/_data/triplan.db
```

---

## Откат миграции

Если что-то пошло не так:

```bash
# Остановите контейнер
docker-compose stop backend

# Восстановите backup
docker run --rm \
  -v triplan_data:/app/data \
  alpine \
  cp /app/data/triplan.db.backup.XXXXXXXX /app/data/triplan.db

# Запустите контейнер
docker-compose up -d backend
```

---

## Альтернатива: Прямой SQL через docker exec

Без использования Python скрипта:

```bash
# Backup
docker exec backend cp /app/data/triplan.db /app/data/triplan.db.backup

# Применить SQL
docker exec backend sqlite3 /app/data/triplan.db \
  "ALTER TABLE users ADD COLUMN has_strength_training INTEGER DEFAULT 0;"

# Перезапуск
docker-compose restart backend
```

---

## Проверка успешности миграции

```bash
# Проверить структуру таблицы
docker exec backend sqlite3 /app/data/triplan.db "PRAGMA table_info(users);"

# В выводе должна быть строка с has_strength_training
```

---

## Важно!

- ✅ **ВСЕГДА делайте backup перед миграцией**
- ✅ Миграционный скрипт безопасен для повторного запуска
- ✅ Проверьте логи после перезапуска: `docker-compose logs -f backend`
- ✅ База данных в Docker volume сохраняется между пересборками контейнера
