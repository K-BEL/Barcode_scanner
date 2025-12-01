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
                INSERT INTO products (barcode, product_name, price, quantity, details, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
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
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict]:
        """
        Get all products in inventory with optional search and filtering.
        
        Args:
            search: Search term for product name
            min_price: Minimum price filter
            max_price: Maximum price filter
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
            
            update_fields.append("timestamp = %s")
            values.append(datetime.utcnow())
            values.append(barcode)
            
            update_query = f"UPDATE products SET {', '.join(update_fields)} WHERE barcode = %s"
            cursor.execute(update_query, values)
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
