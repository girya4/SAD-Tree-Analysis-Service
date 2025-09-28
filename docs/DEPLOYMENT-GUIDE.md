# 🚀 Полное руководство по развертыванию LCT Tree Analysis Service

## 📋 Требования к серверу

### Минимальные требования:
- **ОС**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **RAM**: 2GB (рекомендуется 4GB)
- **CPU**: 2 ядра (рекомендуется 4 ядра)
- **Диск**: 20GB свободного места
- **Сеть**: Открытые порты 80, 443 (опционально)

### Поддерживаемые облачные платформы:
- ✅ Yandex Cloud
- ✅ AWS EC2
- ✅ Google Cloud Platform
- ✅ DigitalOcean
- ✅ VPS от любого провайдера

## 🛠️ Подготовка сервера

### 1. Подключение к серверу
```bash
ssh root@YOUR_SERVER_IP
# или
ssh username@YOUR_SERVER_IP
```

### 2. Обновление системы
```bash
# Ubuntu/Debian
apt update && apt upgrade -y

# CentOS/RHEL
yum update -y
```

### 3. Установка Docker и Docker Compose
```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установка Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Проверка установки
docker --version
docker-compose --version
```

### 4. Настройка пользователя (опционально)
```bash
# Добавить пользователя в группу docker
usermod -aG docker $USER

# Перелогиниться или выполнить
newgrp docker
```

## 📦 Развертывание приложения

### 1. Клонирование репозитория
```bash
# Перейти в домашнюю директорию
cd ~

# Клонировать репозиторий
git clone https://github.com/ValeraYakovlev/LCT_tree.git
cd LCT_tree

# Или загрузить архив
wget https://github.com/ValeraYakovlev/LCT_tree/archive/main.zip
unzip main.zip
cd LCT_tree-main
```

### 2. Настройка переменных окружения
```bash
# Создать файл .env
cp env.cloud.example .env

# Отредактировать .env файл
nano .env
```

**Содержимое .env файла:**
```env
# Database
POSTGRES_DB=image_processing
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here

# Redis
REDIS_PASSWORD=your_redis_password_here

# Application
SECRET_KEY=your_secret_key_here
DEBUG=false

# Domain (опционально)
DOMAIN_NAME=your-domain.com
```

### 3. Генерация безопасных паролей
```bash
# Генерация паролей
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)" >> .env
echo "REDIS_PASSWORD=$(openssl rand -base64 32)" >> .env
echo "SECRET_KEY=$(openssl rand -base64 64)" >> .env
```

### 4. Создание необходимых директорий
```bash
mkdir -p uploads/original uploads/processed logs ssl
chmod -R 755 uploads/
```

### 5. Запуск приложения
```bash
# Запуск всех сервисов
docker-compose -f docker-compose.cloud.yml up -d

# Проверка статуса
docker-compose -f docker-compose.cloud.yml ps
```

### 6. Проверка работы
```bash
# Проверка логов
docker-compose -f docker-compose.cloud.yml logs

# Проверка доступности
curl http://localhost/
curl http://localhost/api/tasks
curl http://localhost/health
```

## 🔧 Управление приложением

### Основные команды
```bash
# Запуск
docker-compose -f docker-compose.cloud.yml up -d

# Остановка
docker-compose -f docker-compose.cloud.yml down

# Перезапуск
docker-compose -f docker-compose.cloud.yml restart

# Просмотр логов
docker-compose -f docker-compose.cloud.yml logs -f

# Обновление (после изменений в коде)
docker-compose -f docker-compose.cloud.yml up -d --build
```

### Мониторинг
```bash
# Статус контейнеров
docker-compose -f docker-compose.cloud.yml ps

# Использование ресурсов
docker stats

# Логи конкретного сервиса
docker-compose -f docker-compose.cloud.yml logs backend
docker-compose -f docker-compose.cloud.yml logs nginx
```

## 🌐 Настройка домена (опционально)

### 1. Настройка DNS
```
A    your-domain.com    -> YOUR_SERVER_IP
A    www.your-domain.com -> YOUR_SERVER_IP
```

