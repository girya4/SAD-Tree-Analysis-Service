# LCT Tree Analysis - Cloud Deployment Guide

## Версия 2.2 - Cloud Deployment

Эта версия оптимизирована для развертывания на Яндекс.Облаке и других облачных платформах.

## 🚀 Быстрый старт

### Автоматическое развертывание на Яндекс.Облаке

1. **Подготовка окружения:**
   ```bash
   # Клонируйте репозиторий
   git clone https://github.com/ValeraYakovlev/LCT_tree.git
   cd LCT_tree
   
   # Переключитесь на ветку cloud deployment
   git checkout v2.2-cloud-deployment
   ```

2. **Настройка Яндекс.Облака:**
   ```bash
   # Инициализация Yandex CLI
   ./yandex-cloud-setup.sh init
   
   # Создание виртуальной машины
   ./yandex-cloud-setup.sh create
   
   # Настройка VM с Docker
   ./yandex-cloud-setup.sh setup
   
   # Развертывание приложения
   ./yandex-cloud-setup.sh deploy
   ```

3. **Проверка статуса:**
   ```bash
   ./yandex-cloud-setup.sh status
   ```

## 📋 Требования

### Системные требования
- **CPU:** 2+ ядра
- **RAM:** 4+ GB
- **Диск:** 20+ GB SSD
- **ОС:** Ubuntu 20.04 LTS или новее

### Программное обеспечение
- Docker 20.10+
- Docker Compose 2.0+
- Git
- Yandex CLI (для автоматического развертывания)

## 🔧 Ручное развертывание

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt-get update && sudo apt-get upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перезагрузка для применения изменений
sudo reboot
```

### 2. Настройка приложения

```bash
# Клонирование репозитория
git clone https://github.com/ValeraYakovlev/LCT_tree.git
cd LCT_tree
git checkout v2.2-cloud-deployment

# Настройка переменных окружения
cp env.cloud.example .env
nano .env  # Отредактируйте настройки
```

### 3. Развертывание

```bash
# Запуск развертывания
./deploy-cloud.sh

# Или пошагово:
docker-compose -f docker-compose.cloud.yml up --build -d
```

## ⚙️ Конфигурация

### Переменные окружения (.env)

```bash
# База данных
POSTGRES_DB=image_processing
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here

# Безопасность
SECRET_KEY=your_very_secure_secret_key_here
DEBUG=False

# Сервер
HOST=0.0.0.0
PORT=8000
WORKERS=2
LOG_LEVEL=info

# Мониторинг
FLOWER_USER=admin
FLOWER_PASSWORD=your_flower_password_here

# Внешний доступ
DOMAIN_NAME=your-domain.com
SSL_EMAIL=your-email@example.com
```

### Настройка домена и SSL

1. **Настройка DNS:**
   - Создайте A-запись, указывающую на IP вашего сервера
   - Обновите `DOMAIN_NAME` в `.env`

2. **SSL сертификат (опционально):**
   ```bash
   # Создание SSL сертификата с Let's Encrypt
   sudo apt-get install certbot
   sudo certbot certonly --standalone -d your-domain.com
   
   # Копирование сертификатов
   sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
   sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
   sudo chown $USER:$USER ssl/*
   ```

## 🐳 Docker Compose Services

### Основные сервисы

- **nginx** - Reverse proxy и статические файлы
- **backend** - FastAPI приложение
- **worker** - Celery worker для обработки изображений
- **db** - PostgreSQL база данных
- **redis** - Redis для Celery
- **flower** - Мониторинг Celery

### Оптимизации для облака

- **Multi-stage builds** для уменьшения размера образов
- **Non-root пользователи** для безопасности
- **Health checks** для всех сервисов
- **Resource limits** для контроля потребления ресурсов
- **Rate limiting** для защиты от DDoS
- **Security headers** для защиты веб-приложения

## 📊 Мониторинг

### Health Checks

- **Приложение:** `http://your-domain.com/health`
- **База данных:** Автоматическая проверка через Docker
- **Redis:** Автоматическая проверка через Docker

### Flower Monitoring

- **URL:** `http://your-domain.com/flower/`
- **Логин:** admin (или значение из FLOWER_USER)
- **Пароль:** значение из FLOWER_PASSWORD

### Логи

```bash
# Все сервисы
docker-compose -f docker-compose.cloud.yml logs -f

# Конкретный сервис
docker-compose -f docker-compose.cloud.yml logs -f backend
docker-compose -f docker-compose.cloud.yml logs -f worker
```

## 🔧 Управление

### Основные команды

```bash
# Запуск
./deploy-cloud.sh deploy

# Остановка
./deploy-cloud.sh stop

# Перезапуск
./deploy-cloud.sh restart

# Обновление
./deploy-cloud.sh update

# Просмотр логов
./deploy-cloud.sh logs

# Статус сервисов
./deploy-cloud.sh status
```

### Обновление приложения

```bash
# Получение обновлений
git pull origin v2.2-cloud-deployment

# Пересборка и перезапуск
./deploy-cloud.sh update
```

## 🛡️ Безопасность

### Рекомендации

1. **Измените пароли по умолчанию:**
   - POSTGRES_PASSWORD
   - SECRET_KEY
   - FLOWER_PASSWORD

2. **Настройте файрвол:**
   ```bash
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   sudo ufw enable
   ```

3. **Регулярно обновляйте систему:**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

4. **Настройте резервное копирование:**
   ```bash
   # Создание бэкапа базы данных
   docker-compose -f docker-compose.cloud.yml exec db pg_dump -U postgres image_processing > backup.sql
   ```

## 🚨 Устранение неполадок

### Частые проблемы

1. **Сервисы не запускаются:**
   ```bash
   # Проверка логов
   docker-compose -f docker-compose.cloud.yml logs
   
   # Проверка статуса
   docker-compose -f docker-compose.cloud.yml ps
   ```

2. **Проблемы с базой данных:**
   ```bash
   # Проверка подключения
   docker-compose -f docker-compose.cloud.yml exec db pg_isready -U postgres
   
   # Запуск миграций вручную
   docker-compose -f docker-compose.cloud.yml exec backend alembic upgrade head
   ```

3. **Проблемы с памятью:**
   ```bash
   # Мониторинг ресурсов
   docker stats
   
   # Увеличение лимитов в docker-compose.cloud.yml
   ```

### Логи и отладка

```bash
# Детальные логи
docker-compose -f docker-compose.cloud.yml logs --tail=100 -f

# Проверка конфигурации
docker-compose -f docker-compose.cloud.yml config

# Пересборка без кэша
docker-compose -f docker-compose.cloud.yml build --no-cache
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `./deploy-cloud.sh logs`
2. Проверьте статус: `./deploy-cloud.sh status`
3. Создайте issue в репозитории GitHub
4. Обратитесь к документации Docker и Yandex Cloud

## 🔄 Миграция с предыдущих версий

### С версии 2.1

1. Создайте бэкап данных:
   ```bash
   docker-compose exec db pg_dump -U postgres image_processing > backup.sql
   ```

2. Переключитесь на новую ветку:
   ```bash
   git checkout v2.2-cloud-deployment
   ```

3. Обновите конфигурацию:
   ```bash
   cp env.cloud.example .env
   # Отредактируйте .env файл
   ```

4. Разверните новую версию:
   ```bash
   ./deploy-cloud.sh deploy
   ```

5. Восстановите данные:
   ```bash
   docker-compose -f docker-compose.cloud.yml exec -T db psql -U postgres image_processing < backup.sql
   ```

---

**Версия:** 2.2-cloud-deployment  
**Дата:** $(date)  
**Автор:** ValeraYakovlev
