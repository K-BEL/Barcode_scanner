"""Inventory management service using raw MySQL queries."""
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import HTTPException
import mysql.connector

from app.core.database import get_db
from app.core.logging import logger
from app.core.exceptions import ProductNotFoundError, ProductAlreadyExistsError


class InventoryService:
    """Service for inventory management operations."""
    
    def add_product(self, barcode: str, product_data: Dict) -> Dict:
        """
        Add a new product to inventory.
        
        Args:
            barcode: Product barcode
            product_data: Product data dictionary
            
        Returns:
            Created product dictionary
            
        Raises:
            HTTPException: If product already exists
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Check if product exists
            cursor.execute("SELECT * FROM products WHERE barcode = %s", (barcode,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.close()
                raise ProductAlreadyExistsError(f"Product with barcode {barcode} already exists.")
            
            # Insert new product
            insert_query = """
                INSERT INTO products (barcode, product_name, price, quantity, details, reorder_point, category_id, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            details = product_data.get('details', 'to fill')
            if not details:
                details = 'to fill'
            
            values = (
                barcode,
                product_data.get('product_name', 'Unknown Product'),
                product_data.get('price', 0.0),
                product_data.get('quantity', 1),
                details,
                product_data.get('reorder_point', 0),
                product_data.get('category_id'),
                datetime.utcnow()
            )
            
            cursor.execute(insert_query, values)
            conn.commit()
            
            # Fetch created product
            cursor.execute("SELECT * FROM products WHERE barcode = %s", (barcode,))
            product = cursor.fetchone()
            cursor.close()
            
            logger.info(f"Product added to inventory: {barcode}")
            return product
    
    def get_product(self, barcode: str) -> Optional[Dict]:
        """
        Get a product by barcode.
        
        Args:
            barcode: Product barcode
            
        Returns:
            Product dictionary or None
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products WHERE barcode = %s", (barcode,))
            product = cursor.fetchone()
            cursor.close()
            return product
    
    def get_all_products(
        self,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        category_id: Optional[int] = None,
        low_stock_only: Optional[bool] = None,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict]:
        """
        Get all products in inventory with optional search and filtering.
        
        Args:
            search: Search term for product name
            min_price: Minimum price filter
            max_price: Maximum price filter
            category_id: Filter by category ID
            low_stock_only: If True, only return products below reorder point
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            List of product dictionaries
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Build WHERE clause using parameterized queries
            # All clause strings are hardcoded to prevent SQL injection
            where_clauses = []
            params = []
            
            if search:
                where_clauses.append("product_name LIKE %s")
                params.append(f"%{search}%")
            
            if min_price is not None:
                where_clauses.append("price >= %s")
                params.append(min_price)
            
            if max_price is not None:
                where_clauses.append("price <= %s")
                params.append(max_price)
            
            if category_id is not None:
                where_clauses.append("category_id = %s")
                params.append(category_id)
            
            if low_stock_only:
                where_clauses.append("quantity <= reorder_point AND reorder_point > 0")
            
            # Build query with parameterized WHERE clause
            # WHERE clause parts are hardcoded strings, only values are parameterized
            query_parts = ["SELECT * FROM products"]
            
            if where_clauses:
                query_parts.append("WHERE")
                query_parts.append(" AND ".join(where_clauses))
            
            query_parts.append("ORDER BY timestamp DESC")
            
            # Validate pagination parameters are integers (already validated in API layer)
            offset = (page - 1) * page_size
            query_parts.append("LIMIT %s OFFSET %s")
            params.extend([page_size, offset])
            
            query = " ".join(query_parts)
            cursor.execute(query, params)
            products = cursor.fetchall()
            cursor.close()
            
            # Add is_low_stock flag
            for product in products:
                reorder_point = product.get('reorder_point', 0)
                quantity = product.get('quantity', 0)
                product['is_low_stock'] = reorder_point > 0 and quantity <= reorder_point
            
            return products
    
    def update_product(self, barcode: str, product_data: Dict) -> Dict:
        """
        Update an existing product.
        
        Args:
            barcode: Product barcode
            product_data: Updated product data
            
        Returns:
            Updated product dictionary
            
        Raises:
            HTTPException: If product not found
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Check if product exists
            cursor.execute("SELECT * FROM products WHERE barcode = %s", (barcode,))
            product = cursor.fetchone()
            
            if not product:
                cursor.close()
                raise ProductNotFoundError(f"Product with barcode {barcode} not found.")
            
            # Track quantity change for stock history
            old_quantity = product['quantity']
            new_quantity = product_data.get('quantity', old_quantity)
            quantity_changed = 'quantity' in product_data and old_quantity != new_quantity
            
            # Build update query dynamically
            update_fields = []
            values = []
            
            if 'product_name' in product_data:
                update_fields.append("product_name = %s")
                values.append(product_data['product_name'])
            if 'price' in product_data:
                update_fields.append("price = %s")
                values.append(product_data['price'])
            if 'quantity' in product_data:
                update_fields.append("quantity = %s")
                values.append(product_data['quantity'])
            if 'details' in product_data:
                update_fields.append("details = %s")
                values.append(product_data['details'])
            if 'reorder_point' in product_data:
                update_fields.append("reorder_point = %s")
                values.append(product_data['reorder_point'])
            if 'category_id' in product_data:
                update_fields.append("category_id = %s")
                values.append(product_data['category_id'])
            
            update_fields.append("timestamp = %s")
            values.append(datetime.utcnow())
            values.append(barcode)
            
            update_query = f"UPDATE products SET {', '.join(update_fields)} WHERE barcode = %s"
            cursor.execute(update_query, values)
            
            # Record stock history if quantity changed
            if quantity_changed:
                self._record_stock_history(
                    cursor, barcode, new_quantity - old_quantity, 
                    old_quantity, new_quantity, 
                    product_data.get('stock_reason', 'Manual update')
                )
            
            conn.commit()
            
            # Fetch updated product
            cursor.execute("SELECT * FROM products WHERE barcode = %s", (barcode,))
            updated_product = cursor.fetchone()
            cursor.close()
            
            logger.info(f"Product updated: {barcode}")
            return updated_product
    
    def delete_product(self, barcode: str) -> Dict:
        """
        Delete a product from inventory.
        
        Args:
            barcode: Product barcode
            
        Returns:
            Deleted product dictionary
            
        Raises:
            HTTPException: If product not found
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get product before deletion
            cursor.execute("SELECT * FROM products WHERE barcode = %s", (barcode,))
            product = cursor.fetchone()
            
            if not product:
                cursor.close()
                raise ProductNotFoundError(f"Product with barcode {barcode} not found.")
            
            # Delete product
            cursor.execute("DELETE FROM products WHERE barcode = %s", (barcode,))
            conn.commit()
            cursor.close()
            
            logger.info(f"Product deleted: {barcode}")
            return product
    
    def _record_stock_history(
        self, cursor, barcode: str, quantity_change: int, 
        previous_quantity: int, new_quantity: int, reason: str, user_id: Optional[str] = None
    ):
        """
        Record stock history entry.
        
        Args:
            cursor: Database cursor
            barcode: Product barcode
            quantity_change: Change in quantity (can be negative)
            previous_quantity: Quantity before change
            new_quantity: Quantity after change
            reason: Reason for change
            user_id: Optional user ID who made the change
        """
        try:
            insert_query = """
                INSERT INTO stock_history 
                (barcode, quantity_change, previous_quantity, new_quantity, reason, user_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                barcode, quantity_change, previous_quantity, new_quantity, reason, user_id, datetime.utcnow()
            ))
        except Exception as e:
            logger.warning(f"Could not record stock history: {e}")
    
    def get_low_stock_products(self) -> List[Dict]:
        """
        Get all products with quantity below reorder point.
        
        Returns:
            List of products with low stock
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM products 
                WHERE quantity <= reorder_point AND reorder_point > 0
                ORDER BY (quantity - reorder_point) ASC
            """)
            products = cursor.fetchall()
            cursor.close()
            return products
    
    def get_stock_history(self, barcode: str, limit: int = 50) -> List[Dict]:
        """
        Get stock history for a product.
        
        Args:
            barcode: Product barcode
            limit: Maximum number of records to return
            
        Returns:
            List of stock history records
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM stock_history 
                WHERE barcode = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (barcode, limit))
            history = cursor.fetchall()
            cursor.close()
            
            # Convert datetime to string
            for record in history:
                if record['created_at'] and isinstance(record['created_at'], datetime):
                    record['created_at'] = record['created_at'].isoformat()
            
            return history
