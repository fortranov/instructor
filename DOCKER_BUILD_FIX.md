# Исправление ошибки Docker сборки

## Проблема
```
failed to solve: failed to compute cache key: failed to calculate checksum of ref 5763501c-1ed1-4203-9386-b937937d406b::kh2qdwatx6pnr3jr7k0klet09: "/app/public": not found
```

## Исправления

### 1. Обновлен package.json
Перенесены зависимости сборки из `devDependencies` в `dependencies`:
- `tailwindcss`
- `autoprefixer` 
- `postcss`

### 2. Улучшен Dockerfile
- Разделен на отдельные стадии: `deps`, `builder`, `runner`
- Правильное копирование зависимостей и файлов
- Добавлен `--chown=nextjs:nodejs` для правильных прав доступа

### 3. Добавлен .dockerignore
Исключает ненужные файлы из контекста сборки для ускорения процесса.

### 4. Обновлен next.config.ts
- Динамическая настройка backend URL через переменную окружения
- Поддержка как development, так и production режимов

### 5. Обновлен docker-compose.yml
Добавлена переменная окружения `BACKEND_URL=http://backend:8000` для frontend.

## Сборка и запуск

### Локальная сборка
```bash
cd frontend
npm install
npm run build
```

### Docker сборка
```bash
# Сборка отдельного образа
docker build -t triplan-frontend ./frontend

# Сборка всего проекта
docker-compose build

# Запуск
docker-compose up -d
```

### Проверка
После запуска проект будет доступен по адресу:
- http://localhost (через nginx)

## Структура файлов

```
frontend/
├── Dockerfile              # Улучшенный multi-stage Dockerfile
├── .dockerignore           # Исключения для Docker контекста
├── next.config.ts          # Конфигурация с поддержкой переменных окружения
├── package.json            # Обновленные зависимости
└── public/                 # Статические файлы (должна существовать)
```

## Переменные окружения

### Frontend
- `NODE_ENV=production` - режим продакшена
- `BACKEND_URL=http://backend:8000` - URL backend сервиса

### Backend  
- `PYTHONPATH=/app`
- `SECRET_KEY=your-secret-key-change-in-production`
- `DB_PATH=/app/data/triplan.db`
