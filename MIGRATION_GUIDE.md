# Руководство по миграциям базы данных

## Обзор

Универсальная система миграций базы данных с использованием отдельного Docker контейнера. Поддерживает SQLite, PostgreSQL и MySQL.

## Структура

```
migrations/
├── Dockerfile              # Docker образ для миграций
├── requirements.txt        # Python зависимости для миграций
└── migration_runner.py     # Основной скрипт миграций

docker-compose.migration.yml # Docker Compose для миграций
migrate.sh                   # Скрипт для Linux/macOS
migrate.bat                  # Скрипт для Windows
env.migration.example        # Пример переменных окружения
```

## Быстрый старт

### 1. SQLite (по умолчанию)

```bash
# Linux/macOS
chmod +x migrate.sh
./migrate.sh

# Windows
migrate.bat

# Или через Docker Compose
docker-compose -f docker-compose.migration.yml run --rm migration
```

### 2. PostgreSQL

```bash
# Через переменную окружения
export DATABASE_URL="postgresql://username:password@localhost:5432/triplan"
./migrate.sh

# Или через профиль Docker Compose
DATABASE_URL="postgresql://username:password@localhost:5432/triplan" \
docker-compose -f docker-compose.migration.yml --profile postgres run --rm migration-postgres
```

### 3. MySQL

```bash
# Через переменную окружения
export DATABASE_URL="mysql://username:password@localhost:3306/triplan"
./migrate.sh

# Или через профиль Docker Compose
DATABASE_URL="mysql://username:password@localhost:3306/triplan" \
docker-compose -f docker-compose.migration.yml --profile mysql run --rm migration-mysql
```

## Опции командной строки

### migrate.sh / migrate.bat

```bash
# Основные опции
-d, --database URL     URL базы данных
-e, --env FILE         Файл с переменными окружения
-h, --help             Показать справку
-v, --verbose          Подробный вывод
--dry-run              Показать что будет выполнено
--check                Только проверить схему БД
```

### Примеры использования

```bash
# Проверить схему базы данных
./migrate.sh --check

# Показать что будет выполнено (без фактического выполнения)
./migrate.sh --dry-run

# Миграция конкретной базы данных
./migrate.sh -d "sqlite:///./production.db"

# Использовать файл переменных окружения
./migrate.sh -e .env.migration

# Подробный вывод
./migrate.sh -v
```

## Переменные окружения

### Основные

- `DATABASE_URL` - URL базы данных (по умолчанию: `sqlite:///./triplan.db`)
- `POSTGRES_URL` - URL PostgreSQL базы данных
- `MYSQL_URL` - URL MySQL базы данных

### Форматы URL

```bash
# SQLite
DATABASE_URL=sqlite:///./triplan.db
DATABASE_URL=sqlite:////absolute/path/to/database.db

# PostgreSQL
DATABASE_URL=postgresql://username:password@host:port/database
DATABASE_URL=postgresql://user:pass@localhost:5432/triplan

# MySQL
DATABASE_URL=mysql://username:password@host:port/database
DATABASE_URL=mysql://user:pass@localhost:3306/triplan
```

## Текущие миграции

### migration_add_user_competition_fields

Добавляет поля в таблицу `users`:
- `competition_date` (DATE, nullable)
- `competition_type` (VARCHAR, nullable)

## Добавление новых миграций

### 1. Создание функции миграции

В файле `migrations/migration_runner.py` добавьте новую функцию:

```python
def migration_your_new_migration(self):
    """Описание миграции"""
    success = True
    
    # Ваша логика миграции
    if not self.add_column("table_name", "column_name", "VARCHAR", nullable=True):
        success = False
    
    return success
```

### 2. Регистрация миграции

Добавьте миграцию в список `migrations` в методе `run_all_migrations`:

```python
migrations = [
    ("add_user_competition_fields", self.migration_add_user_competition_fields),
    ("your_new_migration", self.migration_your_new_migration),  # Добавить здесь
]
```

## Безопасность

### Production рекомендации

1. **Резервное копирование**
   ```bash
   # SQLite
   cp triplan.db triplan.db.backup
   
   # PostgreSQL
   pg_dump -h localhost -U username triplan > backup.sql
   
   # MySQL
   mysqldump -h localhost -u username triplan > backup.sql
   ```

2. **Тестирование миграций**
   ```bash
   # Сначала проверьте что будет выполнено
   ./migrate.sh --dry-run
   
   # Затем выполните на тестовой базе
   ./migrate.sh -d "sqlite:///./test.db"
   ```

3. **Мониторинг**
   ```bash
   # Проверьте схему после миграции
   ./migrate.sh --check
   ```

## Troubleshooting

### Общие проблемы

1. **Docker не найден**
   ```bash
   # Установите Docker
   # Ubuntu/Debian
   sudo apt-get install docker.io docker-compose
   
   # macOS
   brew install docker docker-compose
   
   # Windows
   # Скачайте Docker Desktop
   ```

2. **Ошибки подключения к базе данных**
   - Проверьте URL базы данных
   - Убедитесь что база данных доступна
   - Проверьте права доступа

3. **Ошибки миграций**
   - Проверьте логи контейнера
   - Убедитесь что база данных не заблокирована
   - Проверьте существование таблиц

### Логи и отладка

```bash
# Подробный вывод
./migrate.sh -v

# Проверка схемы
./migrate.sh --check

# Логи Docker контейнера
docker-compose -f docker-compose.migration.yml run --rm migration
```

## CI/CD интеграция

### GitHub Actions

```yaml
name: Database Migration
on:
  push:
    branches: [main]

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run migrations
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          chmod +x migrate.sh
          ./migrate.sh
```

### GitLab CI

```yaml
migrate:
  stage: deploy
  image: docker:latest
  services:
    - docker:dind
  script:
    - export DATABASE_URL="$DATABASE_URL"
    - chmod +x migrate.sh
    - ./migrate.sh
  only:
    - main
```

## Мониторинг и уведомления

### Slack уведомления

```bash
# После успешной миграции
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"✅ Database migration completed successfully"}' \
  $SLACK_WEBHOOK_URL

# После ошибки
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"❌ Database migration failed"}' \
  $SLACK_WEBHOOK_URL
```

## Поддержка

При возникновении проблем:

1. Проверьте логи миграции
2. Убедитесь в корректности URL базы данных
3. Проверьте права доступа к базе данных
4. Создайте issue с подробным описанием проблемы

