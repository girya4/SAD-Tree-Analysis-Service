"""
Pytest configuration and shared fixtures for LCT Tree Analysis Service tests.
"""
import asyncio
import os
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import Mock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.models.task import Task
from app.models.user import User
from main import app


# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def temp_upload_dir():
    """Create a temporary directory for file uploads during tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(scope="function")
def mock_redis():
    """Mock Redis connection for tests."""
    mock_redis = Mock()
    mock_redis.ping.return_value = True
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    return mock_redis


@pytest.fixture(scope="function")
def mock_celery():
    """Mock Celery task for tests."""
    mock_task = Mock()
    mock_task.delay.return_value = Mock(id="test-task-id")
    return mock_task


@pytest.fixture(scope="function")
def sample_image_file():
    """Create a sample image file for testing."""
    from PIL import Image
    import io
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes


@pytest.fixture(scope="function")
def sample_task_data():
    """Sample task data for testing."""
    return {
        "id": 1,
        "status": "PENDING",
        "original_path": "/uploads/original/test.jpg",
        "processed_path": None,
        "tree_type": "oak",
        "tree_type_confidence": 0.85,
        "overall_health_score": 0.75,
        "damages_detected": '[]',
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }


@pytest.fixture(scope="function")
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashed_password_here",
        "is_active": True,
        "created_at": "2023-01-01T00:00:00"
    }


# Pytest markers for different test types
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "frontend: Frontend tests")


# Test environment setup
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = SQLALCHEMY_DATABASE_URL
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DEBUG"] = "true"
    yield
    # Cleanup
    if os.path.exists("test.db"):
        os.remove("test.db")
