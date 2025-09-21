# Инструкция по развертыванию TriPlan в продакшене

## Быстрый старт

### 1. Подготовка сервера

```bash
# Установить Docker и Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Клонировать репозиторий
git clone <repository-url>
cd triplan
```

### 2. Настройка окружения

```bash
# Создать файл с переменными окружения
cp .env.example .env

# Отредактировать переменные
nano .env
```

Пример `.env` файла:
```env
# Секретный ключ для JWT токенов
SECRET_KEY=your-super-secret-key-change-this-in-production

# Путь к базе данных
DB_PATH=/app/data/triplan.db

# Настройки Nginx (опционально)
NGINX_HOST=your-domain.com
NGINX_SSL_CERT=/path/to/cert.pem
NGINX_SSL_KEY=/path/to/key.pem
```

### 3. Развертывание

#### Автоматическое развертывание (рекомендуется)

```bash
# Запустить все сервисы (включая миграции)
make prod-up

# Или напрямую через Docker Compose
docker-compose up -d
```

#### Пошаговое развертывание

```bash
# 1. Выполнить миграции базы данных
make migrate

# 2. Запустить backend
docker-compose up -d backend

# 3. Запустить frontend
docker-compose up -d frontend

# 4. Запустить nginx
docker-compose up -d nginx
```

### 4. Проверка развертывания

```bash
# Проверить статус сервисов
docker-compose ps

# Проверить логи
make logs

# Проверить здоровье сервисов
make health
```

## Управление миграциями

### Выполнение миграций

```bash
# Автоматически при запуске (рекомендуется)
make prod-up

# Вручную
make migrate

# Проверить статус
make migrate-status
```

### Откат миграций

```bash
# Откатить до определенной версии
make migrate-rollback
# Введите версию при запросе

# Или напрямую
docker-compose exec backend python run_migrations.py rollback --version 001_add_preferred_workout_days
```

## Мониторинг

### Логи

```bash
# Все сервисы
make logs

# Отдельные сервисы
make backend-logs
make frontend-logs
make nginx-logs

# Логи миграций
docker-compose logs migrations
```

### Проверка здоровья

```bash
# Автоматическая проверка
make health

# Ручная проверка
curl http://localhost/api/v1/health
curl http://localhost:3000
```

## Обновление

### Обновление кода

```bash
# 1. Остановить сервисы
make prod-down

# 2. Обновить код
git pull origin main

# 3. Пересобрать и запустить
make prod-up
```

### Обновление с миграциями

```bash
# 1. Создать резервную копию базы данных
docker-compose exec backend cp /app/data/triplan.db /app/data/triplan.db.backup

# 2. Обновить код
git pull origin main

# 3. Выполнить миграции
make migrate

# 4. Запустить сервисы
make prod-up
```

## Резервное копирование

### База данных

```bash
# Создать резервную копию
docker-compose exec backend cp /app/data/triplan.db /app/data/backup-$(date +%Y%m%d-%H%M%S).db

# Восстановить из резервной копии
docker-compose exec backend cp /app/data/backup-20240917-142100.db /app/data/triplan.db
```

### Полная резервная копия

```bash
# Создать архив с данными
docker run --rm -v triplan_triplan_data:/data -v $(pwd):/backup alpine tar czf /backup/triplan-backup-$(date +%Y%m%d).tar.gz -C /data .

# Восстановить из архива
docker run --rm -v triplan_triplan_data:/data -v $(pwd):/backup alpine tar xzf /backup/triplan-backup-20240917.tar.gz -C /data
```

## Безопасность

### SSL сертификаты

```bash
# Получить сертификат Let's Encrypt
certbot certonly --standalone -d your-domain.com

# Обновить nginx.conf
# Указать пути к сертификатам в .env файле
```

### Firewall

```bash
# Открыть только необходимые порты
ufw allow 80
ufw allow 443
ufw allow 22  # SSH
ufw enable
```

## Устранение неполадок

### Проблемы с миграциями

```bash
# Проверить статус миграций
make migrate-status

# Просмотреть логи миграций
docker-compose logs migrations

# Выполнить миграции вручную
docker-compose exec backend python run_migrations.py migrate
```

### Проблемы с базой данных

```bash
# Проверить подключение к БД
docker-compose exec backend python -c "from database import SessionLocal; print('DB OK')"

# Проверить структуру таблиц
docker-compose exec backend sqlite3 /app/data/triplan.db ".schema"
```

### Проблемы с сервисами

```bash
# Перезапустить сервис
make restart-backend
make restart-frontend

# Пересобрать образы
make rebuild
```

## Производительность

### Мониторинг ресурсов

```bash
# Использование ресурсов контейнерами
docker stats

# Логи производительности
docker-compose logs backend | grep -i "slow\|timeout\|error"
```

### Оптимизация

```bash
# Очистка неиспользуемых образов
docker system prune -f

# Очистка логов
docker-compose logs --tail=0 -f > /dev/null
```

## Автоматизация

### Systemd сервис

Создать файл `/etc/systemd/system/triplan.service`:

```ini
[Unit]
Description=TriPlan Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/triplan
ExecStart=/usr/bin/make prod-up
ExecStop=/usr/bin/make prod-down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Активировать сервис
sudo systemctl enable triplan
sudo systemctl start triplan
```

### Cron задачи

```bash
# Добавить в crontab для автоматических резервных копий
0 2 * * * cd /path/to/triplan && make backup-db
```

## Поддержка

При возникновении проблем:

1. Проверьте логи: `make logs`
2. Проверьте статус сервисов: `docker-compose ps`
3. Проверьте здоровье: `make health`
4. Проверьте миграции: `make migrate-status`

Для получения помощи создайте issue в репозитории с:
- Версией Docker и Docker Compose
- Логами ошибок
- Описанием проблемы
