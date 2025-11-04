# Быстрое исправление: Силовые тренировки

## TL;DR (Очень кратко)

### На продакшене (Docker):

```bash
# 1. Проверка
docker exec backend python check_database_schema.py /app/data/triplan.db

# 2. Если нужна миграция:
docker exec backend cp /app/data/triplan.db /app/data/triplan.db.backup.$(date +%Y%m%d_%H%M%S)
docker exec backend python migrate_add_strength_training.py /app/data/triplan.db

# 3. Перезапуск
docker-compose restart backend

# 4. Пользователям: Профиль → Включить силовые → Пересоздать план
```

### На продакшене (без Docker):

```bash
# 1. Проверка
cd /path/to/triplan/backend
python check_database_schema.py ./triplan.db

# 2. Если нужна миграция:
cp triplan.db triplan.db.backup.$(date +%Y%m%d_%H%M%S)
python migrate_add_strength_training.py ./triplan.db

# 3. Перезапуск
sudo systemctl restart triplan-backend  # или pm2 restart

# 4. Пользователям: Профиль → Включить силовые → Пересоздать план
```

---

## Причина проблемы

1. **База данных не имеет поля `has_strength_training`** → Нужна миграция
2. **План создан до включения настройки** → Нужно пересоздать план

---

## Что делать пользователям

1. Открыть **Профиль**
2. Включить **"Включить силовые тренировки в план"**
3. Нажать **"Изменить план тренировок"**

⚠️ План не обновляется автоматически!

---

## Файлы

- **Проверка БД:** `backend/check_database_schema.py`
- **Миграция:** `backend/migrate_add_strength_training.py`
- **Docker инструкция:** `DOCKER_STRENGTH_TRAINING_FIX.md` ⭐
- **Общая инструкция:** `PRODUCTION_STRENGTH_TRAINING_FIX.md`

---

## Результат

- **~9 силовых тренировок** для 12-недельного плана
- **1 тренировка/неделю** в фазах base и build
- **50 минут** длительность
