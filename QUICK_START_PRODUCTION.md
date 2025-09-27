# Быстрый старт для продакшена

## 🚀 Запуск в продакшене за 5 минут

### 1. Подготовка

```bash
# Клонируйте проект
git clone <repository-url>
cd triplan

# Скопируйте файл окружения
cp env.example .env

# Отредактируйте .env (ОБЯЗАТЕЛЬНО измените SECRET_KEY и ADMIN_MIGRATION_TOKEN!)
nano .env
```

### 2. Настройка переменных окружения

Минимальные настройки в `.env`:

```bash
SECRET_KEY=your-super-secret-key-min-32-characters-long
ADMIN_MIGRATION_TOKEN=your-admin-token-for-migrations
DB_PATH=/app/data/triplan.db
```

### 3. Запуск

```bash
# Полная настройка и запуск
make setup
make deploy
```

### 4. Проверка

```bash
# Проверить статус
make status

# Проверить здоровье
make health

# Посмотреть логи
make logs
```

## 📋 Основные команды

```bash
# Управление сервисами
make up          # Запустить
make down        # Остановить
make restart     # Перезапустить

# Миграции
make migrate     # Выполнить миграции
make backup      # Создать бэкап
make rollback    # Откатить изменения

# Мониторинг
make status      # Статус сервисов
make logs        # Логи
make health      # Проверка здоровья
```

## 🛠 Устранение неполадок

### Проблемы с миграциями

```bash
# Проверить схему БД
make check

# Валидировать миграции
make validate

# Откатить изменения
make rollback
```

### Проблемы с сервисами

```bash
# Перезапустить все
make restart

# Посмотреть детальные логи
make logs-backend
make logs-migration
```

### Проблемы с Docker

```bash
# Очистить и пересобрать
make clean
make build
make deploy
```

## 🔒 Безопасность

1. **ОБЯЗАТЕЛЬНО измените** `SECRET_KEY` и `ADMIN_MIGRATION_TOKEN` в `.env`
2. Настройте SSL сертификаты в `nginx/ssl/`
3. Обновите домен в `nginx/nginx.conf`

## 📊 Мониторинг

- **API документация**: `https://yourdomain.com/docs`
- **Health check**: `https://yourdomain.com/api/v1/health`
- **Схема БД**: `https://yourdomain.com/api/v1/admin/schema`

## 🆘 Поддержка

При проблемах:

1. Проверьте логи: `make logs`
2. Проверьте статус: `make status`
3. Проверьте здоровье: `make health`
4. Создайте бэкап: `make backup`
5. Откатите изменения: `make rollback`

## 📁 Структура проекта

```
triplan/
├── backend/                 # Backend код
├── frontend/               # Frontend код
├── nginx/                  # Nginx конфигурация
├── scripts/                # Скрипты миграций
├── data/                   # База данных
├── backups/                # Резервные копии
├── logs/                   # Логи
├── docker-compose.production.yml
├── Makefile
└── .env                    # Переменные окружения
```
