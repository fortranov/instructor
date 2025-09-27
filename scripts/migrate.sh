#!/bin/bash

# Универсальный скрипт для миграций базы данных в продакшене

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для цветного вывода
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка зависимостей
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    log_success "Dependencies check passed"
}

# Создание необходимых директорий
create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p data
    mkdir -p backups
    mkdir -p logs
    
    log_success "Directories created"
}

# Создание резервной копии
create_backup() {
    log_info "Creating database backup..."
    
    BACKUP_NAME="triplan_backup_$(date +%Y%m%d_%H%M%S)"
    
    docker-compose -f docker-compose.production.yml run --rm \
        -v "$(pwd)/backups:/app/backups" \
        migration backup
    
    log_success "Backup created: $BACKUP_NAME"
}

# Выполнение миграций
run_migrations() {
    log_info "Running database migrations..."
    
    # Создаем бэкап перед миграцией
    create_backup
    
    # Запускаем миграции
    docker-compose -f docker-compose.production.yml run --rm migration migrate
    
    if [ $? -eq 0 ]; then
        log_success "Migrations completed successfully"
    else
        log_error "Migrations failed"
        exit 1
    fi
}

# Проверка схемы базы данных
check_schema() {
    log_info "Checking database schema..."
    
    docker-compose -f docker-compose.production.yml run --rm migration check
}

# Валидация миграций
validate_migrations() {
    log_info "Validating migrations..."
    
    docker-compose -f docker-compose.production.yml run --rm migration validate
}

# Ожидание доступности базы данных
wait_for_database() {
    log_info "Waiting for database to be available..."
    
    docker-compose -f docker-compose.production.yml run --rm migration wait
}

# Откат к последнему бэкапу
rollback() {
    log_warning "Rolling back to last backup..."
    
    # Находим последний бэкап
    LATEST_BACKUP=$(ls -t backups/triplan.db.backup.* 2>/dev/null | head -n1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        log_error "No backup found"
        exit 1
    fi
    
    log_info "Restoring from: $LATEST_BACKUP"
    
    # Останавливаем backend
    docker-compose -f docker-compose.production.yml stop backend
    
    # Восстанавливаем бэкап
    cp "$LATEST_BACKUP" data/triplan.db
    
    # Запускаем backend
    docker-compose -f docker-compose.production.yml start backend
    
    log_success "Rollback completed"
}

# Полный деплой с миграциями
full_deploy() {
    log_info "Starting full deployment with migrations..."
    
    # Останавливаем сервисы
    docker-compose -f docker-compose.production.yml down
    
    # Создаем директории
    create_directories
    
    # Запускаем миграции
    run_migrations
    
    # Запускаем все сервисы
    docker-compose -f docker-compose.production.yml up -d
    
    # Ждем готовности
    log_info "Waiting for services to be ready..."
    sleep 10
    
    # Проверяем здоровье
    if docker-compose -f docker-compose.production.yml ps | grep -q "Up"; then
        log_success "Deployment completed successfully"
    else
        log_error "Deployment failed"
        exit 1
    fi
}

# Отображение помощи
show_help() {
    echo "Triplan Database Migration Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  migrate          - Run database migrations"
    echo "  check            - Check database schema"
    echo "  validate         - Validate migrations"
    echo "  backup           - Create database backup"
    echo "  rollback         - Rollback to last backup"
    echo "  deploy           - Full deployment with migrations"
    echo "  wait             - Wait for database to be available"
    echo "  help             - Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  VALIDATE_ONLY    - Only validate, don't run migrations"
    echo "  SKIP_BACKUP      - Skip backup creation"
    echo "  FORCE_MIGRATION  - Force migration even if validation fails"
}

# Основная функция
main() {
    local command="${1:-help}"
    
    case "$command" in
        "migrate")
            check_dependencies
            create_directories
            run_migrations
            ;;
        "check")
            check_dependencies
            check_schema
            ;;
        "validate")
            check_dependencies
            validate_migrations
            ;;
        "backup")
            check_dependencies
            create_backup
            ;;
        "rollback")
            check_dependencies
            rollback
            ;;
        "deploy")
            check_dependencies
            full_deploy
            ;;
        "wait")
            check_dependencies
            wait_for_database
            ;;
        "help")
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Запуск
main "$@"
