# Исправление ошибки обновления тарифов администратором

## Проблема

При попытке изменить тариф пользователя на странице администрирования возникает ошибка:

```
Error: Ошибка при обновлении тарифа: (sqlite3.OperationalError) no such column: tariffs.allow_running
```

## Причина

В продакшн базе данных отсутствуют колонки для управления доступными видами спорта в тарифах:
- `allow_running` - доступен ли бег
- `allow_cycling` - доступен ли велосипед
- `allow_swimming` - доступно ли плавание
- `allow_triathlon` - доступен ли триатлон

## Решение

Добавлена автоматическая миграция в функцию `ensure_database_compatibility()` в файле `backend/database.py`.

Миграция выполняется автоматически при каждом запуске приложения и:
1. Проверяет наличие колонок в таблице `tariffs`
2. Добавляет отсутствующие колонки с правильными значениями по умолчанию
3. Обновляет существующие тарифы:
   - Для всех тарифов: `allow_running = 1` (бег доступен всегда)
   - Для PRO тарифа: все виды спорта включены

## Применение исправления

### Автоматическое применение (при следующем деплое)

1. Просто перезапустите Docker контейнеры:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

2. Миграция выполнится автоматически при старте приложения

### Ручное применение (без перезапуска)

Если нужно применить миграцию без перезапуска, выполните:

```bash
# Зайдите в контейнер backend
docker exec -it backend bash

# Запустите скрипт миграции
python migrate_tariffs_add_sport_columns.py

# Выйдите из контейнера
exit
```

## Проверка

После применения миграции проверьте:

1. Страница администрирования пользователей должна загружаться без ошибок
2. Изменение тарифа пользователя должно работать корректно
3. В логах backend должно быть сообщение:
   ```
   ✅ All required columns are present in tariffs table
   ```

## Что было исправлено

### Файлы изменены:

1. **backend/database.py** - добавлена проверка и миграция таблицы `tariffs` в функцию `ensure_database_compatibility()`

2. **backend/api_admin.py** - улучшена обработка ошибок в эндпоинте `get_all_users`:
   - Добавлена безопасная загрузка тарифа через явный запрос к БД
   - Добавлена обработка ошибок для каждого пользователя отдельно
   - Добавлено детальное логирование

3. **backend/migrate_tariffs_add_sport_columns.py** - создан отдельный скрипт миграции для ручного применения

### Схема таблицы tariffs после миграции:

```sql
CREATE TABLE tariffs (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    type VARCHAR NOT NULL UNIQUE,
    view_full_plan INTEGER DEFAULT 0,
    view_two_weeks INTEGER DEFAULT 1,
    allow_running INTEGER DEFAULT 1,      -- Новая колонка
    allow_cycling INTEGER DEFAULT 0,      -- Новая колонка
    allow_swimming INTEGER DEFAULT 0,     -- Новая колонка
    allow_triathlon INTEGER DEFAULT 0,    -- Новая колонка
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

## Дополнительная информация

- Миграция безопасна и не удаляет существующие данные
- Все существующие тарифы сохраняют свои ID и связи с пользователями
- Миграция идемпотентна - можно запускать многократно без побочных эффектов
