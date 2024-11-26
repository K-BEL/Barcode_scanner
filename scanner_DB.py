import cv2, json, uuid, os, time
from pyzbar.pyzbar import decode
from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Dict, Optional
from models import SessionLocal, Product, Cart, User, Bill

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

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

# Function to add product to inventory
def add_product_to_inventory(db: Session, barcode: str, product_data: dict):
    existing_product = db.query(Product).filter(Product.barcode == barcode).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this barcode already exists.")
    
    new_product = Product(
        barcode=barcode,
        product_name=product_data['product_name'],
        price=product_data['price'],
        quantity=product_data['quantity'],
        details=product_data['details'],
        timestamp=datetime.utcnow()
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# Barcode scanning and updating inventory
@app.get("/scan_barcode", response_model=ProductInfo)
def scan_barcode(db: Session = Depends(get_db)):
    cap = cv2.VideoCapture(0)
    scanned_barcodes = set()
    start_time = time.time()
    timeout = 30  # Timeout for scanning

    if not cap.isOpened():
        return {"error": "Could not open camera"}

    product_info = None
    while time.time() - start_time < timeout:
        ret, frame = cap.read()
        if not ret:
            return {"error": "Failed to capture image"}

        detected_barcodes = decode(frame)

        for barcode in detected_barcodes:
            barcode_data = barcode.data.decode("utf-8")
            if barcode_data not in scanned_barcodes:
                scanned_barcodes.add(barcode_data)

                # Check if product exists in the database
                product = db.query(Product).filter(Product.barcode == barcode_data).first()

                if product:
                    product_info = {
                        "barcode": barcode_data,
                        "product_name": product.product_name,
                        "price": product.price,
                        "quantity": product.quantity,
                        "details": product.details,
                        "timestamp": product.timestamp.isoformat()
                    }
                else:
                    # Add product to inventory if not found
                    add_product_to_inventory(db, barcode_data, {
                        'product_name': 'Unknown Product',
                        'price': 0.0,
                        'quantity': 1,
                        'details': 'to fill'
                    })
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

# API to add a new product to inventory (Database version)
@app.post("/add_product_inventory")
def add_product_inventory(barcode: str, product: ProductUpdate, db: Session = Depends(get_db)):
    return add_product_to_inventory(db, barcode, product.dict())

# API to modify an existing product in inventory
@app.put("/modify_product_inventory/{barcode}")
def modify_product_inventory(barcode: str, product: ProductUpdate, db: Session = Depends(get_db)):
    existing_product = db.query(Product).filter(Product.barcode == barcode).first()
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    existing_product.product_name = product.product_name
    existing_product.price = product.price
    existing_product.quantity = product.quantity
    existing_product.details = product.details
    existing_product.timestamp = datetime.now()

    db.commit()
    db.refresh(existing_product)
    return {"message": "Product modified successfully", "product": existing_product}

# API to delete a product from inventory
@app.delete("/delete_product_inventory/{barcode}")
def delete_product_inventory(barcode: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.barcode == barcode).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully", "deleted_product": product}

@app.get("/get_inventory")
def get_inventory(db: Session = Depends(get_db)):
    # Query all products in the inventory
    products = db.query(Product).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found in inventory.")
    
    # Prepare the response
    inventory_products = [
        {
            "barcode": product.barcode,
            "product_name": product.product_name,
            "price": product.price,
            "quantity": product.quantity,
            "details": product.details,
            "timestamp": product.timestamp.isoformat()
        }
        for product in products
    ]
    return {"inventory": inventory_products}


# API to add a product to cart
@app.post("/add_product_cart")
def add_product_cart(barcode: str, product: ProductUpdate, db: Session = Depends(get_db)):
    cart_item = db.query(Cart).filter(Cart.barcode == barcode).first()
    if cart_item:
        raise HTTPException(status_code=400, detail="Product already in cart.")
    
    new_cart_item = Cart(
        barcode=barcode,
        product_name=product.product_name,
        price=product.price,
        quantity=product.quantity,
        details=product.details,
        timestamp=datetime.utcnow()
    )
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return {"message": "Product added to cart", "product": new_cart_item}

# API to modify a product in cart
@app.put("/modify_product_cart/{barcode}")
def modify_product_cart(barcode: str, product: ProductUpdate, db: Session = Depends(get_db)):
    cart_item = db.query(Cart).filter(Cart.barcode == barcode).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Product not found in cart.")
    
    cart_item.product_name = product.product_name
    cart_item.price = product.price
    cart_item.quantity = product.quantity
    cart_item.details = product.details
    cart_item.timestamp = datetime.now()

    db.commit()
    db.refresh(cart_item)
    return {"message": "Product modified in cart", "product": cart_item}

# API to delete a product from cart
@app.delete("/delete_product_cart/{barcode}")
def delete_product_cart(barcode: str, db: Session = Depends(get_db)):
    cart_item = db.query(Cart).filter(Cart.barcode == barcode).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Product not found in cart.")
    
    db.delete(cart_item)
    db.commit()
    return {"message": "Product deleted from cart", "deleted_product": cart_item}

@app.get("/get_cart")
def get_cart(db: Session = Depends(get_db)):
    # Query all products in the cart
    cart_items = db.query(Cart).all()
    if not cart_items:
        raise HTTPException(status_code=404, detail="No products found in cart.")
    
    # Prepare the response
    cart_products = [
        {
            "barcode": item.barcode,
            "product_name": item.product_name,
            "price": item.price,
            "quantity": item.quantity,
            "details": item.details,
            "timestamp": item.timestamp.isoformat()
        }
        for item in cart_items
    ]
    return {"cart": cart_products}


# API to clear all products in the cart
@app.delete("/clear_cart")
def clear_cart(db: Session = Depends(get_db)):
    db.query(Cart).delete()
    db.commit()
    return {"message": "All products cleared from cart"}

# API to generate a bill ticket
@app.get("/generate-bill")
def generate_bill_endpoint(cashier_name: Optional[str] = Query(None), db: Session = Depends(get_db)):
    cart_items = db.query(Cart).all()
    if not cart_items:
        raise HTTPException(status_code=404, detail="Cart is empty.")
    
    total_price = 0
    bill = "BILL TICKET\n"
    bill += "-------------------------\n"
    bill += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    if cashier_name:
        bill += f"Cashier: {cashier_name}\n"
    bill += "-------------------------\n"

    for item in cart_items:
        item_total = round(item.price * item.quantity, 2)
        bill += f"Product: {item.product_name}\n"
        bill += f"Quantity: {item.quantity}\n"
        bill += f"Price per Unit: {item.price} USD\n"
        bill += f"Total Price: {item_total} USD\n"
        bill += "-------------------------\n"
        total_price += item_total

    total_price = round(total_price, 2)  # Round total price
    bill += f"Total: {total_price} USD\n"
    bill += "-------------------------\n"

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    bill_file_path = f'C:/Users/LENOVO/Desktop/Barcode_Scanner/Bills/bill_ticket_{timestamp}.txt'
    
    with open(bill_file_path, 'w') as file:
        file.write(bill)
    
    return {"message": "Bill ticket generated successfully", "file_path": bill_file_path}

# API to add a new user to the database
@app.post("/add_user")
def add_user(user: User, db: Session = Depends(get_db)):
    user_id = str(uuid.uuid4())  # Generate a unique ID for the user

    new_user = User(
        id=user_id,
        name=user.name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User added successfully", "user": new_user}

# API to modify an existing user in the database
@app.put("/modify_user/{user_id}")
def modify_user(user_id: str, name: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    user.name = name
    db.commit()
    db.refresh(user)
    return {"message": "User modified successfully", "user": user}

# API to delete a user from the database
@app.delete("/delete_user/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully", "deleted_user": user}
