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

# Restart individual services
restart-backend:
	docker-compose restart backend

restart-frontend:
	docker-compose restart frontend
