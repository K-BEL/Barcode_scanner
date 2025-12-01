"""Bill generation service using raw MySQL queries."""
from typing import Optional, Dict
from datetime import datetime
from pathlib import Path
from fastapi import HTTPException

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import logger


class BillService:
    """Service for bill generation operations."""
    
    def generate_bill(self, cashier_name: Optional[str] = None) -> Dict:
        """
        Generate a bill from cart items.
        
        Args:
            cashier_name: Optional cashier name
            
        Returns:
            Dictionary containing bill information
            
        Raises:
            HTTPException: If cart is empty
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM cart ORDER BY timestamp ASC")
            cart_items = cursor.fetchall()
            cursor.close()
        
        if not cart_items:
            raise HTTPException(status_code=404, detail="Cart is empty.")
        
        total_price = 0.0
        bill_lines = []
        
        bill_lines.append("BILL TICKET")
        bill_lines.append("-------------------------")
        bill_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if cashier_name:
            bill_lines.append(f"Cashier: {cashier_name}")
        bill_lines.append("-------------------------")
        
        for item in cart_items:
            item_total = round(item['price'] * item['quantity'], 2)
            bill_lines.append(f"Product: {item['product_name']}")
            bill_lines.append(f"Quantity: {item['quantity']}")
            bill_lines.append(f"Price per Unit: {item['price']} USD")
            bill_lines.append(f"Total Price: {item_total} USD")
            bill_lines.append("-------------------------")
            total_price += item_total
        
        total_price = round(total_price, 2)
        bill_lines.append(f"Total: {total_price} USD")
        bill_lines.append("-------------------------")
        
        bill_text = "\n".join(bill_lines)
        
        # Save bill to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        bill_file_path = settings.bills_path / f"bill_ticket_{timestamp}.txt"
        
        try:
            with open(bill_file_path, 'w') as file:
                file.write(bill_text)
            logger.info(f"Bill generated: {bill_file_path}")
        except Exception as e:
            logger.error(f"Error saving bill file: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error saving bill file: {str(e)}"
            )
        
        # Save bill to database and clear the cart in one transaction
        cleared_items = 0
        with get_db() as conn:
            cursor = conn.cursor()
            try:
                insert_query = """
                    INSERT INTO bills (bill_text, cashier_name, total_amount, file_path, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """
                values = (
                    bill_text,
                    cashier_name,
                    total_price,
                    str(bill_file_path),
                    datetime.utcnow()
                )
                cursor.execute(insert_query, values)
                
                cursor.execute("DELETE FROM cart")
                cleared_items = cursor.rowcount
                
                conn.commit()
            finally:
                cursor.close()
        
        logger.info(f"Bill stored in database and cart cleared ({cleared_items} item(s))")
        
        return {
            "message": "Bill ticket generated successfully",
            "cashier": cashier_name if cashier_name else "No cashier name provided",
            "file_path": str(bill_file_path),
            "total_amount": total_price
        }
