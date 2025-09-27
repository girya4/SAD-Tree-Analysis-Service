# Image Processing Service

Сервис обработки изображений с использованием FastAPI, Celery, PostgreSQL и Redis.

## Архитектура

- **FastAPI** - веб-фреймворк для API
- **Celery** - система очередей для асинхронной обработки
- **PostgreSQL** - база данных для хранения задач и пользователей
- **Redis** - брокер сообщений для Celery
- **Docker** - контейнеризация всех сервисов

## Функциональность

- Загрузка изображений через API
- Автоматическая авторизация через Cookie
- Асинхронная обработка изображений
- Отслеживание статуса задач
- Webhook для обновления статусов

## API Endpoints

### POST /api/newTask
Загружает изображение и создает задачу обработки.

**Параметры:**
- `file` - файл изображения (multipart/form-data)

**Ответ:**
```json
{
  "task_id": 123,
  "message": "Task created successfully"
}
```

### GET /api/isReady/{task_id}
Проверяет статус задачи.

**Ответ:**
```json
{
  "id": 123,
  "status": "completed",
  "result_path": "/app/uploads/processed/processed_image.jpg",
  "metadata": "{\"original_size\": 1024000, \"processed_size\": 512000}"
}
```

### GET /
Health check endpoint.

**Ответ:**
```json
{
  "status": "healthy",
  "message": "Image processing service is running"
}
```

### POST /api/webhook/task-complete
Webhook для обновления статуса задачи (используется Celery).

## Запуск приложения

### С помощью Docker Compose (рекомендуется)

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd LCT_tree_task
```

2. Запустите все сервисы:
```bash
make docker-up
# или
docker-compose up --build
```

3. Приложение будет доступно по адресу: http://localhost

### Локальная разработка

1. Установите зависимости:
```bash
make install
# или
pip install -r requirements.txt
```

2. Запустите PostgreSQL и Redis локально

3. Запустите приложение:
```bash
make dev
# или
python run.py
```

4. В другом терминале запустите Celery worker:
```bash
make worker
# или
python run_worker.py
```

### Полезные команды

```bash
make help          # Показать все доступные команды
make setup         # Настроить окружение разработки
make test          # Запустить тесты API
make clean         # Очистить временные файлы
make docker-logs   # Показать логи Docker контейнеров
make docker-down   # Остановить все Docker сервисы
```

## Мониторинг

- **Frontend**: http://localhost/frontend/
- **API документация**: http://localhost/docs
- **Celery Flower**: http://localhost/flower/
- **Health Check**: http://localhost/

## Структура проекта

```
LCT_tree_task/
├── app/
│   ├── api/
│   │   ├── routes.py          # API endpoints
│   │   └── schemas.py         # Pydantic модели
│   ├── core/
│   │   ├── auth.py           # Авторизация через Cookie
│   │   ├── database.py       # Настройки БД
│   │   └── middleware.py     # Middleware
│   ├── models/
│   │   ├── user.py           # Модель пользователя
│   │   └── task.py           # Модель задачи
│   ├── services/
│   │   └── image_processor.py # Celery задачи
│   └── utils/
│       └── file_utils.py     # Утилиты для работы с файлами
├── uploads/
│   ├── original/             # Исходные файлы
│   └── processed/            # Обработанные файлы
├── main.py                   # Точка входа FastAPI
├── celery_app.py            # Конфигурация Celery
├── config.py                # Настройки приложения
├── docker-compose.yml       # Docker Compose конфигурация
├── Dockerfile               # Dockerfile для backend
├── Dockerfile.worker        # Dockerfile для Celery worker
└── requirements.txt         # Python зависимости
```

## Обработка изображений

Сервис выполняет следующие операции с изображениями:
- Конвертация в RGB формат
- Изменение размера (максимум 800x600 с сохранением пропорций)
- Сохранение в JPEG формате с качеством 85%
- Генерация метаданных (размеры, размер файла)

## Безопасность

- Автоматическая генерация уникальных cookie токенов
- Валидация типов и размеров файлов
- Проверка владения задачами
- CORS настройки для кросс-доменных запросов

## Масштабирование

Для увеличения производительности:
1. Увеличьте количество Celery workers
2. Используйте Redis Cluster
3. Настройте PostgreSQL репликацию
4. Добавьте балансировщик нагрузки
