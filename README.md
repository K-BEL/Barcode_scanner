# Barcode Scanner System

A modern, scalable barcode scanning and inventory management system built with FastAPI and Streamlit.

## Features

- 📷 **Barcode Scanning**: Real-time barcode scanning using camera
- 📦 **Inventory Management**: Complete CRUD operations for products
- 🛒 **Shopping Cart**: Manage cart items before checkout
- 🧾 **Bill Generation**: Generate and save bill tickets
- 👥 **User Management**: Manage system users
- 🗄️ **MySQL Database**: Pure MySQL implementation (no ORM)
- 📊 **Dashboard**: Real-time statistics and quick actions
- 🎨 **Modern UI**: Beautiful, intuitive Streamlit interface

## Quick Start

### Prerequisites

- Python 3.8+
- MySQL Server
- Camera (for barcode scanning)

### Installation

1. **Clone and navigate to project**
```bash
cd Barcode_scanner
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up MySQL**

Create database and user:
```sql
CREATE DATABASE barcode_scanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'barcode_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON barcode_scanner.* TO 'barcode_user'@'localhost';
FLUSH PRIVILEGES;
```

4. **Configure environment**

Create `.env` file:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=barcode_user
DB_PASSWORD=your_password
DB_NAME=barcode_scanner
DB_CHARSET=utf8mb4
FRONTEND_BASE_URL=http://127.0.0.1:8000
```

### Running the Application

**Terminal 1 - Start API Server:**
```bash
python run_api.py
```

**Terminal 2 - Start Frontend:**
```bash
python run_frontend.py
```

- **API**: http://127.0.0.1:8000
- **Frontend**: http://localhost:8501
- **API Docs**: http://127.0.0.1:8000/docs

## Project Structure

```
Barcode_scanner/
├── app/
│   ├── api/          # API routes
│   ├── services/     # Business logic
│   ├── core/         # Configuration & database
│   ├── frontend/     # Streamlit UI
│   ├── schemas/      # Pydantic models
│   └── utils/        # Utilities
├── Bills/            # Generated bills
├── logs/             # Application logs
├── run_api.py        # API server script
├── run_frontend.py   # Frontend script
└── requirements.txt  # Dependencies
```

## Usage

### Dashboard
View statistics, quick actions, and current cart items.

### Scan Barcode
Quick barcode scanning to view product information.

### Inventory Management
- **View All**: Browse all products in inventory
- **Add Product**: Scan or manually add products
- **Modify Product**: Update product details
- **Delete Product**: Remove products from inventory

### Cart Management
- **View Cart**: See all cart items with totals
- **Add Product**: Scan or add products to cart
- **Smart Quantity Updates**: Scanning/adding the same barcode again automatically increases its quantity
- **Modify Product**: Update cart items
- **Delete Product**: Remove items from cart
- **Clear Cart**: Remove all items

### Generate Bill
Generate bills from cart items. Bills are saved to `Bills/` directory and the cart is automatically cleared to prepare for the next customer.

### User Management
Manage system users (add, modify, delete, view).

## API Endpoints

### Scanner
- `GET /scan/barcode` - Scan a barcode

### Inventory
- `GET /inventory/products` - Get all products
- `POST /inventory/products` - Add product
- `PUT /inventory/products/{barcode}` - Update product
- `DELETE /inventory/products/{barcode}` - Delete product

### Cart
- `GET /cart/products` - Get cart items
- `POST /cart/products` - Add to cart
- `PUT /cart/products/{barcode}` - Update cart item
- `DELETE /cart/products/{barcode}` - Remove from cart
- `DELETE /cart/clear` - Clear cart

### Users
- `GET /users` - Get all users
- `POST /users` - Add user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

### Bills
- `GET /bills/generate` - Generate bill

## Database

The application uses **pure MySQL** (no ORM). Tables are automatically created on first run:

- `products` - Product inventory
- `cart` - Shopping cart items
- `users` - System users
- `bills` - Generated bills

## Configuration

All configuration is done via `.env` file or environment variables:

- `DB_HOST` - MySQL host (default: localhost)
- `DB_PORT` - MySQL port (default: 3306)
- `DB_USER` - MySQL username
- `DB_PASSWORD` - MySQL password
- `DB_NAME` - Database name (default: barcode_scanner)
- `FRONTEND_BASE_URL` - API base URL for frontend

## Troubleshooting

### API Connection Issues
- Ensure API server is running: `python run_api.py`
- Check `FRONTEND_BASE_URL` in `.env`
- Verify firewall settings

### Database Issues
- Check MySQL service is running
- Verify credentials in `.env`
- Ensure database exists

### Camera Issues
- Grant camera permissions to browser
- Check if camera is in use by another app
- Try different camera index in config

## Development

### Project Structure
- **API Layer** (`app/api/`): HTTP endpoints
- **Service Layer** (`app/services/`): Business logic with MySQL queries
- **Core** (`app/core/`): Configuration and database connection
- **Frontend** (`app/frontend/`): Streamlit UI

### Adding Features
1. Add service method in `app/services/`
2. Create API route in `app/api/`
3. Update frontend in `app/frontend/main.py`

## License

[Add your license here]

## Support

For issues or questions, check:
- API logs: `logs/app.log` and `logs/errors.log`
- API documentation: http://127.0.0.1:8000/docs
- Database connection status in frontend sidebar
