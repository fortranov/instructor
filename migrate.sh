#!/bin/bash

# Универсальный скрипт для запуска миграций базы данных
# Поддерживает SQLite, PostgreSQL, MySQL

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Функция помощи
show_help() {
    cat << EOF
Использование: $0 [ОПЦИИ]

Опции:
    -d, --database URL     URL базы данных (по умолчанию: sqlite:///./triplan.db)
    -e, --env FILE         Файл с переменными окружения
    -h, --help             Показать эту справку
    -v, --verbose          Подробный вывод
    --dry-run              Показать что будет выполнено без фактического выполнения
    --check                Только проверить текущую схему базы данных

Примеры:
    $0                                    # Миграция SQLite базы данных по умолчанию
    $0 -d "sqlite:///./production.db"     # Миграция конкретной SQLite базы
    $0 -d "postgresql://user:pass@localhost/triplan"  # Миграция PostgreSQL
    $0 -d "mysql://user:pass@localhost/triplan"       # Миграция MySQL
    $0 --check                            # Проверить схему базы данных
    $0 --dry-run                          # Показать что будет выполнено

Переменные окружения:
    DATABASE_URL          URL базы данных
    POSTGRES_URL          URL PostgreSQL базы данных
    MYSQL_URL             URL MySQL базы данных
EOF
}

# Парсинг аргументов
DATABASE_URL=""
ENV_FILE=""
VERBOSE=false
DRY_RUN=false
CHECK_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--database)
            DATABASE_URL="$2"
            shift 2
            ;;
        -e|--env)
            ENV_FILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --check)
            CHECK_ONLY=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            error "Неизвестная опция: $1"
            show_help
            exit 1
            ;;
    esac
done

# Загрузка переменных окружения из файла
if [[ -n "$ENV_FILE" ]]; then
    if [[ -f "$ENV_FILE" ]]; then
        log "Загружаем переменные окружения из $ENV_FILE"
        set -a
        source "$ENV_FILE"
        set +a
    else
        error "Файл переменных окружения не найден: $ENV_FILE"
        exit 1
    fi
fi

# Определение URL базы данных
if [[ -z "$DATABASE_URL" ]]; then
    if [[ -n "$POSTGRES_URL" ]]; then
        DATABASE_URL="$POSTGRES_URL"
        log "Используем PostgreSQL базу данных"
    elif [[ -n "$MYSQL_URL" ]]; then
        DATABASE_URL="$MYSQL_URL"
        log "Используем MySQL базу данных"
    else
        DATABASE_URL="sqlite:///./triplan.db"
        log "Используем SQLite базу данных по умолчанию"
    fi
fi

log "URL базы данных: $DATABASE_URL"

# Проверка существования Docker
if ! command -v docker &> /dev/null; then
    error "Docker не установлен или не найден в PATH"
    exit 1
fi

# Проверка существования docker-compose
if ! command -v docker-compose &> /dev/null; then
    error "docker-compose не установлен или не найден в PATH"
    exit 1
fi

# Проверка существования файлов миграции
if [[ ! -f "migrations/Dockerfile" ]]; then
    error "Файл migrations/Dockerfile не найден"
    exit 1
fi

if [[ ! -f "docker-compose.migration.yml" ]]; then
    error "Файл docker-compose.migration.yml не найден"
    exit 1
fi

# Функция для проверки схемы базы данных
check_schema() {
    log "Проверяем текущую схему базы данных..."
    
    docker-compose -f docker-compose.migration.yml run --rm \
        -e DATABASE_URL="$DATABASE_URL" \
        migration python -c "
import sys
sys.path.append('/app/backend')
from migration_runner import DatabaseMigrator
migrator = DatabaseMigrator('$DATABASE_URL')
schema = migrator.get_current_schema()
print('Текущая схема базы данных:')
for table, columns in schema.items():
    print(f'  {table}: {columns}')
"
}

# Функция для выполнения миграций
run_migration() {
    log "Запускаем миграции базы данных..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Показываем что будет выполнено"
        check_schema
        log "DRY RUN: Миграции не выполнены"
        return 0
    fi
    
    # Выполняем миграцию
    if docker-compose -f docker-compose.migration.yml run --rm \
        -e DATABASE_URL="$DATABASE_URL" \
        migration; then
        success "Миграции выполнены успешно!"
        
        # Показываем итоговую схему
        if [[ "$VERBOSE" == "true" ]]; then
            check_schema
        fi
    else
        error "Ошибка при выполнении миграций"
        exit 1
    fi
}

# Основная логика
main() {
    log "Начинаем процесс миграции базы данных"
    
    if [[ "$CHECK_ONLY" == "true" ]]; then
        check_schema
    else
        run_migration
    fi
    
    success "Процесс завершен"
}

# Запуск основной функции
main "$@"

