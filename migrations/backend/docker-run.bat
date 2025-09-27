@echo off
REM Скрипт для запуска Triplan Backend Service в Docker (Windows)

echo 🐳 Запуск Triplan Backend Service в Docker...

REM Проверяем, существует ли образ
docker image inspect triplan-backend:latest >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 📦 Образ не найден, выполняем сборку...
    call docker-build.bat
)

echo 🚀 Запуск контейнера...
echo 📝 Документация API: http://localhost:8000/docs
echo 🏥 Health check: http://localhost:8000/api/v1/health
echo 🔧 Для остановки нажмите Ctrl+C
echo --------------------------------------------------

REM Запуск контейнера
docker run -it --rm -p 8000:8000 --name triplan-backend triplan-backend:latest
