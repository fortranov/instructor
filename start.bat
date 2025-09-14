@echo off
REM Triplan Quick Start Script for Windows
REM Скрипт для быстрого запуска проекта Triplan на Windows

echo 🚀 Запуск Triplan...
echo ===================

REM Проверяем наличие Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker не установлен. Пожалуйста, установите Docker Desktop.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose не установлен. Пожалуйста, установите Docker Desktop с Docker Compose.
    pause
    exit /b 1
)

REM Создаем .env файл из примера, если его нет
if not exist .env (
    echo 📝 Создаем .env файл из примера...
    copy .env.example .env >nul
    echo ✅ .env файл создан. Отредактируйте его при необходимости.
)

REM Выбор режима запуска
echo.
echo Выберите режим запуска:
echo 1) Продакшн режим (по умолчанию)
echo 2) Режим разработки  
echo 3) Продакшн с Nginx
set /p mode="Введите номер (1-3) [1]: "

if "%mode%"=="2" (
    echo 🔧 Запуск в режиме разработки...
    docker-compose -f docker-compose.dev.yml up -d --build
) else if "%mode%"=="3" (
    echo 🏭 Запуск в продакшн режиме с Nginx...
    docker-compose --profile production up -d --build
) else (
    echo 🏭 Запуск в продакшн режиме...
    docker-compose up -d --build
)

REM Ожидание запуска сервисов
echo.
echo ⏳ Ожидание запуска сервисов...
timeout /t 10 /nobreak >nul

REM Проверка статуса
echo.
echo 📊 Статус сервисов:
docker-compose ps

REM Проверка здоровья backend
echo.
echo 🔍 Проверка backend...
curl -f http://localhost:8000/api/v1/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend работает: http://localhost:8000
    echo 📖 API документация: http://localhost:8000/docs
) else (
    echo ⚠️  Backend еще запускается или есть проблемы
)

REM Проверка frontend
echo.
echo 🔍 Проверка frontend...
curl -f http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend работает: http://localhost:3000
) else (
    echo ⚠️  Frontend еще запускается или есть проблемы
)

echo.
echo 🎉 Запуск завершен!
echo.
echo 📱 Доступные адреса:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo 📋 Полезные команды:
echo    docker-compose logs -f     # Просмотр логов
echo    docker-compose down        # Остановка
echo    make help                  # Все доступные команды
echo.

pause
