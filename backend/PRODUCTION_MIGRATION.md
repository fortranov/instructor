# Быстрая инструкция: Миграция на продакшене

## Шаг 1: Создайте backup базы данных

```bash
cd /path/to/triplan/backend
cp triplan.db triplan.db.backup.$(date +%Y%m%d_%H%M%S)
```

## Шаг 2: Загрузите миграционный скрипт

Загрузите файл `migrate_add_strength_training.py` на production сервер в директорию `backend/`.

## Шаг 3: Примените миграцию

```bash
cd /path/to/triplan/backend
python migrate_add_strength_training.py ./triplan.db
```

Ожидаемый вывод:
```
======================================================================
MIGRACIYA: Dobavlenie has_strength_training v tablicu users
======================================================================

Migraciya bazy dannyh: ./triplan.db
  [SUCCESS] Pole has_strength_training uspeshno dobavleno
  [VERIFIED] Migraciya primenyena uspeshno

[SUCCESS] Migraciya zavershena uspeshno!

NE ZABUD'TE:
  1. Perezapustit' backend server
  2. Proverit' rabotu prilozheniya
```

## Шаг 4: Перезапустите backend

**Для systemd:**
```bash
sudo systemctl restart triplan-backend
sudo systemctl status triplan-backend
```

**Для PM2:**
```bash
pm2 restart triplan-backend
pm2 logs triplan-backend
```

**Для Docker:**
```bash
docker-compose restart backend
docker-compose logs -f backend
```

## Шаг 5: Проверьте работу приложения

1. Откройте приложение в браузере
2. Попробуйте войти в систему
3. Проверьте создание нового плана тренировок
4. Убедитесь, что силовые тренировки отображаются корректно

## Откат (если что-то пошло не так)

```bash
cd /path/to/triplan/backend

# Остановите backend
sudo systemctl stop triplan-backend  # или pm2 stop / docker-compose stop

# Восстановите backup
cp triplan.db.backup.XXXXXXXX_XXXXXX triplan.db

# Запустите backend
sudo systemctl start triplan-backend  # или pm2 start / docker-compose start
```

## Альтернативный метод: Прямой SQL

Если не хочется использовать Python скрипт:

```bash
cd /path/to/triplan/backend
sqlite3 triplan.db "ALTER TABLE users ADD COLUMN has_strength_training INTEGER DEFAULT 0;"
```

Затем перезапустите backend.

---

**ВАЖНО:** Всегда делайте backup перед миграцией!
