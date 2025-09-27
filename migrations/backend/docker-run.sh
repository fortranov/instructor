#!/bin/bash

# Скрипт для запуска Triplan Backend Service в Docker

echo "🐳 Запуск Triplan Backend Service в Docker..."

# Проверяем, существует ли образ
if ! docker image inspect triplan-backend:latest >/dev/null 2>&1; then
    echo "📦 Образ не найден, выполняем сборку..."
    ./docker-build.sh
fi

echo "🚀 Запуск контейнера..."
echo "📝 Документация API: http://localhost:8000/docs"
echo "🏥 Health check: http://localhost:8000/api/v1/health"
echo "🔧 Для остановки нажмите Ctrl+C"
echo "-" * 50

# Запуск контейнера
docker run -it --rm \
    -p 8000:8000 \
    --name triplan-backend \
    triplan-backend:latest
