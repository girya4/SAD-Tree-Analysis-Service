# LCT Tree Analysis Service Makefile v2.3

.PHONY: help install dev test clean docker-build docker-up docker-down

help: ## Show this help message
	@echo "LCT Tree Analysis Service v2.3 - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

dev: ## Run development server (requires Redis and PostgreSQL)
	python run.py

worker: ## Run Celery worker (requires Redis and PostgreSQL)
	python run_worker.py

test: ## Run API tests
	python test_api.py

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
	docker build -f docker/Dockerfile.cloud -t lct-tree-analysis:latest .
	docker build -f docker/Dockerfile.worker.cloud -t lct-tree-analysis-worker:latest .

docker-up-cloud: ## Start cloud deployment
	docker-compose -f docker/docker-compose.cloud.yml up -d

docker-down-cloud: ## Stop cloud deployment
	docker-compose -f docker/docker-compose.cloud.yml down

# Demo commands
demo: ## Run demo script
	./scripts/demo/demo.sh

demo-v2: ## Run ML tree analysis demo
	python3 scripts/demo/demo_v2.py

demo-v2.1: ## Run enhanced UI demo with image thumbnails
	./scripts/demo/demo_v2.1.sh

# Deployment
deploy: ## Deploy to server (requires SERVER_IP)
	@if [ -z "$(SERVER_IP)" ]; then echo "Usage: make deploy SERVER_IP=your_server_ip"; exit 1; fi
	./deploy.sh $(SERVER_IP)

deploy-local: ## Local deployment on current machine
	./deploy.sh local

deploy-quick: ## Quick deploy to server (requires SERVER_IP)
	@if [ -z "$(SERVER_IP)" ]; then echo "Usage: make deploy-quick SERVER_IP=your_server_ip"; exit 1; fi
	./deploy.sh $(SERVER_IP) root quick

# Cleanup
clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf uploads/original/*
	rm -rf uploads/processed/*
	rm -f test_image.jpg

clean-docker: ## Clean up Docker resources
	docker-compose down -v
	docker-compose -f docker/docker-compose.cloud.yml down -v
	docker system prune -f

# Setup
setup: install ## Setup development environment
	mkdir -p uploads/original uploads/processed
	@echo "Development environment setup complete!"
	@echo "To start the application:"
	@echo "  make dev     # Run FastAPI server"
	@echo "  make worker  # Run Celery worker (in another terminal)"
	@echo "  make test    # Run tests"
