# Fix: Gradle/Java Version Compatibility

## Problem
```
Unsupported class file major version 65
Your project's Gradle version is incompatible with the Java version
```

## Cause
- Java 21 (class file version 65) is being used
- Gradle 8.0 doesn't support Java 21
- Need Gradle 8.5+ for Java 21 support

## Solution Applied

✅ Updated `gradle-wrapper.properties`:
- Changed from Gradle 8.0 → Gradle 8.5
- Gradle 8.5 supports Java 17-21

✅ Updated `app/build.gradle`:
- Changed Java compatibility from 1.8 → 17
- Updated Kotlin JVM target from 1.8 → 17

## Next Steps

1. **Clean the project:**
```bash
cd frontend
flutter clean
```

2. **Get dependencies:**
```bash
flutter pub get
```

3. **Try running again:**
```bash
flutter run
```

## Gradle/Java Compatibility

| Java Version | Gradle Version Required |
|-------------|------------------------|
| Java 8      | Gradle 2.0+ |
| Java 11     | Gradle 5.0+ |
| Java 17     | Gradle 7.3+ |
| Java 21     | Gradle 8.5+ |

## If Still Having Issues

### Option 1: Use Java 17 instead of Java 21

If you have multiple Java versions installed, you can configure Flutter to use Java 17:

1. Set JAVA_HOME to Java 17
2. Or configure in Android Studio: File → Project Structure → SDK Location → JDK location

### Option 2: Update to Latest Gradle

You can also try Gradle 8.7 (latest stable):
```properties
distributionUrl=https\://services.gradle.org/distributions/gradle-8.7-all.zip
```

### Option 3: Check Java Version

```bash
java -version
```

If it shows Java 21, you can:
- Keep Java 21 and use Gradle 8.5+ (already done)
- Or switch to Java 17 if preferred

## Verification

After the fix, you should see:
- ✅ No "Unsupported class file" errors
- ✅ Gradle build succeeds
- ✅ App builds and runs

## Files Updated

- ✅ `frontend/android/gradle/wrapper/gradle-wrapper.properties` - Updated to Gradle 8.5
- ✅ `frontend/android/app/build.gradle` - Updated Java/Kotlin targets to 17

