import cv2
import json
import uuid
from pyzbar.pyzbar import decode
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import time
from datetime import datetime  # Import datetime

app = FastAPI()

# Define the file paths for input and output JSON files
input_json_path = r"C:\Users\LENOVO\Desktop\Barcode_Scanner\inventory_list.json"
output_json_path = r"C:\Users\LENOVO\Desktop\Barcode_Scanner\outputs.json"
product_details = r'C:\Users\LENOVO\Desktop\Barcode_Scanner\product_details.json'

# Data model for response
class ProductInfo(BaseModel):
    barcode: str
    product_name: str
    price: float
    details : str
    timestamp: str  # Add timestamp field

class ProductUpdate(BaseModel):
    product_name: str
    price: float
    details : str

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

# Function to load products from JSON file
def load_all_products(file_path: str) -> dict:
    with open(file_path, "r") as file:
        return json.load(file)

# Add a new product to input JSON
def add_product_to_input(barcode_data):
    products = load_products(input_json_path)
    if barcode_data not in products:
        products[barcode_data] = {
            "name": "Unknown Product",
            "price": 0.0,
            "details": "to fill",
            "timestamp": datetime.now().isoformat()  # Add current timestamp
        }
        save_products(products, input_json_path)

# Barcode scanning and updating JSON files
@app.get("/scan_barcode", response_model=ProductInfo)
def scan_barcode():
    products = load_products(input_json_path)
    cap = cv2.VideoCapture(0)
    scanned_barcodes = set()
    start_time = time.time()
    timeout = 30  # Timeout for scanning

    if not cap.isOpened():
        return {"error": "Could not open camera"}

    product_info = None
    output_data = load_products(output_json_path)

    while time.time() - start_time < timeout:
        ret, frame = cap.read()
        if not ret:
            return {"error": "Failed to capture image"}

        detected_barcodes = decode(frame)

        for barcode in detected_barcodes:
            barcode_data = barcode.data.decode("utf-8")
            if barcode_data not in scanned_barcodes:
                scanned_barcodes.add(barcode_data)

                # Retrieve product info from input JSON
                product = products.get(barcode_data)

                if product:
                    product["timestamp"] = datetime.now().isoformat()  # Update timestamp
                    output_data[barcode_data] = product
                    save_products(output_data, output_json_path)
                    product_info = {
                        "barcode": barcode_data,
                        "product_name": product["name"],
                        "price": product["price"],
                        "details": product["details"],
                        "timestamp": product["timestamp"]  # Include timestamp in the response
                    }
                else:
                    add_product_to_input(barcode_data)
                    product_info = {
                        "barcode": barcode_data,
                        "product_name": "Unknown Product",
                        "price": 0.0,
                        "details": "to fill",
                        "timestamp": datetime.now().isoformat()  # Add timestamp for unknown product
                    }
                
                cap.release()
                cv2.destroyAllWindows()
                return product_info

        cv2.imshow("Barcode Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return {"error": "No barcode detected"} if not product_info else product_info

# API to add a new product to input JSON
@app.post("/add_product_inventory")
def add_product_inventory(barcode: str, product: ProductUpdate):
    products = load_products(input_json_path)
    if barcode in products:
        raise HTTPException(status_code=400, detail="Product with this barcode already exists.")
    
    products[barcode] = {
        "name": product.product_name,
        "price": product.price,
        "details": product.details,
        "timestamp": datetime.now().isoformat()  # Add current timestamp
    }
    save_products(products, input_json_path)
    return {"message": "Product added successfully to inventory", "product": products[barcode]}

# API to modify an existing product in input JSON
@app.put("/modify_product_inventory/{barcode}")
def modify_product_inventory(barcode: str, product: ProductUpdate):
    products = load_products(input_json_path)
    if barcode not in products:
        raise HTTPException(status_code=404, detail="Product not found.")

    products[barcode]["name"] = product.product_name
    products[barcode]["price"] = product.price
    products[barcode]["details"] = product.details
    products[barcode]["timestamp"] = datetime.now().isoformat()  # Update timestamp
    save_products(products, input_json_path)
    return {"message": "Product modified successfully in inventory", "product": products[barcode]}

# API to delete a product from input JSON
@app.delete("/delete_product_inventory/{barcode}")
def delete_product_inventory(barcode: str):
    products = load_products(input_json_path)
    if barcode not in products:
        raise HTTPException(status_code=404, detail="Product not found.")

    deleted_product = products.pop(barcode)
    save_products(products, input_json_path)
    return {"message": "Product deleted successfully in inventory", "deleted_product": deleted_product}


# API to add a new product to output JSON
@app.post("/add_product_cart")
def add_product_cart(barcode: str, product: ProductUpdate):
    products = load_products(output_json_path)
    if barcode in products:
        raise HTTPException(status_code=400, detail="Product with this barcode already exists.")
    
    products[barcode] = {
        "name": product.product_name,
        "price": product.price,
        "details": product.details,
        "timestamp": datetime.now().isoformat()  # Add current timestamp
    }
    save_products(products, output_json_path)
    return {"message": "Product added successfully to cart", "product": products[barcode]}


# API to modify an existing product in output JSON
@app.put("/modify_product_cart/{barcode}")
def modify_product_cart(barcode: str, product: ProductUpdate):
    products = load_products(output_json_path)
    if barcode not in products:
        raise HTTPException(status_code=404, detail="Product not found.")

    products[barcode]["name"] = product.product_name
    products[barcode]["price"] = product.price
    products[barcode]["details"] = product.details
    products[barcode]["timestamp"] = datetime.now().isoformat()  # Update timestamp
    save_products(products, output_json_path)
    return {"message": "Product modified successfully in cart", "product": products[barcode]}

# API to delete a product from ouput JSON
@app.delete("/delete_product_cart/{barcode}")
def delete_product_cart(barcode: str):
    products = load_products(output_json_path)
    if barcode not in products:
        raise HTTPException(status_code=404, detail="Product not found.")

    deleted_product = products.pop(barcode)
    save_products(products, output_json_path)
    return {"message": "Product deleted successfully in cart", "deleted_product": deleted_product}

# API to clear all products in the output JSON file
@app.delete("/clear_cart")
def clear_cart():
    products = {}  # Empty dictionary
    save_products(products, output_json_path)
    print ("message"+ ':'+"All products cleared from cart")
    return {"New Purchase"}


# API to get products details from inventory list
@app.put("/get_product_details/{barcode}")
def get_product_details(barcode: str):
    products = {}  # Empty dictionary
    save_products(products, product_details)
    products = load_products(input_json_path)
    if barcode not in products:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    # Get the selected product details
    selected_product = products[barcode]
    # Save the selected product details to the JSON file
    save_products(selected_product, product_details)
    return {"product": selected_product}


# API to get all products from inventory list
@app.put("/get_list_inventory")
def get_list_inventory():
    products = load_all_products(input_json_path)
    # Return all products as a JSON response
    return {"products": products}


# API to get all products from cart
@app.get("/get_list_cart")
def get_list_cart():
    products = load_all_products(output_json_path)
    if not products:
        raise HTTPException(status_code=404, detail="Cart is empty.")
    # Return all products as a JSON response
    return {"products": products}