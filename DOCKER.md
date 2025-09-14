# Docker Setup для Triplan

Этот документ содержит инструкции по запуску проекта Triplan с использованием Docker и docker-compose.

## 🐳 Структура Docker конфигурации

```
triplan/
├── docker-compose.yml          # Продакшн конфигурация
├── docker-compose.dev.yml      # Конфигурация для разработки
├── .env.example               # Пример переменных окружения
├── nginx/
│   └── nginx.conf             # Конфигурация Nginx
├── backend/
│   └── Dockerfile             # Dockerfile для FastAPI backend
└── frontend/
    ├── Dockerfile             # Dockerfile для Next.js (продакшн)
    └── Dockerfile.dev         # Dockerfile для Next.js (разработка)
```

## 🚀 Быстрый старт

### 1. Подготовка

Убедитесь, что у вас установлены:
- Docker
- Docker Compose

### 2. Настройка переменных окружения

```bash
# Скопируйте пример файла окружения
cp .env.example .env

# Отредактируйте .env файл, установив ваши значения
# Особенно важно изменить SECRET_KEY для продакшена
```

### 3. Запуск в режиме продакшена

```bash
# Сборка и запуск всех сервисов
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

Сервисы будут доступны по адресам:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Запуск в режиме разработки

```bash
# Запуск с hot reload для разработки
docker-compose -f docker-compose.dev.yml up --build

# Или в фоновом режиме
docker-compose -f docker-compose.dev.yml up -d --build
```

## 📋 Доступные команды

### Основные команды

```bash
# Сборка образов без запуска
docker-compose build

# Запуск сервисов
docker-compose up

# Запуск в фоновом режиме
docker-compose up -d

# Остановка сервисов
docker-compose down

# Остановка с удалением volumes
docker-compose down -v

# Просмотр логов
docker-compose logs

# Просмотр логов конкретного сервиса
docker-compose logs backend
docker-compose logs frontend
```

### Команды для разработки

```bash
# Запуск в режиме разработки
docker-compose -f docker-compose.dev.yml up

# Остановка режима разработки
docker-compose -f docker-compose.dev.yml down

# Пересборка только одного сервиса
docker-compose build backend
docker-compose build frontend
```

### Полезные команды

```bash
# Выполнение команд внутри контейнера
docker-compose exec backend bash
docker-compose exec frontend sh

# Просмотр состояния контейнеров
docker-compose ps

# Просмотр использования ресурсов
docker stats
```

## 🏗️ Архитектура

### Продакшн режим

```
[Client] → [Nginx:80] → [Frontend:3000]
                    ↘   [Backend:8000]
```

- **Nginx** - reverse proxy, обрабатывает статические файлы и маршрутизацию
- **Frontend** - Next.js приложение в standalone режиме
- **Backend** - FastAPI сервис с SQLite базой данных

### Режим разработки

```
[Client] → [Frontend:3000] → [Backend:8000]
```

- **Frontend** - Next.js в dev режиме с hot reload
- **Backend** - FastAPI с hot reload

## 🔧 Конфигурация

### Переменные окружения

#### Backend
- `SECRET_KEY` - Секретный ключ для JWT токенов
- `DB_PATH` - Путь к файлу базы данных SQLite
- `PYTHONPATH` - Python путь (обычно /app)
- `PYTHONUNBUFFERED` - Отключение буферизации Python вывода

#### Frontend
- `NODE_ENV` - Режим работы (development/production)
- `NEXT_PUBLIC_API_URL` - URL backend API для клиентской части

### Volumes

- `triplan_data` - Постоянное хранилище для базы данных SQLite
- `triplan_data_dev` - Хранилище для разработки

### Networks

- `triplan-network` - Внутренняя сеть для взаимодействия сервисов
- `triplan-network-dev` - Сеть для режима разработки

## 🔍 Мониторинг и отладка

### Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Логи backend
docker-compose logs -f backend

# Логи frontend  
docker-compose logs -f frontend

# Логи nginx (только в продакшне)
docker-compose logs -f nginx
```

### Health checks

Backend имеет встроенную проверку здоровья:

```bash
# Проверка статуса
curl http://localhost:8000/api/v1/health

# Через Docker
docker-compose exec backend curl -f http://localhost:8000/api/v1/health
```

### Подключение к контейнерам

```bash
# Backend (Python/bash)
docker-compose exec backend bash

# Frontend (Node/sh)
docker-compose exec frontend sh

# Nginx (только в продакшне)
docker-compose exec nginx sh
```

## 🚀 Развертывание в продакшене

### С Nginx (рекомендуется)

```bash
# Запуск с Nginx reverse proxy
docker-compose --profile production up -d --build
```

### Без Nginx

```bash
# Запуск только backend и frontend
docker-compose up -d --build backend frontend
```

### Настройка SSL

1. Поместите SSL сертификаты в `nginx/ssl/`
2. Раскомментируйте HTTPS блок в `nginx/nginx.conf`
3. Обновите домен в конфигурации
4. Перезапустите контейнеры

## 🛠️ Разработка

### Добавление новых зависимостей

#### Backend
```bash
# Добавьте пакет в requirements.txt
echo "new-package==1.0.0" >> backend/requirements.txt

# Пересоберите образ
docker-compose build backend
```

#### Frontend
```bash
# Подключитесь к контейнеру
docker-compose exec frontend sh

# Установите пакет
npm install new-package

# Или остановите контейнер и пересоберите образ
```

### Работа с базой данных

```bash
# Подключение к backend контейнеру
docker-compose exec backend bash

# Запуск Python интерпретатора
python

# Работа с базой данных
>>> from database import SessionLocal, engine
>>> from sqlalchemy import text
>>> session = SessionLocal()
>>> result = session.execute(text("SELECT * FROM users"))
>>> print(result.fetchall())
```

## ❗ Troubleshooting

### Общие проблемы

1. **Порты заняты**
   ```bash
   # Проверьте, какие порты используются
   netstat -tulpn | grep :3000
   netstat -tulpn | grep :8000
   
   # Измените порты в docker-compose.yml если нужно
   ```

2. **Проблемы с разрешениями**
   ```bash
   # Убедитесь, что Docker имеет доступ к файлам
   sudo chown -R $USER:$USER .
   ```

3. **Ошибки сборки**
   ```bash
   # Очистите Docker кэш
   docker system prune -a
   
   # Пересоберите без кэша
   docker-compose build --no-cache
   ```

4. **База данных не создается**
   ```bash
   # Проверьте volume
   docker volume ls | grep triplan
   
   # Удалите volume и пересоздайте
   docker-compose down -v
   docker-compose up --build
   ```

### Логи для отладки

```bash
# Подробные логи Docker
docker-compose up --build --verbose

# Логи конкретного сервиса
docker-compose logs --tail=100 backend

# Следить за логами в реальном времени
docker-compose logs -f --tail=0
```

---

**Triplan Docker Setup** - готовая инфраструктура для разработки и продакшена! 🐳
