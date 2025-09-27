# Система миграций базы данных

## Быстрый запуск

### 1. Простой способ (без Docker)
```bash
# Из корневой папки проекта
python run-migration.py

# Или напрямую
cd migrations
python migration_runner.py
```

### 2. Через Docker
```bash
# Из корневой папки проекта
docker-compose -f docker-compose.migration.yml run --rm migration
```

### 3. Через скрипты
```bash
# Linux/macOS
./migrate.sh

# Windows
.\migrate.bat
```

## Поддерживаемые базы данных

- **SQLite** (по умолчанию)
- **PostgreSQL**
- **MySQL**

## Текущие миграции

1. **add_user_competition_fields** - добавляет поля `competition_date` и `competition_type` в таблицу `users`

## Добавление новых миграций

1. Создайте функцию миграции в `migration_runner.py`
2. Добавьте её в список `migrations` в методе `run_all_migrations`

Пример:
```python
def migration_your_new_migration(self, migrator):
    """Описание миграции"""
    success = True
    
    # Ваша логика
    if not migrator.add_column("table_name", "column_name", "VARCHAR", nullable=True):
        success = False
    
    return success
```

