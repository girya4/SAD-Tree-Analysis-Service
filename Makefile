# LCT Tree Analysis Service Makefile v2.3

.PHONY: help install dev test clean docker-build docker-up docker-down test-unit test-integration test-e2e test-all lint security ci

help: ## Show this help message
	@echo "LCT Tree Analysis Service v2.3 - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt
	playwright install chromium

dev: ## Run development server (requires Redis and PostgreSQL)
	python run.py

worker: ## Run Celery worker (requires Redis and PostgreSQL)
	python run_worker.py

# Testing commands
test: ## Run all tests
	pytest tests/ -v

test-unit: ## Run unit tests only
	pytest tests/unit/ -v -m unit

test-integration: ## Run integration tests only
	pytest tests/integration/ -v -m integration

test-e2e: ## Run end-to-end tests only
	pytest tests/e2e/ -v -m e2e

test-coverage: ## Run tests with coverage report
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

test-fast: ## Run fast tests (skip slow ones)
	pytest tests/ -v -m "not slow"

test-api: ## Run API tests only
	pytest tests/ -v -m api

test-frontend: ## Run frontend tests only
	pytest tests/ -v -m frontend

# Linting and code quality
lint: ## Run code linting and formatting checks
	black --check --diff .
	isort --check-only --diff .
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

lint-fix: ## Fix code formatting issues
	black .
	isort .

# Security checks
security: ## Run security checks
	bandit -r app/ -f json -o bandit-report.json
	safety check --json --output safety-report.json

# Docker commands
docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start all services with Docker Compose
	docker-compose up -d

docker-down: ## Stop all Docker services
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-restart: ## Restart all Docker services
	docker-compose restart

# Cloud deployment
docker-build-cloud: ## Build cloud-optimized Docker images
	docker build -f Dockerfile.cloud -t lct-tree-analysis:latest .
	docker build -f Dockerfile.worker.cloud -t lct-tree-analysis-worker:latest .

docker-up-cloud: ## Start cloud deployment
	docker-compose -f docker-compose.cloud.yml up -d

docker-down-cloud: ## Stop cloud deployment
	docker-compose -f docker-compose.cloud.yml down

# Testing with Docker
docker-test: ## Run tests in Docker containers
	docker-compose -f docker-compose.test.yml up --build

docker-test-unit: ## Run unit tests in Docker
	docker-compose -f docker-compose.test.yml run test-backend pytest tests/unit/ -v

docker-test-integration: ## Run integration tests in Docker
	docker-compose -f docker-compose.test.yml run test-backend pytest tests/integration/ -v

docker-test-e2e: ## Run E2E tests in Docker
	docker-compose -f docker-compose.test.yml run test-e2e

# CI/CD simulation
ci: lint security test ## Run all CI checks locally
	@echo "All CI checks completed successfully!"

# Demo commands
demo: ## Run demo script
	./demo.sh

demo-v2: ## Run ML tree analysis demo
	python3 demo_v2.py

demo-v2.1: ## Run enhanced UI demo with image thumbnails
	./demo_v2.1.sh

# Cleanup
clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf uploads/original/*
	rm -rf uploads/processed/*
	rm -f test_image.jpg
	rm -rf htmlcov/
	rm -f coverage.xml
	rm -f bandit-report.json
	rm -f safety-report.json
	rm -f .coverage

clean-docker: ## Clean up Docker resources
	docker-compose down -v
	docker-compose -f docker-compose.test.yml down -v
	docker-compose -f docker-compose.cloud.yml down -v
	docker system prune -f

# Setup
setup: install ## Setup development environment
	mkdir -p uploads/original uploads/processed
	@echo "Development environment setup complete!"
	@echo "To start the application:"
	@echo "  make dev     # Run FastAPI server"
	@echo "  make worker  # Run Celery worker (in another terminal)"
	@echo "  make test    # Run tests"
	@echo "  make lint    # Run linting"
	@echo "  make ci      # Run all CI checks"

setup-test: ## Setup test environment
	export DATABASE_URL="postgresql://test_user:test_password@localhost:5433/test_db"
	export REDIS_URL="redis://localhost:6380"
	export SECRET_KEY="test-secret-key"
	export TESTING="true"
	@echo "Test environment variables set!"
