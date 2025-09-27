@echo off
REM Скрипт для запуска миграций базы данных на Windows production сервере

REM Проверяем, что мы в правильной директории
if not exist "main.py" (
    echo Error: main.py not found. Please run this script from the backend directory.
    exit /b 1
)

echo Starting database migration...

REM Вариант 1: Через переменную окружения (автоматический запуск при старте)
echo Setting RUN_MIGRATIONS=true and restarting backend...
set RUN_MIGRATIONS=true
start /b python main.py

REM Ждем немного и проверяем статус
timeout /t 5 /nobreak >nul
tasklist /fi "imagename eq python.exe" | findstr "python.exe" >nul
if %errorlevel% equ 0 (
    echo Backend started with migrations enabled
    echo Migrations should be running...
    timeout /t 10 /nobreak >nul
    echo Stopping backend...
    taskkill /f /im python.exe >nul 2>&1
) else (
    echo Failed to start backend
    exit /b 1
)

REM Вариант 2: Через HTTP endpoint (если ADMIN_MIGRATION_TOKEN установлен)
if defined ADMIN_MIGRATION_TOKEN (
    echo Attempting migration via HTTP endpoint...
    
    REM Запускаем backend в фоне
    start /b python main.py
    
    REM Ждем запуска
    timeout /t 5 /nobreak >nul
    
    REM Выполняем миграцию через HTTP
    curl -X POST "http://localhost:8000/api/v1/admin/migrate" ^
         -H "Content-Type: application/json" ^
         -H "Authorization: Bearer %ADMIN_MIGRATION_TOKEN%"
    
    REM Останавливаем backend
    taskkill /f /im python.exe >nul 2>&1
) else (
    echo ADMIN_MIGRATION_TOKEN not set. Skipping HTTP migration.
)

REM Вариант 3: Прямой запуск миграций
echo Running direct migration...
python -c "from migrations import run_migrations; run_migrations()"

echo Migration completed!
pause
