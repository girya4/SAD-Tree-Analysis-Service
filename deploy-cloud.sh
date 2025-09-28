#!/bin/bash

# Cloud Deployment Script for Yandex Cloud
# This script automates the deployment process for the LCT Tree Analysis application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="lct-tree-analysis"
COMPOSE_FILE="docker-compose.cloud.yml"
ENV_FILE=".env"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required files exist
check_requirements() {
    log_info "Checking requirements..."
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    if [ ! -f "$ENV_FILE" ]; then
        log_warning "Environment file not found: $ENV_FILE"
        log_info "Creating environment file from template..."
        if [ -f "env.cloud.example" ]; then
            cp env.cloud.example .env
            log_warning "Please update .env file with your configuration before continuing"
            exit 1
        else
            log_error "No environment template found"
            exit 1
        fi
    fi
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    log_success "All requirements met"
}

# Generate secure passwords
generate_passwords() {
    log_info "Generating secure passwords..."
    
    # Generate random passwords
    POSTGRES_PASSWORD=$(openssl rand -base64 32)
    SECRET_KEY=$(openssl rand -base64 64)
    FLOWER_PASSWORD=$(openssl rand -base64 16)
    
    # Update .env file
    sed -i.bak "s/your_secure_password_here/$POSTGRES_PASSWORD/" .env
    sed -i.bak "s/your_very_secure_secret_key_here_change_in_production/$SECRET_KEY/" .env
    sed -i.bak "s/your_flower_password_here/$FLOWER_PASSWORD/" .env
    
    log_success "Passwords generated and updated in .env file"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p uploads/original uploads/processed logs ssl init-db
    
    log_success "Directories created"
}

# Build and start services
deploy_services() {
    log_info "Building and starting services..."
    
    # Stop existing services
    docker-compose -f $COMPOSE_FILE down --remove-orphans
    
    # Build and start services
    docker-compose -f $COMPOSE_FILE up --build -d
    
    log_success "Services deployed successfully"
}

# Wait for services to be healthy
wait_for_services() {
    log_info "Waiting for services to be healthy..."
    
    # Wait for database
    log_info "Waiting for database..."
    timeout 60 bash -c 'until docker-compose -f '$COMPOSE_FILE' exec -T db pg_isready -U postgres; do sleep 2; done'
    
    # Wait for Redis
    log_info "Waiting for Redis..."
    timeout 30 bash -c 'until docker-compose -f '$COMPOSE_FILE' exec -T redis redis-cli ping; do sleep 2; done'
    
    # Wait for backend
    log_info "Waiting for backend..."
    timeout 60 bash -c 'until curl -f http://localhost/health; do sleep 5; done'
    
    log_success "All services are healthy"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    docker-compose -f $COMPOSE_FILE exec -T backend alembic upgrade head
    
    log_success "Database migrations completed"
}

# Show deployment information
show_deployment_info() {
    log_success "Deployment completed successfully!"
    echo ""
    echo "=== Deployment Information ==="
    echo "Application URL: http://$(hostname -I | awk '{print $1}')"
    echo "Health Check: http://$(hostname -I | awk '{print $1}')/health"
    echo "Flower Monitoring: http://$(hostname -I | awk '{print $1}')/flower/"
    echo ""
    echo "=== Service Status ==="
    docker-compose -f $COMPOSE_FILE ps
    echo ""
    echo "=== Logs ==="
    echo "To view logs: docker-compose -f $COMPOSE_FILE logs -f"
    echo "To view specific service logs: docker-compose -f $COMPOSE_FILE logs -f [service_name]"
    echo ""
    echo "=== Management Commands ==="
    echo "Stop services: docker-compose -f $COMPOSE_FILE down"
    echo "Restart services: docker-compose -f $COMPOSE_FILE restart"
    echo "Update services: docker-compose -f $COMPOSE_FILE up --build -d"
}

# Main deployment function
main() {
    log_info "Starting cloud deployment for LCT Tree Analysis..."
    
    check_requirements
    generate_passwords
    create_directories
    deploy_services
    wait_for_services
    run_migrations
    show_deployment_info
    
    log_success "Deployment completed successfully!"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        log_info "Stopping services..."
        docker-compose -f $COMPOSE_FILE down
        log_success "Services stopped"
        ;;
    "restart")
        log_info "Restarting services..."
        docker-compose -f $COMPOSE_FILE restart
        log_success "Services restarted"
        ;;
    "logs")
        docker-compose -f $COMPOSE_FILE logs -f
        ;;
    "status")
        docker-compose -f $COMPOSE_FILE ps
        ;;
    "update")
        log_info "Updating services..."
        docker-compose -f $COMPOSE_FILE down
        docker-compose -f $COMPOSE_FILE up --build -d
        wait_for_services
        log_success "Services updated"
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status|update}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy the application (default)"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - Show logs from all services"
        echo "  status  - Show status of all services"
        echo "  update  - Update and restart all services"
        exit 1
        ;;
esac
