# Barcode Scanner System

A modern, scalable barcode scanning and inventory management system with:
- **FastAPI Backend** - RESTful API with MySQL database
- **Flutter Mobile App** - Android app with camera barcode scanning
- **Streamlit Web Frontend** - Optional web-based testing interface

## Features

- 📷 **Barcode Scanning**: Real-time barcode scanning using phone camera (Flutter) or computer camera (Streamlit)
- 📦 **Inventory Management**: Complete CRUD operations for products
- 🛒 **Shopping Cart**: Manage cart items before checkout
- 🧾 **Bill Generation**: Generate and save bill tickets
- 👥 **User Management**: Manage system users
- 🗄️ **MySQL Database**: Pure MySQL implementation (no ORM)
- 📊 **Dashboard**: Real-time statistics and quick actions
- 🎨 **Modern UI**: Beautiful interfaces for both mobile and web

## Project Structure

```
Barcode_scanner/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── services/          # Business logic
│   │   ├── core/              # Configuration & database
│   │   ├── frontend/          # Streamlit UI (optional)
│   │   ├── schemas/           # Pydantic models
│   │   └── utils/             # Utilities
│   ├── run_api.py             # API server script
│   ├── run_frontend.py        # Streamlit frontend script
│   └── requirements.txt       # Backend dependencies
│
├── frontend/                   # Flutter mobile app
│   ├── lib/
│   │   ├── models/            # Data models
│   │   ├── services/          # API service layer
│   │   └── screens/           # UI screens
│   ├── android/               # Android configuration
│   └── pubspec.yaml           # Flutter dependencies
│
├── Bills/                      # Generated bills
├── logs/                       # Application logs
└── README.md                   # This file
```

## Quick Start

### Prerequisites

- Python 3.8+
- MySQL Server
- Flutter SDK 3.0+ (for mobile app)
- Android Studio / Android SDK (for mobile app)

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Install Python dependencies**
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

Create `backend/.env` file:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=barcode_user
DB_PASSWORD=your_password
DB_NAME=barcode_scanner
DB_CHARSET=utf8mb4
FRONTEND_BASE_URL=http://127.0.0.1:8000
```

5. **Run the API server**
```bash
python run_api.py
```

The API will be available at http://127.0.0.1:8000
API documentation: http://127.0.0.1:8000/docs

### Optional: Streamlit Web Frontend

From the `backend` directory:
```bash
python run_frontend.py
```

The Streamlit interface will be available at http://localhost:8501

### Flutter Mobile App Setup

See [frontend/README.md](frontend/README.md) for detailed Flutter app setup instructions.

Quick setup:
```bash
cd frontend
flutter pub get
flutter run
```

<<<<<<< HEAD
**Note for physical device testing**: Update `lib/services/api_service.dart` with your computer's IP address instead of `10.0.2.2`.
=======
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
>>>>>>> 6ee6f1d48ec387ee4f167c258872756aab4d6efe

## API Endpoints

### Scanner
- `GET /scan/barcode` - Scan a barcode (uses backend camera)

### Inventory
- `GET /inventory/products` - Get all products
- `POST /inventory/products?barcode={barcode}` - Add product
- `PUT /inventory/products/{barcode}` - Update product
- `DELETE /inventory/products/{barcode}` - Delete product

### Cart
- `GET /cart/products` - Get cart items
- `POST /cart/products?barcode={barcode}` - Add to cart
- `PUT /cart/products/{barcode}` - Update cart item
- `DELETE /cart/products/{barcode}` - Remove from cart
- `DELETE /cart/clear` - Clear cart

### Users
- `GET /users` - Get all users
- `POST /users` - Add user
- `PUT /users/{user_id}?name={name}` - Update user
- `DELETE /users/{user_id}` - Delete user

### Bills
- `GET /bills/generate?cashier_name={name}` - Generate bill

## Database

The application uses **pure MySQL** (no ORM). Tables are automatically created on first run:

- `products` - Product inventory
- `cart` - Shopping cart items
- `users` - System users
- `bills` - Generated bills

## Configuration

All backend configuration is done via `.env` file in the `backend/` directory:

- `DB_HOST` - MySQL host (default: localhost)
- `DB_PORT` - MySQL port (default: 3306)
- `DB_USER` - MySQL username
- `DB_PASSWORD` - MySQL password
- `DB_NAME` - Database name (default: barcode_scanner)
- `API_HOST` - API server host (default: 127.0.0.1)
- `API_PORT` - API server port (default: 8000)

## Troubleshooting

### API Connection Issues
- Ensure API server is running: `cd backend && python run_api.py`
- Check `.env` file configuration
- Verify firewall settings
- For mobile app: Use computer's local IP instead of localhost (see Flutter README)

### Database Issues
- Check MySQL service is running
- Verify credentials in `backend/.env`
- Ensure database exists

### Camera Issues (Streamlit)
- Grant camera permissions to browser
- Check if camera is in use by another app
- Try different camera index in config

## Development

### Backend Development
- **API Layer** (`backend/app/api/`): HTTP endpoints
- **Service Layer** (`backend/app/services/`): Business logic with MySQL queries
- **Core** (`backend/app/core/`): Configuration and database connection
- **Frontend** (`backend/app/frontend/`): Streamlit UI

### Mobile App Development
See [frontend/README.md](frontend/README.md) for Flutter app development guide.

### Adding Features
1. Add service method in `backend/app/services/`
2. Create API route in `backend/app/api/`
3. Update Flutter app in `frontend/lib/` or Streamlit frontend in `backend/app/frontend/`

## License

[Add your license here]

## Support

For issues or questions:
- API logs: `logs/app.log` and `logs/errors.log`
- API documentation: http://127.0.0.1:8000/docs
- Check backend and frontend README files for specific setup issues
