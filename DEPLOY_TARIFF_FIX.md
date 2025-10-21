# Инструкция по деплою исправления тарифов

## Проблема
На странице администрирования не работает изменение тарифа пользователя из-за отсутствия колонок `allow_running`, `allow_cycling`, `allow_swimming`, `allow_triathlon` в таблице `tariffs`.

## Исправленные файлы
1. `backend/database.py` - добавлена автоматическая миграция
2. `backend/api_admin.py` - улучшена обработка ошибок в `get_all_users`
3. `backend/migrate_tariffs_add_sport_columns.py` - скрипт для ручной миграции

## Шаги деплоя

### Вариант 1: Автоматический деплой (рекомендуется)

```bash
# 1. Закоммитьте изменения
git add .
git commit -m "fix: добавлена миграция для таблицы tariffs и исправлена обработка ошибок в админке"
git push

# 2. На сервере обновите код
cd /path/to/triplan
git pull

# 3. Пересоберите и перезапустите контейнеры
docker-compose down
docker-compose up -d --build

# 4. Проверьте логи - должно быть сообщение о миграции
docker-compose logs backend | grep -i tariff
```

### Вариант 2: Без перезапуска контейнеров

Если нужно применить миграцию без перезапуска:

```bash
# 1. Скопируйте файл миграции в контейнер
docker cp backend/migrate_tariffs_add_sport_columns.py backend:/app/

# 2. Выполните миграцию
docker exec -it backend python /app/migrate_tariffs_add_sport_columns.py

# 3. Перезапустите только backend (мягкий рестарт)
docker-compose restart backend
```

### Вариант 3: Прямой доступ к БД (для экспертов)

```bash
# 1. Зайдите в контейнер
docker exec -it backend bash

# 2. Откройте SQLite
sqlite3 /app/data/triplan.db

# 3. Выполните SQL команды
ALTER TABLE tariffs ADD COLUMN allow_running INTEGER DEFAULT 1;
ALTER TABLE tariffs ADD COLUMN allow_cycling INTEGER DEFAULT 0;
ALTER TABLE tariffs ADD COLUMN allow_swimming INTEGER DEFAULT 0;
ALTER TABLE tariffs ADD COLUMN allow_triathlon INTEGER DEFAULT 0;

UPDATE tariffs SET allow_running = 1;
UPDATE tariffs SET allow_cycling = 1, allow_swimming = 1, allow_triathlon = 1 WHERE type = 'PRO';

.quit

# 4. Выйдите из контейнера
exit
```

## Проверка работоспособности

После деплоя проверьте:

### 1. Логи миграции
```bash
docker-compose logs backend | tail -50
```

Должны быть строки:
```
[OK] All required columns are present in tariffs table
[OK] Database compatibility check completed
```

### 2. Страница администрирования
- Откройте https://icanrun.ru/admin/users
- Страница должна загрузиться без ошибок
- Попробуйте изменить тариф пользователя - должно работать

### 3. Проверка структуры таблицы
```bash
docker exec -it backend python -c "
import sqlite3
conn = sqlite3.connect('/app/data/triplan.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(tariffs)')
columns = [row[1] for row in cursor.fetchall()]
print('Columns:', columns)
print('Has allow_running:', 'allow_running' in columns)
print('Has allow_cycling:', 'allow_cycling' in columns)
print('Has allow_swimming:', 'allow_swimming' in columns)
print('Has allow_triathlon:', 'allow_triathlon' in columns)
conn.close()
"
```

Вывод должен быть:
```
Has allow_running: True
Has allow_cycling: True
Has allow_swimming: True
Has allow_triathlon: True
```

## Откат изменений (если что-то пошло не так)

```bash
# 1. Откатите код
git reset --hard HEAD~1

# 2. Перезапустите контейнеры
docker-compose down
docker-compose up -d --build
```

## Важные заметки

- ✅ Миграция безопасна - не удаляет данные
- ✅ Миграция идемпотентна - можно запускать многократно
- ✅ Автоматически запускается при старте приложения
- ✅ Не требует ручного вмешательства

## Контакты для помощи

Если возникли проблемы:
1. Проверьте логи: `docker-compose logs backend`
2. Откройте issue в репозитории
3. Свяжитесь с разработчиком
