# Руководство по развертыванию в продакшене

## Обзор

Этот документ описывает процесс развертывания Triplan в продакшене с использованием Docker и автоматизированных миграций базы данных.

## Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │────│    Backend      │────│   Database      │
│  (Reverse Proxy)│    │   (FastAPI)     │    │   (SQLite)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │              ┌─────────────────┐
         └──────────────│   Migration     │
                        │   Container     │
                        └─────────────────┘
```

## Быстрый старт

### 1. Подготовка окружения

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd triplan

# Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env файл
```

### 2. Настройка переменных окружения

Создайте файл `.env`:

```bash
# Безопасность
SECRET_KEY=your-super-secret-key-change-in-production
ADMIN_MIGRATION_TOKEN=your-admin-migration-token

# База данных
DB_PATH=/app/data/triplan.db

# Опционально
VALIDATE_ONLY=false
SKIP_BACKUP=false
FORCE_MIGRATION=false
```

### 3. Первоначальная настройка

```bash
# Настройка проекта (создание директорий, SSL сертификатов)
make setup

# Или вручную:
mkdir -p data backups logs nginx/ssl
openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem -days 365 -nodes \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"
```

### 4. Полный деплой

```bash
# Запуск с автоматическими миграциями
make deploy
```

## Управление миграциями

### Автоматические миграции

Миграции выполняются автоматически при деплое:

```bash
# Полный деплой с миграциями
make deploy

# Только миграции
make migrate

# Миграции + проверка схемы
make migrate-check

# Миграции + валидация
make migrate-validate
```

### Ручные миграции

```bash
# Выполнить миграции
./scripts/migrate.sh migrate

# Проверить схему базы данных
./scripts/migrate.sh check

# Валидировать миграции
./scripts/migrate.sh validate

# Создать резервную копию
./scripts/migrate.sh backup

# Откатить к последнему бэкапу
./scripts/migrate.sh rollback
```

### Windows

```cmd
REM Выполнить миграции
scripts\migrate.bat migrate

REM Проверить схему
scripts\migrate.bat check

REM Создать бэкап
scripts\migrate.bat backup
```

## Команды управления

### Основные команды

```bash
# Сборка образов
make build

# Запуск сервисов
make up

# Остановка сервисов
make down

# Перезапуск
make restart

# Просмотр логов
make logs

# Статус сервисов
make status

# Проверка здоровья
make health
```

### Мониторинг

```bash
# Мониторинг в реальном времени
make monitor

# Логи конкретного сервиса
make logs-backend
make logs-migration
```

### Очистка

```bash
# Очистка неиспользуемых ресурсов
make clean

# Полная очистка (включая образы)
make clean-all
```

## Безопасность

### SSL/TLS

1. Замените самоподписанные сертификаты на реальные
2. Обновите `nginx/nginx.conf` с вашими доменами
3. Настройте автоматическое обновление сертификатов

### Переменные окружения

- `SECRET_KEY`: Сложный ключ для JWT токенов
- `ADMIN_MIGRATION_TOKEN`: Токен для защиты endpoints миграций
- Используйте сильные пароли и токены

### Firewall

```bash
# Открыть только необходимые порты
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 8000/tcp  # Блокировать прямой доступ к backend
```

## Резервное копирование

### Автоматические бэкапы

```bash
# Создать бэкап перед миграцией
make backup

# Настроить cron для регулярных бэкапов
0 2 * * * /path/to/triplan/scripts/migrate.sh backup
```

### Восстановление

```bash
# Откат к последнему бэкапу
make rollback

# Восстановление из конкретного бэкапа
cp backups/triplan_backup_20240101_120000 data/triplan.db
make restart
```

## Мониторинг и логирование

### Логи

```bash
# Все логи
docker-compose -f docker-compose.production.yml logs

# Логи backend
docker-compose -f docker-compose.production.yml logs backend

# Логи Nginx
docker-compose -f docker-compose.production.yml logs nginx
```

### Health checks

```bash
# Проверка здоровья API
curl -f https://yourdomain.com/api/v1/health

# Проверка схемы БД
curl -f https://yourdomain.com/api/v1/admin/schema
```

### Мониторинг ресурсов

```bash
# Использование ресурсов
docker stats

# Дисковое пространство
df -h
du -sh data/ backups/ logs/
```

## Обновление

### Обновление кода

```bash
# Остановить сервисы
make down

# Обновить код
git pull origin main

# Пересобрать образы
make build

# Запустить с миграциями
make deploy
```

### Обновление зависимостей

```bash
# Обновить requirements.txt
# Пересобрать образы
make build

# Перезапустить с новой версией
make restart
```

## Устранение неполадок

### Проблемы с миграциями

```bash
# Проверить схему БД
make check

# Валидировать миграции
make validate

# Посмотреть логи миграций
make logs-migration

# Откатить изменения
make rollback
```

### Проблемы с сервисами

```bash
# Статус сервисов
make status

# Логи сервисов
make logs

# Перезапуск
make restart

# Проверка здоровья
make health
```

### Проблемы с базой данных

```bash
# Проверить файл БД
ls -la data/

# Проверить права доступа
ls -la data/triplan.db

# Проверить подключение
docker-compose -f docker-compose.production.yml exec backend python -c "from database import engine; print('DB OK')"
```

## Производительность

### Настройка Nginx

```nginx
# Увеличить worker connections
events {
    worker_connections 2048;
}

# Настройка буферов
proxy_buffering on;
proxy_buffer_size 4k;
proxy_buffers 8 4k;
```

### Настройка Docker

```yaml
# Ограничения ресурсов
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
    reservations:
      memory: 256M
      cpus: '0.25'
```

## Масштабирование

### Горизонтальное масштабирование

```yaml
# docker-compose.production.yml
services:
  backend:
    deploy:
      replicas: 3
    # ... остальная конфигурация
```

### Load balancer

```nginx
# nginx/nginx.conf
upstream triplan_backend {
    server backend_1:8000;
    server backend_2:8000;
    server backend_3:8000;
}
```

## Поддержка

### Логи для диагностики

```bash
# Собрать все логи
mkdir -p diagnostics/$(date +%Y%m%d_%H%M%S)
docker-compose -f docker-compose.production.yml logs > diagnostics/$(date +%Y%m%d_%H%M%S)/all.log
docker-compose -f docker-compose.production.yml ps > diagnostics/$(date +%Y%m%d_%H%M%S)/status.txt
```

### Контакты

- Документация: `/docs`
- API: `/api/v1`
- Health check: `/api/v1/health`
