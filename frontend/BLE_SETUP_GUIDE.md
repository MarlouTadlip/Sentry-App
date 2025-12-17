# Bluetooth (BLE) Setup Guide

This guide explains how to set up and use Bluetooth Low Energy (BLE) functionality with the Sentry App.

## ⚠️ Important: Native Module Requirement

The app uses `react-native-ble-plx` which is a **native module**. This means:

- ❌ **Expo Go does NOT support it** - You cannot use the Expo Go app
- ✅ **Development builds ARE required** - You need to create a custom build
- ✅ **Once built, you can develop normally** - After the first build, use `npm start` for hot reloading

---

## 🚀 Quick Start (Choose One Method)

### Method 1: Local Build (Recommended for Quick Testing)

If you have Android Studio and Android SDK set up locally:

```bash
# Step 1: Clean prebuild (regenerates native code)
npm run prebuild:clean

# Step 2: Build and install on connected device
npm run build:android

# Step 3: For future development, just use:
npm start
# Then press 'a' to open on Android device
```

**When to use this:**
- You have Android Studio installed
- You want to build locally
- You're comfortable with local Android development setup

---

### Method 2: EAS Build (Recommended for Cloud Builds)

If you don't want to set up Android development locally:

```bash
# Step 1: Install EAS CLI (one-time)
npm install -g eas-cli

# Step 2: Login to Expo (one-time)
eas login

# Step 3: Configure EAS (one-time, creates eas.json)
eas build:configure

# Step 4: Build development build in the cloud
npm run eas:build:dev

# Step 5: Install the APK on your device
# - Follow the link provided after build completes
# - Download and install the APK on your Android device

# Step 6: For future development, just use:
npm start
# The app will automatically connect to your installed development build
```

**When to use this:**
- You don't have Android Studio installed
- You want cloud-based builds
- You're working on different machines
- You want the easiest setup process

---

## 📋 Available Scripts

### Development Scripts

| Script | Description |
|--------|-------------|
| `npm start` | Start Metro bundler (use this for normal development after initial build) |
| `npm run prebuild` | Generate native Android/iOS folders (without cleaning) |
| `npm run prebuild:clean` | Clean and regenerate native folders (removes existing android/ios) |
| `npm run build:android` | Build and install Android app locally (requires Android Studio) |
| `npm run build:android:clean` | Clean prebuild + build Android (all-in-one) |

### EAS Build Scripts

| Script | Description |
|--------|-------------|
| `npm run eas:build:dev` | Create development build for Android (cloud) |
| `npm run eas:build:dev:ios` | Create development build for iOS (cloud) |
| `npm run eas:build:prod` | Create production build for Android (cloud) |
| `npm run eas:build:prod:ios` | Create production build for iOS (cloud) |

---

## 🔄 Development Workflow

### First Time Setup

1. **Choose your build method** (Local or EAS)
2. **Build the app** using one of the methods above
3. **Install the app** on your physical device

### Daily Development (After First Build)

Once you have the development build installed:

```bash
# Just start the Metro bundler
npm start

# Press 'a' for Android or scan the QR code
# Your changes will hot reload automatically!
```

You **don't need to rebuild** for:
- ✅ JavaScript/TypeScript code changes
- ✅ React component changes
- ✅ Style changes
- ✅ Most configuration changes

You **DO need to rebuild** when:
- ❌ Adding new native modules
- ❌ Changing native code
- ❌ Modifying `app.json` plugins
- ❌ Changing app signing or bundle identifier

---

## 🔧 Troubleshooting

### Issue: "BLE Manager not available" Warning

**Cause:** The native module isn't loaded because:
- The app hasn't been built yet, OR
- You're using Expo Go (which doesn't support native modules)

**Solution:**
1. Make sure you've built a development build (Method 1 or 2 above)
2. Make sure you're running the development build, not Expo Go
3. If you just rebuilt, try restarting the Metro bundler: `npm start -- --clear`

### Issue: Build Fails with Native Module Errors

**Solution:**
```bash
# Clean everything and rebuild
npm run prebuild:clean
npm run build:android
```

### Issue: App Crashes When Trying to Use BLE

**Possible causes:**
1. **Missing permissions** - Make sure Bluetooth permissions are granted in device settings
2. **Bluetooth is disabled** - Enable Bluetooth on your device
3. **Location permission** - Android requires location permission for BLE scanning
4. **App not rebuilt** - Rebuild the app after adding BLE functionality

**Check permissions:**
- Go to Android Settings → Apps → Sentry App → Permissions
- Enable: Location, Bluetooth, Nearby Devices

### Issue: "Cannot read property 'createClient' of null"

**Cause:** The native module didn't load properly.

**Solution:**
1. Make sure you've run `npm run prebuild:clean` and `npm run build:android`
2. Uninstall the old app from your device
3. Rebuild and reinstall: `npm run build:android:clean`
4. Restart Metro bundler: `npm start -- --clear`

---

## 📱 Testing Bluetooth

Once your app is built and installed:

1. **Start the app** on your device
2. **Enable Bluetooth** on your device
3. **Grant permissions** when prompted (Location + Bluetooth)
4. **Go to Home screen** in the app
5. **Tap "Scan for Devices"** to find your ESP32 Sentry device
6. **Tap "Connect"** on the device you want to connect to
7. **Sensor data** should start appearing automatically

---

## 🏗️ Project Structure

```
frontend/
├── services/bluetooth/
│   ├── bleManager.ts        # BLE manager implementation
│   └── deviceScanner.ts     # Device scanning utilities
├── context/
│   └── DeviceContext.tsx    # React context for BLE state
├── app.json                 # Expo config (includes BLE plugin)
└── package.json             # Dependencies and scripts
```

---

## 📚 Additional Resources

- [Expo Development Builds Guide](https://docs.expo.dev/develop/development-builds/introduction/)
- [react-native-ble-plx Documentation](https://github.com/dotintent/react-native-ble-plx)
- [EAS Build Documentation](https://docs.expo.dev/build/introduction/)
- [Expo Prebuild Documentation](https://docs.expo.dev/workflow/prebuild/)

---

## 💡 Tips

1. **First build takes longer** - Subsequent builds are faster due to caching
2. **Use EAS Build for production** - Use `npm run eas:build:prod` for release builds
3. **Development builds are separate** - You can have both Expo Go and development build installed
4. **Hot reload works great** - After first build, development is smooth with hot reloading
5. **Check logs** - Use `npx expo start --clear` to see full logs if issues occur

---

## ✅ Checklist

Before using BLE features, ensure:

- [ ] Development build has been created (Method 1 or 2)
- [ ] App is installed on physical device
- [ ] Bluetooth is enabled on device
- [ ] Location permission is granted
- [ ] Bluetooth permission is granted
- [ ] Metro bundler is running (`npm start`)
- [ ] App is running the development build (not Expo Go)

