# Barcode Scanner Flutter App

Flutter mobile application for the Barcode Scanner System. This app provides barcode scanning functionality using the phone's camera and connects to the FastAPI backend.

## Features

- 📷 **Barcode Scanning** - Use phone camera to scan barcodes
- 📦 **Inventory Management** - View, add, edit, and delete products
- 🛒 **Shopping Cart** - Manage cart items and checkout
- 👥 **User Management** - Add and manage users
- 🧾 **Bill Generation** - Generate bills from cart items
- 📊 **Dashboard** - View statistics and quick actions

## Prerequisites

- Flutter SDK 3.0 or higher
- Android Studio / Android SDK
- Android device or emulator (API 21+)
- Backend API server running (see main README)

## Setup

1. **Install Flutter dependencies**
```bash
cd frontend
flutter pub get
```

2. **Configure API Base URL**

Edit `lib/services/api_service.dart`:

For Android emulator:
```dart
static const String baseUrl = 'http://10.0.2.2:8000';
```

For physical Android device:
```dart
// Replace YOUR_COMPUTER_IP with your computer's local IP address
// Find your IP: Windows (ipconfig), Linux/Mac (ifconfig)
static const String baseUrl = 'http://YOUR_COMPUTER_IP:8000';
```

Example:
```dart
static const String baseUrl = 'http://192.168.1.100:8000';
```

3. **Ensure backend is running**

Make sure the FastAPI backend is running on your computer:
```bash
cd backend
python run_api.py
```

## Running the App

### On Android Emulator
```bash
flutter run
```

### On Physical Device

1. Enable USB debugging on your Android device
2. Connect device via USB
3. Run:
```bash
flutter run
```

### Build APK for Installation
```bash
flutter build apk
```

The APK will be in `build/app/outputs/flutter-apk/app-release.apk`

## Project Structure

```
frontend/
├── lib/
│   ├── main.dart              # App entry point
│   ├── models/                # Data models
│   │   ├── product.dart
│   │   ├── cart.dart
│   │   ├── user.dart
│   │   └── bill.dart
│   ├── services/              # API and services
│   │   ├── api_service.dart   # HTTP client for backend API
│   │   └── barcode_service.dart # Barcode scanner service
│   └── screens/               # UI screens
│       ├── home_screen.dart   # Main navigation
│       ├── dashboard_screen.dart
│       ├── scan_screen.dart
│       ├── inventory_screen.dart
│       ├── cart_screen.dart
│       ├── users_screen.dart
│       └── bills_screen.dart
├── android/                   # Android configuration
└── pubspec.yaml              # Dependencies
```

## Permissions

The app requires the following permissions (already configured in `AndroidManifest.xml`):

- **Internet** - To connect to the backend API
- **Camera** - For barcode scanning

These permissions are automatically requested when needed.

## Usage

### Scanning Barcodes

1. Navigate to the "Scan" tab
2. Tap "Start Scanning"
3. Point camera at barcode
4. The app will automatically detect and process the barcode
5. Product information will be displayed

### Managing Inventory

1. Navigate to "Inventory" tab
2. Tap the "+" button to add a product
3. Enter product details (barcode, name, price, etc.)
4. Use edit/delete buttons to manage existing products

### Shopping Cart

1. Add products to cart from inventory
2. View cart in "Cart" tab
3. Modify quantities or remove items
4. Proceed to checkout

### Generating Bills

1. Ensure cart has items
2. Navigate to "Bills" tab
3. Review cart summary
4. Tap "Generate Bill"
5. Optionally enter cashier name
6. Bill will be generated on the backend

## Troubleshooting

### Cannot Connect to Backend

1. **Check backend is running**: Ensure FastAPI server is running
2. **Check IP address**: Verify the IP in `api_service.dart` matches your computer's IP
3. **Check network**: Ensure phone and computer are on the same network
4. **Check firewall**: Allow port 8000 through firewall on your computer
5. **For emulator**: Use `10.0.2.2` instead of localhost

### Camera Not Working

1. Grant camera permissions when prompted
2. Check device settings if permissions were denied
3. Ensure no other app is using the camera

### Build Errors

1. Run `flutter clean`
2. Run `flutter pub get`
3. Ensure all dependencies are compatible
4. Check Flutter version: `flutter --version`

### API Errors

1. Check backend logs: `logs/app.log`
2. Verify backend API is accessible: Open `http://YOUR_IP:8000/docs` in browser
3. Check CORS settings in backend (should allow all origins for development)

## Dependencies

Main dependencies (see `pubspec.yaml`):

- `http` / `dio` - HTTP client for API calls
- `mobile_scanner` - Barcode scanning
- `provider` - State management
- `intl` - Internationalization

## Development

### Adding New Features

1. Create models in `lib/models/`
2. Add API methods in `lib/services/api_service.dart`
3. Create screens in `lib/screens/`
4. Update navigation in `home_screen.dart`

### Code Style

Follow Flutter/Dart style guidelines:
```bash
flutter analyze
flutter format .
```

## Testing

To run tests:
```bash
flutter test
```

## Building for Release

### APK
```bash
flutter build apk --release
```

### App Bundle (for Play Store)
```bash
flutter build appbundle --release
```

## Support

For issues:
- Check backend API logs
- Verify API connection settings
- Review Flutter/Dart console output
- Check device logs: `adb logcat`

## License

[Add your license here]

