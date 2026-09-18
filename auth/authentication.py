"""
Authentication system for aRe_Agent application.
Handles user signup, login, and password management.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import bcrypt

from utils.config import config
from utils.logging import get_logger
from utils.helpers import generate_id

logger = get_logger(__name__)


class AuthenticationService:
    """Service for user authentication and management."""
    
    def __init__(self):
        """Initialize authentication service."""
        self.users_file = Path(config.DATA_DIR) / "users.json"
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize users file if it doesn't exist
        if not self.users_file.exists():
            self._save_users({})
        
        logger.info("Authentication service initialized")
    
    def _load_users(self) -> Dict[str, Any]:
        """
        Load users from storage.
        
        Returns:
            Dictionary of users
        """
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            return {}
    
    def _save_users(self, users: Dict[str, Any]) -> bool:
        """
        Save users to storage.
        
        Args:
            users: Dictionary of users
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving users: {e}")
            return False
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            hashed: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def validate_username(self, username: str) -> tuple[bool, Optional[str]]:
        """
        Validate username format.
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username:
            return False, "Username cannot be empty"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 30:
            return False, "Username must be at most 30 characters long"
        
        if not username.replace('_', '').replace('-', '').isalnum():
            return False, "Username can only contain letters, numbers, hyphens, and underscores"
        
        return True, None
    
    def validate_password(self, password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password cannot be empty"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        if len(password) > 100:
            return False, "Password is too long"
        
        # Basic strength requirements
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            return False, "Password must contain at least one uppercase letter, one lowercase letter, and one digit"
        
        return True, None
    
    def signup(
        self,
        username: str,
        password: str,
        email: Optional[str] = None
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Create a new user account.
        
        Args:
            username: Username
            password: Password
            email: Optional email address
            
        Returns:
            Tuple of (success, error_message, user_id)
        """
        try:
            # Validate username
            is_valid, error = self.validate_username(username)
            if not is_valid:
                return False, error, None
            
            # Validate password
            is_valid, error = self.validate_password(password)
            if not is_valid:
                return False, error, None
            
            # Load existing users
            users = self._load_users()
            
            # Check if username already exists
            username_lower = username.lower()
            for user_data in users.values():
                if user_data.get('username', '').lower() == username_lower:
                    return False, "Username already exists", None
            
            # Create user
            user_id = generate_id()
            hashed_password = self._hash_password(password)
            
            users[user_id] = {
                'user_id': user_id,
                'username': username,
                'password_hash': hashed_password,
                'email': email,
                'created_at': datetime.now().isoformat(),
                'last_login': None
            }
            
            # Save users
            if self._save_users(users):
                logger.info(f"User created: {username} (ID: {user_id})")
                return True, None, user_id
            else:
                return False, "Failed to save user data", None
                
        except Exception as e:
            logger.error(f"Error during signup: {e}")
            return False, f"Signup failed: {str(e)}", None
    
    def login(
        self,
        username: str,
        password: str
    ) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Authenticate a user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, error_message, user_data)
        """
        try:
            if not username or not password:
                return False, "Username and password are required", None
            
            users = self._load_users()
            
            # Find user by username
            username_lower = username.lower()
            user_data = None
            user_id = None
            
            for uid, data in users.items():
                if data.get('username', '').lower() == username_lower:
                    user_id = uid
                    user_data = data
                    break
            
            if not user_data:
                return False, "Invalid username or password", None
            
            # Verify password
            password_hash = user_data.get('password_hash', '')
            if not self._verify_password(password, password_hash):
                return False, "Invalid username or password", None
            
            # Update last login
            user_data['last_login'] = datetime.now().isoformat()
            users[user_id] = user_data
            self._save_users(users)
            
            # Return user data without password hash
            safe_user_data = {
                'user_id': user_data['user_id'],
                'username': user_data['username'],
                'email': user_data.get('email'),
                'created_at': user_data.get('created_at'),
                'last_login': user_data.get('last_login')
            }
            
            logger.info(f"User logged in: {username}")
            return True, None, safe_user_data
            
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False, f"Login failed: {str(e)}", None
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user data by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            User data dictionary (without password) or None
        """
        try:
            users = self._load_users()
            user_data = users.get(user_id)
            
            if not user_data:
                return None
            
            # Return without password hash
            return {
                'user_id': user_data['user_id'],
                'username': user_data['username'],
                'email': user_data.get('email'),
                'created_at': user_data.get('created_at'),
                'last_login': user_data.get('last_login')
            }
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> tuple[bool, Optional[str]]:
        """
        Change user password.
        
        Args:
            user_id: User identifier
            old_password: Current password
            new_password: New password
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Validate new password
            is_valid, error = self.validate_password(new_password)
            if not is_valid:
                return False, error
            
            users = self._load_users()
            user_data = users.get(user_id)
            
            if not user_data:
                return False, "User not found"
            
            # Verify old password
            if not self._verify_password(old_password, user_data['password_hash']):
                return False, "Current password is incorrect"
            
            # Update password
            user_data['password_hash'] = self._hash_password(new_password)
            users[user_id] = user_data
            
            if self._save_users(users):
                logger.info(f"Password changed for user {user_id}")
                return True, None
            else:
                return False, "Failed to save new password"
                
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False, f"Failed to change password: {str(e)}"
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user account.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            users = self._load_users()
            
            if user_id not in users:
                logger.warning(f"Attempted to delete non-existent user: {user_id}")
                return False
            
            del users[user_id]
            
            if self._save_users(users):
                logger.info(f"User deleted: {user_id}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False


# Singleton instance
_auth_service = None


def get_auth_service() -> AuthenticationService:
    """Get or create authentication service instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthenticationService()
    return _auth_service
