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

**Note for physical device testing**: Update `lib/services/api_service.dart` with your computer's IP address instead of `10.0.2.2`.

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

All backend configuration is done via `.env` file in the `backend/` directory.

### Required Environment Variables

- `DB_HOST` - MySQL host (default: localhost)
- `DB_PORT` - MySQL port (default: 3306)
- `DB_USERNAME` or `DB_USER` - MySQL username (required)
- `DB_PASSWORD` - MySQL password (required)
- `DB_DATABASE` or `DB_NAME` - Database name (required)
- `DB_CHARSET` - Database charset (default: utf8mb4)
- `DB_POOL_SIZE` - Connection pool size (default: 10)

### Optional Environment Variables

- `API_HOST` - API server host (default: 127.0.0.1)
- `API_PORT` - API server port (default: 8000)
- `DEBUG` - Enable debug mode (default: False)
- `ALLOWED_ORIGINS` - CORS allowed origins (comma-separated, empty for development)
- `FRONTEND_BASE_URL` - Frontend base URL (default: http://127.0.0.1:8000)

### Creating .env File

1. Copy the example file (if available) or create a new `.env` file in the `backend/` directory
2. Set all required variables with your actual values
3. Never commit the `.env` file to version control

Example `.env` file:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USERNAME=barcode_user
DB_PASSWORD=your_secure_password
DB_DATABASE=barcode_scanner
DEBUG=False
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Deployment

### Production Deployment Considerations

1. **Security**
   - Set `DEBUG=False` in production
   - Configure `ALLOWED_ORIGINS` with specific domains (never use `*` in production)
   - Use strong database passwords
   - Enable HTTPS/SSL for API endpoints
   - Consider implementing API authentication (currently not implemented)

2. **Database**
   - Use a production-grade MySQL server
   - Set up proper backups
   - Configure connection pooling appropriately
   - Monitor database performance

3. **Docker Deployment**
   - Use `docker-compose.yml` for containerized deployment
   - Set environment variables via `.env` file or Docker secrets
   - Configure health checks
   - Set up log rotation

4. **Environment Variables**
   - Never commit `.env` files to version control
   - Use secrets management in production (e.g., Docker secrets, Kubernetes secrets)
   - Rotate credentials regularly

### Docker Deployment

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## API Authentication

**Note:** Currently, the API does not implement authentication. All endpoints are publicly accessible. For production use, consider implementing:

- JWT-based authentication
- API key authentication
- OAuth2 integration
- Role-based access control (RBAC)

This is a planned feature for future versions.

## Troubleshooting

### API Connection Issues

**Problem:** Cannot connect to API server

**Solutions:**
- Ensure API server is running: `cd backend && python run_api.py`
- Check `.env` file configuration
- Verify firewall settings allow connections on the API port
- Check if port 8000 is already in use: `netstat -an | grep 8000` (Linux/Mac) or `netstat -an | findstr 8000` (Windows)
- For mobile app: Use computer's local IP instead of localhost (see Flutter README)
- Check API logs in `logs/app.log` and `logs/errors.log`

### Database Issues

**Problem:** Database connection errors

**Solutions:**
- Check MySQL service is running: `sudo systemctl status mysql` (Linux) or check Services (Windows)
- Verify credentials in `backend/.env` match your MySQL setup
- Ensure database exists: `mysql -u root -p -e "SHOW DATABASES;"`
- Check database user has proper permissions
- Verify network connectivity to database server
- Check database connection pool settings if experiencing connection exhaustion

**Problem:** "Table doesn't exist" errors

**Solutions:**
- Database tables are auto-created on first run
- Check `backend/app/core/db_init.py` for table creation scripts
- Manually run database initialization if needed
- Check database logs for creation errors

### Flutter App Issues

**Problem:** App cannot connect to API

**Solutions:**
- Update `lib/services/api_service.dart` with correct base URL
- For emulator: Use `http://10.0.2.2:8000`
- For physical device: Use your computer's local IP (e.g., `http://192.168.1.100:8000`)
- Ensure API server is accessible from the device's network
- Check firewall allows incoming connections
- Verify API server is bound to `0.0.0.0` not just `127.0.0.1`

**Problem:** Barcode scanning not working

**Solutions:**
- Grant camera permissions to the app
- Check device camera is not in use by another app
- Verify `mobile_scanner` package is properly installed
- Check AndroidManifest.xml has camera permissions

### Camera Issues (Streamlit)

**Problem:** Camera not detected or not working

**Solutions:**
- Grant camera permissions to browser
- Check if camera is in use by another app
- Try different camera index in config
- On Linux, may need to install `v4l-utils`
- Check browser console for errors

### Validation Errors

**Problem:** API returns 400 Bad Request or 422 Unprocessable Entity

**Solutions:**
- Check request body matches schema requirements
- Verify barcode format (alphanumeric, max 255 chars)
- Ensure prices are non-negative and within valid range
- Check quantities are non-negative integers
- Verify string lengths are within limits (product names max 255 chars)

### Performance Issues

**Problem:** Slow API responses

**Solutions:**
- Check database query performance
- Monitor connection pool usage
- Consider adding database indexes
- Review and optimize slow queries
- Check server resource usage (CPU, memory)
- Consider implementing caching for frequently accessed data

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
