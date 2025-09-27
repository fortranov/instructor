#!/bin/bash

# Скрипт для запуска миграций базы данных на production сервере

# Проверяем, что мы в правильной директории
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found. Please run this script from the backend directory."
    exit 1
fi

echo "Starting database migration..."

# Вариант 1: Через переменную окружения (автоматический запуск при старте)
echo "Setting RUN_MIGRATIONS=true and restarting backend..."
export RUN_MIGRATIONS=true
python main.py &

# Ждем немного и проверяем статус
sleep 5
if pgrep -f "python main.py" > /dev/null; then
    echo "Backend started with migrations enabled"
    echo "Migrations should be running..."
    sleep 10
    echo "Stopping backend..."
    pkill -f "python main.py"
else
    echo "Failed to start backend"
    exit 1
fi

# Вариант 2: Через HTTP endpoint (если ADMIN_MIGRATION_TOKEN установлен)
if [ ! -z "$ADMIN_MIGRATION_TOKEN" ]; then
    echo "Attempting migration via HTTP endpoint..."
    
    # Запускаем backend в фоне
    python main.py &
    BACKEND_PID=$!
    
    # Ждем запуска
    sleep 5
    
    # Выполняем миграцию через HTTP
    curl -X POST "http://localhost:8000/api/v1/admin/migrate" \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $ADMIN_MIGRATION_TOKEN"
    
    # Останавливаем backend
    kill $BACKEND_PID
else
    echo "ADMIN_MIGRATION_TOKEN not set. Skipping HTTP migration."
fi

# Вариант 3: Прямой запуск миграций
echo "Running direct migration..."
python -c "from db_migrations import run_migrations; run_migrations()"

echo "Migration completed!"
