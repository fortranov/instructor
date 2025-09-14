@echo off
REM Скрипт для сборки Docker образа Triplan Backend Service (Windows)

echo 🐳 Сборка Docker образа Triplan Backend Service...

REM Сборка образа
docker build -t triplan-backend:latest .

REM Проверка успешности сборки
if %ERRORLEVEL% EQU 0 (
    echo ✅ Docker образ успешно собран!
    echo 📦 Образ: triplan-backend:latest
    echo.
    echo 🚀 Для запуска используйте:
    echo    docker run -p 8000:8000 triplan-backend:latest
    echo    или
    echo    docker-compose up
) else (
    echo ❌ Ошибка при сборке Docker образа
    exit /b 1
)
