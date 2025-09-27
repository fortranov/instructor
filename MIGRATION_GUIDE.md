# Руководство по миграциям базы данных

## Варианты запуска миграций на production сервере

### 1. Через переменную окружения (рекомендуемый)

Самый простой способ - установить переменную окружения `RUN_MIGRATIONS=true` и перезапустить backend:

```bash
# Linux/macOS
export RUN_MIGRATIONS=true
python main.py

# Windows
set RUN_MIGRATIONS=true
python main.py
```

Миграции выполнятся автоматически при запуске приложения.

### 2. Через HTTP endpoint

Если backend уже запущен, можно выполнить миграции через API:

```bash
# Установить токен безопасности
export ADMIN_MIGRATION_TOKEN="your-secret-token"

# Запустить backend (если не запущен)
python main.py &

# Выполнить миграцию
curl -X POST "http://localhost:8000/api/v1/admin/migrate" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your-secret-token"
```

### 3. Прямой запуск миграций

Без запуска всего приложения:

```bash
cd backend
python -c "from migrations import run_migrations; run_migrations()"
```

### 4. Через готовые скрипты

Используйте готовые скрипты:

```bash
# Linux/macOS
chmod +x backend/run_migration.sh
./backend/run_migration.sh

# Windows
backend\run_migration.bat
```

### 5. Через Docker (без отдельного контейнера)

Если используете Docker Compose:

```bash
# Вариант 1: Прямая миграция
docker-compose -f docker-compose.migration.yml run --rm migration

# Вариант 2: Через HTTP endpoint
ADMIN_MIGRATION_TOKEN="your-secret-token" docker-compose -f docker-compose.migration.yml run --rm backend-migration
```

### 6. Через существующий контейнер

Если backend уже запущен в контейнере:

```bash
# Выполнить команду в существующем контейнере
docker exec -it <container_name> python -c "from migrations import run_migrations; run_migrations()"

# Или через docker-compose
docker-compose exec backend python -c "from migrations import run_migrations; run_migrations()"
```

## Безопасность

- Установите переменную `ADMIN_MIGRATION_TOKEN` для защиты endpoints миграций
- В production используйте сложный токен
- Миграции выполняются идемпотентно - безопасно запускать несколько раз

## Проверка схемы базы данных

Для проверки текущей схемы:

```bash
# Через API
curl "http://localhost:8000/api/v1/admin/schema"

# Прямая проверка
python -c "from migrations import check_database_schema; print(check_database_schema())"
```

## Логирование

Все миграции логируются. Проверьте логи backend приложения для отслеживания процесса миграции.

## Откат изменений

Текущие миграции не имеют автоматического отката. Для отката нужно:

1. Создать резервную копию базы данных перед миграцией
2. При необходимости восстановить из резервной копии

## Примеры для production

### Kubernetes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: migration
spec:
  containers:
  - name: migration
    image: your-backend-image
    env:
    - name: RUN_MIGRATIONS
      value: "true"
    - name: DB_PATH
      value: "/data/triplan.db"
    volumeMounts:
    - name: database
      mountPath: /data
  restartPolicy: Never
```

### Systemd service

```ini
[Unit]
Description=Triplan Migration
After=network.target

[Service]
Type=oneshot
Environment=RUN_MIGRATIONS=true
WorkingDirectory=/opt/triplan/backend
ExecStart=/usr/bin/python3 main.py
User=triplan

[Install]
WantedBy=multi-user.target
```

## Мониторинг

После миграции проверьте:

1. Логи приложения на наличие ошибок
2. Схему базы данных через API endpoint
3. Функциональность приложения (регистрация, создание планов)
