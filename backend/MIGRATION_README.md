# Миграция: Добавление поля has_strength_training

## Что делает эта миграция?

Добавляет поле `has_strength_training` в таблицу `users` для поддержки силовых тренировок в планах.

- **Безопасно**: не изменяет существующие данные
- **Идемпотентно**: можно запускать многократно
- **Откатываемо**: можно восстановить из backup

---

## Быстрый старт

### Docker окружение (продакшен):

```bash
docker exec backend cp /app/data/triplan.db /app/data/triplan.db.backup
docker exec backend python migrate_add_strength_training.py /app/data/triplan.db
docker-compose restart backend
```

### Локальная разработка:

```bash
cd backend
python migrate_add_strength_training.py
# Перезапустите backend сервер
```

---

## Все доступные способы

1. **Docker с docker exec** ⭐ РЕКОМЕНДУЕТСЯ
   - См. файл: `DOCKER_MIGRATION.md`
   - Команды выше

2. **Docker с автоматической миграцией при старте**
   - См. файл: `DOCKER_MIGRATION.md` (Способ 3.1)
   - Использует `entrypoint.sh`

3. **Прямой SQL в Docker**
   ```bash
   docker exec backend sqlite3 /app/data/triplan.db \
     "ALTER TABLE users ADD COLUMN has_strength_training INTEGER DEFAULT 0;"
   ```

4. **Обычный сервер (без Docker)**
   - См. файл: `PRODUCTION_MIGRATION.md`

5. **Через доступ к Docker volume**
   - См. файл: `DOCKER_MIGRATION.md` (Способ 4)

---

## Файлы миграции

- **`migrate_add_strength_training.py`** - Python скрипт для миграции
- **`entrypoint.sh`** - Опциональный скрипт для автоматических миграций
- **`DOCKER_MIGRATION.md`** - Подробная инструкция для Docker
- **`PRODUCTION_MIGRATION.md`** - Инструкция для обычного сервера
- **`MIGRATION_GUIDE.md`** - Детальное руководство со всеми вариантами
- **`MIGRATION_README.md`** - Этот файл (обзор)

---

## Проверка успешности

```bash
# Docker
docker exec backend sqlite3 /app/data/triplan.db "PRAGMA table_info(users);" | grep strength

# Локально
sqlite3 triplan.db "PRAGMA table_info(users);" | grep strength
```

Ожидаемый вывод:
```
14|has_strength_training|INTEGER|0|0|0
```

---

## Откат

Если что-то пошло не так, восстановите из backup:

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

## FAQ

**Q: Нужно ли останавливать сервер для миграции?**
A: Нет, но рекомендуется для безопасности. SQLite поддерживает миграцию на лету.

**Q: Что произойдет с существующими пользователями?**
A: Ничего. Новое поле получит значение 0 (без силовых тренировок).

**Q: Можно ли запустить миграцию дважды?**
A: Да, скрипт проверяет наличие поля и не добавит его повторно.

**Q: Нужно ли обновлять код перед миграцией?**
A: Да, убедитесь что новый код уже на сервере (с обновленными моделями).

---

## Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs -f backend`
2. Убедитесь что backup создан
3. Проверьте права доступа к файлу БД
4. Обратитесь к подробным инструкциям в соответствующих файлах
