# Makefile для управления Triplan проектом

.PHONY: help build up down migrate check validate backup rollback deploy logs clean

# Переменные
COMPOSE_FILE = docker-compose.production.yml
MIGRATION_SCRIPT = scripts/migrate.sh
MIGRATION_SCRIPT_WIN = scripts/migrate.bat

# Определяем операционную систему
ifeq ($(OS),Windows_NT)
    MIGRATE_CMD = $(MIGRATION_SCRIPT_WIN)
    RM_CMD = del /s /q
    MKDIR_CMD = mkdir
else
    MIGRATE_CMD = ./$(MIGRATION_SCRIPT)
    RM_CMD = rm -rf
    MKDIR_CMD = mkdir -p
endif

help: ## Показать справку
	@echo "Triplan Project Management"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Собрать Docker образы
	@echo "Building Docker images..."
	docker-compose -f $(COMPOSE_FILE) build

up: ## Запустить все сервисы
	@echo "Starting services..."
	docker-compose -f $(COMPOSE_FILE) up -d

down: ## Остановить все сервисы
	@echo "Stopping services..."
	docker-compose -f $(COMPOSE_FILE) down

migrate: ## Выполнить миграции базы данных
	@echo "Running database migrations..."
	@if [ "$(OS)" = "Windows_NT" ]; then \
		$(MIGRATE_CMD) migrate; \
	else \
		chmod +x $(MIGRATE_CMD) && $(MIGRATE_CMD) migrate; \
	fi

check: ## Проверить схему базы данных
	@echo "Checking database schema..."
	@if [ "$(OS)" = "Windows_NT" ]; then \
		$(MIGRATE_CMD) check; \
	else \
		chmod +x $(MIGRATE_CMD) && $(MIGRATE_CMD) check; \
	fi

validate: ## Валидировать миграции
	@echo "Validating migrations..."
	@if [ "$(OS)" = "Windows_NT" ]; then \
		$(MIGRATE_CMD) validate; \
	else \
		chmod +x $(MIGRATE_CMD) && $(MIGRATE_CMD) validate; \
	fi

backup: ## Создать резервную копию базы данных
	@echo "Creating database backup..."
	@if [ "$(OS)" = "Windows_NT" ]; then \
		$(MIGRATE_CMD) backup; \
	else \
		chmod +x $(MIGRATE_CMD) && $(MIGRATE_CMD) backup; \
	fi

rollback: ## Откатить к последней резервной копии
	@echo "Rolling back to last backup..."
	@if [ "$(OS)" = "Windows_NT" ]; then \
		$(MIGRATE_CMD) rollback; \
	else \
		chmod +x $(MIGRATE_CMD) && $(MIGRATE_CMD) rollback; \
	fi

deploy: ## Полный деплой с миграциями
	@echo "Starting full deployment..."
	@if [ "$(OS)" = "Windows_NT" ]; then \
		$(MIGRATE_CMD) deploy; \
	else \
		chmod +x $(MIGRATE_CMD) && $(MIGRATE_CMD) deploy; \
	fi

logs: ## Показать логи сервисов
	@echo "Showing service logs..."
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-backend: ## Показать логи backend
	@echo "Showing backend logs..."
	docker-compose -f $(COMPOSE_FILE) logs -f backend

logs-migration: ## Показать логи миграций
	@echo "Showing migration logs..."
	docker-compose -f $(COMPOSE_FILE) logs migration

status: ## Показать статус сервисов
	@echo "Service status:"
	docker-compose -f $(COMPOSE_FILE) ps

clean: ## Очистить неиспользуемые Docker ресурсы
	@echo "Cleaning up Docker resources..."
	docker system prune -f
	docker volume prune -f

clean-all: ## Очистить все Docker ресурсы (включая образы)
	@echo "Cleaning up all Docker resources..."
	docker system prune -a -f
	docker volume prune -f

setup: ## Первоначальная настройка проекта
	@echo "Setting up project..."
	$(MKDIR_CMD) data backups logs nginx/ssl
	@if [ ! -f "nginx/ssl/cert.pem" ]; then \
		echo "Creating self-signed SSL certificate..."; \
		openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"; \
	fi
	@echo "Project setup completed!"

dev: ## Запустить в режиме разработки
	@echo "Starting development environment..."
	docker-compose up -d

prod: ## Запустить в режиме продакшена
	@echo "Starting production environment..."
	$(MAKE) setup
	$(MAKE) deploy

restart: ## Перезапустить сервисы
	@echo "Restarting services..."
	$(MAKE) down
	$(MAKE) up

health: ## Проверить здоровье сервисов
	@echo "Checking service health..."
	@curl -f http://localhost:8000/api/v1/health || echo "Backend health check failed"

# Специальные команды для миграций
migrate-check: migrate check ## Выполнить миграции и проверить схему
migrate-validate: migrate validate ## Выполнить миграции и валидировать
migrate-backup: backup migrate ## Создать бэкап и выполнить миграции

# Команды для мониторинга
monitor: ## Мониторинг сервисов
	@echo "Monitoring services..."
	@while true; do \
		echo "=== $(date) ==="; \
		$(MAKE) status; \
		$(MAKE) health; \
		echo ""; \
		sleep 30; \
	done