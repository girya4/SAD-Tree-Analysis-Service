#!/bin/bash

# Ручное развертывание LCT Tree Analysis Service
# Использование: ./manual-deploy.sh

set -e

echo "🚀 Ручное развертывание LCT Tree Analysis Service"
echo ""

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Устанавливаем..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "✅ Docker установлен"
else
    echo "✅ Docker уже установлен"
fi

# Проверка Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Устанавливаем..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose установлен"
else
    echo "✅ Docker Compose уже установлен"
fi

# Создание .env файла
if [ ! -f .env ]; then
    echo "📝 Создаем .env файл..."
    cp env.cloud.example .env
    
    # Генерация паролей
    POSTGRES_PASSWORD=$(openssl rand -base64 32)
    REDIS_PASSWORD=$(openssl rand -base64 32)
    SECRET_KEY=$(openssl rand -base64 64)
    
    echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >> .env
    echo "REDIS_PASSWORD=$REDIS_PASSWORD" >> .env
    echo "SECRET_KEY=$SECRET_KEY" >> .env
    
    echo "✅ .env файл создан с безопасными паролями"
else
    echo "✅ .env файл уже существует"
fi

# Создание директорий
echo "📁 Создаем необходимые директории..."
mkdir -p uploads/original uploads/processed logs ssl
chmod -R 755 uploads/
echo "✅ Директории созданы"

# Остановка предыдущих контейнеров
echo "🛑 Останавливаем предыдущие контейнеры..."
docker-compose -f docker-compose.cloud.yml down 2>/dev/null || true

# Запуск приложения
echo "🚀 Запускаем приложение..."
docker-compose -f docker-compose.cloud.yml up -d --build

# Ожидание запуска
echo "⏳ Ожидаем запуска сервисов..."
sleep 30

# Проверка статуса
echo "🔍 Проверяем статус сервисов..."
docker-compose -f docker-compose.cloud.yml ps

# Проверка работы
echo "🧪 Проверяем работу приложения..."

# Проверка фронтенда
if curl -s http://localhost/ | grep -q "Tree Analysis Service"; then
    echo "✅ Фронтенд работает: http://localhost/"
else
    echo "⚠️ Фронтенд может не работать"
fi

# Проверка API
if curl -s http://localhost/api/tasks | grep -q "tasks"; then
    echo "✅ API работает: http://localhost/api/tasks"
else
    echo "⚠️ API может не работать"
fi

# Проверка health check
if curl -s http://localhost/health | grep -q "healthy"; then
    echo "✅ Health check работает: http://localhost/health"
else
    echo "⚠️ Health check может не работать"
fi

echo ""
echo "🎉 Развертывание завершено!"
echo ""
echo "🌐 Ваше приложение доступно по адресу:"
echo "   Frontend: http://localhost/"
echo "   API: http://localhost/api/tasks"
echo "   Health: http://localhost/health"
echo ""
echo "📋 Полезные команды:"
echo "   docker-compose -f docker-compose.cloud.yml ps"
echo "   docker-compose -f docker-compose.cloud.yml logs"
echo "   docker-compose -f docker-compose.cloud.yml restart"
echo "   docker-compose -f docker-compose.cloud.yml down"
echo ""
echo "📖 Документация: DEPLOYMENT-GUIDE.md"
