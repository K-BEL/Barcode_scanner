# Android Setup Guide

This guide will help you run the Barcode Scanner app on your Android phone.

## Prerequisites

1. **Flutter SDK** (3.0 or higher)
   - Download from: https://flutter.dev/docs/get-started/install
   - Verify installation: `flutter doctor`

2. **Android Studio** (optional but recommended)
   - Download from: https://developer.android.com/studio
   - Includes Android SDK and emulator

3. **Backend API Running**
   - The FastAPI backend must be running on your computer
   - See main README for backend setup

## Step 1: Configure API Connection

### Find Your Computer's IP Address

**Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" under your active network adapter (usually starts with 192.168.x.x)

**Mac/Linux:**
```bash
ifconfig
# or
ip addr show
```
Look for your local IP address (usually starts with 192.168.x.x)

### Update API Service

1. Open `frontend/lib/services/api_service.dart`

2. Find this line (around line 12):
```dart
static const String baseUrl = 'http://10.0.2.2:8000';
```

3. Replace with your computer's IP address:
```dart
static const String baseUrl = 'http://192.168.1.100:8000'; // Replace with YOUR IP
```

**Important Notes:**
- Use `10.0.2.2` only for Android emulator
- For physical device, use your computer's actual IP address
- Both phone and computer must be on the same Wi-Fi network

## Step 2: Configure Backend CORS

1. Open `backend/.env` (or create from `.env.example`)

2. Set `ALLOWED_ORIGINS` to allow your phone:
```env
ALLOWED_ORIGINS=*
```
Or for production, specify exact origins:
```env
ALLOWED_ORIGINS=http://192.168.1.100:8000,http://localhost:8000
```

3. Restart the backend server

## Step 3: Enable USB Debugging (For Physical Device)

1. On your Android phone:
   - Go to **Settings** → **About Phone**
   - Tap **Build Number** 7 times to enable Developer Options
   - Go back to **Settings** → **Developer Options**
   - Enable **USB Debugging**

2. Connect phone to computer via USB

3. Verify connection:
```bash
flutter devices
```
You should see your device listed

## Step 4: Install Dependencies

```bash
cd frontend
flutter pub get
```

## Step 5: Run the App

### Option A: Run Directly on Phone

```bash
cd frontend
flutter run
```

Flutter will build and install the app on your connected device.

### Option B: Build APK for Manual Installation

1. Build the APK:
```bash
cd frontend
flutter build apk
```

2. The APK will be at:
```
frontend/build/app/outputs/flutter-apk/app-release.apk
```

3. Transfer APK to your phone and install:
   - Transfer via USB, email, or cloud storage
   - On phone, enable "Install from Unknown Sources" if needed
   - Open the APK file to install

## Step 6: Test the Connection

1. **Start the backend server:**
```bash
cd backend
python run_api.py
```

2. **Verify backend is accessible:**
   - On your phone's browser, go to: `http://YOUR_COMPUTER_IP:8000/docs`
   - You should see the API documentation

3. **Open the app on your phone:**
   - The app should connect to the backend automatically
   - Try scanning a barcode or viewing inventory

## Troubleshooting

### App Can't Connect to Backend

1. **Check IP Address:**
   - Verify the IP in `api_service.dart` matches your computer's IP
   - Make sure both devices are on the same Wi-Fi network

2. **Check Firewall:**
   - Windows: Allow port 8000 through Windows Firewall
   - Mac: Allow incoming connections on port 8000
   - Linux: Configure firewall to allow port 8000

3. **Check Backend:**
   - Ensure backend is running: `python run_api.py`
   - Check backend logs for errors
   - Verify backend is listening on `0.0.0.0` or your IP, not just `127.0.0.1`

4. **Test Connection:**
   - From phone browser: `http://YOUR_IP:8000/docs`
   - Should show API documentation

### Camera Not Working

1. **Grant Permissions:**
   - When app requests camera permission, tap "Allow"
   - If denied, go to Settings → Apps → Barcode Scanner → Permissions → Camera

2. **Check Device:**
   - Ensure no other app is using the camera
   - Restart the app if needed

### Build Errors

1. **Clean and Rebuild:**
```bash
cd frontend
flutter clean
flutter pub get
flutter run
```

2. **Check Flutter Version:**
```bash
flutter --version
```
Should be 3.0 or higher

3. **Check Dependencies:**
```bash
flutter doctor
```
Fix any issues shown

### API Errors

1. **Check Backend Logs:**
   - Look in `backend/logs/app.log` and `backend/logs/errors.log`

2. **Verify API Endpoints:**
   - Backend now uses `/api/v1/` prefix
   - App has been updated to use versioned endpoints

3. **Check CORS:**
   - Ensure `ALLOWED_ORIGINS` in backend `.env` includes `*` or your IP

## Quick Reference

### Common Commands

```bash
# Check connected devices
flutter devices

# Run on connected device
flutter run

# Build APK
flutter build apk

# Check Flutter setup
flutter doctor

# Get dependencies
flutter pub get

# Clean build
flutter clean
```

### File Locations

- **API Service Config**: `frontend/lib/services/api_service.dart`
- **Backend Config**: `backend/.env`
- **APK Output**: `frontend/build/app/outputs/flutter-apk/app-release.apk`

### Network Requirements

- Phone and computer on same Wi-Fi network
- Backend accessible on port 8000
- Firewall allows port 8000
- CORS configured to allow phone's requests

## Next Steps

Once the app is running:

1. **Test Barcode Scanning:**
   - Go to Scan tab
   - Point camera at a barcode
   - Product should be detected

2. **Add Products:**
   - Go to Inventory tab
   - Add products manually or via scanning

3. **Test Cart:**
   - Add products to cart
   - Generate a bill

4. **Customize:**
   - Update app name, icon, colors as needed
   - See Flutter documentation for customization

## Support

If you encounter issues:

1. Check backend logs: `backend/logs/`
2. Check Flutter console output
3. Verify network connectivity
4. Ensure all prerequisites are installed
5. Review error messages carefully

For more help, see:
- Flutter Documentation: https://flutter.dev/docs
- Backend README: `README.md`
- Frontend README: `frontend/README.md`

