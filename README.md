# SAD-Tree-Analysis-Service

AI-powered tree analysis service with FastAPI, Celery, PostgreSQL and Redis. Uses machine learning to analyze tree health, detect damage, and provide treatment recommendations.

## 🚀 Version 2.3 - Production Ready

**NEW:** Version 2.3 includes optimized cloud deployment configuration and production-ready setup.

### 🚀 Quick deployment

```bash
# Automatic deployment to a new server
./deploy.sh YOUR_SERVER_IP

# Local deployment
./deploy.sh local

# Using the Makefile
make deploy SERVER_IP=YOUR_SERVER_IP
make deploy-local
```

**Deployment documentation:** [docs/DEPLOYMENT-GUIDE.md](docs/DEPLOYMENT-GUIDE.md)

### 🔧 Quick local start

```bash
cd docker
docker-compose build
docker-compose up -d
```

## 📁 Project structure

```
LCT_tree_task/
├── app/                    # Main application
│   ├── api/               # API endpoints
│   ├── config/            # ML configuration
│   ├── core/              # Core components
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── docker/                # Docker configurations
│   ├── Dockerfile.cloud
│   ├── Dockerfile.nginx
│   ├── Dockerfile.worker.cloud
│   └── docker-compose.cloud.yml
├── scripts/               # Scripts
│   ├── deployment/        # Deployment scripts
│   └── demo/              # Demo scripts
├── docs/                  # Documentation
│   ├── DEPLOYMENT-GUIDE.md
│   ├── README-CLOUD.md
│   └── SSH-SETUP.md
├── config/                # Configuration files
│   └── env.cloud.example
├── frontend/              # Frontend
│   └── index.html
├── nginx/                 # Nginx configuration
│   ├── nginx.simple.conf
│   └── nginx.cloud.conf
├── uploads/               # Uploaded files
│   ├── original/
│   └── processed/
├── logs/                  # Logs
├── ssl/                   # SSL certificates
├── deploy.sh              # Main deployment script
├── Makefile               # Development commands
└── requirements.txt       # Python dependencies
```

## 🌩️ Version 2.2 - Cloud Deployment Ready

Version 2.2 includes optimized cloud deployment configuration for Yandex Cloud and other cloud platforms. See [docs/README-CLOUD.md](docs/README-CLOUD.md) for detailed cloud deployment instructions.

## Architecture

- **FastAPI** - web framework for the API
- **Celery** - task queue for asynchronous processing
- **PostgreSQL** - database for storing tasks and users
- **Redis** - message broker for Celery
- **Docker** - containerization for all services

## Features

- Uploading images via the API
- Automatic authentication via cookies
- Asynchronous image processing
- Tracking task status
- Webhook for status updates

## API Endpoints

### POST /api/newTask
Uploads an image and creates a processing task.

**Parameters:**
- `file` - image file (multipart/form-data)

**Response:**
```json
{
  "task_id": 123,
  "message": "Task created successfully"
}
```

### GET /api/isReady/{task_id}
Checks the task status.

**Response:**
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

**Response:**
```json
{
  "status": "healthy",
  "message": "Image processing service is running"
}
```

### POST /api/webhook/task-complete
Webhook for updating the task status (used by Celery).

## Running the application

### Using Docker Compose (recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd LCT_tree_task
```

2. Start all services:
```bash
make docker-up
# or
docker-compose up --build
```

3. The application will be available at: http://localhost

### Local development

1. Install dependencies:
```bash
make install
# or
pip install -r requirements.txt
```

2. Start PostgreSQL and Redis locally

3. Run the application:
```bash
make dev
# or
python run.py
```

4. In another terminal, start the Celery worker:
```bash
make worker
# or
python run_worker.py
```

### Useful commands

```bash
make help              # Show all available commands
make setup             # Set up the development environment
make test              # Run API tests
make clean             # Clean temporary files
make docker-logs       # Show Docker container logs
make docker-down       # Stop all Docker services
make docker-up-cloud   # Start cloud deployment
make docker-down-cloud # Stop cloud deployment
```

## Monitoring

- **Frontend**: http://localhost/frontend/
- **API documentation**: http://localhost/docs
- **Celery Flower**: http://localhost/flower/
- **Health Check**: http://localhost/

## 🌳 ML Tree Analysis Features

### Tree Type Detection
- Oak, Pine, Birch, Maple, Cherry, Unknown
- Confidence scoring for each prediction

### Damage Detection
- Insect damage, Fungal infection, Bark damage
- Leaf discoloration, Branch breakage, Root damage
- Drought stress, Nutrient deficiency
- Severity levels: Low, Medium, High

### Health Assessment
- Overall health score (0.0 - 1.0)
- Treatment recommendations
- Processing time: 5-25 seconds per image

### API Endpoints
- `POST /api/newTasks` - Upload multiple images
- `GET /api/tasks` - List user tasks with ML results
- `GET /api/isReady/{id}` - Get task status with analysis

### Demo Commands
```bash
make demo-v2.1  # Run enhanced UI demo with image thumbnails
make demo-v2    # Run ML tree analysis demo
make demo       # Run basic image processing demo
```

## 🖼️ Enhanced UI Features (v2.1)

### Image Thumbnails
- Tree images displayed next to each task
- Hover effects and responsive design
- Fallback for missing images

### Smart Task Ordering
- Newest tasks appear at the top
- Chronological sorting by creation time
- Better user experience

### Flexible ML Configuration
- Easy-to-modify ML mock service
- Comprehensive configuration comments
- Database-compatible field changes
- Frontend adaptation guides

### ML Configuration Guide
- Clear instructions for adding new tree types
- Damage type configuration examples
- Output field modification guides
- Database migration notes

## Image processing

The service performs the following operations on images:
- Convert to RGB
- Resize (max 800x600 while preserving aspect ratio)
- Save as JPEG with quality 85%
- Generate metadata (dimensions, file size)

## Security

- Automatic generation of unique cookie tokens
- Validation of file types and sizes
- Task ownership checks
- CORS configuration for cross-domain requests

## Scaling

To increase performance:
1. Increase the number of Celery workers
2. Use Redis Cluster
3. Configure PostgreSQL replication
4. Add a load balancer
