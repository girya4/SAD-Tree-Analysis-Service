# 🔐 Настройка SSH для автоматического развертывания

## 📋 Требования

Для автоматического развертывания необходимо настроить SSH ключи для беспарольного подключения к серверу.

## 🛠️ Настройка SSH ключей

### 1. Генерация SSH ключей (если еще нет)

```bash
# Генерация новой пары ключей
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Или использование существующих ключей
ls ~/.ssh/
```

### 2. Копирование публичного ключа на сервер

```bash
# Автоматическое копирование (рекомендуется)
ssh-copy-id username@YOUR_SERVER_IP

# Или ручное копирование
cat ~/.ssh/id_rsa.pub | ssh username@YOUR_SERVER_IP "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### 3. Проверка подключения

```bash
# Тест подключения без пароля
ssh username@YOUR_SERVER_IP "echo 'SSH подключение работает!'"
```

## 🔧 Альтернативные методы развертывания

### Метод 1: Ручное развертывание

```bash
# 1. Подключиться к серверу
ssh username@YOUR_SERVER_IP

# 2. Клонировать репозиторий
git clone https://github.com/ValeraYakovlev/LCT_tree.git
cd LCT_tree

# 3. Запустить скрипт развертывания
./quick-deploy.sh
```

### Метод 2: Использование пароля

```bash
# Запуск с вводом пароля
sshpass -p 'your_password' ./quick-deploy.sh YOUR_SERVER_IP
```

### Метод 3: SCP загрузка

```bash
# Загрузка файлов через SCP
scp -r . username@YOUR_SERVER_IP:/home/username/lct-tree-analysis/

# Подключение и запуск
ssh username@YOUR_SERVER_IP "cd /home/username/lct-tree-analysis && ./quick-deploy.sh"
```

## 🚀 Быстрый старт без SSH ключей

### 1. Подготовка сервера

```bash
# Подключиться к серверу
ssh username@YOUR_SERVER_IP

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh

# Установить Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 2. Загрузка кода

```bash
# Клонировать репозиторий
git clone https://github.com/ValeraYakovlev/LCT_tree.git
cd LCT_tree
```

### 3. Настройка и запуск

```bash
# Создать .env файл
cp env.cloud.example .env

# Сгенерировать пароли
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)" >> .env
echo "REDIS_PASSWORD=$(openssl rand -base64 32)" >> .env
echo "SECRET_KEY=$(openssl rand -base64 64)" >> .env

# Создать директории
mkdir -p uploads/original uploads/processed logs ssl
chmod -R 755 uploads/

# Запустить приложение
docker-compose -f docker-compose.cloud.yml up -d --build
```

### 4. Проверка

```bash
# Проверить статус
docker-compose -f docker-compose.cloud.yml ps

# Проверить работу
curl http://localhost/
curl http://localhost/api/tasks
curl http://localhost/health
```

## 🔍 Устранение проблем

### Проблема: Permission denied (publickey)

```bash
# Проверить SSH ключи
ls -la ~/.ssh/

# Проверить права доступа
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

### Проблема: Host key verification failed

```bash
# Добавить сервер в known_hosts
ssh-keyscan YOUR_SERVER_IP >> ~/.ssh/known_hosts
```

### Проблема: Connection refused

```bash
# Проверить доступность сервера
ping YOUR_SERVER_IP

# Проверить SSH сервис
ssh -v username@YOUR_SERVER_IP
```

## 📚 Дополнительные ресурсы

- [SSH ключи - подробное руководство](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [Docker установка](https://docs.docker.com/engine/install/)
- [Docker Compose установка](https://docs.docker.com/compose/install/)
