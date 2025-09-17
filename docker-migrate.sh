#!/bin/bash
# Скрипт для выполнения миграций в Docker контейнере

set -e  # Остановить выполнение при ошибке

echo "🐳 Запуск миграций в Docker контейнере..."

# Проверить, что база данных доступна
if [ -z "$DB_PATH" ]; then
    export DB_PATH="/app/triplan.db"
fi

echo "📁 Путь к базе данных: $DB_PATH"

# Создать директорию для базы данных если её нет
DB_DIR=$(dirname "$DB_PATH")
if [ ! -d "$DB_DIR" ]; then
    echo "📂 Создание директории для базы данных: $DB_DIR"
    mkdir -p "$DB_DIR"
fi

# Установить права доступа
chmod 755 "$DB_DIR" 2>/dev/null || true

# Выполнить миграции
echo "🔄 Выполнение миграций..."
python run_migrations.py migrate

echo "✅ Миграции завершены успешно!"
