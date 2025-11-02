#!/bin/bash
# Entrypoint скрипт для автоматического применения миграций при старте контейнера

set -e

echo "========================================"
echo "Starting Triplan Backend"
echo "========================================"

# Проверяем существование базы данных
if [ -f "/app/data/triplan.db" ]; then
    echo "Database found: /app/data/triplan.db"

    # Применяем миграции автоматически
    echo "Checking and applying migrations..."
    python migrate_add_strength_training.py /app/data/triplan.db

    if [ $? -eq 0 ]; then
        echo "Migrations applied successfully"
    else
        echo "WARNING: Migration failed, but continuing..."
    fi
else
    echo "Database not found, will be created on first request"
fi

echo "========================================"
echo "Starting application server..."
echo "========================================"

# Запускаем основное приложение
exec "$@"
