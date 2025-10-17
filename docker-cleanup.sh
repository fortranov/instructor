#!/bin/bash

# Скрипт для очистки Docker ресурсов

echo "=========================================="
echo "Очистка Docker ресурсов"
echo "=========================================="
echo ""

# Показываем текущее использование
echo "Текущее использование места на диске:"
df -h / | grep -v Filesystem
echo ""

echo "Текущее использование Docker:"
docker system df
echo ""

# Спрашиваем подтверждение
read -p "Вы хотите очистить неиспользуемые Docker ресурсы? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo ""
    echo "Останавливаем контейнеры..."
    docker-compose down
    
    echo ""
    echo "Удаляем остановленные контейнеры..."
    docker container prune -f
    
    echo ""
    echo "Удаляем неиспользуемые образы..."
    docker image prune -a -f
    
    echo ""
    echo "Удаляем неиспользуемые volumes..."
    docker volume prune -f
    
    echo ""
    echo "Очищаем build cache..."
    docker builder prune -a -f
    
    echo ""
    echo "=========================================="
    echo "Очистка завершена!"
    echo "=========================================="
    echo ""
    
    echo "Новое использование места на диске:"
    df -h / | grep -v Filesystem
    echo ""
    
    echo "Новое использование Docker:"
    docker system df
    echo ""
    
    echo "Рекомендация: Теперь можете запустить сборку проекта"
    echo "docker-compose build --no-cache"
else
    echo "Очистка отменена."
fi

