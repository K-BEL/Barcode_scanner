"""Category management service using raw MySQL queries."""
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import HTTPException
import mysql.connector

from app.core.database import get_db
from app.core.logging import logger
from app.core.exceptions import ProductNotFoundError


class CategoryService:
    """Service for category management operations."""
    
    def add_category(self, category_data: Dict) -> Dict:
        """
        Add a new category.
        
        Args:
            category_data: Category data dictionary
            
        Returns:
            Created category dictionary
            
        Raises:
            HTTPException: If category already exists
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Check if category exists
            cursor.execute("SELECT * FROM categories WHERE name = %s", (category_data['name'],))
            existing = cursor.fetchone()
            
            if existing:
                cursor.close()
                raise HTTPException(status_code=400, detail=f"Category '{category_data['name']}' already exists.")
            
            # Insert new category
            insert_query = """
                INSERT INTO categories (name, description, created_at)
                VALUES (%s, %s, %s)
            """
            values = (
                category_data['name'],
                category_data.get('description'),
                datetime.utcnow()
            )
            
            cursor.execute(insert_query, values)
            conn.commit()
            
            # Fetch created category
            cursor.execute("SELECT * FROM categories WHERE id = LAST_INSERT_ID()")
            category = cursor.fetchone()
            cursor.close()
            
            logger.info(f"Category added: {category_data['name']}")
            return category
    
    def get_category(self, category_id: int) -> Optional[Dict]:
        """
        Get a category by ID.
        
        Args:
            category_id: Category ID
            
        Returns:
            Category dictionary or None
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
            category = cursor.fetchone()
            cursor.close()
            return category
    
    def get_all_categories(self) -> List[Dict]:
        """
        Get all categories.
        
        Returns:
            List of category dictionaries
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM categories ORDER BY name ASC")
            categories = cursor.fetchall()
            cursor.close()
            return categories
    
    def update_category(self, category_id: int, category_data: Dict) -> Dict:
        """
        Update an existing category.
        
        Args:
            category_id: Category ID
            category_data: Updated category data
            
        Returns:
            Updated category dictionary
            
        Raises:
            HTTPException: If category not found
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Check if category exists
            cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
            category = cursor.fetchone()
            
            if not category:
                cursor.close()
                raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found.")
            
            # Check if name is being changed and if new name already exists
            if 'name' in category_data and category_data['name'] != category['name']:
                cursor.execute("SELECT * FROM categories WHERE name = %s AND id != %s", 
                             (category_data['name'], category_id))
                existing = cursor.fetchone()
                if existing:
                    cursor.close()
                    raise HTTPException(status_code=400, detail=f"Category '{category_data['name']}' already exists.")
            
            # Build update query dynamically
            update_fields = []
            values = []
            
            if 'name' in category_data:
                update_fields.append("name = %s")
                values.append(category_data['name'])
            if 'description' in category_data:
                update_fields.append("description = %s")
                values.append(category_data['description'])
            
            if update_fields:
                values.append(category_id)
                update_query = f"UPDATE categories SET {', '.join(update_fields)} WHERE id = %s"
                cursor.execute(update_query, values)
                conn.commit()
            
            # Fetch updated category
            cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
            updated_category = cursor.fetchone()
            cursor.close()
            
            logger.info(f"Category updated: {category_id}")
            return updated_category
    
    def delete_category(self, category_id: int) -> Dict:
        """
        Delete a category.
        
        Args:
            category_id: Category ID
            
        Returns:
            Deleted category dictionary
            
        Raises:
            HTTPException: If category not found or has products
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Check if category exists
            cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
            category = cursor.fetchone()
            
            if not category:
                cursor.close()
                raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found.")
            
            # Check if category has products
            cursor.execute("SELECT COUNT(*) as count FROM products WHERE category_id = %s", (category_id,))
            result = cursor.fetchone()
            if result['count'] > 0:
                cursor.close()
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cannot delete category. {result['count']} product(s) are using this category."
                )
            
            # Delete category
            cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
            conn.commit()
            cursor.close()
            
            logger.info(f"Category deleted: {category_id}")
            return category

