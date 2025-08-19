# Multi-Agent AI Developer - Development Makefile
# One-liner commands for managing the local development stack

.PHONY: help up down build logs clean health test

# Default target
help:
	@echo "Multi-Agent AI Developer - Development Commands"
	@echo ""
	@echo "Stack Management:"
	@echo "  up          - Bring up the entire stack (DB, Redis, API, UI, Orchestrator)"
	@echo "  down        - Stop all services"
	@echo "  restart     - Restart all services"
	@echo "  build       - Build all Docker images"
	@echo ""
	@echo "Monitoring:"
	@echo "  logs        - Tail logs from all services"
	@echo "  logs-api    - Tail API logs only"
	@echo "  logs-ui     - Tail UI logs only"
	@echo "  logs-orch   - Tail orchestrator logs only"
	@echo "  health      - Check health of all services"
	@echo ""
	@echo "Development:"
	@echo "  test        - Run all tests"
	@echo "  test-api    - Run API tests only"
	@echo "  test-ui     - Run UI tests only"
	@echo "  clean       - Clean up containers, volumes, and images"
	@echo ""
	@echo "Database:"
	@echo "  db-reset    - Reset database (WARNING: destroys all data)"
	@echo "  db-shell    - Open PostgreSQL shell"
	@echo "  db-backup   - Create database backup"
	@echo ""
	@echo "Quick Start:"
	@echo "  make up     - Start everything"
	@echo "  make health - Verify all services are healthy"
	@echo "  make logs   - Monitor logs"

# Bring up the entire stack
up:
	@echo "🚀 Starting Multi-Agent AI Developer stack..."
	docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	@make health
	@echo "✅ Stack is up and healthy!"

# Stop all services
down:
	@echo "🛑 Stopping all services..."
	docker-compose down

# Restart all services
restart:
	@echo "🔄 Restarting all services..."
	docker-compose restart
	@make health

# Build all Docker images
build:
	@echo "🔨 Building Docker images..."
	docker-compose build --no-cache

# Tail logs from all services
logs:
	@echo "📋 Tailing logs from all services..."
	docker-compose logs -f

# Tail API logs only
logs-api:
	@echo "📋 Tailing API logs..."
	docker-compose logs -f api

# Tail UI logs only
logs-ui:
	@echo "📋 Tailing UI logs..."
	docker-compose logs -f ui

# Tail orchestrator logs only
logs-orch:
	@echo "📋 Tailing orchestrator logs..."
	docker-compose logs -f orchestrator

# Check health of all services
health:
	@echo "🏥 Checking service health..."
	@echo "📊 API Health:"
	@curl -s http://localhost:8002/healthz | jq . || echo "❌ API not responding"
	@echo ""
	@echo "📊 UI Health:"
	@curl -s http://localhost:3002 | head -1 || echo "❌ UI not responding"
	@echo ""
	@echo "📊 Database Health:"
	@docker-compose exec -T postgres pg_isready -U gizmo_user -d gizmo_dev || echo "❌ Database not responding"
	@echo ""
	@echo "📊 Redis Health:"
	@docker-compose exec -T redis redis-cli ping || echo "❌ Redis not responding"
	@echo ""
	@echo "📊 Orchestrator Health:"
	@curl -s http://localhost:8003/healthz | jq . || echo "❌ Orchestrator not responding"

# Run all tests
test:
	@echo "🧪 Running all tests..."
	@make test-api
	@make test-ui

# Run API tests only
test-api:
	@echo "🧪 Running API tests..."
	docker-compose exec api pytest

# Run UI tests only
test-ui:
	@echo "🧪 Running UI tests..."
	docker-compose exec ui npm test

# Clean up containers, volumes, and images
clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v --rmi all
	docker system prune -f
	@echo "✅ Cleanup complete!"

# Reset database (WARNING: destroys all data)
db-reset:
	@echo "⚠️  WARNING: This will destroy all database data!"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo "🗑️  Resetting database..."; \
		docker-compose down postgres; \
		docker volume rm gizmo_postgres_data; \
		docker-compose up -d postgres; \
		echo "✅ Database reset complete!"; \
	else \
		echo "❌ Database reset cancelled"; \
	fi

# Open PostgreSQL shell
db-shell:
	@echo "🐘 Opening PostgreSQL shell..."
	docker-compose exec postgres psql -U gizmo_user -d gizmo_dev

# Create database backup
db-backup:
	@echo "💾 Creating database backup..."
	@mkdir -p backups
	docker-compose exec -T postgres pg_dump -U gizmo_user -d gizmo_dev > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created in backups/ directory"

# Show service status
status:
	@echo "📊 Service Status:"
	docker-compose ps

# Show resource usage
resources:
	@echo "💻 Resource Usage:"
	docker stats --no-stream

# Quick development commands
dev:
	@echo "🚀 Quick development commands:"
	@echo "  make up     - Start everything"
	@echo "  make health - Check health"
	@echo "  make logs   - Monitor logs"
	@echo "  make test   - Run tests"
	@echo "  make down   - Stop everything"
