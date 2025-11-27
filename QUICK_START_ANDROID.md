# Quick Start: Run on Android Phone

## ⚠️ Prerequisites

**If Flutter is not installed yet, see `FLUTTER_INSTALLATION_GUIDE.md` first!**

## 🚀 Fast Setup (5 minutes)

### 1. Find Your Computer's IP Address

**Windows:**
```bash
ipconfig
```
Copy the IPv4 address (e.g., `192.168.1.100`)

**Mac/Linux:**
```bash
ifconfig | grep "inet "
```
Copy the IP address (usually `192.168.x.x`)

### 2. Update API URL in Flutter App

Edit `frontend/lib/services/api_service.dart`:

Change line 12 from:
```dart
static const String baseUrl = 'http://10.0.2.2:8000';
```

To (replace with YOUR IP):
```dart
static const String baseUrl = 'http://192.168.1.100:8000'; // YOUR IP HERE
```

### 3. Start Backend Server

```bash
cd backend
python run_api.py
```

The server should start on `http://0.0.0.0:8000`

### 4. Connect Your Phone

- Connect phone to computer via USB
- Enable USB Debugging on phone (Settings → Developer Options)

### 5. Run the App

```bash
cd frontend
flutter pub get
flutter run
```

The app will build and install on your phone automatically!

## ✅ Verify It Works

1. Open the app on your phone
2. Go to Dashboard or Inventory tab
3. If you see data or can add products, it's working!

## 🔧 Troubleshooting

**Can't connect?**
- Make sure phone and computer are on the same Wi-Fi
- Check firewall allows port 8000
- Verify IP address is correct

**Need more help?**
See `ANDROID_SETUP_GUIDE.md` for detailed instructions.

