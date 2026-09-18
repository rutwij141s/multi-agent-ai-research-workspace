"""
Tests for authentication system.
"""

import pytest
import tempfile
import os
from pathlib import Path

from auth.authentication import AuthenticationService


@pytest.fixture
def temp_auth_service(monkeypatch):
    """Create authentication service with temporary storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_file = Path(tmpdir) / "users.json"
        
        # Create a test instance
        auth = AuthenticationService()
        auth.users_file = temp_file
        auth._save_users({})
        
        yield auth


class TestAuthenticationService:
    """Test authentication service functionality."""
    
    def test_signup_success(self, temp_auth_service):
        """Test successful user signup."""
        success, error, user_id = temp_auth_service.signup(
            username="testuser",
            password="Test123"
        )
        
        assert success is True
        assert error is None
        assert user_id is not None
    
    def test_signup_weak_password(self, temp_auth_service):
        """Test signup with weak password."""
        success, error, user_id = temp_auth_service.signup(
            username="testuser",
            password="weak"
        )
        
        assert success is False
        assert "uppercase" in error.lower() or "digit" in error.lower()
        assert user_id is None
    
    def test_signup_short_username(self, temp_auth_service):
        """Test signup with short username."""
        success, error, user_id = temp_auth_service.signup(
            username="ab",
            password="Test123"
        )
        
        assert success is False
        assert "3 characters" in error
        assert user_id is None
    
    def test_signup_duplicate_username(self, temp_auth_service):
        """Test signup with duplicate username."""
        # Create first user
        temp_auth_service.signup("testuser", "Test123")
        
        # Try to create duplicate
        success, error, user_id = temp_auth_service.signup(
            "testuser",
            "Test456"
        )
        
        assert success is False
        assert "exists" in error.lower()
        assert user_id is None
    
    def test_login_success(self, temp_auth_service):
        """Test successful login."""
        # Create user
        temp_auth_service.signup("testuser", "Test123")
        
        # Login
        success, error, user_data = temp_auth_service.login(
            "testuser",
            "Test123"
        )
        
        assert success is True
        assert error is None
        assert user_data is not None
        assert user_data['username'] == "testuser"
        assert 'password_hash' not in user_data  # Should not return password
    
    def test_login_wrong_password(self, temp_auth_service):
        """Test login with wrong password."""
        # Create user
        temp_auth_service.signup("testuser", "Test123")
        
        # Login with wrong password
        success, error, user_data = temp_auth_service.login(
            "testuser",
            "WrongPass123"
        )
        
        assert success is False
        assert "Invalid" in error
        assert user_data is None
    
    def test_login_nonexistent_user(self, temp_auth_service):
        """Test login with nonexistent user."""
        success, error, user_data = temp_auth_service.login(
            "nonexistent",
            "Test123"
        )
        
        assert success is False
        assert "Invalid" in error
        assert user_data is None
    
    def test_password_hashing(self, temp_auth_service):
        """Test that passwords are properly hashed."""
        password = "Test123"
        hashed = temp_auth_service._hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 50  # Bcrypt hashes are long
        
        # Test verification
        assert temp_auth_service._verify_password(password, hashed) is True
        assert temp_auth_service._verify_password("wrong", hashed) is False
    
    def test_username_validation(self, temp_auth_service):
        """Test username validation."""
        # Valid usernames
        assert temp_auth_service.validate_username("user123")[0] is True
        assert temp_auth_service.validate_username("test_user")[0] is True
        assert temp_auth_service.validate_username("user-name")[0] is True
        
        # Invalid usernames
        assert temp_auth_service.validate_username("ab")[0] is False  # Too short
        assert temp_auth_service.validate_username("")[0] is False  # Empty
        assert temp_auth_service.validate_username("a" * 31)[0] is False  # Too long
        assert temp_auth_service.validate_username("user@name")[0] is False  # Invalid char
    
    def test_password_validation(self, temp_auth_service):
        """Test password validation."""
        # Valid passwords
        assert temp_auth_service.validate_password("Test123")[0] is True
        assert temp_auth_service.validate_password("Abc123def")[0] is True
        
        # Invalid passwords
        assert temp_auth_service.validate_password("test")[0] is False  # Too short
        assert temp_auth_service.validate_password("")[0] is False  # Empty
        assert temp_auth_service.validate_password("test123")[0] is False  # No uppercase
        assert temp_auth_service.validate_password("TEST123")[0] is False  # No lowercase
        assert temp_auth_service.validate_password("TestTest")[0] is False  # No digit
