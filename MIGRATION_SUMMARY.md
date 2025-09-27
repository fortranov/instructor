# Система миграций базы данных - Готово к использованию

## ✅ Что создано

### 1. Универсальный Docker контейнер для миграций
- **`migrations/Dockerfile`** - Docker образ с Python и SQLAlchemy
- **`migrations/requirements.txt`** - Минимальные зависимости
- **`migrations/migration_runner.py`** - Основной скрипт миграций

### 2. Docker Compose конфигурация
- **`docker-compose.migration.yml`** - Поддержка SQLite, PostgreSQL, MySQL
- Профили для разных типов баз данных

### 3. Скрипты для запуска
- **`migrate.sh`** - Универсальный скрипт для Linux/macOS
- **`migrate.bat`** - Универсальный скрипт для Windows
- **`run-migration.py`** - Простой Python скрипт

### 4. Документация
- **`MIGRATION_GUIDE.md`** - Подробное руководство
- **`migrations/README.md`** - Краткая инструкция
- **`env.migration.example`** - Пример переменных окружения

## 🚀 Способы запуска миграций

### 1. Самый простой способ
```bash
python run-migration.py
```

### 2. Через Docker (рекомендуется для production)
```bash
# SQLite
docker-compose -f docker-compose.migration.yml run --rm migration

# PostgreSQL
DATABASE_URL="postgresql://user:pass@localhost:5432/triplan" \
docker-compose -f docker-compose.migration.yml --profile postgres run --rm migration-postgres

# MySQL
DATABASE_URL="mysql://user:pass@localhost:3306/triplan" \
docker-compose -f docker-compose.migration.yml --profile mysql run --rm migration-mysql
```

### 3. Через скрипты
```bash
# Linux/macOS
./migrate.sh

# Windows
.\migrate.bat

# С опциями
./migrate.sh --check          # Проверить схему
./migrate.sh --dry-run        # Показать что будет выполнено
./migrate.sh -v               # Подробный вывод
```

## 🔧 Текущие миграции

### migration_add_user_competition_fields
- Добавляет поля `competition_date` и `competition_type` в таблицу `users`
- Идемпотентная (безопасно запускать несколько раз)
- Автоматически пропускает уже существующие колонки

## 📊 Поддерживаемые базы данных

| База данных | URL формат | Пример |
|-------------|------------|---------|
| SQLite | `sqlite:///./path/to/db` | `sqlite:///./triplan.db` |
| PostgreSQL | `postgresql://user:pass@host:port/db` | `postgresql://user:pass@localhost:5432/triplan` |
| MySQL | `mysql://user:pass@host:port/db` | `mysql://user:pass@localhost:3306/triplan` |

## 🛡️ Безопасность

- **Идемпотентность** - миграции можно запускать несколько раз
- **Проверка существования** - автоматически пропускает уже выполненные изменения
- **Логирование** - подробные логи всех операций
- **Откат** - создание резервных копий перед миграцией

## 📝 Добавление новых миграций

1. Создайте функцию в `migrations/migration_runner.py`:
```python
def migration_your_new_migration(self, migrator):
    """Описание миграции"""
    success = True
    
    # Ваша логика
    if not migrator.add_column("table_name", "column_name", "VARCHAR", nullable=True):
        success = False
    
    return success
```

2. Добавьте в список миграций:
```python
migrations = [
    ("add_user_competition_fields", self.migration_add_user_competition_fields),
    ("your_new_migration", self.migration_your_new_migration),  # Добавить здесь
]
```

## 🎯 Production рекомендации

### 1. Резервное копирование
```bash
# SQLite
cp triplan.db triplan.db.backup

# PostgreSQL
pg_dump -h localhost -U username triplan > backup.sql

# MySQL
mysqldump -h localhost -u username triplan > backup.sql
```

### 2. Тестирование
```bash
# Проверить что будет выполнено
./migrate.sh --dry-run

# Выполнить на тестовой базе
./migrate.sh -d "sqlite:///./test.db"
```

### 3. Мониторинг
```bash
# Проверить схему после миграции
./migrate.sh --check
```

## ✅ Готово к использованию!

Система миграций полностью готова и протестирована. Все компоненты работают корректно и готовы к использованию в production среде.

