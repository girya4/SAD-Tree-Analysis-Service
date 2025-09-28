"""
Unit tests for database models.
"""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.task import Task
from app.models.user import User


class TestUserModel:
    """Test cases for User model."""
    
    @pytest.mark.unit
    def test_create_user(self, db_session):
        """Test creating a new user."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.created_at is not None
    
    @pytest.mark.unit
    def test_user_unique_username(self, db_session):
        """Test that usernames must be unique."""
        user1 = User(
            username="testuser",
            email="test1@example.com",
            hashed_password="hashed_password"
        )
        user2 = User(
            username="testuser",
            email="test2@example.com",
            hashed_password="hashed_password"
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    @pytest.mark.unit
    def test_user_unique_email(self, db_session):
        """Test that emails must be unique."""
        user1 = User(
            username="testuser1",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        user2 = User(
            username="testuser2",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestTaskModel:
    """Test cases for Task model."""
    
    @pytest.mark.unit
    def test_create_task(self, db_session):
        """Test creating a new task."""
        task = Task(
            original_path="/uploads/original/test.jpg",
            status="PENDING"
        )
        db_session.add(task)
        db_session.commit()
        
        assert task.id is not None
        assert task.original_path == "/uploads/original/test.jpg"
        assert task.status == "PENDING"
        assert task.created_at is not None
        assert task.updated_at is not None
    
    @pytest.mark.unit
    def test_task_status_enum(self, db_session):
        """Test that task status must be valid enum value."""
        task = Task(
            original_path="/uploads/original/test.jpg",
            status="INVALID_STATUS"
        )
        db_session.add(task)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    @pytest.mark.unit
    def test_task_default_values(self, db_session):
        """Test default values for task fields."""
        task = Task(
            original_path="/uploads/original/test.jpg",
            status="PENDING"
        )
        db_session.add(task)
        db_session.commit()
        
        assert task.processed_path is None
        assert task.tree_type is None
        assert task.tree_type_confidence is None
        assert task.overall_health_score is None
        assert task.damages_detected == "[]"
    
    @pytest.mark.unit
    def test_task_update_timestamp(self, db_session):
        """Test that updated_at timestamp changes when task is modified."""
        task = Task(
            original_path="/uploads/original/test.jpg",
            status="PENDING"
        )
        db_session.add(task)
        db_session.commit()
        
        original_updated_at = task.updated_at
        
        # Wait a small amount to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        task.status = "PROCESSING"
        db_session.commit()
        
        assert task.updated_at > original_updated_at
