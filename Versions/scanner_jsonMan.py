import cv2, json
from pyzbar.pyzbar import decode
from fastapi import FastAPI
from pydantic import BaseModel
import time
import os

app = FastAPI()

# Define the file paths for input and output JSON files
input_json_path = r"C:\Users\LENOVO\Desktop\Barcode_Scanner\inputs.json"
output_json_path = r"C:\Users\LENOVO\Desktop\Barcode_Scanner\outputs.json"

# Data model for response
class ProductInfo(BaseModel):
    barcode: str
    product_name: str
    price: float

def load_products(file_path):
    # Create file if it doesn't exist or if it's empty
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, "w") as f:
            json.dump({}, f)  # Initialize as an empty JSON object
    
    # Load JSON content and ensure it's a dictionary
    with open(file_path, "r") as f:
        data = json.load(f)
        if not isinstance(data, dict):  # Check if the loaded data is a dictionary
            data = {}
            save_products(data, file_path)  # Re-save as empty dict if data is invalid
        return data


# Save products to a JSON file
def save_products(products, file_path):
    with open(file_path, "w") as f:
        json.dump(products, f, indent=4)

# Add unknown barcode to input JSON file
def add_unknown_product(barcode_data):
    products = load_products(input_json_path)
    if barcode_data not in products:
        # Default details for unknown products, can be customized
        products[barcode_data] = {"name": "Unknown Product", "price": 0.0}
        save_products(products, input_json_path)

# Scan barcode and update JSON files
@app.get("/scan_barcode", response_model=ProductInfo)
def scan_barcode():
    # Load existing products from input JSON
    products = load_products(input_json_path)
    cap = cv2.VideoCapture(0)
    scanned_barcodes = set()
    start_time = time.time()
    timeout = 30  # Timeout for scanning in seconds

    if not cap.isOpened():
        return {"error": "Could not open camera"}

    product_info = None
    output_data = load_products(output_json_path)  # Load current output data

    while time.time() - start_time < timeout:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            return {"error": "Failed to capture image"}

        # Decode the barcode from the frame
        detectedBarcodes = decode(frame)

        for barcode in detectedBarcodes:
            barcode_data = barcode.data.decode("utf-8")
            if barcode_data not in scanned_barcodes:
                scanned_barcodes.add(barcode_data)

                # Check if barcode is in the input file
                product = products.get(barcode_data)
                
                if product:
                    # If product known, add to output file
                    output_data[barcode_data] = product
                    save_products(output_data, output_json_path)
                    
                    product_info = {
                        "barcode": barcode_data,
                        "product_name": product["name"],
                        "price": product["price"]
                    }
                else:
                    # If product unknown, add it to input file
                    add_unknown_product(barcode_data)
                    product_info = {
                        "barcode": barcode_data,
                        "product_name": "Unknown Product",
                        "price": 0.0
                    }
                
                cap.release()
                cv2.destroyAllWindows()
                return product_info

        # Display the frame for user reference (optional)
        cv2.imshow("Barcode Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return {"error": "No barcode detected"} if not product_info else product_info
