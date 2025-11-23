"""Barcode scanning service using raw MySQL queries."""
import cv2
import time
from pyzbar.pyzbar import decode
from typing import Dict
from datetime import datetime

from app.core.config import settings
from app.core.logging import logger
from app.services.inventory_service import InventoryService


class BarcodeService:
    """Service for barcode scanning operations."""
    
    def scan_barcode(self) -> Dict:
        """
        Scan a barcode using the camera.
        
        Returns:
            Dictionary containing product information or error
        """
        cap = cv2.VideoCapture(settings.CAMERA_INDEX)
        scanned_barcodes = set()
        start_time = time.time()
        timeout = settings.SCANNER_TIMEOUT
        
        if not cap.isOpened():
            logger.error("Could not open camera")
            return {"error": "Could not open camera"}
        
        product_info = None
        inventory_service = InventoryService()
        
        try:
            while time.time() - start_time < timeout:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to capture image")
                    return {"error": "Failed to capture image"}
                
                detected_barcodes = decode(frame)
                
                for barcode in detected_barcodes:
                    barcode_data = barcode.data.decode("utf-8")
                    if barcode_data not in scanned_barcodes:
                        scanned_barcodes.add(barcode_data)
                        logger.info(f"Barcode scanned: {barcode_data}")
                        
                        # Check if product exists in inventory
                        product = inventory_service.get_product(barcode_data)
                        
                        if product:
                            product_info = {
                                "barcode": barcode_data,
                                "product_name": product["product_name"],
                                "price": product["price"],
                                "quantity": product["quantity"],
                                "details": product["details"],
                                "timestamp": product["timestamp"].isoformat() if isinstance(product["timestamp"], datetime) else product["timestamp"]
                            }
                        else:
                            # Add product to inventory if not found
                            logger.info(f"Product not found, adding to inventory: {barcode_data}")
                            inventory_service.add_product(
                                barcode_data,
                                {
                                    'product_name': 'Unknown Product',
                                    'price': 0.0,
                                    'quantity': 1,
                                    'details': 'to fill'
                                }
                            )
                            product_info = {
                                "barcode": barcode_data,
                                "product_name": "Unknown Product",
                                "price": 0.0,
                                "quantity": 1,
                                "details": "to fill",
                                "timestamp": datetime.now().isoformat()
                            }
                        
                        cap.release()
                        cv2.destroyAllWindows()
                        return product_info
                
                cv2.imshow("Barcode Scanner", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            if not product_info:
                logger.warning("No barcode detected within timeout period")
                return {"error": "No barcode detected"}
            
            return product_info
            
        except Exception as e:
            logger.error(f"Error during barcode scanning: {e}")
            return {"error": f"Error scanning barcode: {str(e)}"}
        finally:
            cap.release()
            cv2.destroyAllWindows()
