# Быстрое применение миграции has_strength_training

> ⚠️ **ВАЖНО: Всегда делайте backup перед миграцией!**

## Для Docker (продакшен) ⭐ РЕКОМЕНДУЕТСЯ

Выполните последовательно три команды:

```bash
# 1. Создаем backup
docker exec backend cp /app/data/triplan.db /app/data/triplan.db.backup

# 2. Применяем миграцию
docker exec backend python migrate_add_strength_training.py /app/data/triplan.db

# 3. Перезапускаем backend
docker-compose restart backend
```

**Готово!** Проверьте логи: `docker-compose logs -f backend`

---

## Для локальной разработки

```bash
# 1. Backup
cd backend
cp triplan.db triplan.db.backup

# 2. Миграция
python migrate_add_strength_training.py

# 3. Перезапуск backend сервера
# (Ctrl+C и заново запустить python main.py)
```

---

## Проверка успешности миграции

```bash
# Docker
docker exec backend sqlite3 /app/data/triplan.db "PRAGMA table_info(users);" | grep strength

# Локально
cd backend
sqlite3 triplan.db "PRAGMA table_info(users);" | grep strength
```

Ожидаемый вывод:
```
14|has_strength_training|INTEGER|0|0|0
```

---

## Откат (если что-то пошло не так)

```bash
# Docker
docker-compose stop backend
docker exec backend cp /app/data/triplan.db.backup /app/data/triplan.db
docker-compose start backend

# Локально
cd backend
cp triplan.db.backup triplan.db
# Перезапустите backend
```

---

## 📚 Подробные инструкции

- **`backend/MIGRATION_README.md`** - Обзор всех способов миграции
- **`backend/DOCKER_MIGRATION.md`** - Детальная инструкция для Docker
- **`backend/PRODUCTION_MIGRATION.md`** - Инструкция для обычного сервера
- **`backend/MIGRATION_GUIDE.md`** - Полное руководство со всеми вариантами

---

## ⚡ Альтернативный способ: Прямой SQL

Без использования Python скрипта:

```bash
# Docker
docker exec backend sqlite3 /app/data/triplan.db \
  "ALTER TABLE users ADD COLUMN has_strength_training INTEGER DEFAULT 0;"

# Локально
cd backend
sqlite3 triplan.db "ALTER TABLE users ADD COLUMN has_strength_training INTEGER DEFAULT 0;"
```

Затем перезапустите backend.
