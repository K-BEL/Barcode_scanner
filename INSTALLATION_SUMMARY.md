# Installation Summary

## What You Need to Install

To run the Barcode Scanner app on your Android phone, you need:

1. ✅ **Flutter SDK** - The framework for building the app
2. ✅ **Android Studio** - Development environment and Android SDK
3. ✅ **Android SDK** - Tools to build Android apps
4. ✅ **USB Drivers** - To connect your phone (usually automatic)

## Installation Order

### 1. Install Flutter First
- Download from: https://flutter.dev/docs/get-started/install/windows
- Extract to `C:\src\flutter` (or similar)
- Add to PATH
- Verify: `flutter --version`

### 2. Install Android Studio
- Download from: https://developer.android.com/studio
- Install with Standard setup
- Let it download Android SDK components

### 3. Configure Android
- Run: `flutter doctor --android-licenses`
- Accept all licenses
- Run: `flutter doctor` to verify

### 4. Set Up Your Phone
- Enable Developer Options (tap Build Number 7 times)
- Enable USB Debugging
- Connect via USB

### 5. Verify Everything
```bash
flutter doctor          # Check Flutter setup
flutter devices        # Check phone connection
```

## Quick Commands Reference

```bash
# Check Flutter installation
flutter --version

# Check setup status
flutter doctor

# Accept Android licenses
flutter doctor --android-licenses

# Check connected devices
flutter devices

# Install project dependencies
cd frontend
flutter pub get

# Run the app
flutter run
```

## Installation Time

- **Flutter SDK:** 10-15 minutes (download + setup)
- **Android Studio:** 20-30 minutes (download + install + SDK)
- **Configuration:** 5-10 minutes
- **Total:** ~45-60 minutes

## Detailed Guides

- **Flutter Installation:** See `FLUTTER_INSTALLATION_GUIDE.md`
- **Android Setup:** See `ANDROID_SETUP_GUIDE.md`
- **Quick Start:** See `QUICK_START_ANDROID.md` (after installation)

## Common Issues

| Issue | Solution |
|-------|----------|
| Flutter not found | Add to PATH, restart terminal |
| No devices found | Enable USB debugging, check drivers |
| License errors | Run `flutter doctor --android-licenses` |
| Build errors | Run `flutter clean && flutter pub get` |

## After Installation

Once everything is installed:

1. Update API URL in `frontend/lib/services/api_service.dart`
2. Start backend: `cd backend && python run_api.py`
3. Run app: `cd frontend && flutter run`

---

**Start with:** `FLUTTER_INSTALLATION_GUIDE.md`

