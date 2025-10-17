# Оптимизация Docker для уменьшения размера образов

## Проблема
Текущий `frontend/Dockerfile` создает большой образ, что требует много места на диске при сборке.

## Решение

### Использование оптимизированного Dockerfile

Создан `frontend/Dockerfile.optimized` с multi-stage build, который:
- ✅ Уменьшает финальный размер образа на ~40-50%
- ✅ Использует только production зависимости в финальном образе
- ✅ Улучшает безопасность (непривилегированный пользователь)
- ✅ Кэширует слои для ускорения пересборки

### Как использовать

#### Вариант 1: Заменить текущий Dockerfile

```bash
# На сервере
cd /path/to/triplan
cp frontend/Dockerfile.optimized frontend/Dockerfile
docker-compose build --no-cache frontend
docker-compose up -d
```

#### Вариант 2: Временно использовать для сборки

В `docker-compose.yml` измените:
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile.optimized  # Используем оптимизированный
```

Затем:
```bash
docker-compose build --no-cache frontend
docker-compose up -d
```

## Сравнение размеров

### Обычный Dockerfile
- Все dev зависимости включены
- Размер: ~800-1000 MB
- Временные файлы сборки остаются

### Оптимизированный Dockerfile (multi-stage)
- Только production зависимости
- Размер: ~400-600 MB
- Временные файлы сборки не попадают в финальный образ

## Дополнительные оптимизации

### 1. Использование .dockerignore

Создайте `frontend/.dockerignore`:
```
node_modules
.next
.git
.gitignore
README.md
*.md
.env*.local
.vscode
.idea
*.log
.DS_Store
```

### 2. Оптимизация кэширования слоев

Текущий порядок команд в Dockerfile оптимален:
1. Копируем package.json
2. Устанавливаем зависимости (кэшируется)
3. Копируем код (часто меняется)
4. Собираем приложение

При изменении кода зависимости не переустанавливаются.

### 3. Использование Node.js Alpine образов

Уже используется `node:18-alpine` вместо `node:18`:
- Размер base образа: ~50 MB вместо ~350 MB
- Меньше уязвимостей безопасности

## Рекомендации для production

### Backend тоже можно оптимизировать

Создать `backend/Dockerfile.optimized` с multi-stage build:

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Копируем установленные пакеты
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
```

### Автоматизация очистки

Используйте созданные скрипты:
- **Linux/Mac**: `./docker-cleanup.sh`
- **Windows**: `docker-cleanup.bat`

Или настройте автоматическую очистку на сервере (cron job).

## Проверка результата

После применения оптимизаций:

```bash
# Проверить размеры образов
docker images | grep triplan

# Должно быть примерно:
# triplan-frontend  latest  400-600 MB
# triplan-backend   latest  200-400 MB
```

## Rollback

Если возникнут проблемы, вернитесь к обычному Dockerfile:

```bash
cd /path/to/triplan
git checkout frontend/Dockerfile
docker-compose build frontend
docker-compose up -d
```

