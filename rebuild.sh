#!/bin/bash

# Скрипт для полной пересборки Docker образов

echo "🔄 Очистка и пересборка Triplan..."
echo "==================================="

echo "📦 Остановка и удаление контейнеров..."
docker-compose down

echo "🧹 Удаление старых образов..."
docker-compose down --rmi all

echo "🔨 Пересборка без кэша..."
docker-compose build --no-cache

echo "🚀 Запуск обновленных сервисов..."
docker-compose up -d

echo "✅ Пересборка завершена!"
echo ""
echo "📱 Проверьте доступность:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000/docs"
echo ""
