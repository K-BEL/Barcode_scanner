"""Cart management service using raw MySQL queries."""
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import HTTPException

from app.core.database import get_db
from app.core.logging import logger
from app.core.exceptions import CartItemNotFoundError, CartItemAlreadyExistsError, ProductNotFoundError


class CartService:
    """Service for cart management operations."""
    
    def add_product(self, barcode: str, product_data: Dict) -> Dict:
        """
        Add a product to cart.
        
        If the product already exists in the cart, its quantity (and any
        updated details) are merged instead of raising an error. This mimics
        the behaviour of a physical caisse where scanning the same item again
        increments its quantity.
        
        Args:
            barcode: Product barcode
            product_data: Product data dictionary
            
        Returns:
            Created or updated cart item dictionary
            
        Raises:
            HTTPException: If product not found in inventory
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Use SELECT FOR UPDATE to lock the row and prevent race conditions
            cursor.execute("SELECT * FROM cart WHERE barcode = %s FOR UPDATE", (barcode,))
            cart_item = cursor.fetchone()
            
            if cart_item:
                quantity_to_add = product_data.get('quantity')
                if quantity_to_add is None:
                    quantity_to_add = 1
                
                new_quantity = cart_item['quantity'] + quantity_to_add
                updated_name = product_data.get('product_name') or cart_item['product_name']
                updated_price = (
                    product_data['price']
                    if product_data.get('price') is not None
                    else cart_item['price']
                )
                updated_details = (
                    product_data.get('details')
                    if product_data.get('details')
                    else cart_item.get('details') or 'to fill'
                )
                
                update_query = """
                    UPDATE cart
                    SET product_name = %s,
                        price = %s,
                        quantity = %s,
                        details = %s,
                        timestamp = %s
                    WHERE barcode = %s
                """
                cursor.execute(
                    update_query,
                    (
                        updated_name,
                        updated_price,
                        new_quantity,
                        updated_details,
                        datetime.utcnow(),
                        barcode
                    )
                )
                conn.commit()
                
                cursor.execute("SELECT * FROM cart WHERE barcode = %s", (barcode,))
                updated_cart_item = cursor.fetchone()
                cursor.close()
                
                logger.info(f"Cart quantity updated: {barcode} -> {new_quantity}")
                return updated_cart_item
            
            # Verify product exists in inventory for new cart entries
            cursor.execute("SELECT * FROM products WHERE barcode = %s", (barcode,))
            product = cursor.fetchone()
            if not product:
                cursor.close()
                raise ProductNotFoundError(f"Product with barcode {barcode} not found in inventory.")
            
            insert_query = """
                INSERT INTO cart (barcode, product_name, price, quantity, details, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            details = product_data.get('details') or product.get('details') or 'to fill'
            quantity = product_data.get('quantity')
            if quantity is None:
                quantity = 1
            
            values = (
                barcode,
                product_data.get('product_name', product['product_name']),
                product_data.get('price', product['price']),
                quantity,
                details,
                datetime.utcnow()
            )
            
            cursor.execute(insert_query, values)
            conn.commit()
            
            # Fetch created cart item
            cursor.execute("SELECT * FROM cart WHERE barcode = %s", (barcode,))
            new_cart_item = cursor.fetchone()
            cursor.close()
            
            logger.info(f"Product added to cart: {barcode}")
            return new_cart_item
    
    def get_cart_item(self, barcode: str) -> Optional[Dict]:
        """Get a cart item by barcode."""
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM cart WHERE barcode = %s", (barcode,))
            item = cursor.fetchone()
            cursor.close()
            return item
    
    def get_all_cart_items(self) -> List[Dict]:
        """Get all items in cart."""
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM cart ORDER BY timestamp DESC")
            items = cursor.fetchall()
            cursor.close()
            return items
    
    def update_cart_item(self, barcode: str, product_data: Dict) -> Dict:
        """Update a cart item."""
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Check if cart item exists
            cursor.execute("SELECT * FROM cart WHERE barcode = %s", (barcode,))
            cart_item = cursor.fetchone()
            
            if not cart_item:
                cursor.close()
                raise CartItemNotFoundError(f"Product with barcode {barcode} not found in cart.")
            
            # Build update query
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
            
            update_query = f"UPDATE cart SET {', '.join(update_fields)} WHERE barcode = %s"
            cursor.execute(update_query, values)
            conn.commit()
            
            # Fetch updated item
            cursor.execute("SELECT * FROM cart WHERE barcode = %s", (barcode,))
            updated_item = cursor.fetchone()
            cursor.close()
            
            logger.info(f"Cart item updated: {barcode}")
            return updated_item
    
    def delete_cart_item(self, barcode: str) -> Dict:
        """Delete a cart item."""
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get item before deletion
            cursor.execute("SELECT * FROM cart WHERE barcode = %s", (barcode,))
            cart_item = cursor.fetchone()
            
            if not cart_item:
                cursor.close()
                raise CartItemNotFoundError(f"Product with barcode {barcode} not found in cart.")
            
            # Delete item
            cursor.execute("DELETE FROM cart WHERE barcode = %s", (barcode,))
            conn.commit()
            cursor.close()
            
            logger.info(f"Cart item deleted: {barcode}")
            return cart_item
    
    def clear_cart(self) -> int:
        """Clear all items from cart."""
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get count before deletion
            cursor.execute("SELECT COUNT(*) as count FROM cart")
            count = cursor.fetchone()[0]
            
            # Delete all items
            cursor.execute("DELETE FROM cart")
            conn.commit()
            cursor.close()
            
            logger.info(f"Cart cleared: {count} items removed")
            return count
