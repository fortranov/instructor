# Устранение проблемы нехватки места на диске

## Проблема
Ошибка при сборке Docker образа: `ENOSPC: no space left on device`

## Диагностика

### 1. Проверка места на диске
```bash
df -h
```

### 2. Проверка использования Docker
```bash
docker system df
```

## Решение

### Шаг 1: Очистка Docker (рекомендуется)

#### Остановить все контейнеры
```bash
docker-compose down
```

#### Удалить неиспользуемые образы, контейнеры и volumes
```bash
# Полная очистка всех неиспользуемых ресурсов
docker system prune -a --volumes

# Или пошагово:
# Удалить остановленные контейнеры
docker container prune -f

# Удалить неиспользуемые образы
docker image prune -a -f

# Удалить неиспользуемые volumes
docker volume prune -f

# Очистить build cache
docker builder prune -a -f
```

### Шаг 2: Проверка системных логов и кэша
```bash
# Проверить размер логов Docker
sudo du -sh /var/lib/docker/

# Очистить системные логи (если нужно)
sudo journalctl --vacuum-time=7d

# Очистить apt кэш (для Ubuntu/Debian)
sudo apt-get clean
sudo apt-get autoclean
```

### Шаг 3: Оптимизированная пересборка

После очистки пересоберите проект:

```bash
# Сборка без кэша (как вы делали)
docker-compose build --no-cache

# Или только frontend, если проблема только с ним
docker-compose build --no-cache frontend

# Запуск
docker-compose up -d
```

## Альтернативные решения

### Вариант 1: Сборка только измененных сервисов
Если backend уже собран, можно собрать только frontend:
```bash
docker-compose build frontend
docker-compose up -d
```

### Вариант 2: Использование multi-stage build для frontend
Оптимизированный Dockerfile уменьшает финальный размер образа (см. frontend/Dockerfile.optimized)

### Вариант 3: Увеличение места на диске
- Удалить ненужные файлы
- Расширить диск на сервере
- Переместить Docker на другой диск (изменить директорию /var/lib/docker)

## Предотвращение проблемы в будущем

### Регулярная очистка Docker (добавить в cron)
```bash
# Создать скрипт очистки
cat > /usr/local/bin/docker-cleanup.sh << 'EOF'
#!/bin/bash
echo "Cleaning Docker resources..."
docker system prune -f --volumes --filter "until=168h"
echo "Docker cleanup completed"
EOF

chmod +x /usr/local/bin/docker-cleanup.sh

# Добавить в cron (каждую неделю)
sudo crontab -e
# Добавить строку:
# 0 2 * * 0 /usr/local/bin/docker-cleanup.sh > /var/log/docker-cleanup.log 2>&1
```

### Мониторинг места на диске
```bash
# Добавить алерт при заполнении диска > 80%
cat > /usr/local/bin/disk-monitor.sh << 'EOF'
#!/bin/bash
THRESHOLD=80
USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$USAGE" -gt "$THRESHOLD" ]; then
    echo "Warning: Disk usage is at ${USAGE}%"
    # Отправить уведомление (настроить по необходимости)
fi
EOF

chmod +x /usr/local/bin/disk-monitor.sh
```

## Проверка результата

После очистки и пересборки:
```bash
# Проверить, что контейнеры запущены
docker-compose ps

# Проверить логи
docker-compose logs -f

# Проверить оставшееся место
df -h
docker system df
```

## Типичные размеры

Для справки, типичные размеры компонентов проекта:
- Node.js образ с зависимостями: 500-800 MB
- Python образ с зависимостями: 300-500 MB
- npm cache во время установки: 200-400 MB
- Build cache: может накапливаться до нескольких GB

Рекомендуемый минимум свободного места для сборки: **3-5 GB**

