# Flutter Installation Guide for Android

This guide will help you install Flutter and set up your development environment to run the Barcode Scanner app on your Android phone.

## Prerequisites

- Windows 10 or later (64-bit)
- At least 2GB of free disk space
- Internet connection

## Step 1: Install Flutter SDK

### Option A: Download Flutter (Recommended)

1. **Download Flutter SDK:**
   - Go to: https://flutter.dev/docs/get-started/install/windows
   - Click "Download Flutter SDK"
   - Download the latest stable version (ZIP file, ~1.5GB)

2. **Extract Flutter:**
   - Extract the ZIP file to a location like:
     - `C:\src\flutter`
     - **Important:** Don't install in `C:\Program Files\` (requires admin permissions)

3. **Add Flutter to PATH:**
   - Press `Win + X` and select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "User variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\src\flutter\bin` (or your Flutter path)
   - Click "OK" on all dialogs

4. **Verify Installation:**
   - Open a new Command Prompt or PowerShell
   - Run: `flutter --version`
   - You should see Flutter version information

### Option B: Using Git (Alternative)

```bash
git clone https://github.com/flutter/flutter.git -b stable
```

Then add to PATH as described above.

## Step 2: Install Android Studio

### Download and Install

1. **Download Android Studio:**
   - Go to: https://developer.android.com/studio
   - Click "Download Android Studio"
   - Run the installer

2. **Installation Steps:**
   - Follow the installation wizard
   - Choose "Standard" installation
   - Accept license agreements
   - Let it download Android SDK components (this takes time)

3. **First Launch Setup:**
   - Open Android Studio
   - Complete the setup wizard
   - Install Android SDK Platform-Tools
   - Install Android SDK Build-Tools

### Configure Android SDK

1. In Android Studio, go to: **File → Settings → Appearance & Behavior → System Settings → Android SDK**
2. Under "SDK Platforms" tab:
   - Check "Android 13.0 (Tiramisu)" or latest
   - Check "Android SDK Platform 33" or latest
3. Under "SDK Tools" tab:
   - Check "Android SDK Build-Tools"
   - Check "Android SDK Platform-Tools"
   - Check "Android SDK Command-line Tools"
   - Check "Google Play services"
   - Check "Intel x86 Emulator Accelerator (HAXM installer)" if available
4. Click "Apply" and let it download

## Step 3: Accept Android Licenses

Open Command Prompt or PowerShell and run:

```bash
flutter doctor --android-licenses
```

Accept all licenses by typing `y` when prompted.

## Step 4: Verify Flutter Installation

Run Flutter doctor to check your setup:

```bash
flutter doctor
```

You should see something like:

```
[✓] Flutter (Channel stable, 3.x.x)
[✓] Android toolchain - develop for Android devices
[✓] Chrome - develop for the web
[✓] Visual Studio - develop for Windows
[✓] Android Studio (version 2023.x)
[✓] VS Code (optional)
[✓] Connected device
[✓] Network resources
```

**Fix any issues shown:**
- If Android toolchain shows issues, run: `flutter doctor --android-licenses`
- If Android Studio is missing, install it (Step 2)
- If VS Code is mentioned, it's optional (you can use Android Studio)

## Step 5: Set Up Your Android Phone

### Enable Developer Options

1. On your Android phone:
   - Go to **Settings → About Phone**
   - Find **Build Number**
   - Tap **Build Number** 7 times
   - You'll see "You are now a developer!"

### Enable USB Debugging

1. Go to **Settings → Developer Options**
2. Enable **USB Debugging**
3. Enable **Install via USB** (if available)

### Connect Phone to Computer

1. Connect phone via USB cable
2. On phone, when prompted, tap "Allow USB debugging"
3. Check "Always allow from this computer" (optional)
4. Tap "Allow"

## Step 6: Verify Device Connection

Run:

```bash
flutter devices
```

You should see your phone listed, something like:
```
sdk gphone64 arm64 (mobile) • emulator-5554 • android-arm64 • Android 13
```

Or your physical device:
```
SM-G991B (mobile) • R58M30ABCDE • android-arm64 • Android 13
```

## Step 7: Install Project Dependencies

Now that Flutter is installed, set up the project:

```bash
cd frontend
flutter pub get
```

This will download all required packages.

## Step 8: Run the App

```bash
flutter run
```

Flutter will:
1. Build the app
2. Install it on your connected phone
3. Launch it automatically

## Quick Installation Checklist

- [ ] Download Flutter SDK
- [ ] Extract Flutter to `C:\src\flutter` (or similar)
- [ ] Add Flutter to PATH
- [ ] Download and install Android Studio
- [ ] Install Android SDK components
- [ ] Run `flutter doctor --android-licenses`
- [ ] Run `flutter doctor` and fix any issues
- [ ] Enable Developer Options on phone
- [ ] Enable USB Debugging on phone
- [ ] Connect phone via USB
- [ ] Run `flutter devices` to verify connection
- [ ] Run `flutter pub get` in frontend folder
- [ ] Run `flutter run` to launch app

## Troubleshooting

### Flutter Command Not Found

- Make sure Flutter is added to PATH
- Close and reopen Command Prompt/PowerShell
- Verify: `flutter --version` works

### Android Licenses Not Accepted

```bash
flutter doctor --android-licenses
```

Accept all licenses.

### No Devices Found

1. **Check USB connection:**
   - Try different USB cable
   - Try different USB port
   - Enable "File Transfer" mode on phone

2. **Check USB drivers:**
   - Install phone manufacturer's USB drivers
   - Or install Google USB drivers from Android Studio

3. **Verify device:**
   ```bash
   adb devices
   ```
   Should show your device. If not, install ADB drivers.

### Build Errors

1. **Clean and rebuild:**
   ```bash
   cd frontend
   flutter clean
   flutter pub get
   flutter run
   ```

2. **Check Flutter version:**
   ```bash
   flutter --version
   ```
   Should be 3.0 or higher.

3. **Update Flutter:**
   ```bash
   flutter upgrade
   ```

### Android Studio Issues

- If Android Studio is slow, increase memory:
  - Help → Edit Custom VM Options
  - Increase `-Xmx` value (e.g., `-Xmx4096m`)

- If SDK download fails:
  - Check internet connection
  - Try using VPN
  - Download SDK manually from Android website

## Alternative: Install Flutter via Package Manager

### Using Chocolatey (Windows)

If you have Chocolatey installed:

```bash
choco install flutter
```

### Using Scoop (Windows)

If you have Scoop installed:

```bash
scoop install flutter
```

## Next Steps

Once Flutter is installed and working:

1. **Update API URL:**
   - Edit `frontend/lib/services/api_service.dart`
   - Set `baseUrl` to your computer's IP address

2. **Start Backend:**
   ```bash
   cd backend
   python run_api.py
   ```

3. **Run App:**
   ```bash
   cd frontend
   flutter run
   ```

## Resources

- **Flutter Documentation:** https://flutter.dev/docs
- **Flutter Installation:** https://flutter.dev/docs/get-started/install/windows
- **Android Studio:** https://developer.android.com/studio
- **Flutter Troubleshooting:** https://flutter.dev/docs/get-started/install/windows#troubleshooting

## Need Help?

If you encounter issues:

1. Run `flutter doctor -v` for detailed diagnostics
2. Check Flutter's troubleshooting guide
3. Search Flutter GitHub issues
4. Ask on Flutter Discord or Stack Overflow

---

**Estimated Installation Time:** 30-60 minutes (depending on internet speed)

**After installation, proceed to:** `QUICK_START_ANDROID.md` or `ANDROID_SETUP_GUIDE.md`

