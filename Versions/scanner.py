import cv2, json, uuid, os, time
from pyzbar.pyzbar import decode
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime  # Import datetime
from typing import Dict, Optional

app = FastAPI()

# Define the file paths for input and output JSON files
input_json_path = r"C:\Users\LENOVO\Desktop\Barcode_Scanner\inventory_list.json"
output_json_path = r"C:\Users\LENOVO\Desktop\Barcode_Scanner\outputs.json"
product_details = r'C:\Users\LENOVO\Desktop\Barcode_Scanner\product_details.json'
users_json_path = r"C:\Users\LENOVO\Desktop\Barcode_Scanner\users.json"


# Data model for response with quantity
class ProductInfo(BaseModel):
    barcode: str
    product_name: str
    price: float
    quantity: int  # New field for quantity
    details: str
    timestamp: str  # Add timestamp field

class ProductUpdate(BaseModel):
    product_name: str
    price: float
    quantity: int  # New field for quantity
    details: str
    
# Data model for User
class User(BaseModel):
    name: str

def load_products(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, "w") as f:
            json.dump({}, f)
    
    with open(file_path, "r") as f:
        data = json.load(f)
        if not isinstance(data, dict):
            data = {}
            save_products(data, file_path)
        return data

def save_products(products, file_path):
    with open(file_path, "w") as f:
        json.dump(products, f, indent=4)

def load_all_products(file_path: str) -> dict:
    with open(file_path, "r") as file:
        return json.load(file)

# Add a new product to input JSON
def add_product_to_input(barcode_data):
    products = load_products(input_json_path)
    if barcode_data not in products:
        products[barcode_data] = {
            "product_name": "Unknown Product",
            "price": 0.0,
            "quantity": 1,
            "details": "to fill",
            "timestamp": datetime.now().isoformat()
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
                    product["timestamp"] = datetime.now().isoformat()
                    if barcode_data in output_data:
                        output_data[barcode_data]["quantity"] += 1  # Increment quantity if already in cart
                    else:
                        output_data[barcode_data] = product
                        output_data[barcode_data]["quantity"] = 1  # Initialize quantity for new items

                    save_products(output_data, output_json_path)
                    product_info = {
                        "barcode": barcode_data,
                        "product_name": product["product_name"],
                        "price": product["price"],
                        "quantity": output_data[barcode_data]["quantity"],
                        "details": product["details"],
                        "timestamp": product["timestamp"]
                    }
                else:
                    add_product_to_input(barcode_data)
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
        "product_name": product.product_name,
        "price": product.price,
        "quantity": product.quantity,
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

    products[barcode]["product_name"] = product.product_name
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
        "product_name": product.product_name,
        "price": product.price,
        "quantity": product.quantity,
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

    products[barcode]["product_name"] = product.product_name
    products[barcode]["price"] = product.price
    products[barcode]["quantity"] = product.quantity
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


# Function to generate a bill ticket including quantity
def generate_bill(data: Dict, cashier_name: Optional[str] = None):
    total_price = 0
    bill = "BILL TICKET\n"
    bill += "-------------------------\n"
    bill += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    if cashier_name:
        bill += f"Cashier: {cashier_name}\n"
    bill += "-------------------------\n"
    
    # Loop through items in JSON
    for item_id, item in data.items():
        item_total = round(item['price'] * item['quantity'], 2)
        bill += f"Product: {item['product_name']}\n"
        bill += f"Quantity: {item['quantity']}\n"
        bill += f"Price per Unit: {item['price']} USD\n"
        bill += f"Total Price: {item_total} USD\n"
        bill += "-------------------------\n"
        total_price += item_total
    
   # Add total to the bill
    total_price = round(total_price, 2)  # Round total price
    bill += f"Total: {total_price} USD\n"
    bill += "-------------------------\n"
    return bill

# Endpoint to generate and save the bill ticket as a text file with timestamped filename
@app.get("/generate-bill")
def generate_bill_endpoint(cashier_name: Optional[str] = Query(None)):
    with open(output_json_path, 'r') as file:
        data = json.load(file)
    
    bill_ticket = generate_bill(data, cashier_name)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    bill_file_path = rf'C:\Users\LENOVO\Desktop\Barcode_Scanner\Bills\bill_ticket_{timestamp}.txt'
    
    with open(bill_file_path, 'w') as file:
        file.write(bill_ticket)
    
    print(bill_ticket)
    return {
        "message": "Bill ticket generated successfully",
        "cashier": cashier_name if cashier_name else "No cashier name provided",
        "file_path": bill_file_path
    }

# Load users from JSON
def load_users():
    if not os.path.exists(users_json_path):
        with open(users_json_path, "w") as f:
            json.dump({}, f)
    
    with open(users_json_path, "r") as f:
        return json.load(f)

# Save users to JSON
def save_users(users):
    with open(users_json_path, "w") as f:
        json.dump(users, f, indent=4)

# Add a new user with a generated ID
@app.post("/add_user")
def add_user(user: User):
    users = load_users()
    user_id = str(uuid.uuid4())  # Generate a unique ID for the user

    users[user_id] = {
        "name": user.name,
        "added_at": datetime.now().isoformat()
    }
    save_users(users)
    return {"message": "User added successfully", "user": users[user_id], "user_id": user_id}

# Modify an existing user
@app.put("/modify_user/{user_id}")
def modify_user(user_id: str, name: str):
    users = load_users()
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found.")
    
    users[user_id]["name"] = name
    users[user_id]["modified_at"] = datetime.now().isoformat()
    save_users(users)
    return {"message": "User modified successfully", "user": users[user_id]}

# Delete a user
@app.delete("/delete_user/{user_id}")
def delete_user(user_id: str):
    users = load_users()
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found.")
    
    deleted_user = users.pop(user_id)
    save_users(users)
    return {"message": "User deleted successfully", "deleted_user": deleted_user}

# Get all users from the JSON file
@app.get("/get_users")
def get_users():
    users = load_users()
    if not users:
        raise HTTPException(status_code=404, detail="No users found.")
    return {"users": users}
