# 🚀 **Gizmo AI - Development Automation**
# Comprehensive development commands and automation
#
# Developer: Shashank B
# Repository: https://github.com/ShashankBejjanki1241/GIZMO
# Last Updated: December 2024

# Configuration
COMPOSE_FILE = config/docker/docker-compose.yml
PROJECT_NAME = gizmo-ai

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

# Default target
.PHONY: help
help: ## Show this help message
	@echo "$(GREEN)Gizmo AI - Development Commands$(NC)"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# 🚀 **Stack Management**
# =============================================================================

.PHONY: up
up: ## Start the complete development stack
	@echo "$(GREEN)🚀 Starting Gizmo AI development stack...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✅ Stack started!$(NC)"
	@echo "$(YELLOW)📱 Frontend: http://localhost:3002$(NC)"
	@echo "$(YELLOW)🚀 API: http://localhost:8002$(NC)"
	@echo "$(YELLOW)🧠 Orchestrator: http://localhost:8003$(NC)"
	@echo "$(YELLOW)🗄️ Database: localhost:5433$(NC)"
	@echo "$(YELLOW)⚡ Redis: localhost:6379$(NC)"

.PHONY: down
down: ## Stop the development stack
	@echo "$(YELLOW)🛑 Stopping Gizmo AI development stack...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)✅ Stack stopped!$(NC)"

.PHONY: restart
restart: ## Restart all services
	@echo "$(YELLOW)🔄 Restarting Gizmo AI services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) restart
	@echo "$(GREEN)✅ Services restarted!$(NC)"

.PHONY: rebuild
rebuild: ## Rebuild and restart all services
	@echo "$(YELLOW)🔨 Rebuilding Gizmo AI services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down
	@docker-compose -f $(COMPOSE_FILE) build --no-cache
	@docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✅ Services rebuilt and started!$(NC)"

# =============================================================================
# 📊 **Monitoring & Debugging**
# =============================================================================

.PHONY: logs
logs: ## View logs from all services
	@echo "$(GREEN)📋 Viewing logs from all services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: logs-api
logs-api: ## View API service logs
	@echo "$(GREEN)📋 Viewing API service logs...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) logs -f api

.PHONY: logs-ui
logs-ui: ## View frontend service logs
	@echo "$(GREEN)📋 Viewing frontend service logs...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) logs -f ui

.PHONY: logs-orch
logs-orch: ## View orchestrator service logs
	@echo "$(GREEN)📋 Viewing orchestrator service logs...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) logs -f orchestrator

.PHONY: status
status: ## Check status of all services
	@echo "$(GREEN)📊 Checking service status...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) ps

# =============================================================================
# 🧪 **Testing & Validation**
# =============================================================================

.PHONY: test
test: ## Run all test suites
	@echo "$(GREEN)🧪 Running Gizmo AI test suites...$(NC)"
	@echo "$(YELLOW)Running unit tests...$(NC)"
	@python3 -m pytest tests/unit/ -v
	@echo "$(YELLOW)Running integration tests...$(NC)"
	@python3 -m pytest tests/integration/ -v
	@echo "$(YELLOW)Running end-to-end tests...$(NC)"
	@python3 -m pytest tests/e2e/ -v
	@echo "$(GREEN)✅ All tests completed!$(NC)"

.PHONY: test-unit
test-unit: ## Run unit tests only
	@echo "$(GREEN)🧪 Running unit tests...$(NC)"
	@python3 -m pytest tests/unit/ -v

.PHONY: test-integration
test-integration: ## Run integration tests only
	@echo "$(GREEN)🧪 Running integration tests...$(NC)"
	@python3 -m pytest tests/integration/ -v

.PHONY: test-e2e
test-e2e: ## Run end-to-end tests only
	@echo "$(GREEN)🧪 Running end-to-end tests...$(NC)"
	@python3 -m pytest tests/e2e/ -v

.PHONY: test-curated
test-curated: ## Run the curated task suite
	@echo "$(GREEN)🧪 Running curated task suite...$(NC)"
	@python3 scripts/curated_tasks.py

.PHONY: demo-ui
demo-ui: ## Run the UI demonstration script
	@echo "$(GREEN)🎬 Running UI demonstration...$(NC)"
	@python3 scripts/demo_phase6.py

# =============================================================================
# 🗄️ **Database Operations**
# =============================================================================

.PHONY: db-shell
db-shell: ## Open PostgreSQL shell
	@echo "$(GREEN)🗄️ Opening PostgreSQL shell...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec postgres psql -U gizmo_user -d gizmo_dev

.PHONY: db-backup
db-backup: ## Create database backup
	@echo "$(GREEN)🗄️ Creating database backup...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec postgres pg_dump -U gizmo_user -d gizmo_dev > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Backup created!$(NC)"

.PHONY: db-reset
db-reset: ## Reset database (WARNING: destroys data)
	@echo "$(RED)⚠️  WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo "$(YELLOW)🗄️ Resetting database...$(NC)"; \
		docker-compose -f $(COMPOSE_FILE) exec postgres psql -U gizmo_user -d gizmo_dev -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"; \
		docker-compose -f $(COMPOSE_FILE) exec postgres psql -U gizmo_user -d gizmo_dev -f /docker-entrypoint-initdb.d/init.sql; \
		echo "$(GREEN)✅ Database reset!$(NC)"; \
	else \
		echo "$(YELLOW)Database reset cancelled.$(NC)"; \
	fi

