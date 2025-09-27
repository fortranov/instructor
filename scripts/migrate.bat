@echo off
REM Универсальный скрипт для миграций базы данных в продакшене (Windows)

setlocal enabledelayedexpansion

REM Цвета для вывода (PowerShell)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

REM Функции для вывода
:log_info
echo %INFO% %~1
goto :eof

:log_success
echo %SUCCESS% %~1
goto :eof

:log_warning
echo %WARNING% %~1
goto :eof

:log_error
echo %ERROR% %~1
goto :eof

REM Проверка зависимостей
:check_dependencies
call :log_info "Checking dependencies..."

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log_error "Docker is not installed"
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log_error "Docker Compose is not installed"
    exit /b 1
)

call :log_success "Dependencies check passed"
goto :eof

REM Создание необходимых директорий
:create_directories
call :log_info "Creating necessary directories..."

if not exist "data" mkdir data
if not exist "backups" mkdir backups
if not exist "logs" mkdir logs

call :log_success "Directories created"
goto :eof

REM Создание резервной копии
:create_backup
call :log_info "Creating database backup..."

for /f "tokens=1-3 delims=/" %%a in ('date /t') do (
    set "day=%%a"
    set "month=%%b"
    set "year=%%c"
)
for /f "tokens=1-2 delims=:" %%a in ('time /t') do (
    set "hour=%%a"
    set "minute=%%b"
)

set "backup_name=triplan_backup_%year%%month%%day%_%hour%%minute%"

docker-compose -f docker-compose.production.yml run --rm ^
    -v "%cd%/backups:/app/backups" ^
    migration backup

call :log_success "Backup created: %backup_name%"
goto :eof

REM Выполнение миграций
:run_migrations
call :log_info "Running database migrations..."

REM Создаем бэкап перед миграцией
call :create_backup

REM Запускаем миграции
docker-compose -f docker-compose.production.yml run --rm migration migrate

if %errorlevel% neq 0 (
    call :log_error "Migrations failed"
    exit /b 1
)

call :log_success "Migrations completed successfully"
goto :eof

REM Проверка схемы базы данных
:check_schema
call :log_info "Checking database schema..."

docker-compose -f docker-compose.production.yml run --rm migration check
goto :eof

REM Валидация миграций
:validate_migrations
call :log_info "Validating migrations..."

docker-compose -f docker-compose.production.yml run --rm migration validate
goto :eof

REM Ожидание доступности базы данных
:wait_for_database
call :log_info "Waiting for database to be available..."

docker-compose -f docker-compose.production.yml run --rm migration wait
goto :eof

REM Откат к последнему бэкапу
:rollback
call :log_warning "Rolling back to last backup..."

REM Находим последний бэкап
for /f %%i in ('dir /b /o-d backups\triplan.db.backup.* 2^>nul') do (
    set "latest_backup=%%i"
    goto :found_backup
)

call :log_error "No backup found"
exit /b 1

:found_backup
call :log_info "Restoring from: !latest_backup!"

REM Останавливаем backend
docker-compose -f docker-compose.production.yml stop backend

REM Восстанавливаем бэкап
copy "backups\!latest_backup!" "data\triplan.db"

REM Запускаем backend
docker-compose -f docker-compose.production.yml start backend

call :log_success "Rollback completed"
goto :eof

REM Полный деплой с миграциями
:full_deploy
call :log_info "Starting full deployment with migrations..."

REM Останавливаем сервисы
docker-compose -f docker-compose.production.yml down

REM Создаем директории
call :create_directories

REM Запускаем миграции
call :run_migrations

REM Запускаем все сервисы
docker-compose -f docker-compose.production.yml up -d

REM Ждем готовности
call :log_info "Waiting for services to be ready..."
timeout /t 10 /nobreak >nul

REM Проверяем здоровье
docker-compose -f docker-compose.production.yml ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    call :log_success "Deployment completed successfully"
) else (
    call :log_error "Deployment failed"
    exit /b 1
)
goto :eof

REM Отображение помощи
:show_help
echo Triplan Database Migration Script
echo.
echo Usage: %~nx0 [COMMAND]
echo.
echo Commands:
echo   migrate          - Run database migrations
echo   check            - Check database schema
echo   validate         - Validate migrations
echo   backup           - Create database backup
echo   rollback         - Rollback to last backup
echo   deploy           - Full deployment with migrations
echo   wait             - Wait for database to be available
echo   help             - Show this help message
echo.
echo Environment variables:
echo   VALIDATE_ONLY    - Only validate, don't run migrations
echo   SKIP_BACKUP      - Skip backup creation
echo   FORCE_MIGRATION  - Force migration even if validation fails
goto :eof

REM Основная функция
:main
set "command=%~1"
if "%command%"=="" set "command=help"

if "%command%"=="migrate" (
    call :check_dependencies
    call :create_directories
    call :run_migrations
) else if "%command%"=="check" (
    call :check_dependencies
    call :check_schema
) else if "%command%"=="validate" (
    call :check_dependencies
    call :validate_migrations
) else if "%command%"=="backup" (
    call :check_dependencies
    call :create_backup
) else if "%command%"=="rollback" (
    call :check_dependencies
    call :rollback
) else if "%command%"=="deploy" (
    call :check_dependencies
    call :full_deploy
) else if "%command%"=="wait" (
    call :check_dependencies
    call :wait_for_database
) else if "%command%"=="help" (
    call :show_help
) else (
    call :log_error "Unknown command: %command%"
    call :show_help
    exit /b 1
)

goto :eof

REM Запуск
call :main %*
