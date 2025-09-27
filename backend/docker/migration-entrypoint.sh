#!/bin/bash

# Универсальный entrypoint для миграций базы данных

set -e  # Выходим при любой ошибке

# Функция для логирования
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Функция для проверки подключения к базе данных
check_database_connection() {
    log "Checking database connection..."
    
    # Проверяем доступность файла базы данных
    if [ ! -f "$DB_PATH" ]; then
        log "Database file not found at $DB_PATH"
        return 1
    fi
    
    # Проверяем, что можем подключиться к базе
    python -c "
from database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
"
}

# Функция для создания резервной копии
create_backup() {
    if [ -f "$DB_PATH" ]; then
        BACKUP_PATH="${DB_PATH}.backup.$(date +%Y%m%d_%H%M%S)"
        log "Creating backup: $BACKUP_PATH"
        cp "$DB_PATH" "$BACKUP_PATH"
        log "Backup created successfully"
        echo "$BACKUP_PATH" > /tmp/backup_path.txt
    fi
}

# Функция для восстановления из резервной копии
restore_backup() {
    if [ -f "/tmp/backup_path.txt" ]; then
        BACKUP_PATH=$(cat /tmp/backup_path.txt)
        log "Restoring from backup: $BACKUP_PATH"
        cp "$BACKUP_PATH" "$DB_PATH"
        log "Backup restored successfully"
    fi
}

# Функция для выполнения миграций
run_migrations() {
    log "Starting database migrations..."
    
    # Создаем резервную копию
    create_backup
    
    # Выполняем миграции
    python -c "
import sys
from db_migrations import run_migrations
try:
    run_migrations()
    print('Migrations completed successfully')
except Exception as e:
    print(f'Migration failed: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        log "Migrations completed successfully"
    else
        log "Migrations failed, restoring backup..."
        restore_backup
        exit 1
    fi
}

# Функция для проверки схемы базы данных
check_schema() {
    log "Checking database schema..."
    python -c "
from db_migrations import check_database_schema
import json
schema = check_database_schema()
print('Database schema:')
for table, columns in schema.items():
    print(f'  {table}: {columns}')
"
}

# Функция для валидации миграций
validate_migrations() {
    log "Validating migrations..."
    
    # Проверяем подключение к базе
    check_database_connection
    
    # Проверяем схему
    check_schema
    
    # Проверяем, что все необходимые таблицы существуют
    python -c "
from database import engine
from sqlalchemy import text, inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
required_tables = ['users', 'training_plans', 'workouts', 'workout_completion_marks']
missing_tables = [table for table in required_tables if table not in tables]
if missing_tables:
    print(f'Missing tables: {missing_tables}')
    exit(1)
else:
    print('All required tables exist')
"
    
    if [ $? -eq 0 ]; then
        log "Migration validation successful"
    else
        log "Migration validation failed"
        exit 1
    fi
}

# Функция для ожидания доступности базы данных
wait_for_database() {
    log "Waiting for database to be available..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if check_database_connection > /dev/null 2>&1; then
            log "Database is available"
            return 0
        fi
        
        log "Attempt $attempt/$max_attempts: Database not ready, waiting..."
        sleep 2
        ((attempt++))
    done
    
    log "Database is not available after $max_attempts attempts"
    exit 1
}

# Функция для отображения помощи
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  migrate          - Run database migrations"
    echo "  check            - Check database schema"
    echo "  validate         - Validate migrations"
    echo "  wait             - Wait for database to be available"
    echo "  backup           - Create database backup"
    echo "  restore          - Restore from backup"
    echo "  help             - Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  DB_PATH          - Path to database file (default: /app/triplan.db)"
    echo "  BACKUP_DIR       - Directory for backups (default: /app/backups)"
    echo "  VALIDATE_ONLY    - Only validate, don't run migrations (default: false)"
}

# Основная логика
main() {
    log "Migration container started"
    log "Command: $1"
    log "DB_PATH: ${DB_PATH:-/app/triplan.db}"
    log "BACKUP_DIR: ${BACKUP_DIR:-/app/backups}"
    
    # Создаем директорию для бэкапов
    mkdir -p "${BACKUP_DIR:-/app/backups}"
    
    case "${1:-migrate}" in
        "migrate")
            wait_for_database
            run_migrations
            validate_migrations
            ;;
        "check")
            wait_for_database
            check_schema
            ;;
        "validate")
            wait_for_database
            validate_migrations
            ;;
        "wait")
            wait_for_database
            ;;
        "backup")
            create_backup
            ;;
        "restore")
            restore_backup
            ;;
        "help")
            show_help
            ;;
        *)
            log "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
    
    log "Migration container finished successfully"
}

# Запускаем основную функцию
main "$@"
