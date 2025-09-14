#!/bin/bash

# Triplan Quick Start Script
# Скрипт для быстрого запуска проекта Triplan

echo "🚀 Запуск Triplan..."
echo "==================="

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Пожалуйста, установите Docker и Docker Compose."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Пожалуйста, установите Docker Compose."
    exit 1
fi

# Создаем .env файл из примера, если его нет
if [ ! -f .env ]; then
    echo "📝 Создаем .env файл из примера..."
    cp .env.example .env
    echo "✅ .env файл создан. Отредактируйте его при необходимости."
fi

# Выбор режима запуска
echo ""
echo "Выберите режим запуска:"
echo "1) Продакшн режим (по умолчанию)"
echo "2) Режим разработки"
echo "3) Продакшн с Nginx"
read -p "Введите номер (1-3) [1]: " mode

case $mode in
    2)
        echo "🔧 Запуск в режиме разработки..."
        docker-compose -f docker-compose.dev.yml up -d --build
        ;;
    3)
        echo "🏭 Запуск в продакшн режиме с Nginx..."
        docker-compose --profile production up -d --build
        ;;
    *)
        echo "🏭 Запуск в продакшн режиме..."
        docker-compose up -d --build
        ;;
esac

# Ожидание запуска сервисов
echo ""
echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверка статуса
echo ""
echo "📊 Статус сервисов:"
docker-compose ps

# Проверка здоровья backend
echo ""
echo "🔍 Проверка backend..."
if curl -f http://localhost:8000/api/v1/health &> /dev/null; then
    echo "✅ Backend работает: http://localhost:8000"
    echo "📖 API документация: http://localhost:8000/docs"
else
    echo "⚠️  Backend еще запускается или есть проблемы"
fi

# Проверка frontend
echo ""
echo "🔍 Проверка frontend..."
if curl -f http://localhost:3000 &> /dev/null; then
    echo "✅ Frontend работает: http://localhost:3000"
else
    echo "⚠️  Frontend еще запускается или есть проблемы"
fi

echo ""
echo "🎉 Запуск завершен!"
echo ""
echo "📱 Доступные адреса:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Полезные команды:"
echo "   docker-compose logs -f     # Просмотр логов"
echo "   docker-compose down        # Остановка"
echo "   make help                  # Все доступные команды"
echo ""
