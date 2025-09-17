@echo off
REM Скрипт для выполнения миграций в Docker контейнере (Windows)

echo 🐳 Запуск миграций в Docker контейнере...

REM Проверить, что база данных доступна
if "%DB_PATH%"=="" (
    set DB_PATH=/app/triplan.db
)

echo 📁 Путь к базе данных: %DB_PATH%

REM Создать директорию для базы данных если её нет
for %%F in ("%DB_PATH%") do set DB_DIR=%%~dpF
if not exist "%DB_DIR%" (
    echo 📂 Создание директории для базы данных: %DB_DIR%
    mkdir "%DB_DIR%"
)

REM Выполнить миграции
echo 🔄 Выполнение миграций...
python run_migrations.py migrate

if %ERRORLEVEL% EQU 0 (
    echo ✅ Миграции завершены успешно!
) else (
    echo ❌ Ошибка при выполнении миграций!
    exit /b 1
)
