# Система миграций базы данных TriPlan

## Обзор

Система миграций TriPlan позволяет безопасно обновлять структуру базы данных в продакшене без потери данных.

## Структура

```
migrations/
├── __init__.py
├── migration_manager.py          # Менеджер миграций
└── migration_001_add_preferred_workout_days.py  # Пример миграции
```

## Использование

### Локальная разработка

```bash
# Выполнить все ожидающие миграции
python run_migrations.py migrate

# Выполнить миграции до определенной версии
python run_migrations.py migrate --version 001

# Показать статус миграций
python run_migrations.py status

# Откатить до определенной версии
python run_migrations.py rollback --version 000
```

### Продакшен (Docker)

#### Автоматические миграции при запуске

```bash
# Запустить все сервисы (миграции выполнятся автоматически)
docker-compose up -d

# Или только миграции
docker-compose up migrations
```

#### Ручное выполнение миграций

```bash
# Выполнить миграции в запущенном контейнере
docker-compose exec backend python run_migrations.py migrate

# Показать статус
docker-compose exec backend python run_migrations.py status
```

#### Использование скриптов

```bash
# Linux/macOS
chmod +x docker-migrate.sh
./docker-migrate.sh

# Windows
docker-migrate.bat
```

## Создание новой миграции

1. Создайте файл `migrations/migration_XXX_description.py`:

```python
#!/usr/bin/env python3
"""
Миграция XXX: Описание изменений
"""

import sqlite3
import os

# Метаданные миграции
version = "XXX"
description = "Описание изменений"
checksum = "hash_of_migration_content"

def up():
    """Выполнить миграцию"""
    db_path = os.getenv("DB_PATH", "./triplan.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Ваш код миграции здесь
        cursor.execute("ALTER TABLE users ADD COLUMN new_field TEXT")
        conn.commit()
    finally:
        conn.close()

def down():
    """Откатить миграцию"""
    db_path = os.getenv("DB_PATH", "./triplan.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Код отката здесь
        # SQLite не поддерживает DROP COLUMN, нужна пересоздание таблицы
        pass
    finally:
        conn.close()
```

2. Протестируйте миграцию локально:

```bash
python run_migrations.py migrate
python run_migrations.py rollback --version XXX
python run_migrations.py migrate
```

## Отслеживание миграций

Система создает таблицу `schema_migrations` для отслеживания выполненных миграций:

```sql
CREATE TABLE schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(255)
);
```

## Лучшие практики

### 1. Безопасность данных
- Всегда создавайте резервную копию перед миграциями в продакшене
- Тестируйте миграции на копии продакшен данных
- Используйте транзакции для атомарности

### 2. Обратная совместимость
- Реализуйте функцию `down()` для отката
- Избегайте удаления колонок без предварительного предупреждения
- Используйте значения по умолчанию для новых полей

### 3. Производительность
- Для больших таблиц используйте индексы
- Рассмотрите возможность выполнения миграций в фоновом режиме
- Мониторьте время выполнения миграций

### 4. Версионирование
- Используйте последовательную нумерацию (001, 002, 003...)
- Включайте описание изменений в название файла
- Документируйте breaking changes

## Примеры миграций

### Добавление колонки
```python
def up():
    cursor.execute("ALTER TABLE users ADD COLUMN new_field TEXT DEFAULT ''")
    cursor.execute("UPDATE users SET new_field = 'default_value' WHERE new_field IS NULL")
```

### Создание таблицы
```python
def up():
    cursor.execute("""
        CREATE TABLE new_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
```

### Создание индекса
```python
def up():
    cursor.execute("CREATE INDEX idx_users_email ON users (email)")
```

## Мониторинг

### Логи миграций
```bash
# Просмотр логов миграций
docker-compose logs migrations

# Просмотр логов backend после миграций
docker-compose logs backend
```

### Проверка статуса
```bash
# Статус миграций
python run_migrations.py status

# Проверка структуры БД
sqlite3 triplan.db ".schema users"
```

## Устранение неполадок

### Миграция не выполняется
1. Проверьте права доступа к файлу БД
2. Убедитесь, что БД не заблокирована другими процессами
3. Проверьте синтаксис SQL в миграции

### Ошибка отката
1. SQLite не поддерживает некоторые операции отката
2. Для сложных изменений может потребоваться ручной откат
3. Всегда делайте резервные копии перед миграциями

### Конфликт версий
1. Проверьте, что версии миграций уникальны
2. Убедитесь, что все миграции протестированы
3. Используйте `--version` для выполнения до определенной версии

## Интеграция с CI/CD

### GitHub Actions
```yaml
- name: Run migrations
  run: |
    docker-compose up migrations
    docker-compose logs migrations
```

### GitLab CI
```yaml
migrate:
  script:
    - docker-compose up migrations
    - docker-compose logs migrations
```

## Безопасность

- Никогда не коммитьте пароли или секретные ключи в миграции
- Используйте переменные окружения для конфигурации
- Ограничьте доступ к скриптам миграций в продакшене
- Логируйте все операции миграций для аудита
