.PHONY: help up down build logs restart clean migrate seed test test-backend test-frontend lint format

# === Colors ===
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

help: ## Show this help
	@echo ""
	@echo "$(BLUE)ClipoAI$(RESET) - Enterprise AI Video Processing Platform"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# === Docker ===
up: ## Start all services
	docker compose up -d

up-build: ## Build and start all services
	docker compose up -d --build

down: ## Stop all services
	docker compose down

down-clean: ## Stop all services and remove volumes
	docker compose down -v

build: ## Build all images
	docker compose build

logs: ## Tail all logs
	docker compose logs -f

logs-backend: ## Tail backend logs
	docker compose logs -f backend

restart: ## Restart all services
	docker compose restart

# === Database ===
migrate: ## Run database migrations
	docker compose exec backend alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MSG="description")
	docker compose exec backend alembic revision --autogenerate -m "$(MSG)"

migrate-downgrade: ## Rollback last migration
	docker compose exec backend alembic downgrade -1

seed: ## Seed database with sample data
	docker compose exec backend python -m scripts.seed

# === Testing ===
test: test-backend ## Run all tests

test-backend: ## Run backend tests
	docker compose exec backend pytest -v --tb=short

test-backend-cov: ## Run backend tests with coverage
	docker compose exec backend pytest -v --tb=short --cov=app --cov-report=term-missing

# === Code Quality ===
lint: ## Lint backend code
	docker compose exec backend ruff check app/

format: ## Format backend code
	docker compose exec backend ruff format app/

# === Utilities ===
shell-backend: ## Open a shell in the backend container
	docker compose exec backend bash

shell-db: ## Open psql in the database container
	docker compose exec postgres psql -U clipoai -d clipoai

clean: ## Remove all build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true

health: ## Check service health
	@echo "$(YELLOW)Checking services...$(RESET)"
	@curl -sf http://localhost/api/health && echo "$(GREEN) Backend: OK$(RESET)" || echo "$(YELLOW) Backend: DOWN$(RESET)"
	@curl -sf http://localhost:9001/minio/health/live && echo "$(GREEN) MinIO: OK$(RESET)" || echo "$(YELLOW) MinIO: DOWN$(RESET)"
