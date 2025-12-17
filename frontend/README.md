# Sentry Safety Helmet App 👷‍♂️

This is an Expo React Native app for the Sentry Safety Helmet project, created with [`create-expo-app`](https://www.npmjs.com/package/create-expo-app).

## ⚠️ Important: Bluetooth Support

This app uses Bluetooth Low Energy (BLE) which requires a **development build** (not Expo Go).

**👉 See [BLE_SETUP_GUIDE.md](./BLE_SETUP_GUIDE.md) for complete setup instructions.**

## Quick Start

1. Install dependencies

   ```bash
   npm install
   ```

2. Build the app (required for BLE support)

   **Option A: Local Build**
   ```bash
   npm run build:android:clean
   ```

   **Option B: EAS Build (cloud)**
   ```bash
   npm install -g eas-cli
   eas login
   eas build:configure
   npm run eas:build:dev
   ```

3. Start development server (after first build)

   ```bash
   npm start
   ```

   Press `a` for Android or scan the QR code with your device.

## Available Scripts

- `npm start` - Start Metro bundler (normal development)
- `npm run build:android` - Build and install Android app locally
- `npm run build:android:clean` - Clean build (recommended for first build)
- `npm run eas:build:dev` - Create development build via EAS (cloud)
- `npm run eas:build:prod` - Create production build via EAS
- `npm run prebuild` - Generate native Android/iOS folders
- `npm run prebuild:clean` - Clean and regenerate native folders

For more details, see [BLE_SETUP_GUIDE.md](./BLE_SETUP_GUIDE.md).

## Get a fresh project

When you're ready, run:

```bash
npm run reset-project
```

This command will move the starter code to the **app-example** directory and create a blank **app** directory where you can start developing.

## Learn more

To learn more about developing your project with Expo, look at the following resources:

- [Expo documentation](https://docs.expo.dev/): Learn fundamentals, or go into advanced topics with our [guides](https://docs.expo.dev/guides).
- [Learn Expo tutorial](https://docs.expo.dev/tutorial/introduction/): Follow a step-by-step tutorial where you'll create a project that runs on Android, iOS, and the web.

## Join the community

Join our community of developers creating universal apps.

- [Expo on GitHub](https://github.com/expo/expo): View our open source platform and contribute.
- [Discord community](https://chat.expo.dev): Chat with Expo users and ask questions.
