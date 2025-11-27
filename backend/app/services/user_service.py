"""User management service using raw MySQL queries."""
from typing import List, Optional, Dict
from datetime import datetime
from fastapi import HTTPException
import uuid

from app.core.database import get_db
from app.core.logging import logger
from app.core.exceptions import UserNotFoundError


class UserService:
    """Service for user management operations."""
    
    def add_user(self, name: str) -> Dict:
        """Add a new user."""
        user_id = str(uuid.uuid4())
        
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            insert_query = """
                INSERT INTO users (id, name, added_at)
                VALUES (%s, %s, %s)
            """
            values = (user_id, name, datetime.utcnow())
            
            cursor.execute(insert_query, values)
            conn.commit()
            
            # Fetch created user
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            
            logger.info(f"User added: {user_id}")
            return user
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get a user by ID."""
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            return user
    
    def get_all_users(self, page: int = 1, page_size: int = 100) -> List[Dict]:
        """
        Get all users with pagination.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            List of user dictionaries
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            offset = (page - 1) * page_size
            cursor.execute(
                "SELECT * FROM users ORDER BY added_at DESC LIMIT %s OFFSET %s",
                (page_size, offset)
            )
            users = cursor.fetchall()
            cursor.close()
            return users
    
    def update_user(self, user_id: str, name: str) -> Dict:
        """Update a user."""
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                raise UserNotFoundError(f"User with ID {user_id} not found.")
            
            # Update user
            update_query = """
                UPDATE users SET name = %s, modified_at = %s WHERE id = %s
            """
            cursor.execute(update_query, (name, datetime.utcnow(), user_id))
            conn.commit()
            
            # Fetch updated user
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            updated_user = cursor.fetchone()
            cursor.close()
            
            logger.info(f"User updated: {user_id}")
            return updated_user
    
    def delete_user(self, user_id: str) -> Dict:
        """Delete a user."""
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get user before deletion
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                raise UserNotFoundError(f"User with ID {user_id} not found.")
            
            # Delete user
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            cursor.close()
            
            logger.info(f"User deleted: {user_id}")
            return user
