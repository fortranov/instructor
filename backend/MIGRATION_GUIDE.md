# Применение миграции has_strength_training на продакшене

## Вариант 1: Через Python скрипт (Рекомендуется)

1. Загрузите файл `migrate_add_strength_training.py` на production сервер
2. Подключитесь к серверу по SSH
3. Перейдите в директорию backend:
   ```bash
   cd /path/to/triplan/backend
   ```
4. Запустите миграцию:
   ```bash
   python migrate_add_strength_training.py
   ```
5. Перезапустите backend сервис:
   ```bash
   # Для systemd
   sudo systemctl restart triplan-backend

   # Для PM2
   pm2 restart triplan-backend

   # Для Docker
   docker-compose restart backend
   ```

## Вариант 2: Через прямой SQL запрос

1. Подключитесь к серверу по SSH
2. Откройте базу данных:
   ```bash
   cd /path/to/triplan/backend
   sqlite3 triplan.db
   ```
3. Выполните SQL команду:
   ```sql
   ALTER TABLE users ADD COLUMN has_strength_training INTEGER DEFAULT 0;
   ```
4. Выйдите из sqlite:
   ```sql
   .exit
   ```
5. Перезапустите backend сервис (см. команды выше)

## Вариант 3: Через backup и восстановление (для больших баз)

1. Создайте backup базы данных:
   ```bash
   cd /path/to/triplan/backend
   cp triplan.db triplan.db.backup
   ```
2. Примените один из вариантов выше
3. Проверьте работу приложения
4. Если все работает - удалите backup:
   ```bash
   rm triplan.db.backup
   ```

## Проверка успешности миграции

После применения миграции проверьте структуру таблицы:

```bash
sqlite3 triplan.db "PRAGMA table_info(users);"
```

В выводе должна быть строка:
```
14|has_strength_training|INTEGER|0|0|0
```

## Откат миграции (если что-то пошло не так)

Если нужно откатить изменения:

1. Восстановите из backup:
   ```bash
   cp triplan.db.backup triplan.db
   ```

2. Или удалите поле вручную (SQLite не поддерживает DROP COLUMN напрямую):
   ```bash
   # Потребуется пересоздать таблицу без этого поля
   # Лучше использовать backup!
   ```

## Важные замечания

- **ВСЕГДА делайте backup перед миграцией!**
- Проверьте, что миграция не запущена дважды (скрипт проверяет это автоматически)
- После миграции убедитесь, что приложение корректно работает
- Миграция не влияет на существующих пользователей - значение по умолчанию 0 (нет силовых тренировок)
