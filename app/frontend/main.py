"""Modern Streamlit frontend for Barcode Management System."""
import streamlit as st
import requests
import os
from datetime import datetime
from pathlib import Path

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Get base URL from environment or use default
BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://127.0.0.1:8000")

# Page configuration
st.set_page_config(
    page_title="Barcode Scanner System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .product-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
    }
    .scan-button {
        background-color: #4CAF50;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📦 Barcode Management System</div>', unsafe_allow_html=True)

# Sidebar with navigation and info
with st.sidebar:
    st.image("https://via.placeholder.com/200x100/1f77b4/ffffff?text=Barcode+Scanner", use_container_width=True)
    
    st.markdown("---")
    
    menu = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📷 Scan Barcode", "📦 Inventory", "🛒 Cart", "👥 Users", "🧾 Generate Bill"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Connection status
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("⚠️ API Error")
    except:
        st.error("❌ API Disconnected")
        st.info("Start API: `python run_api.py`")
    
    st.markdown("---")
    st.caption(f"API: {BASE_URL}")

# Dashboard
if menu == "🏠 Dashboard":
    st.header("📊 Dashboard")
    
    # Get statistics
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        # Inventory stats
        inv_response = requests.get(f"{BASE_URL}/inventory/products", timeout=5)
        inv_count = len(inv_response.json()) if inv_response.status_code == 200 else 0
        
        # Cart stats
        cart_response = requests.get(f"{BASE_URL}/cart/products", timeout=5)
        cart_data = cart_response.json() if cart_response.status_code == 200 else {"products": {}}
        cart_count = len(cart_data.get("products", {}))
        cart_total = sum(item['price'] * item['quantity'] for item in cart_data.get("products", {}).values())
        
        # Users stats
        users_response = requests.get(f"{BASE_URL}/users", timeout=5)
        users_count = len(users_response.json()) if users_response.status_code == 200 else 0
        
        with col1:
            st.metric("📦 Products in Inventory", inv_count)
        with col2:
            st.metric("🛒 Items in Cart", cart_count)
        with col3:
            st.metric("💰 Cart Total", f"${cart_total:.2f}")
        with col4:
            st.metric("👥 Total Users", users_count)
    except:
        with col1:
            st.metric("📦 Products in Inventory", "N/A")
        with col2:
            st.metric("🛒 Items in Cart", "N/A")
        with col3:
            st.metric("💰 Cart Total", "N/A")
        with col4:
            st.metric("👥 Total Users", "N/A")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📷 Scan Barcode", use_container_width=True):
            st.info("Use the sidebar menu to navigate to 'Scan Barcode'")
    
    with col2:
        if st.button("📦 Add to Inventory", use_container_width=True):
            st.info("Use the sidebar menu to navigate to 'Inventory' → 'Add Product'")
    
    with col3:
        if st.button("🛒 Add to Cart", use_container_width=True):
            st.info("Use the sidebar menu to navigate to 'Cart' → 'Add Product'")
    
    # Recent activity (if cart has items)
    try:
        cart_response = requests.get(f"{BASE_URL}/cart/products", timeout=5)
        if cart_response.status_code == 200:
            cart_data = cart_response.json()
            products = cart_data.get("products", {})
            if products:
                st.markdown("---")
                st.subheader("🛒 Current Cart Items")
                for barcode, product in list(products.items())[:5]:
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**{product['product_name']}**")
                        with col2:
                            st.write(f"Qty: {product['quantity']}")
                        with col3:
                            st.write(f"${product['price'] * product['quantity']:.2f}")
                        st.caption(f"Barcode: {barcode}")
    except:
        pass

# Scan Barcode
elif menu == "📷 Scan Barcode":
    st.header("📷 Scan Barcode")
    st.info("Point your camera at a barcode to scan. The product will be automatically added to inventory if not found.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🎥 Start Scanning", type="primary", use_container_width=True):
            try:
                with st.spinner("🔄 Scanning... Please point camera at barcode"):
                    response = requests.get(f"{BASE_URL}/scan/barcode", timeout=35)
                    if response.status_code == 200:
                        scanned_data = response.json()
                        st.session_state['last_scan'] = scanned_data
                        st.success("✅ Barcode scanned successfully!")
                    else:
                        st.error(f"❌ {response.json().get('detail', 'Error scanning barcode')}")
            except requests.exceptions.Timeout:
                st.error("⏱️ Scanning timeout. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error(f"❌ Could not connect to API at {BASE_URL}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Display scanned data
    if 'last_scan' in st.session_state:
        st.markdown("---")
        st.subheader("📋 Scanned Product Information")
        scan_data = st.session_state['last_scan']
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Barcode:** {scan_data.get('barcode', 'N/A')}")
            st.info(f"**Product Name:** {scan_data.get('product_name', 'N/A')}")
        with col2:
            st.info(f"**Price:** ${scan_data.get('price', 0):.2f}")
            st.info(f"**Quantity:** {scan_data.get('quantity', 0)}")
        
        if scan_data.get('details'):
            st.info(f"**Details:** {scan_data.get('details')}")

# Inventory Management
elif menu == "📦 Inventory":
    st.header("📦 Inventory Management")
    
    action = st.selectbox(
        "Select Action",
        ["View All Products", "Add Product", "Modify Product", "Delete Product"],
        key="inventory_action"
    )
    
    if action == "View All Products":
        try:
            response = requests.get(f"{BASE_URL}/inventory/products", timeout=5)
            if response.status_code == 200:
                products = response.json()
                if products:
                    st.success(f"Found {len(products)} product(s)")
                    
                    # Display as table
                    import pandas as pd
                    products_list = []
                    for barcode, product in products.items():
                        products_list.append({
                            "Barcode": barcode,
                            "Product Name": product.get('product_name', ''),
                            "Price": f"${product.get('price', 0):.2f}",
                            "Quantity": product.get('quantity', 0),
                            "Details": product.get('details', '')[:50] + "..." if len(product.get('details', '')) > 50 else product.get('details', ''),
                            "Last Updated": product.get('timestamp', '')[:10] if product.get('timestamp') else ''
                        })
                    
                    df = pd.DataFrame(products_list)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("📭 No products in inventory. Add your first product!")
            else:
                st.error("❌ Error fetching inventory")
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Could not connect to API at {BASE_URL}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    elif action == "Add Product":
        st.subheader("➕ Add New Product")
        
        # Scan and Fetch buttons outside form
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            barcode = st.text_input(
                "Barcode *", 
                value=st.session_state.get('inv_scanned_barcode', ''),
                key="inv_barcode_input",
                help="Enter barcode or click Scan button"
            )
        with col2:
            if st.button("📷 Scan", key="inv_scan_btn", use_container_width=True):
                try:
                    with st.spinner("🔄 Scanning... Please point camera at barcode"):
                        scan_response = requests.get(f"{BASE_URL}/scan/barcode", timeout=35)
                        if scan_response.status_code == 200:
                            scanned_data = scan_response.json()
                            scanned_barcode = scanned_data.get('barcode', '')
                            
                            # Store in separate session state keys
                            st.session_state['inv_scanned_barcode'] = scanned_barcode
                            st.session_state['inv_scanned_product_name'] = scanned_data.get('product_name', '')
                            st.session_state['inv_scanned_price'] = scanned_data.get('price', 0.0)
                            st.session_state['inv_scanned_quantity'] = scanned_data.get('quantity', 1)
                            st.session_state['inv_scanned_details'] = scanned_data.get('details', '')
                            st.success(f"✅ Scanned: {scanned_barcode}")
                            st.rerun()
                        else:
                            st.error(f"❌ {scan_response.json().get('detail', 'Error scanning barcode')}")
                except requests.exceptions.Timeout:
                    st.error("⏱️ Scanning timeout. Please try again.")
                except Exception as e:
                    st.error(f"❌ Scan error: {str(e)}")
        with col3:
            if st.button("🔍 Fetch", key="inv_fetch_btn", use_container_width=True):
                current_barcode = st.session_state.get('inv_scanned_barcode', barcode)
                if not current_barcode:
                    st.error("❌ Please enter a barcode first")
                else:
                    try:
                        inv_response = requests.get(f"{BASE_URL}/inventory/products", timeout=5)
                        if inv_response.status_code == 200:
                            products = inv_response.json()
                            if current_barcode in products:
                                product = products[current_barcode]
                                st.session_state['inv_scanned_product_name'] = product.get('product_name', '')
                                st.session_state['inv_scanned_price'] = product.get('price', 0.0)
                                st.session_state['inv_scanned_quantity'] = product.get('quantity', 0)
                                st.session_state['inv_scanned_details'] = product.get('details', '')
                                st.success("✅ Product loaded from inventory!")
                                st.rerun()
                            else:
                                st.warning("⚠️ Product not found in inventory")
                    except Exception as e:
                        st.error(f"❌ Fetch error: {str(e)}")
        
        st.markdown("---")
        
        # Form for product details
        with st.form("add_product_form", clear_on_submit=True):
            product_name = st.text_input(
                "Product Name *",
                value=st.session_state.get('inv_scanned_product_name', ''),
                key="inv_product_name_form"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                price = st.number_input(
                    "Price (USD) *",
                    min_value=0.0,
                    step=0.01,
                    value=float(st.session_state.get('inv_scanned_price', 0.0)),
                    key="inv_price_form"
                )
            with col2:
                quantity = st.number_input(
                    "Quantity *",
                    min_value=0,
                    step=1,
                    value=int(st.session_state.get('inv_scanned_quantity', 0)),
                    key="inv_quantity_form"
                )
            
            details = st.text_area(
                "Details",
                value=st.session_state.get('inv_scanned_details', ''),
                key="inv_details_form",
                placeholder="Additional product information..."
            )
            
            submit = st.form_submit_button("➕ Add Product", type="primary", use_container_width=True)
            
            if submit:
                current_barcode = st.session_state.get('inv_scanned_barcode', barcode)
                if not current_barcode:
                    st.error("❌ Please enter or scan a barcode")
                elif not product_name:
                    st.error("❌ Please enter a product name")
                else:
                    try:
                        data = {
                            "product_name": product_name,
                            "price": price,
                            "quantity": quantity,
                            "details": details or "to fill"
                        }
                        response = requests.post(
                            f"{BASE_URL}/inventory/products",
                            params={"barcode": current_barcode},
                            json=data,
                            timeout=5
                        )
                        if response.status_code == 200:
                            st.success("✅ Product added successfully!")
                            # Clear session state
                            for key in ['inv_scanned_barcode', 'inv_scanned_product_name', 'inv_scanned_price', 'inv_scanned_quantity', 'inv_scanned_details']:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.rerun()
                        else:
                            st.error(f"❌ {response.json().get('detail', 'Error adding product')}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    elif action == "Modify Product":
        st.subheader("✏️ Modify Product")
        
        barcode = st.text_input("Enter Barcode to Modify", key="modify_barcode")
        
        if barcode:
            try:
                response = requests.get(f"{BASE_URL}/inventory/products", timeout=5)
                if response.status_code == 200:
                    products = response.json()
                    if barcode in products:
                        product = products[barcode]
                        
                        with st.form("modify_product_form"):
                            product_name = st.text_input("Product Name", value=product.get('product_name', ''))
                            col1, col2 = st.columns(2)
                            with col1:
                                price = st.number_input("Price", min_value=0.0, step=0.01, value=float(product.get('price', 0.0)))
                            with col2:
                                quantity = st.number_input("Quantity", min_value=0, step=1, value=int(product.get('quantity', 0)))
                            details = st.text_area("Details", value=product.get('details', ''))
                            
                            if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                                data = {
                                    "product_name": product_name,
                                    "price": price,
                                    "quantity": quantity,
                                    "details": details
                                }
                                update_response = requests.put(
                                    f"{BASE_URL}/inventory/products/{barcode}",
                                    json=data,
                                    timeout=5
                                )
                                if update_response.status_code == 200:
                                    st.success("✅ Product updated successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {update_response.json().get('detail', 'Error updating product')}")
                    else:
                        st.warning("⚠️ Product not found")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    elif action == "Delete Product":
        st.subheader("🗑️ Delete Product")
        st.warning("⚠️ This action cannot be undone!")
        
        barcode = st.text_input("Enter Barcode to Delete", key="delete_barcode")
        
        if barcode:
            try:
                response = requests.get(f"{BASE_URL}/inventory/products", timeout=5)
                if response.status_code == 200:
                    products = response.json()
                    if barcode in products:
                        product = products[barcode]
                        st.info(f"**Product:** {product.get('product_name')} | **Price:** ${product.get('price', 0):.2f}")
                        
                        if st.button("🗑️ Delete Product", type="primary"):
                            del_response = requests.delete(f"{BASE_URL}/inventory/products/{barcode}", timeout=5)
                            if del_response.status_code == 200:
                                st.success("✅ Product deleted successfully!")
                                st.rerun()
                            else:
                                st.error(f"❌ {del_response.json().get('detail', 'Error deleting product')}")
                    else:
                        st.warning("⚠️ Product not found")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Cart Management
elif menu == "🛒 Cart":
    st.header("🛒 Shopping Cart")
    
    action = st.selectbox(
        "Select Action",
        ["View Cart", "Add Product", "Modify Product", "Delete Product", "Clear Cart"],
        key="cart_action"
    )
    
    if action == "View Cart":
        try:
            response = requests.get(f"{BASE_URL}/cart/products", timeout=5)
            if response.status_code == 200:
                cart_data = response.json()
                products = cart_data.get("products", {})
                if products:
                    st.success(f"🛒 {len(products)} item(s) in cart")
                    
                    total = 0
                    import pandas as pd
                    cart_list = []
                    for barcode, product in products.items():
                        item_total = product['price'] * product['quantity']
                        total += item_total
                        cart_list.append({
                            "Barcode": barcode,
                            "Product": product['product_name'],
                            "Price": f"${product['price']:.2f}",
                            "Quantity": product['quantity'],
                            "Total": f"${item_total:.2f}"
                        })
                    
                    df = pd.DataFrame(cart_list)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        st.metric("💰 Total", f"${total:.2f}")
                else:
                    st.info("🛒 Cart is empty. Add products to get started!")
            else:
                st.error("❌ Error fetching cart")
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Could not connect to API at {BASE_URL}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    elif action == "Add Product":
        st.subheader("➕ Add Product to Cart")
        
        # Scan button outside form
        col1, col2 = st.columns([3, 1])
        with col1:
            barcode_input_key = "cart_barcode_input"
            barcode = st.text_input(
                "Barcode *", 
                value=st.session_state.get('cart_scanned_barcode', ''),
                key=barcode_input_key,
                help="Enter barcode or click Scan button"
            )
        with col2:
            if st.button("📷 Scan Barcode", key="cart_scan_btn", use_container_width=True):
                try:
                    with st.spinner("🔄 Scanning... Please point camera at barcode"):
                        scan_response = requests.get(f"{BASE_URL}/scan/barcode", timeout=35)
                        if scan_response.status_code == 200:
                            scanned_data = scan_response.json()
                            scanned_barcode = scanned_data.get('barcode', '')
                            
                            # Store in separate session state keys
                            st.session_state['cart_scanned_barcode'] = scanned_barcode
                            
                            # Fetch from inventory
                            try:
                                inv_response = requests.get(f"{BASE_URL}/inventory/products", timeout=5)
                                if inv_response.status_code == 200:
                                    products = inv_response.json()
                                    if scanned_barcode in products:
                                        product = products[scanned_barcode]
                                        st.session_state['cart_scanned_product_name'] = product.get('product_name', '')
                                        st.session_state['cart_scanned_price'] = product.get('price', 0.0)
                                        st.session_state['cart_scanned_details'] = product.get('details', '')
                                    else:
                                        st.session_state['cart_scanned_product_name'] = scanned_data.get('product_name', '')
                                        st.session_state['cart_scanned_price'] = scanned_data.get('price', 0.0)
                                        st.session_state['cart_scanned_details'] = scanned_data.get('details', '')
                            except:
                                st.session_state['cart_scanned_product_name'] = scanned_data.get('product_name', '')
                                st.session_state['cart_scanned_price'] = scanned_data.get('price', 0.0)
                                st.session_state['cart_scanned_details'] = scanned_data.get('details', '')
                            
                            st.session_state['cart_scanned_quantity'] = 1
                            st.success(f"✅ Scanned: {scanned_barcode}")
                            st.rerun()
                        else:
                            st.error(f"❌ {scan_response.json().get('detail', 'Error scanning barcode')}")
                except requests.exceptions.Timeout:
                    st.error("⏱️ Scanning timeout. Please try again.")
                except Exception as e:
                    st.error(f"❌ Scan error: {str(e)}")
        
        # Fetch button
        if st.button("🔍 Fetch from Inventory", key="cart_fetch_btn"):
            current_barcode = st.session_state.get('cart_scanned_barcode', barcode)
            if not current_barcode:
                st.error("❌ Please enter a barcode first")
            else:
                try:
                    inv_response = requests.get(f"{BASE_URL}/inventory/products", timeout=5)
                    if inv_response.status_code == 200:
                        products = inv_response.json()
                        if current_barcode in products:
                            product = products[current_barcode]
                            st.session_state['cart_scanned_product_name'] = product.get('product_name', '')
                            st.session_state['cart_scanned_price'] = product.get('price', 0.0)
                            st.session_state['cart_scanned_details'] = product.get('details', '')
                            st.session_state['cart_scanned_quantity'] = 1
                            st.success("✅ Product loaded from inventory!")
                            st.rerun()
                        else:
                            st.warning("⚠️ Product not found in inventory")
                except Exception as e:
                    st.error(f"❌ Fetch error: {str(e)}")
        
        st.markdown("---")
        
        # Form for product details
        with st.form("add_cart_form", clear_on_submit=True):
            product_name = st.text_input(
                "Product Name *",
                value=st.session_state.get('cart_scanned_product_name', ''),
                key="cart_product_name_form"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                price = st.number_input(
                    "Price (USD) *",
                    min_value=0.0,
                    step=0.01,
                    value=float(st.session_state.get('cart_scanned_price', 0.0)),
                    key="cart_price_form"
                )
            with col2:
                quantity = st.number_input(
                    "Quantity *",
                    min_value=1,
                    step=1,
                    value=int(st.session_state.get('cart_scanned_quantity', 1)),
                    key="cart_quantity_form"
                )
            
            details = st.text_area(
                "Details",
                value=st.session_state.get('cart_scanned_details', ''),
                key="cart_details_form"
            )
            
            submit = st.form_submit_button("➕ Add to Cart", type="primary", use_container_width=True)
            
            if submit:
                current_barcode = st.session_state.get('cart_scanned_barcode', barcode)
                if not current_barcode:
                    st.error("❌ Please enter or scan a barcode")
                elif not product_name:
                    st.error("❌ Please enter a product name")
                else:
                    try:
                        payload = {
                            "product_name": product_name,
                            "price": price,
                            "quantity": quantity,
                            "details": details or "to fill"
                        }
                        response = requests.post(
                            f"{BASE_URL}/cart/products",
                            params={"barcode": current_barcode},
                            json=payload,
                            timeout=5
                        )
                        if response.status_code == 200:
                            st.success("✅ Product added to cart!")
                            # Clear session state
                            for key in ['cart_scanned_barcode', 'cart_scanned_product_name', 'cart_scanned_price', 'cart_scanned_quantity', 'cart_scanned_details']:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.rerun()
                        else:
                            st.error(f"❌ {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    elif action == "Modify Product":
        st.subheader("✏️ Modify Cart Item")
        barcode = st.text_input("Enter Barcode", key="cart_modify_barcode")
        
        if barcode:
            try:
                response = requests.get(f"{BASE_URL}/cart/products", timeout=5)
                if response.status_code == 200:
                    cart_data = response.json()
                    products = cart_data.get("products", {})
                    if barcode in products:
                        product = products[barcode]
                        
                        with st.form("modify_cart_form"):
                            product_name = st.text_input("Product Name", value=product.get('product_name', ''))
                            col1, col2 = st.columns(2)
                            with col1:
                                price = st.number_input("Price", min_value=0.0, step=0.01, value=float(product.get('price', 0.0)))
                            with col2:
                                quantity = st.number_input("Quantity", min_value=1, step=1, value=int(product.get('quantity', 1)))
                            details = st.text_area("Details", value=product.get('details', ''))
                            
                            if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                                payload = {
                                    "product_name": product_name,
                                    "price": price,
                                    "quantity": quantity,
                                    "details": details
                                }
                                update_response = requests.put(
                                    f"{BASE_URL}/cart/products/{barcode}",
                                    json=payload,
                                    timeout=5
                                )
                                if update_response.status_code == 200:
                                    st.success("✅ Cart item updated!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {update_response.json().get('detail', 'Unknown error')}")
                    else:
                        st.warning("⚠️ Product not found in cart")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    elif action == "Delete Product":
        st.subheader("🗑️ Remove from Cart")
        barcode = st.text_input("Enter Barcode", key="cart_delete_barcode")
        
        if barcode:
            if st.button("🗑️ Remove from Cart", type="primary"):
                try:
                    response = requests.delete(f"{BASE_URL}/cart/products/{barcode}", timeout=5)
                    if response.status_code == 200:
                        st.success("✅ Product removed from cart!")
                        st.rerun()
                    else:
                        st.error(f"❌ {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    elif action == "Clear Cart":
        st.subheader("🗑️ Clear Cart")
        st.warning("⚠️ This will remove ALL items from cart!")
        
        if st.button("🗑️ Clear All Items", type="primary"):
            try:
                response = requests.delete(f"{BASE_URL}/cart/clear", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Cart cleared successfully!")
                    st.rerun()
                else:
                    st.error("❌ Error clearing cart")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# User Management
elif menu == "👥 Users":
    st.header("👥 User Management")
    
    action = st.selectbox(
        "Select Action",
        ["View All Users", "Add User", "Modify User", "Delete User"],
        key="user_action"
    )
    
    if action == "View All Users":
        try:
            response = requests.get(f"{BASE_URL}/users", timeout=5)
            if response.status_code == 200:
                users = response.json()
                if users:
                    import pandas as pd
                    users_list = []
                    for user_id, user in users.items():
                        users_list.append({
                            "User ID": user_id,
                            "Name": user.get('name', ''),
                            "Added": user.get('added_at', '')[:10] if user.get('added_at') else '',
                            "Modified": user.get('modified_at', '')[:10] if user.get('modified_at') else 'Never'
                        })
                    df = pd.DataFrame(users_list)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("👥 No users found")
            else:
                st.error("❌ Error fetching users")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    elif action == "Add User":
        st.subheader("➕ Add New User")
        with st.form("add_user_form"):
            name = st.text_input("User Name *", key="add_user_name")
            if st.form_submit_button("➕ Add User", type="primary", use_container_width=True):
                if not name:
                    st.error("❌ Please enter a name")
                else:
                    try:
                        response = requests.post(f"{BASE_URL}/users", json={"name": name}, timeout=5)
                        if response.status_code == 200:
                            st.success("✅ User added successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ {response.json().get('detail', 'Error adding user')}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    elif action == "Modify User":
        st.subheader("✏️ Modify User")
        user_id = st.text_input("User ID", key="modify_user_id")
        name = st.text_input("New Name", key="modify_user_name")
        
        if user_id and name:
            if st.button("💾 Save Changes", type="primary"):
                try:
                    response = requests.put(
                        f"{BASE_URL}/users/{user_id}",
                        params={"name": name},
                        timeout=5
                    )
                    if response.status_code == 200:
                        st.success("✅ User updated successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ {response.json().get('detail', 'Error modifying user')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    elif action == "Delete User":
        st.subheader("🗑️ Delete User")
        st.warning("⚠️ This action cannot be undone!")
        user_id = st.text_input("User ID", key="delete_user_id")
        
        if user_id:
            if st.button("🗑️ Delete User", type="primary"):
                try:
                    response = requests.delete(f"{BASE_URL}/users/{user_id}", timeout=5)
                    if response.status_code == 200:
                        st.success("✅ User deleted successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ {response.json().get('detail', 'Error deleting user')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Generate Bill
elif menu == "🧾 Generate Bill":
    st.header("🧾 Generate Bill")
    
    # Show cart summary first
    try:
        response = requests.get(f"{BASE_URL}/cart/products", timeout=5)
        if response.status_code == 200:
            cart_data = response.json()
            products = cart_data.get("products", {})
            
            if products:
                st.subheader("📋 Cart Summary")
                total = 0
                for barcode, product in products.items():
                    item_total = product['price'] * product['quantity']
                    total += item_total
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{product['product_name']}**")
                    with col2:
                        st.write(f"Qty: {product['quantity']}")
                    with col3:
                        st.write(f"${item_total:.2f}")
                
                st.markdown("---")
                col1, col2 = st.columns([3, 1])
                with col2:
                    st.metric("💰 Total Amount", f"${total:.2f}")
                
                st.markdown("---")
                
                cashier_name = st.text_input("Cashier Name (Optional)", key="cashier_name")
                
                if st.button("🧾 Generate Bill", type="primary", use_container_width=True):
                    try:
                        params = {}
                        if cashier_name:
                            params["cashier_name"] = cashier_name
                        response = requests.get(f"{BASE_URL}/bills/generate", params=params, timeout=10)
                        if response.status_code == 200:
                            bill_data = response.json()
                            st.success("✅ Bill generated successfully!")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.info(f"**File:** {bill_data.get('file_path', 'N/A')}")
                            with col2:
                                st.info(f"**Total:** ${bill_data.get('total_amount', 0):.2f}")
                            
                            if bill_data.get('cashier'):
                                st.info(f"**Cashier:** {bill_data.get('cashier')}")
                        else:
                            st.error(f"❌ {response.json().get('detail', 'Error generating bill')}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("🛒 Cart is empty. Add products to cart before generating a bill.")
                st.info("Use the sidebar menu to navigate to 'Cart' to add products")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
