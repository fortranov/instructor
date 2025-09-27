# Dockerfile для контейнера миграций
FROM python:3.12-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование файлов требований
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание скрипта запуска миграций
COPY migration_runner.py .

# Установка исполняемых прав
RUN chmod +x migration_runner.py

# Команда по умолчанию
CMD ["python", "migration_runner.py"]

