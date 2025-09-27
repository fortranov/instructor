@echo off
REM Универсальный скрипт для запуска миграций базы данных на Windows
REM Поддерживает SQLite, PostgreSQL, MySQL

setlocal enabledelayedexpansion

REM Парсинг аргументов
set DATABASE_URL=
set ENV_FILE=
set VERBOSE=false
set DRY_RUN=false
set CHECK_ONLY=false

:parse_args
if "%~1"=="" goto :main
if "%~1"=="-d" (
    set DATABASE_URL=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--database" (
    set DATABASE_URL=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-e" (
    set ENV_FILE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--env" (
    set ENV_FILE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-v" (
    set VERBOSE=true
    shift
    goto :parse_args
)
if "%~1"=="--verbose" (
    set VERBOSE=true
    shift
    goto :parse_args
)
if "%~1"=="--dry-run" (
    set DRY_RUN=true
    shift
    goto :parse_args
)
if "%~1"=="--check" (
    set CHECK_ONLY=true
    shift
    goto :parse_args
)
if "%~1"=="-h" goto :help
if "%~1"=="--help" goto :help

echo Ошибка: Неизвестная опция %~1
goto :help

:help
echo.
echo Использование: %0 [ОПЦИИ]
echo.
echo Опции:
echo     -d, --database URL     URL базы данных (по умолчанию: sqlite:///./triplan.db)
echo     -e, --env FILE         Файл с переменными окружения
echo     -h, --help             Показать эту справку
echo     -v, --verbose          Подробный вывод
echo     --dry-run              Показать что будет выполнено без фактического выполнения
echo     --check                Только проверить текущую схему базы данных
echo.
echo Примеры:
echo     %0                                    # Миграция SQLite базы данных по умолчанию
echo     %0 -d "sqlite:///./production.db"     # Миграция конкретной SQLite базы
echo     %0 -d "postgresql://user:pass@localhost/triplan"  # Миграция PostgreSQL
echo     %0 -d "mysql://user:pass@localhost/triplan"       # Миграция MySQL
echo     %0 --check                            # Проверить схему базы данных
echo     %0 --dry-run                          # Показать что будет выполнено
echo.
echo Переменные окружения:
echo     DATABASE_URL          URL базы данных
echo     POSTGRES_URL          URL PostgreSQL базы данных
echo     MYSQL_URL             URL MySQL базы данных
echo.
exit /b 0

:main
echo [%date% %time%] Начинаем процесс миграции базы данных

REM Загрузка переменных окружения из файла
if not "%ENV_FILE%"=="" (
    if exist "%ENV_FILE%" (
        echo [INFO] Загружаем переменные окружения из %ENV_FILE%
        for /f "usebackq tokens=1,2 delims==" %%a in ("%ENV_FILE%") do (
            set %%a=%%b
        )
    ) else (
        echo [ERROR] Файл переменных окружения не найден: %ENV_FILE%
        exit /b 1
    )
)

REM Определение URL базы данных
if "%DATABASE_URL%"=="" (
    if not "%POSTGRES_URL%"=="" (
        set DATABASE_URL=%POSTGRES_URL%
        echo [INFO] Используем PostgreSQL базу данных
    ) else if not "%MYSQL_URL%"=="" (
        set DATABASE_URL=%MYSQL_URL%
        echo [INFO] Используем MySQL базу данных
    ) else (
        set DATABASE_URL=sqlite:///./triplan.db
        echo [INFO] Используем SQLite базу данных по умолчанию
    )
)

echo [INFO] URL базы данных: %DATABASE_URL%

REM Проверка существования Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker не установлен или не найден в PATH
    exit /b 1
)

REM Проверка существования docker-compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] docker-compose не установлен или не найден в PATH
    exit /b 1
)

REM Проверка существования файлов миграции
if not exist "migrations\Dockerfile" (
    echo [ERROR] Файл migrations\Dockerfile не найден
    exit /b 1
)

if not exist "docker-compose.migration.yml" (
    echo [ERROR] Файл docker-compose.migration.yml не найден
    exit /b 1
)

REM Выполнение миграций или проверки схемы
if "%CHECK_ONLY%"=="true" (
    echo [INFO] Проверяем текущую схему базы данных...
    docker-compose -f docker-compose.migration.yml run --rm -e DATABASE_URL="%DATABASE_URL%" migration python -c "import sys; sys.path.append('/app/backend'); from migration_runner import DatabaseMigrator; migrator = DatabaseMigrator('%DATABASE_URL%'); schema = migrator.get_current_schema(); print('Текущая схема базы данных:'); [print(f'  {table}: {columns}') for table, columns in schema.items()]"
) else (
    if "%DRY_RUN%"=="true" (
        echo [INFO] DRY RUN: Показываем что будет выполнено
        docker-compose -f docker-compose.migration.yml run --rm -e DATABASE_URL="%DATABASE_URL%" migration python -c "import sys; sys.path.append('/app/backend'); from migration_runner import DatabaseMigrator; migrator = DatabaseMigrator('%DATABASE_URL%'); schema = migrator.get_current_schema(); print('Текущая схема базы данных:'); [print(f'  {table}: {columns}') for table, columns in schema.items()]"
        echo [INFO] DRY RUN: Миграции не выполнены
    ) else (
        echo [INFO] Запускаем миграции базы данных...
        docker-compose -f docker-compose.migration.yml run --rm -e DATABASE_URL="%DATABASE_URL%" migration
        if %errorlevel% equ 0 (
            echo [SUCCESS] Миграции выполнены успешно!
            if "%VERBOSE%"=="true" (
                echo [INFO] Показываем итоговую схему базы данных...
                docker-compose -f docker-compose.migration.yml run --rm -e DATABASE_URL="%DATABASE_URL%" migration python -c "import sys; sys.path.append('/app/backend'); from migration_runner import DatabaseMigrator; migrator = DatabaseMigrator('%DATABASE_URL%'); schema = migrator.get_current_schema(); print('Итоговая схема базы данных:'); [print(f'  {table}: {columns}') for table, columns in schema.items()]"
            )
        ) else (
            echo [ERROR] Ошибка при выполнении миграций
            exit /b 1
        )
    )
)

echo [SUCCESS] Процесс завершен
pause

