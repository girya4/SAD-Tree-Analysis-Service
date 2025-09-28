#!/bin/bash

# Yandex Cloud Setup Script
# This script helps set up the environment for deploying to Yandex Cloud

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if Yandex CLI is installed
check_yandex_cli() {
    log_info "Checking Yandex CLI installation..."
    
    if ! command -v yc &> /dev/null; then
        log_warning "Yandex CLI not found. Installing..."
        
        # Install Yandex CLI
        curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash
        source ~/.bashrc
        
        log_success "Yandex CLI installed"
    else
        log_success "Yandex CLI is already installed"
    fi
}

# Initialize Yandex Cloud
init_yandex_cloud() {
    log_info "Initializing Yandex Cloud..."
    
    if [ ! -f ~/.config/yandex-cloud/config.yaml ]; then
        log_info "Please run 'yc init' to configure Yandex Cloud CLI"
        log_info "You will need:"
        log_info "  - Yandex Cloud account"
        log_info "  - Cloud ID"
        log_info "  - Folder ID"
        log_info "  - Default availability zone"
        echo ""
        read -p "Press Enter when you have completed 'yc init'..."
    else
        log_success "Yandex Cloud is already initialized"
    fi
}

# Create compute instance
create_compute_instance() {
    log_info "Creating compute instance..."
    
    # Get current folder ID
    FOLDER_ID=$(yc config get folder-id)
    
    # Create instance
    INSTANCE_NAME="lct-tree-analysis-$(date +%s)"
    
    log_info "Creating instance: $INSTANCE_NAME"
    
    yc compute instance create \
        --name $INSTANCE_NAME \
        --zone ru-central1-a \
        --network-interface subnet-name=default,nat-ip-version=ipv4 \
        --create-boot-disk image-folder-id=standard-images,image-family=ubuntu-2004-lts,size=20 \
        --ssh-key ~/.ssh/id_rsa.pub \
        --memory 4 \
        --cores 2 \
        --core-fraction 100 \
        --preemptible
    
    # Get instance IP
    INSTANCE_IP=$(yc compute instance get $INSTANCE_NAME --format json | jq -r '.network_interfaces[0].primary_v4_address.one_to_one_nat.address')
    
    log_success "Instance created: $INSTANCE_NAME"
    log_success "Public IP: $INSTANCE_IP"
    
    echo "INSTANCE_NAME=$INSTANCE_NAME" > .yandex-cloud.env
    echo "INSTANCE_IP=$INSTANCE_IP" >> .yandex-cloud.env
}

# Setup instance
setup_instance() {
    if [ ! -f .yandex-cloud.env ]; then
        log_error "Yandex Cloud environment file not found. Please run 'create_compute_instance' first."
        exit 1
    fi
    
    source .yandex-cloud.env
    
    log_info "Setting up instance: $INSTANCE_NAME"
    
    # Create setup script
    cat > setup-instance.sh << 'EOF'
#!/bin/bash
set -e

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install additional tools
sudo apt-get install -y git curl wget jq

# Create application directory
mkdir -p /home/$USER/lct-tree-analysis
cd /home/$USER/lct-tree-analysis

echo "Instance setup completed. Please log out and log back in to use Docker without sudo."
EOF

    # Copy setup script to instance
    scp setup-instance.sh ubuntu@$INSTANCE_IP:/home/ubuntu/
    
    # Run setup script
    ssh ubuntu@$INSTANCE_IP "chmod +x setup-instance.sh && ./setup-instance.sh"
    
    log_success "Instance setup completed"
}

# Deploy application
deploy_application() {
    if [ ! -f .yandex-cloud.env ]; then
        log_error "Yandex Cloud environment file not found. Please run 'create_compute_instance' first."
        exit 1
    fi
    
    source .yandex-cloud.env
    
    log_info "Deploying application to instance: $INSTANCE_NAME"
    
    # Create deployment directory
    ssh ubuntu@$INSTANCE_IP "mkdir -p /home/ubuntu/lct-tree-analysis"
    
    # Copy application files
    rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
        ./ ubuntu@$INSTANCE_IP:/home/ubuntu/lct-tree-analysis/
    
    # Deploy application
    ssh ubuntu@$INSTANCE_IP "cd /home/ubuntu/lct-tree-analysis && ./deploy-cloud.sh"
    
    log_success "Application deployed successfully"
    log_info "Application URL: http://$INSTANCE_IP"
}

# Show status
show_status() {
    if [ ! -f .yandex-cloud.env ]; then
        log_error "Yandex Cloud environment file not found."
        exit 1
    fi
    
    source .yandex-cloud.env
    
    log_info "Yandex Cloud Status:"
    echo "Instance Name: $INSTANCE_NAME"
    echo "Instance IP: $INSTANCE_IP"
    echo "Application URL: http://$INSTANCE_IP"
    echo "Health Check: http://$INSTANCE_IP/health"
    echo "Flower Monitoring: http://$INSTANCE_IP/flower/"
    
    # Check instance status
    yc compute instance get $INSTANCE_NAME --format table
}

# Cleanup
cleanup() {
    if [ ! -f .yandex-cloud.env ]; then
        log_error "Yandex Cloud environment file not found."
        exit 1
    fi
    
    source .yandex-cloud.env
    
    log_warning "This will delete the compute instance: $INSTANCE_NAME"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        yc compute instance delete $INSTANCE_NAME
        rm .yandex-cloud.env
        log_success "Instance deleted and environment file removed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Main menu
main() {
    case "${1:-help}" in
        "init")
            check_yandex_cli
            init_yandex_cloud
            ;;
        "create")
            create_compute_instance
            ;;
        "setup")
            setup_instance
            ;;
        "deploy")
            deploy_application
            ;;
        "status")
            show_status
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            echo "Yandex Cloud Setup Script"
            echo ""
            echo "Usage: $0 {init|create|setup|deploy|status|cleanup}"
            echo ""
            echo "Commands:"
            echo "  init    - Initialize Yandex Cloud CLI"
            echo "  create  - Create compute instance"
            echo "  setup   - Setup instance with Docker and dependencies"
            echo "  deploy  - Deploy application to instance"
            echo "  status  - Show current status"
            echo "  cleanup - Delete instance and cleanup"
            echo ""
            echo "Typical workflow:"
            echo "  1. $0 init"
            echo "  2. $0 create"
            echo "  3. $0 setup"
            echo "  4. $0 deploy"
            echo "  5. $0 status"
            ;;
    esac
}

main "$@"
