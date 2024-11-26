import streamlit as st
import requests

# Define base URL for FastAPI
BASE_URL = "http://127.0.0.1:8000"  # Adjust if hosted on another server

st.title("Barcode Management System")

# Navigation
menu = st.sidebar.selectbox("Menu", ["Scan Barcode", "Inventory", "Cart", "Users", "Generate Bill"])

# Scan Barcode
if menu == "Scan Barcode":
    st.header("Scan Barcode")
    if st.button("Start Scanning"):
        response = requests.get(f"{BASE_URL}/scan_barcode")
        if response.status_code == 200:
            st.success("Barcode scanned successfully!")
            st.json(response.json())
        else:
            st.error(response.json().get("detail", "Error occurred while scanning"))

# Inventory Management
elif menu == "Inventory":
    st.header("Inventory Management")
    action = st.selectbox("Action", ["View All", "Add Product", "Modify Product", "Delete Product"])
    
    if action == "View All":
        response = requests.put(f"{BASE_URL}/get_list_inventory")
        if response.status_code == 200:
            st.json(response.json())
        else:
            st.error("Error fetching inventory")
    
    elif action == "Add Product":
        barcode = st.text_input("Barcode")
        product_name = st.text_input("Product Name")
        price = st.number_input("Price", min_value=0.0)
        quantity = st.number_input("Quantity", min_value=0)
        details = st.text_area("Details")
        
        if st.button("Add Product"):
            data = {"product_name": product_name, "price": price, "quantity": quantity, "details": details}
            response = requests.post(f"{BASE_URL}/add_product_inventory", params={"barcode": barcode}, json=data)
            if response.status_code == 200:
                st.success("Product added successfully!")
            else:
                st.error("Error adding product")

    elif action == "Modify Product":
        barcode = st.text_input("Barcode")
        product_name = st.text_input("Product Name")
        price = st.number_input("Price", min_value=0.0)
        quantity = st.number_input("Quantity", min_value=0)
        details = st.text_area("Details")
        
        if st.button("Modify Product"):
            data = {"product_name": product_name, "price": price, "quantity": quantity, "details": details}
            response = requests.put(f"{BASE_URL}/modify_product_inventory/{barcode}", json=data)
            if response.status_code == 200:
                st.success("Product modified successfully!")
            else:
                st.error("Error modifying product")

    elif action == "Delete Product":
        barcode = st.text_input("Barcode")
        if st.button("Delete Product"):
            response = requests.delete(f"{BASE_URL}/delete_product_inventory/{barcode}")
            if response.status_code == 200:
                st.success("Product deleted successfully!")
            else:
                st.error("Error deleting product")

# Cart Management
elif menu == "Cart":
    st.header("Cart Management")
    action = st.selectbox("Action", ["View All", "Add Product", "Modify Product", "Delete Product", "Clear Cart"])
    
    # View All Products in Cart
    if action == "View All":
        response = requests.get(f"{BASE_URL}/get_list_cart")
        if response.status_code == 200:
            cart_data = response.json()
            products = cart_data.get("products", {})
            if products:
                for barcode, product in products.items():
                    st.write(f"**Barcode:** {barcode}")
                    st.write(f"**Name:** {product['product_name']}")
                    st.write(f"**Price:** ${product['price']}")
                    st.write(f"**Quantity:** {product['quantity']}")
                    st.write(f"**Details:** {product['details']}")
                    st.write(f"**Timestamp:** {product['timestamp']}")
                    st.write("---")
            else:
                st.warning("Cart is empty.")
        else:
            st.error("Error fetching cart data.")

    # Add a Product to Cart
    elif action == "Add Product":
        st.subheader("Add Product to Cart")
        barcode = st.text_input("Enter Barcode")
        product_name = st.text_input("Enter Product Name")
        price = st.number_input("Enter Price", min_value=0.0, step=0.01)
        quantity = st.number_input("Enter Quantity", min_value=1, step=1)
        details = st.text_area("Enter Details")

        if st.button("Add Product"):
            payload = {
                "product_name": product_name,
                "price": price,
                "quantity": quantity,
                "details": details
            }
            response = requests.post(f"{BASE_URL}/add_product_cart", params={"barcode": barcode}, json=payload)
            if response.status_code == 200:
                st.success("Product added to cart successfully!")
            else:
                st.error(f"Error adding product: {response.json().get('detail', 'Unknown error')}")

    # Modify a Product in Cart
    elif action == "Modify Product":
        st.subheader("Modify Product in Cart")
        barcode = st.text_input("Enter Barcode of Product to Modify")
        product_name = st.text_input("Enter New Product Name")
        price = st.number_input("Enter New Price", min_value=0.0, step=0.01)
        quantity = st.number_input("Enter New Quantity", min_value=1, step=1)
        details = st.text_area("Enter New Details")

        if st.button("Modify Product"):
            payload = {
                "product_name": product_name,
                "price": price,
                "quantity": quantity,
                "details": details
            }
            response = requests.put(f"{BASE_URL}/modify_product_cart/{barcode}", json=payload)
            if response.status_code == 200:
                st.success("Product modified successfully!")
            else:
                st.error(f"Error modifying product: {response.json().get('detail', 'Unknown error')}")

    # Delete a Product from Cart
    elif action == "Delete Product":
        st.subheader("Delete Product from Cart")
        barcode = st.text_input("Enter Barcode of Product to Delete")

        if st.button("Delete Product"):
            response = requests.delete(f"{BASE_URL}/delete_product_cart/{barcode}")
            if response.status_code == 200:
                st.success("Product deleted successfully!")
            else:
                st.error(f"Error deleting product: {response.json().get('detail', 'Unknown error')}")

    # Clear All Products in Cart
    elif action == "Clear Cart":
        if st.button("Clear Cart"):
            response = requests.delete(f"{BASE_URL}/clear_cart")
            if response.status_code == 200:
                st.success("Cart cleared successfully!")
            else:
                st.error("Error clearing cart.")

# User Management
elif menu == "Users":
    st.header("User Management")
    action = st.selectbox("Action", ["View All", "Add User", "Modify User", "Delete User"])
    
    if action == "View All":
        response = requests.get(f"{BASE_URL}/get_users")
        if response.status_code == 200:
            st.json(response.json())
        else:
            st.error("No users found")
    
    elif action == "Add User":
        name = st.text_input("Name")
        if st.button("Add User"):
            data = {"name": name}
            response = requests.post(f"{BASE_URL}/add_user", json=data)
            if response.status_code == 200:
                st.success("User added successfully!")
            else:
                st.error("Error adding user")

    elif action == "Modify User":
        user_id = st.text_input("User ID")
        name = st.text_input("New Name")
        if st.button("Modify User"):
            response = requests.put(f"{BASE_URL}/modify_user/{user_id}", params={"name": name})
            if response.status_code == 200:
                st.success("User modified successfully!")
            else:
                st.error("Error modifying user")

    elif action == "Delete User":
        user_id = st.text_input("User ID")
        if st.button("Delete User"):
            response = requests.delete(f"{BASE_URL}/delete_user/{user_id}")
            if response.status_code == 200:
                st.success("User deleted successfully!")
            else:
                st.error("Error deleting user")

# Generate Bill
elif menu == "Generate Bill":
    st.header("Generate Bill")
    cashier_name = st.text_input("Cashier Name (Optional)")
    if st.button("Generate Bill"):
        response = requests.get(f"{BASE_URL}/generate-bill", params={"cashier_name": cashier_name})
        if response.status_code == 200:
            st.success("Bill generated successfully!")
            st.json(response.json())
        else:
            st.error("Error generating bill")
