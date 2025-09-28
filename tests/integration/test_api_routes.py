"""
Integration tests for API routes.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json

from app.models.task import Task
from app.models.user import User
from app.core.auth import get_password_hash


class TestHealthEndpoint:
    """Test cases for health check endpoint."""
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data


class TestTaskEndpoints:
    """Test cases for task-related endpoints."""
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_get_tasks_empty(self, client):
        """Test getting tasks when none exist."""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        
        data = response.json()
        assert data == []
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_get_tasks_with_data(self, client, db_session):
        """Test getting tasks when data exists."""
        # Create test task
        task = Task(
            original_path="/uploads/original/test.jpg",
            status="PENDING"
        )
        db_session.add(task)
        db_session.commit()
        
        response = client.get("/api/tasks")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == task.id
        assert data[0]["status"] == "PENDING"
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_get_task_by_id(self, client, db_session):
        """Test getting specific task by ID."""
        # Create test task
        task = Task(
            original_path="/uploads/original/test.jpg",
            status="PENDING"
        )
        db_session.add(task)
        db_session.commit()
        
        response = client.get(f"/api/tasks/{task.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == task.id
        assert data["status"] == "PENDING"
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_get_task_not_found(self, client):
        """Test getting non-existent task."""
        response = client.get("/api/tasks/999")
        assert response.status_code == 404
    
    @pytest.mark.integration
    @pytest.mark.api
    @patch('app.api.routes.process_image_task.delay')
    def test_create_task_success(self, mock_celery_task, client, sample_image_file):
        """Test successful task creation."""
        mock_celery_task.return_value = Mock(id="test-task-id")
        
        files = {"file": ("test.jpg", sample_image_file, "image/jpeg")}
        response = client.post("/api/tasks", files=files)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "PENDING"
        assert "original_path" in data
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_create_task_no_file(self, client):
        """Test task creation without file."""
        response = client.post("/api/tasks")
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_create_task_invalid_file(self, client):
        """Test task creation with invalid file."""
        files = {"file": ("test.txt", b"not an image", "text/plain")}
        response = client.post("/api/tasks", files=files)
        assert response.status_code == 400
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_create_task_file_too_large(self, client):
        """Test task creation with file too large."""
        # Create a large file (simulate)
        large_content = b"x" * (10 * 1024 * 1024)  # 10MB
        files = {"file": ("large.jpg", large_content, "image/jpeg")}
        response = client.post("/api/tasks", files=files)
        assert response.status_code == 413  # Payload too large


class TestUserEndpoints:
    """Test cases for user-related endpoints."""
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_create_user_success(self, client):
        """Test successful user creation."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = client.post("/api/users", json=user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "password" not in data  # Password should not be returned
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_create_user_duplicate_username(self, client, db_session):
        """Test user creation with duplicate username."""
        # Create existing user
        user = User(
            username="testuser",
            email="existing@example.com",
            hashed_password=get_password_hash("password")
        )
        db_session.add(user)
        db_session.commit()
        
        # Try to create user with same username
        user_data = {
            "username": "testuser",
            "email": "new@example.com",
            "password": "newpassword123"
        }
        
        response = client.post("/api/users", json=user_data)
        assert response.status_code == 400
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_create_user_invalid_data(self, client):
        """Test user creation with invalid data."""
        user_data = {
            "username": "",  # Empty username
            "email": "invalid-email",  # Invalid email
            "password": "123"  # Too short password
        }
        
        response = client.post("/api/users", json=user_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_login_success(self, client, db_session):
        """Test successful user login."""
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("testpassword123")
        )
        db_session.add(user)
        db_session.commit()
        
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_login_invalid_credentials(self, client, db_session):
        """Test login with invalid credentials."""
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("testpassword123")
        )
        db_session.add(user)
        db_session.commit()
        
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 401
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent",
            "password": "password123"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Test cases for protected endpoints requiring authentication."""
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/users/me")
        assert response.status_code == 401
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 401
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_protected_endpoint_with_valid_token(self, client, db_session):
        """Test accessing protected endpoint with valid token."""
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("testpassword123")
        )
        db_session.add(user)
        db_session.commit()
        
        # Get token
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        login_response = client.post("/api/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
