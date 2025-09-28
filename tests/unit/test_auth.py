"""
Unit tests for authentication functionality.
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from app.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    get_current_user
)


class TestPasswordHashing:
    """Test cases for password hashing functionality."""
    
    @pytest.mark.unit
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
    
    @pytest.mark.unit
    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes."""
        password = "test_password_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTToken:
    """Test cases for JWT token functionality."""
    
    @pytest.mark.unit
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    @pytest.mark.unit
    def test_verify_valid_token(self):
        """Test verification of valid token."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
    
    @pytest.mark.unit
    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        invalid_token = "invalid.token.here"
        
        payload = verify_token(invalid_token)
        assert payload is None
    
    @pytest.mark.unit
    def test_verify_expired_token(self):
        """Test verification of expired token."""
        # Create token with very short expiration
        data = {"sub": "testuser"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        payload = verify_token(token)
        assert payload is None
    
    @pytest.mark.unit
    def test_token_expiration_time(self):
        """Test that token has correct expiration time."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload is not None
        
        # Check that expiration is in the future
        exp = payload.get("exp")
        assert exp is not None
        assert datetime.fromtimestamp(exp) > datetime.utcnow()


class TestUserAuthentication:
    """Test cases for user authentication."""
    
    @pytest.mark.unit
    def test_get_current_user_valid_token(self, db_session):
        """Test getting current user with valid token."""
        # Create test user
        from app.models.user import User
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password")
        )
        db_session.add(user)
        db_session.commit()
        
        # Create token for user
        token = create_access_token({"sub": user.username})
        
        # Mock the database dependency
        from app.core.database import get_db
        def mock_get_db():
            yield db_session
        
        # Test getting current user
        current_user = get_current_user(token, db_session)
        assert current_user is not None
        assert current_user.username == "testuser"
    
    @pytest.mark.unit
    def test_get_current_user_invalid_token(self, db_session):
        """Test getting current user with invalid token."""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):  # Should raise authentication error
            get_current_user(invalid_token, db_session)
    
    @pytest.mark.unit
    def test_get_current_user_nonexistent_user(self, db_session):
        """Test getting current user for non-existent user."""
        token = create_access_token({"sub": "nonexistent_user"})
        
        with pytest.raises(Exception):  # Should raise authentication error
            get_current_user(token, db_session)
