"""Bill generation service using raw MySQL queries."""
from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path
from fastapi import HTTPException

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import logger
from app.core.exceptions import EmptyCartError

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("reportlab not available. PDF generation will be disabled.")


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
        # Perform all operations in a single transaction for atomicity
        cleared_items = 0
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                # Lock cart rows to prevent concurrent modifications
                cursor.execute("SELECT * FROM cart ORDER BY timestamp ASC FOR UPDATE")
                cart_items = cursor.fetchall()
                
                if not cart_items:
                    raise EmptyCartError("Cart is empty. Cannot generate bill.")
                
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
                
                # Save bill to file (outside transaction, but if it fails, transaction will rollback)
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
                
                # Save bill to database and clear the cart in the same transaction
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
                bill_id = cursor.lastrowid
                
                # Decrement inventory quantities for all cart items
                for item in cart_items:
                    # Check current inventory quantity
                    cursor.execute("SELECT quantity FROM products WHERE barcode = %s FOR UPDATE", (item['barcode'],))
                    product = cursor.fetchone()
                    
                    if product:
                        new_quantity = max(0, product['quantity'] - item['quantity'])
                        cursor.execute(
                            "UPDATE products SET quantity = %s WHERE barcode = %s",
                            (new_quantity, item['barcode'])
                        )
                        logger.info(f"Inventory updated: {item['barcode']} -> {new_quantity} (decremented {item['quantity']})")
                    else:
                        logger.warning(f"Product {item['barcode']} not found in inventory, skipping inventory update")
                
                cursor.execute("DELETE FROM cart")
                cleared_items = cursor.rowcount
                
                conn.commit()
                logger.info(f"Bill stored in database (ID: {bill_id}), inventory updated, and cart cleared ({cleared_items} item(s))")
            except (EmptyCartError, HTTPException):
                # Re-raise application exceptions
                conn.rollback()
                raise
            except Exception as e:
                # Rollback on any other error
                conn.rollback()
                logger.error(f"Error generating bill: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error generating bill: {str(e)}"
                )
            finally:
                cursor.close()
        
        # Generate PDF if available
        pdf_path = None
        if PDF_AVAILABLE:
            try:
                pdf_path = self._generate_pdf_bill(
                    cart_items,
                    total_price,
                    cashier_name,
                    timestamp
                )
                logger.info(f"PDF bill generated: {pdf_path}")
            except Exception as e:
                logger.error(f"Error generating PDF bill: {e}")
        
        return {
            "message": "Bill ticket generated successfully",
            "bill_id": bill_id,
            "cashier": cashier_name if cashier_name else "No cashier name provided",
            "file_path": str(bill_file_path),
            "pdf_path": str(pdf_path) if pdf_path else None,
            "total_amount": total_price
        }
    
    def _generate_pdf_bill(
        self,
        cart_items: list,
        total_price: float,
        cashier_name: Optional[str],
        timestamp: str
    ) -> Path:
        """
        Generate a PDF version of the bill.
        
        Args:
            cart_items: List of cart items
            total_price: Total bill amount
            cashier_name: Optional cashier name
            timestamp: Timestamp string for filename
            
        Returns:
            Path to generated PDF file
        """
        if not PDF_AVAILABLE:
            raise RuntimeError("PDF generation not available. Install reportlab.")
        
        pdf_file_path = settings.bills_path / f"bill_ticket_{timestamp}.pdf"
        c = canvas.Canvas(str(pdf_file_path), pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 20)
        c.drawString(2 * inch, height - 1 * inch, "BILL TICKET")
        
        # Date and cashier
        c.setFont("Helvetica", 12)
        y_position = height - 1.5 * inch
        c.drawString(1 * inch, y_position, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        y_position -= 0.25 * inch
        
        if cashier_name:
            c.drawString(1 * inch, y_position, f"Cashier: {cashier_name}")
            y_position -= 0.25 * inch
        
        # Line separator
        y_position -= 0.1 * inch
        c.line(1 * inch, y_position, width - 1 * inch, y_position)
        y_position -= 0.3 * inch
        
        # Items
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, y_position, "Items:")
        y_position -= 0.3 * inch
        c.setFont("Helvetica", 10)
        
        for item in cart_items:
            if y_position < 2 * inch:  # Start new page if needed
                c.showPage()
                y_position = height - 1 * inch
                c.setFont("Helvetica", 10)
            
            item_total = round(item['price'] * item['quantity'], 2)
            c.drawString(1 * inch, y_position, f"{item['product_name']}")
            y_position -= 0.2 * inch
            c.drawString(1.2 * inch, y_position, f"Qty: {item['quantity']} x ${item['price']:.2f} = ${item_total:.2f}")
            y_position -= 0.3 * inch
        
        # Total
        y_position -= 0.2 * inch
        c.line(1 * inch, y_position, width - 1 * inch, y_position)
        y_position -= 0.3 * inch
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1 * inch, y_position, f"Total: ${total_price:.2f}")
        
        c.save()
        return pdf_file_path
    
    def get_bills(
        self,
        page: int = 1,
        page_size: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        cashier_name: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> List[Dict]:
        """
        Get all bills with optional filtering and pagination.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            start_date: Start date filter (YYYY-MM-DD format)
            end_date: End date filter (YYYY-MM-DD format)
            cashier_name: Filter by cashier name
            min_amount: Minimum total amount filter
            max_amount: Maximum total amount filter
            
        Returns:
            List of bill dictionaries
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Build WHERE clause
            where_clauses = []
            params = []
            
            if start_date:
                where_clauses.append("DATE(created_at) >= %s")
                params.append(start_date)
            
            if end_date:
                where_clauses.append("DATE(created_at) <= %s")
                params.append(end_date)
            
            if cashier_name:
                where_clauses.append("cashier_name = %s")
                params.append(cashier_name)
            
            if min_amount is not None:
                where_clauses.append("total_amount >= %s")
                params.append(min_amount)
            
            if max_amount is not None:
                where_clauses.append("total_amount <= %s")
                params.append(max_amount)
            
            # Build query
            query_parts = ["SELECT id as bill_id, cashier_name, total_amount, created_at, file_path FROM bills"]
            
            if where_clauses:
                query_parts.append("WHERE")
                query_parts.append(" AND ".join(where_clauses))
            
            query_parts.append("ORDER BY created_at DESC")
            
            # Add pagination
            offset = (page - 1) * page_size
            query_parts.append("LIMIT %s OFFSET %s")
            params.extend([page_size, offset])
            
            query = " ".join(query_parts)
            cursor.execute(query, params)
            bills = cursor.fetchall()
            cursor.close()
            
            # Convert datetime to string
            for bill in bills:
                if bill['created_at'] and isinstance(bill['created_at'], datetime):
                    bill['created_at'] = bill['created_at'].isoformat()
            
            return bills
    
    def get_bill(self, bill_id: int) -> Optional[Dict]:
        """
        Get a specific bill by ID.
        
        Args:
            bill_id: Bill ID
            
        Returns:
            Bill dictionary or None if not found
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM bills WHERE id = %s",
                (bill_id,)
            )
            bill = cursor.fetchone()
            cursor.close()
            
            if bill:
                # Convert datetime to string
                if bill['created_at'] and isinstance(bill['created_at'], datetime):
                    bill['created_at'] = bill['created_at'].isoformat()
                bill['bill_id'] = bill.pop('id')
            
            return bill
