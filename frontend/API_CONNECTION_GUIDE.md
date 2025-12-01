# API Connection Guide for Debugging

This guide explains how to connect your Flutter app to the API server while debugging.

## Quick Setup

### For Android Emulator
The default configuration uses `http://10.0.2.2:8000` which works automatically with the Android emulator.

### For Physical Device
You need to update the API URL with your computer's IP address.

## Finding Your Computer's IP Address

### Windows
1. Open **Command Prompt** (cmd)
2. Type: `ipconfig`
3. Look for **"IPv4 Address"** under your active network adapter (usually Wi-Fi or Ethernet)
4. Example: `192.168.1.100` or `172.16.111.16`

### Mac
1. Open **Terminal**
2. Type: `ifconfig | grep "inet " | grep -v 127.0.0.1`
3. Look for the IP address (usually starts with 192.168.x.x or 10.0.x.x)

### Linux
1. Open **Terminal**
2. Type: `ip addr show` or `hostname -I`
3. Look for the IP address (not 127.0.0.1)

## Configuring the API URL

### Method 1: Update Config File (Recommended)

Edit `lib/config/api_config.dart`:

```dart
// For Android Emulator
static const String debugBaseUrl = 'http://10.0.2.2:8000';

// For Physical Device - Replace with your computer's IP
static const String debugBaseUrl = 'http://YOUR_IP_ADDRESS:8000';
// Example: static const String debugBaseUrl = 'http://192.168.1.100:8000';
```

### Method 2: Override at Runtime (Advanced)

You can override the base URL programmatically:

```dart
import 'package:your_app/services/api_service.dart';

// In your app initialization (e.g., main.dart)
void main() {
  // Override API URL for physical device
  ApiService.setBaseUrl('http://192.168.1.100:8000');
  
  runApp(const MyApp());
}
```

## Testing the Connection

1. **Start the API server:**
   ```bash
   cd backend
   python run_api.py
   ```
   The API should be running at `http://localhost:8000`

2. **Verify the API is accessible:**
   - From your computer's browser: `http://localhost:8000`
   - Should show: `{"message": "Welcome to Barcode Scanner API", ...}`

3. **Check firewall settings:**
   - Make sure port 8000 is not blocked
   - Windows: Check Windows Firewall settings
   - Allow Python/uvicorn through firewall if prompted

4. **Run your Flutter app:**
   ```bash
   flutter run
   ```

## Troubleshooting

### "Unable to connect to server" Error

**Problem:** App can't reach the API server

**Solutions:**
- ✅ Verify API server is running: `http://localhost:8000` in browser
- ✅ Check IP address is correct in `api_config.dart`
- ✅ Ensure phone/emulator and computer are on the same network (for physical device)
- ✅ Check firewall isn't blocking port 8000
- ✅ Try pinging your computer's IP from the device

### "Connection refused" Error

**Problem:** API server not accepting connections

**Solutions:**
- ✅ Make sure API server is bound to `0.0.0.0` not just `127.0.0.1`
- ✅ Check `backend/run_api.py` uses `host="0.0.0.0"` for physical device access
- ✅ Verify port 8000 is not in use by another application

### Works on Emulator but Not Physical Device

**Problem:** Emulator works but physical device can't connect

**Solutions:**
- ✅ Update `debugBaseUrl` in `api_config.dart` with your computer's IP
- ✅ Ensure phone and computer are on the same Wi-Fi network
- ✅ Check router doesn't have AP isolation enabled
- ✅ Try disabling VPN if active

## Environment-Specific Configuration

The app automatically uses:
- **Debug mode:** `debugBaseUrl` from `api_config.dart`
- **Release mode:** `releaseBaseUrl` from `api_config.dart`

You can set different URLs for development and production builds.

## Quick Reference

| Environment | URL Format | Example |
|------------|------------|---------|
| Android Emulator | `http://10.0.2.2:8000` | Default |
| iOS Simulator | `http://localhost:8000` | `http://127.0.0.1:8000` |
| Physical Device | `http://YOUR_IP:8000` | `http://192.168.1.100:8000` |

## Current Configuration

Check `lib/config/api_config.dart` for the current API URL settings.

