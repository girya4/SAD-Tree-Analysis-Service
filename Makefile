# Image Processing Service Makefile

.PHONY: help install dev test clean docker-build docker-up docker-down

help: ## Show this help message
	@echo "Image Processing Service - Available commands:"
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

demo: ## Run demo script
	./demo.sh

demo-v2: ## Run ML tree analysis demo
	python3 demo_v2.py

demo-v2.1: ## Run enhanced UI demo with image thumbnails
	python3 demo_v2.1.py

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf uploads/original/*
	rm -rf uploads/processed/*
	rm -f test_image.jpg

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

setup: install ## Setup development environment
	mkdir -p uploads/original uploads/processed
	@echo "Development environment setup complete!"
	@echo "To start the application:"
	@echo "  make dev     # Run FastAPI server"
	@echo "  make worker  # Run Celery worker (in another terminal)"
	@echo "  make test    # Run tests"
