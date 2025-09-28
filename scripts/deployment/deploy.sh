#!/bin/bash

# LCT Tree Analysis Service - Автоматический скрипт развертывания
# Использование: ./deploy.sh [SERVER_IP] [USERNAME]

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка параметров
if [ $# -lt 1 ]; then
    echo "Использование: $0 <SERVER_IP> [USERNAME]"
    echo "Пример: $0 158.160.195.121 root"
    exit 1
fi

SERVER_IP=$1
USERNAME=${2:-root}
SERVER_PATH="/home/$USERNAME/lct-tree-analysis"

log "Начинаем развертывание LCT Tree Analysis Service на $SERVER_IP"

# Проверка подключения к серверу
log "Проверяем подключение к серверу..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes $USERNAME@$SERVER_IP exit 2>/dev/null; then
    error "Не удается подключиться к серверу $SERVER_IP"
    error "Убедитесь, что:"
    error "1. Сервер доступен"
    error "2. SSH ключи настроены"
    error "3. Пользователь $USERNAME существует"
    exit 1
fi
success "Подключение к серверу успешно"

# Подготовка сервера
log "Подготавливаем сервер..."
ssh $USERNAME@$SERVER_IP << 'EOF'
    # Обновление системы
    apt update && apt upgrade -y
    
    # Установка необходимых пакетов
    apt install -y curl wget unzip git
    
    # Установка Docker
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
    fi
    
    # Установка Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    # Создание директории для приложения
    mkdir -p /home/$USER/lct-tree-analysis
    cd /home/$USER/lct-tree-analysis
EOF

success "Сервер подготовлен"

# Загрузка файлов на сервер
log "Загружаем файлы на сервер..."
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
    ./ $USERNAME@$SERVER_IP:$SERVER_PATH/

success "Файлы загружены"

# Настройка на сервере
log "Настраиваем приложение на сервере..."
ssh $USERNAME@$SERVER_IP << EOF
    cd $SERVER_PATH
    
    # Создание .env файла
    if [ ! -f .env ]; then
        cp env.cloud.example .env
        
        # Генерация безопасных паролей
        POSTGRES_PASSWORD=\$(openssl rand -hex 32)
        REDIS_PASSWORD=\$(openssl rand -hex 32)
        SECRET_KEY=\$(openssl rand -hex 64)
        
        # Обновление .env файла
        sed -i "s/your_secure_password_here/\$POSTGRES_PASSWORD/" .env
        sed -i "s/your_redis_password_here/\$REDIS_PASSWORD/" .env
        sed -i "s/your_secret_key_here/\$SECRET_KEY/" .env
        
        echo "POSTGRES_PASSWORD=\$POSTGRES_PASSWORD" >> .env
        echo "REDIS_PASSWORD=\$REDIS_PASSWORD" >> .env
        echo "SECRET_KEY=\$SECRET_KEY" >> .env
    fi
    
    # Создание необходимых директорий
    mkdir -p uploads/original uploads/processed logs ssl
    chmod -R 755 uploads/
    
    # Запуск приложения
    docker-compose -f docker-compose.cloud.yml down 2>/dev/null || true
    docker-compose -f docker-compose.cloud.yml up -d --build
    
    # Ожидание запуска
    sleep 30
    
    # Проверка статуса
    docker-compose -f docker-compose.cloud.yml ps
EOF

success "Приложение настроено и запущено"

# Проверка работы
log "Проверяем работу приложения..."
sleep 10

# Проверка фронтенда
if curl -s http://$SERVER_IP/ | grep -q "Tree Analysis Service"; then
    success "Фронтенд работает: http://$SERVER_IP/"
else
    warning "Фронтенд может не работать. Проверьте логи:"
    ssh $USERNAME@$SERVER_IP "cd $SERVER_PATH && docker-compose -f docker-compose.cloud.yml logs nginx"
fi

# Проверка API
if curl -s http://$SERVER_IP/api/tasks | grep -q "tasks"; then
    success "API работает: http://$SERVER_IP/api/tasks"
else
    warning "API может не работать. Проверьте логи:"
    ssh $USERNAME@$SERVER_IP "cd $SERVER_PATH && docker-compose -f docker-compose.cloud.yml logs backend"
fi

# Проверка health check
if curl -s http://$SERVER_IP/health | grep -q "healthy"; then
    success "Health check работает: http://$SERVER_IP/health"
else
    warning "Health check может не работать. Проверьте логи:"
    ssh $USERNAME@$SERVER_IP "cd $SERVER_PATH && docker-compose -f docker-compose.cloud.yml logs backend"
fi

echo ""
success "🎉 Развертывание завершено!"
echo ""
echo "🌐 Ваше приложение доступно по адресу:"
echo "   Frontend: http://$SERVER_IP/"
echo "   API: http://$SERVER_IP/api/tasks"
echo "   Health: http://$SERVER_IP/health"
echo ""
echo "📋 Полезные команды для управления:"
echo "   ssh $USERNAME@$SERVER_IP 'cd $SERVER_PATH && docker-compose -f docker-compose.cloud.yml ps'"
echo "   ssh $USERNAME@$SERVER_IP 'cd $SERVER_PATH && docker-compose -f docker-compose.cloud.yml logs'"
echo "   ssh $USERNAME@$SERVER_IP 'cd $SERVER_PATH && docker-compose -f docker-compose.cloud.yml restart'"
echo ""
echo "📖 Подробная документация: DEPLOYMENT-GUIDE.md"