### 2. Обновление .env файла
```env
DOMAIN_NAME=your-domain.com
```

### 3. Перезапуск nginx
```bash
docker-compose -f docker-compose.cloud.yml restart nginx
```

## 🔒 Настройка SSL (опционально)

### 1. Получение SSL сертификата
```bash
# Установка Certbot
apt install certbot

# Получение сертификата
certbot certonly --standalone -d your-domain.com

# Копирование сертификатов
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
```

### 2. Обновление nginx конфигурации
```bash
# Использовать nginx.cloud.conf вместо nginx.simple.conf
# в Dockerfile.nginx
```

## 📊 Мониторинг и логи

### Просмотр логов
```bash
# Все логи
docker-compose -f docker-compose.cloud.yml logs

# Логи конкретного сервиса
docker-compose -f docker-compose.cloud.yml logs backend
docker-compose -f docker-compose.cloud.yml logs nginx
docker-compose -f docker-compose.cloud.yml logs db
```

### Мониторинг ресурсов
```bash
# Использование ресурсов
docker stats

# Место на диске
df -h

# Использование памяти
free -h
```

## 🔄 Обновление приложения

### 1. Остановка сервисов
```bash
docker-compose -f docker-compose.cloud.yml down
```

### 2. Обновление кода
```bash
# Если используете git
git pull origin main

# Или загрузить новую версию
wget https://github.com/ValeraYakovlev/LCT_tree/archive/main.zip
unzip -o main.zip
```

### 3. Пересборка и запуск
```bash
docker-compose -f docker-compose.cloud.yml up -d --build
```

## 🚨 Устранение неполадок

### Проблема: 404 ошибка
```bash
# Проверка nginx конфигурации
docker-compose -f docker-compose.cloud.yml exec nginx nginx -t

# Перезапуск nginx
docker-compose -f docker-compose.cloud.yml restart nginx
```

### Проблема: База данных не подключается
```bash
# Проверка логов базы данных
docker-compose -f docker-compose.cloud.yml logs db

# Перезапуск базы данных
docker-compose -f docker-compose.cloud.yml restart db
```

### Проблема: Backend не отвечает
```bash
# Проверка логов backend
docker-compose -f docker-compose.cloud.yml logs backend

# Перезапуск backend
docker-compose -f docker-compose.cloud.yml restart backend
```

### Проблема: Недостаточно места
```bash
# Очистка неиспользуемых образов
docker system prune -a

# Очистка логов
docker-compose -f docker-compose.cloud.yml down
docker volume prune
```

## 📋 Чек-лист развертывания

- [ ] Сервер подготовлен (Docker установлен)
- [ ] Код загружен на сервер
- [ ] Файл .env настроен
- [ ] Директории созданы
- [ ] Приложение запущено
- [ ] Проверена доступность фронтенда
- [ ] Проверена работа API
- [ ] Проверен health check
- [ ] Настроен домен (если нужно)
- [ ] Настроен SSL (если нужно)

## 🆘 Получение помощи

Если возникли проблемы:

1. **Проверьте логи**: `docker-compose -f docker-compose.cloud.yml logs`
2. **Проверьте статус**: `docker-compose -f docker-compose.cloud.yml ps`
3. **Перезапустите сервисы**: `docker-compose -f docker-compose.cloud.yml restart`
4. **Обратитесь к документации**: README.md, README-CLOUD.md

## 🎯 Быстрый старт

```bash
# 1. Подготовка сервера
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 2. Загрузка кода
git clone https://github.com/ValeraYakovlev/LCT_tree.git
cd LCT_tree

# 3. Настройка
cp env.cloud.example .env
# Отредактировать .env файл

# 4. Запуск
mkdir -p uploads/original uploads/processed logs ssl
docker-compose -f docker-compose.cloud.yml up -d

# 5. Проверка
curl http://localhost/
```

**Готово! Ваше приложение работает на http://YOUR_SERVER_IP** 🎉
