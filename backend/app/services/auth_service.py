"""Authentication service using raw MySQL queries."""
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from passlib.context import CryptContext
import secrets
import uuid
import jwt
from jwt import PyJWTError

from app.core.database import get_db
from app.core.logging import logger
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings (in production, use environment variables)
SECRET_KEY = getattr(settings, 'SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


class AuthService:
    """Service for authentication operations."""
    
    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def register_user(self, username: str, password: str, name: str, email: Optional[str] = None) -> Dict:
        """
        Register a new user.
        
        Args:
            username: Username
            password: Plain text password
            name: Full name
            email: Optional email
            
        Returns:
            Created user dictionary
            
        Raises:
            HTTPException: If username already exists
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Check if username exists
            cursor.execute("SELECT * FROM user_auth WHERE username = %s", (username,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.close()
                raise HTTPException(status_code=400, detail="Username already exists")
            
            # Create user in users table first
            user_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO users (id, name, added_at) VALUES (%s, %s, %s)",
                (user_id, name, datetime.utcnow())
            )
            
            # Create auth record
            password_hash = self._hash_password(password)
            cursor.execute("""
                INSERT INTO user_auth (user_id, username, password_hash, email, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, username, password_hash, email, True, datetime.utcnow()))
            
            # Assign default cashier role
            cursor.execute("""
                INSERT INTO user_roles (user_id, role, created_at)
                VALUES (%s, %s, %s)
            """, (user_id, 'cashier', datetime.utcnow()))
            
            conn.commit()
            
            # Fetch created user
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.execute("SELECT role FROM user_roles WHERE user_id = %s", (user_id,))
            roles = [row['role'] for row in cursor.fetchall()]
            cursor.close()
            
            logger.info(f"User registered: {username}")
            return {
                "user_id": user_id,
                "username": username,
                "name": name,
                "email": email,
                "roles": roles
            }
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User dictionary with token if successful, None otherwise
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get auth record
            cursor.execute("""
                SELECT ua.*, u.name 
                FROM user_auth ua
                JOIN users u ON ua.user_id = u.id
                WHERE ua.username = %s
            """, (username,))
            auth_record = cursor.fetchone()
            
            if not auth_record:
                cursor.close()
                return None
            
            # Check if user is active
            if not auth_record.get('is_active', True):
                cursor.close()
                raise HTTPException(status_code=403, detail="User account is inactive")
            
            # Verify password
            if not self._verify_password(password, auth_record['password_hash']):
                cursor.close()
                return None
            
            # Get user roles
            cursor.execute("SELECT role FROM user_roles WHERE user_id = %s", (auth_record['user_id'],))
            roles = [row['role'] for row in cursor.fetchall()]
            
            # Update last login
            cursor.execute(
                "UPDATE user_auth SET last_login = %s WHERE user_id = %s",
                (datetime.utcnow(), auth_record['user_id'])
            )
            conn.commit()
            cursor.close()
            
            # Create access token
            token_data = {
                "sub": auth_record['user_id'],
                "username": username,
                "roles": roles
            }
            access_token = self._create_access_token(data=token_data)
            
            logger.info(f"User authenticated: {username}")
            return {
                "user_id": auth_record['user_id'],
                "username": username,
                "name": auth_record['name'],
                "email": auth_record.get('email'),
                "roles": roles,
                "access_token": access_token
            }
    
    def get_user_by_token(self, token: str) -> Optional[Dict]:
        """
        Get user information from JWT token.
        
        Args:
            token: JWT access token
            
        Returns:
            User dictionary or None if invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            username: str = payload.get("username")
            roles: List[str] = payload.get("roles", [])
            
            if user_id is None:
                return None
            
            with get_db() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT ua.*, u.name 
                    FROM user_auth ua
                    JOIN users u ON ua.user_id = u.id
                    WHERE ua.user_id = %s AND ua.is_active = TRUE
                """, (user_id,))
                user = cursor.fetchone()
                cursor.close()
                
                if not user:
                    return None
                
                return {
                    "user_id": user_id,
                    "username": username,
                    "name": user['name'],
                    "email": user.get('email'),
                    "roles": roles
                }
        except PyJWTError:
            return None
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            True if successful
            
        Raises:
            HTTPException: If old password is incorrect
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get current password hash
            cursor.execute("SELECT password_hash FROM user_auth WHERE user_id = %s", (user_id,))
            auth_record = cursor.fetchone()
            
            if not auth_record:
                cursor.close()
                raise HTTPException(status_code=404, detail="User not found")
            
            # Verify old password
            if not self._verify_password(old_password, auth_record['password_hash']):
                cursor.close()
                raise HTTPException(status_code=400, detail="Incorrect password")
            
            # Update password
            new_password_hash = self._hash_password(new_password)
            cursor.execute(
                "UPDATE user_auth SET password_hash = %s, updated_at = %s WHERE user_id = %s",
                (new_password_hash, datetime.utcnow(), user_id)
            )
            conn.commit()
            cursor.close()
            
            logger.info(f"Password changed for user: {user_id}")
            return True
    
    def assign_role(self, user_id: str, role: str) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id: User ID
            role: Role name (admin, manager, cashier)
            
        Returns:
            True if successful
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Check if role already assigned
            cursor.execute(
                "SELECT * FROM user_roles WHERE user_id = %s AND role = %s",
                (user_id, role)
            )
            existing = cursor.fetchone()
            
            if existing:
                cursor.close()
                return True
            
            # Assign role
            cursor.execute("""
                INSERT INTO user_roles (user_id, role, created_at)
                VALUES (%s, %s, %s)
            """, (user_id, role, datetime.utcnow()))
            conn.commit()
            cursor.close()
            
            logger.info(f"Role {role} assigned to user: {user_id}")
            return True
    
    def remove_role(self, user_id: str, role: str) -> bool:
        """
        Remove a role from a user.
        
        Args:
            user_id: User ID
            role: Role name
            
        Returns:
            True if successful
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "DELETE FROM user_roles WHERE user_id = %s AND role = %s",
                (user_id, role)
            )
            conn.commit()
            cursor.close()
            
            logger.info(f"Role {role} removed from user: {user_id}")
            return True

