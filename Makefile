# Triplan Docker Commands

.PHONY: help build up down logs clean dev-up dev-down prod-up prod-down

# Default target
help:
	@echo "Available commands:"
	@echo "  make build       - Build all Docker images"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - Show logs for all services"
	@echo "  make clean       - Remove containers, networks, and volumes"
	@echo "  make rebuild     - Rebuild all images from scratch"
	@echo ""
	@echo "Development:"
	@echo "  make dev-up      - Start services in development mode"
	@echo "  make dev-down    - Stop development services"
	@echo "  make dev-logs    - Show development logs"
	@echo ""
	@echo "Production:"
	@echo "  make prod-up     - Start services in production mode with Nginx"
	@echo "  make prod-down   - Stop production services"
	@echo "  make prod-logs   - Show production logs"
	@echo ""
	@echo "Migrations:"
	@echo "  make migrate     - Run database migrations in Docker"
	@echo "  make migrate-status - Show migration status"
	@echo "  make migrate-rollback - Rollback migrations"
	@echo "  make migrate-local - Run migrations locally"
	@echo "  make migrate-local-status - Show local migration status"

# Build all images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d --build

# Stop all services
down:
	docker-compose down

# Show logs
logs:
	docker-compose logs -f

# Clean up everything
clean:
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -f

# Rebuild everything from scratch
rebuild:
	docker-compose down --rmi all
	docker-compose build --no-cache
	docker-compose up -d

# Development commands
dev-up:
	docker-compose -f docker-compose.dev.yml up -d --build

dev-down:
	docker-compose -f docker-compose.dev.yml down

dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# Production commands with Nginx
prod-up:
	docker-compose --profile production up -d --build

prod-down:
	docker-compose --profile production down

prod-logs:
	docker-compose --profile production logs -f

# Individual service commands
backend-logs:
	docker-compose logs -f backend

frontend-logs:
	docker-compose logs -f frontend

nginx-logs:
	docker-compose logs -f nginx

# Health checks
health:
	@echo "Checking backend health..."
	@curl -f http://localhost:8000/api/v1/health || echo "Backend not healthy"
	@echo "Checking frontend..."
	@curl -f http://localhost:3000 || echo "Frontend not accessible"

# Database commands
db-shell:
	docker-compose exec backend python -c "from database import SessionLocal; session = SessionLocal(); print('Database shell ready')"

# Migration commands
migrate:
	docker-compose up migrations

migrate-status:
	docker-compose exec backend python run_migrations.py status

migrate-rollback:
	@read -p "Enter version to rollback to: " version; \
	docker-compose exec backend python run_migrations.py rollback --version $$version

migrate-local:
	python run_migrations.py migrate

migrate-local-status:
	python run_migrations.py status

migrate-local-rollback:
	@read -p "Enter version to rollback to: " version; \
	python run_migrations.py rollback --version $$version

# Restart individual services
restart-backend:
	docker-compose restart backend

restart-frontend:
	docker-compose restart frontend