# =============================================================================
# 🔧 **Development & Maintenance**
# =============================================================================

.PHONY: clean
clean: ## Remove all containers, volumes, and images
	@echo "$(RED)🧹 Cleaning up all Docker resources...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down -v --rmi all
	@docker system prune -f
	@echo "$(GREEN)✅ Cleanup completed!$(NC)"

.PHONY: health
health: ## Check health of all services
	@echo "$(GREEN)🏥 Checking service health...$(NC)"
	@echo "$(YELLOW)Frontend (UI):$(NC)"
	@curl -s http://localhost:3002 | head -1 || echo "$(RED)❌ Frontend not responding$(NC)"
	@echo "$(YELLOW)API Backend:$(NC)"
	@curl -s http://localhost:8002/healthz | python3 -m json.tool || echo "$(RED)❌ API not responding$(NC)"
	@echo "$(YELLOW)Orchestrator:$(NC)"
	@curl -s http://localhost:8003/healthz | python3 -m json.tool || echo "$(RED)❌ Orchestrator not responding$(NC)"
	@echo "$(YELLOW)Database:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec postgres pg_isready -U gizmo_user || echo "$(RED)❌ Database not responding$(NC)"
	@echo "$(YELLOW)Redis:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec redis redis-cli ping || echo "$(RED)❌ Redis not responding$(NC)"

.PHONY: install-deps
install-deps: ## Install development dependencies
	@echo "$(GREEN)📦 Installing development dependencies...$(NC)"
	@pip3 install -r config/docker/requirements.txt --break-system-packages
	@cd app && npm install
	@echo "$(GREEN)✅ Dependencies installed!$(NC)"

# =============================================================================
# 📚 **Documentation & Help**
# =============================================================================

.PHONY: docs
docs: ## Open project documentation
	@echo "$(GREEN)📚 Opening project documentation...$(NC)"
	@echo "$(YELLOW)📖 README: README.md$(NC)"
	@echo "$(YELLOW)🏗️ Structure: PROJECT_STRUCTURE.md$(NC)"
	@echo "$(YELLOW)📋 Requirements: docs/requirements/PRD.md$(NC)"
	@echo "$(YELLOW)🚀 Deployment: docs/deployment/deploy.md$(NC)"
	@echo "$(YELLOW)🧪 Testing: tests/$(NC)"
	@echo "$(YELLOW)📜 Scripts: scripts/$(NC)"

.PHONY: structure
structure: ## Show project structure
	@echo "$(GREEN)🏗️ Gizmo AI Project Structure$(NC)"
	@echo "================================"
	@tree -I 'node_modules|__pycache__|*.pyc|.git|.next|.env*' -a

# =============================================================================
# 🚀 **Quick Start Commands**
# =============================================================================

.PHONY: quickstart
quickstart: ## Quick start for new developers
	@echo "$(GREEN)🚀 Gizmo AI Quick Start$(NC)"
	@echo "========================"
	@echo "$(YELLOW)1. Start the stack:$(NC) make up"
	@echo "$(YELLOW)2. Check health:$(NC) make health"
	@echo "$(YELLOW)3. View logs:$(NC) make logs"
	@echo "$(YELLOW)4. Run tests:$(NC) make test"
	@echo "$(YELLOW)5. Stop stack:$(NC) make down"
	@echo ""
	@echo "$(GREEN)🌐 Open http://localhost:3002 to see the UI!$(NC)"

# =============================================================================
# 🎯 **Portfolio & Demo Commands**
# =============================================================================

.PHONY: demo
demo: ## Run complete portfolio demonstration
	@echo "$(GREEN)🎬 Running Gizmo AI Portfolio Demo$(NC)"
	@echo "================================"
	@echo "$(YELLOW)1. Starting development stack...$(NC)"
	@make up
	@echo "$(YELLOW)2. Waiting for services to be ready...$(NC)"
	@sleep 10
	@echo "$(YELLOW)3. Checking service health...$(NC)"
	@make health
	@echo "$(YELLOW)4. Running curated task suite...$(NC)"
	@make test-curated
	@echo "$(YELLOW)5. Running UI demonstration...$(NC)"
	@make demo-ui
	@echo "$(GREEN)🎉 Demo completed! Open http://localhost:3002$(NC)"

.PHONY: portfolio
portfolio: ## Show portfolio-ready features
	@echo "$(GREEN)🎯 Gizmo AI Portfolio Features$(NC)"
	@echo "================================"
	@echo "$(GREEN)✅ Multi-Agent AI Development Platform$(NC)"
	@echo "$(GREEN)✅ Enterprise-Grade Reliability Features$(NC)"
	@echo "$(GREEN)✅ Professional UI with Real-time Updates$(NC)"
	@echo "$(GREEN)✅ Comprehensive Testing & Documentation$(NC)"
	@echo "$(GREEN)✅ Production Deployment Ready$(NC)"
	@echo "$(GREEN)✅ Cost-Controlled Public Demo$(NC)"
	@echo ""
	@echo "$(YELLOW)🚀 Ready for portfolio demonstration!$(NC)"

# =============================================================================
# 📋 **Default Target**
# =============================================================================

.DEFAULT_GOAL := help
