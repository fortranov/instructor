#!/bin/bash

# Скрипт для сборки Docker образа Triplan Backend Service

echo "🐳 Сборка Docker образа Triplan Backend Service..."

# Сборка образа
docker build -t triplan-backend:latest .

# Проверка успешности сборки
if [ $? -eq 0 ]; then
    echo "✅ Docker образ успешно собран!"
    echo "📦 Образ: triplan-backend:latest"
    echo ""
    echo "🚀 Для запуска используйте:"
    echo "   docker run -p 8000:8000 triplan-backend:latest"
    echo "   или"
    echo "   docker-compose up"
else
    echo "❌ Ошибка при сборке Docker образа"
    exit 1
fi
