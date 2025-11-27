"""Bill generation service using raw MySQL queries."""
from typing import Optional, Dict
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
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM cart ORDER BY timestamp ASC")
            cart_items = cursor.fetchall()
            cursor.close()
        
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
        
        # Save bill to database
        with get_db() as conn:
            cursor = conn.cursor()
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
            conn.commit()
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
