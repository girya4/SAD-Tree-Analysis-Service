#!/bin/bash

# Быстрое развертывание LCT Tree Analysis Service
# Использование: ./quick-deploy.sh [SERVER_IP]

set -e

SERVER_IP=${1:-"158.160.195.121"}
USERNAME="root"

echo "🚀 Быстрое развертывание LCT Tree Analysis Service на $SERVER_IP"

# Проверка подключения
echo "📡 Проверяем подключение к серверу..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes $USERNAME@$SERVER_IP exit 2>/dev/null; then
    echo "❌ Не удается подключиться к серверу $SERVER_IP"
    echo "Убедитесь, что SSH ключи настроены"
    exit 1
fi
echo "✅ Подключение успешно"

# Подготовка сервера
echo "🔧 Подготавливаем сервер..."
ssh $USERNAME@$SERVER_IP << 'EOF'
    # Обновление и установка Docker
    apt update && apt install -y curl wget
    
    # Установка Docker
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && rm get-docker.sh
    fi
    
    # Установка Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
EOF

# Загрузка файлов
echo "📦 Загружаем файлы на сервер..."
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
    ./ $USERNAME@$SERVER_IP:/home/$USERNAME/lct-tree-analysis/

# Настройка и запуск
echo "⚙️ Настраиваем и запускаем приложение..."
ssh $USERNAME@$SERVER_IP << EOF
    cd /home/$USERNAME/lct-tree-analysis
    
    # Создание .env файла
    if [ ! -f .env ]; then
        cp env.cloud.example .env
        echo "POSTGRES_PASSWORD=\$(openssl rand -hex 32)" >> .env
        echo "REDIS_PASSWORD=\$(openssl rand -hex 32)" >> .env
        echo "SECRET_KEY=\$(openssl rand -hex 64)" >> .env
    fi
    
    # Создание директорий
    mkdir -p uploads/original uploads/processed logs ssl
    chmod -R 755 uploads/
    
    # Запуск
    docker-compose -f docker-compose.cloud.yml down 2>/dev/null || true
    docker-compose -f docker-compose.cloud.yml up -d --build
    
    # Ожидание
    sleep 30
EOF

# Проверка
echo "🔍 Проверяем работу приложения..."
sleep 10

if curl -s http://$SERVER_IP/ | grep -q "Tree Analysis Service"; then
    echo "✅ Фронтенд работает: http://$SERVER_IP/"
else
    echo "⚠️ Фронтенд может не работать"
fi

if curl -s http://$SERVER_IP/api/tasks | grep -q "tasks"; then
    echo "✅ API работает: http://$SERVER_IP/api/tasks"
else
    echo "⚠️ API может не работать"
fi

if curl -s http://$SERVER_IP/health | grep -q "healthy"; then
    echo "✅ Health check работает: http://$SERVER_IP/health"
else
    echo "⚠️ Health check может не работать"
fi

echo ""
echo "🎉 Развертывание завершено!"
echo "🌐 Приложение доступно по адресу: http://$SERVER_IP/"
echo ""
echo "📋 Управление:"
echo "   ssh $USERNAME@$SERVER_IP 'cd /home/$USERNAME/lct-tree-analysis && docker-compose -f docker-compose.cloud.yml ps'"
echo "   ssh $USERNAME@$SERVER_IP 'cd /home/$USERNAME/lct-tree-analysis && docker-compose -f docker-compose.cloud.yml logs'"
