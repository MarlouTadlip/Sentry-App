# Two-Tier Crash Detection Approach

## Implementation Checklist

> **Status**: Phase 1 Partially Complete | **Last Updated**: 2025
> 
> This checklist tracks all implementation tasks for the two-tier crash detection system. The implementation is divided into two phases:
> - **Phase 1**: Tier 1 - Client-Side Fast Threshold Detection (immediate alerts)
> - **Phase 2**: Tier 2 - Backend AI Analysis (intelligent confirmation)
> 
> Complete Phase 1 first to get basic crash detection working, then implement Phase 2 for AI-powered confirmation.

### Recent Updates & Notes

**GPS Implementation Status**:
- ⚠️ GPS data collection from phone (React Native) needs to be implemented (Phase 1)
- ⚠️ Location permission requests need to be added to UI (Phase 1)
- ⚠️ GPS data service using `expo-location` needs to be created (Phase 1)
- ⚠️ Speed calculation (client-side) needs to be implemented (Phase 1)
- ⚠️ GPS data storage in `DeviceContext` needs to be updated (Phase 1)
- ⚠️ GPS data is **NOW included** in crash alert requests (Phase 2 - needs implementation)

**BLE Library**:
- ✅ Using `react-native-ble-plx` (not `react-native-ble-manager` or `expo-bluetooth`)
- ✅ Requires native build: `npx expo prebuild && npx expo run:android`

**Phase 2 Implementation Status** (✅ COMPLETED):
- ✅ GPS fields added to `CrashEvent` model
- ✅ GPS schema (`GPSDataSchema`) added to backend
- ✅ `CrashAlertRequest` updated to include GPS data (backend & frontend)
- ✅ `useCrashDetection` hook updated to send GPS to backend
- ✅ Crash controller stores GPS in CrashEvent
- ✅ FCM service includes GPS in crash notifications
- ✅ Loved ones notification utility created (`notify_loved_ones_with_gps()`)
- ✅ **Migration completed**: GPS fields migration has been run
- ✅ **UI Updates completed**: CrashAlert component now displays AI analysis results
- ✅ **Rate limiting implemented**: Client-side throttling prevents excessive API calls (configurable interval, default 15 seconds)
- ✅ **Field name mapping fixed**: Threshold result transformed from camelCase to snake_case for backend compatibility
- ✅ **API key authentication**: Frontend configured to use `X-API-Key` header with `EXPO_PUBLIC_DEVICE_API_KEY`
- ✅ **Backend-stored settings**: Crash alert interval stored in `UserSettings` model (10-60 seconds range)
- ✅ **Enhanced AI analysis**: Gemini AI now receives both sensor data AND crash event history for better context
- ✅ **Dynamic context**: Higher interval settings allow more sensor data and crash events to be analyzed

---

## Phase 1: Tier 1 - Client-Side Threshold Detection

> **Goal**: Implement fast, local crash detection that provides immediate alerts (<100ms) without backend dependency.

### Frontend Setup

#### Project Setup & Structure
- [x] Create folder structure (`services`, `hooks`, `context`, `lib`, `types`, `utils`, `components`)
- [x] Setup TypeScript path aliases (`@/` for root directory)

#### React Context (Local State)
- [x] Create `context/DeviceContext.tsx`
  - [x] BLE connection state management
  - [x] Current sensor reading state
  - [x] Connect/disconnect functions
  - [x] Start/stop receiving data functions
- [x] Create `context/CrashContext.tsx`
  - [x] Last crash alert state
  - [x] Processing state
  - [x] Setter functions

#### Bluetooth Low Energy (BLE)
- [x] Choose BLE library (✅ Using `react-native-ble-plx` - already implemented)
- [x] Create `services/bluetooth/bleManager.ts` (✅ Implemented - handles sensor data only, GPS now comes from phone)
  - [x] BLE manager initialization (placeholder)
  - [x] Device scanning functionality (placeholder)
  - [x] Device connection/disconnection (placeholder)
  - [x] Characteristic subscription (placeholder)
  - [x] Listener cleanup (prevent memory leaks) (placeholder)
  - [x] Sensor data parsing with error handling (placeholder)
- [x] Create `services/bluetooth/deviceScanner.ts` (⚠️ Placeholder - needs implementation)
  - [x] Device scanning logic (placeholder)
  - [x] Device pairing/connection flow (placeholder)
- [ ] Test BLE connection with ESP32 device
- [ ] Handle BLE disconnection scenarios
- [ ] Implement reconnection logic

#### GPS Integration (Phase 1)
- [x] Install `expo-location` package for GPS access
- [x] Create `services/location/locationService.ts`
  - [x] Request location permissions (optional - user can deny)
  - [x] Get current GPS location from phone
  - [x] Start location tracking (continuous updates)
  - [x] Calculate speed from GPS coordinates (distance/time)
  - [x] Handle location errors gracefully
  - [x] Stop location tracking when not needed
- [x] Update `context/DeviceContext.tsx` to store GPS data
  - [x] Add `currentGPSData` state (stores latest GPS reading from phone)
  - [x] Add `currentSpeed` state (calculated from GPS)
  - [x] Integrate location service
  - [x] Update GPS data state when received from location service
  - [x] **Note**: GPS data stored locally only in Tier 1 (not sent to backend until crash detected)
- [x] Update `types/device.ts` to include GPS data types
  - [x] Create `GPSData` interface (accuracy, latitude, longitude, altitude, speed, timestamp)
  - [x] Add `speed` field to GPSData (calculated from GPS coordinates)
  - [x] Add `speed_change` field to GPSData (sudden deceleration detection)
  - [ ] Add GPS data to `SensorReading` interface (optional, for combined data)
- [x] Add location permission UI
  - [x] Request permission on app startup (optional)
  - [x] Show permission status in settings
  - [x] Allow user to enable/disable GPS tracking
  - [x] Handle permission denied gracefully (GPS is optional)

#### Crash Detection Logic
- [x] Create `services/crash/threshold.ts`
  - [x] `ThresholdDetector` class
  - [x] Threshold configuration (G-force, tilt, consecutive triggers)
  - [x] Consecutive trigger detection logic (fixed version)
  - [x] Severity calculation
  - [x] Trigger type determination
  - [ ] Add speed-based threshold detection (optional - for immediate alerts)
- [x] Create `services/crash/calculator.ts`
  - [x] `calculateGForce()` function (with proper unit conversion)
  - [x] `calculateTilt()` function (roll and pitch)
  - [x] `isTiltExceeded()` helper function
  - [x] `calculateSpeed()` function (from GPS coordinates - distance/time)
  - [x] `calculateSpeedChange()` function (sudden deceleration detection)
  - [x] `isSuddenDeceleration()` helper function

#### Crash Detection Hook (Tier 1 Only)
- [x] Create `hooks/useCrashDetection.ts`
  - [x] Integrate `ThresholdDetector`
  - [x] Process sensor data from BLE
  - [x] Race condition protection (useRef for processing state)
  - [x] **Console log** threshold exceeded events (no notifications yet)
    - [x] Log threshold result details (severity, trigger type, G-force, tilt)
    - [x] Log timestamp and sensor data
  - [x] Store threshold alerts locally (in state/context)
  - [x] Reset detector after processing
  - [x] **Note**: Backend API calls and notifications will be added in Phase 2

#### TypeScript Types
- [x] Create `types/device.ts`
  - [x] `SensorReading` interface
  - [x] `BLEDevice` interface
  - [x] `GPSData` interface (fix, satellites, latitude, longitude, altitude, timestamp)
- [x] Create `types/crash.ts`
  - [x] `ThresholdResult` interface
  - [x] `ThresholdConfig` interface
  - [x] `CrashEvent` interface (for future use)
- [x] Create `types/api.ts` (Phase 2 types prepared)
  - [ ] Add GPS data to `CrashAlertRequest` interface (Phase 2)

#### UI Components (Tier 1)
- [x] Create `components/crash/CrashAlert.tsx`
  - [x] Display crash alert UI
  - [x] Show threshold detection results
  - [x] Display severity and trigger type
  - [x] **Note**: AI analysis results will be added in Phase 2 (structure ready)
- [x] Create `components/crash/CrashIndicator.tsx`
  - [x] Visual indicator for crash detection status
  - [x] Show when threshold is exceeded
- [x] Create `components/device/SensorDisplay.tsx`
  - [x] Display real-time sensor data
  - [x] Show BLE connection status
  - [x] Display G-force and tilt values
  - [ ] Display GPS data (latitude, longitude, accuracy, speed) (optional)
  - [ ] Display speed from GPS (km/h or mph)
  - [ ] Show location permission status
  - [ ] Show GPS tracking status (enabled/disabled)

#### Integration (Tier 1)
- [x] Integrate BLE data flow with crash detection hook (✅ Integrated - ready when BLE is implemented)
- [x] Connect DeviceContext to BLE manager (✅ Connected in app layout)
- [x] Connect CrashContext to crash detection (✅ Connected in app layout)
- [x] Integrate with existing app navigation (✅ Added providers to app layout)
- [x] Add crash detection to appropriate screens (✅ Integrated into home screen)
- [ ] Test Tier 1 flow: BLE → Threshold → Console Log (⚠️ Requires BLE implementation)

#### Utilities & Constants
- [x] Create `utils/math.ts` (not needed - calculator.ts covers it)
- [x] Create `utils/validation.ts` (data validation utilities) (✅ Implemented)
- [x] Create `utils/constants.ts`
  - [x] `CRASH_DETECTION_CONFIG` constants
  - [x] BLE UUIDs (make configurable)
  - [x] Threshold values
  - [x] **Crash alert interval** (✅ Default: 15 seconds, stored in backend UserSettings model, range: 10-60 seconds)

### ESP32 Device Configuration (Phase 1)

- [x] Setup ESP32 development environment
- [x] Install MPU6050 library
- [x] Configure BLE
  - [x] Set BLE service UUID
  - [x] Set sensor data characteristic UUID
  - [x] Configure device name (e.g., "Sentry Device")
- [x] Implement sensor reading
  - [x] Read MPU6050 accelerometer data
  - [x] Calculate roll, pitch, tilt_detected
  - [x] Format data as JSON
- [x] Implement BLE transmission
  - [x] Send sensor data every 2 seconds
  - [x] Handle BLE connection/disconnection
  - [x] Error handling for sensor read failures
- [ ] Test BLE communication with mobile app
- [ ] Optimize battery usage

**Note**: GPS data is now collected from the phone (React Native app), not from ESP32 device. This provides more accurate location data and allows speed calculation.

### Phase 1 Testing

- [ ] Unit tests for threshold detection logic
- [ ] Unit tests for G-force and tilt calculations
- [ ] Unit tests for consecutive trigger logic
- [ ] Integration tests for BLE connection (requires physical device)
- [ ] Integration tests for crash detection hook
- [ ] Test Tier 1 end-to-end: BLE → Threshold → Console Log
- [ ] Test with various sensor data scenarios
- [ ] Test BLE disconnection handling
- [ ] Verify console logs show threshold events correctly

### Phase 1 Completion Criteria

- [ ] ESP32 device sends sensor data via BLE every 2 seconds
- [ ] Mobile app receives and parses BLE sensor data
- [ ] Mobile app collects GPS data from phone (via `expo-location`)
- [ ] Location permissions requested (optional - user can deny)
- [ ] Speed calculated from GPS coordinates (client-side)
- [ ] GPS data stored in DeviceContext (local storage only in Tier 1)
- [ ] Threshold detection works correctly (G-force, tilt, and optionally speed)
- [ ] Console logs show threshold exceeded events with details
- [ ] UI displays crash alerts, sensor data, and GPS/speed (if available)
- [ ] Basic error handling in place
- [ ] Tier 1 testing completed
- [ ] **Note**: Notifications will be implemented in Phase 2
- [ ] **Note**: GPS data sent to backend only when crash detected (Phase 2)

### Phase 2 Completion Criteria

- [x] Backend receives crash alerts from mobile app (with GPS data) (✅ Schema and controller updated)
- [x] Gemini AI analyzes crash data and provides confirmation (✅ Already implemented)
- [x] CrashEvent records created in database (with GPS location) for all AI analyses - both confirmed crashes AND false positives (✅ GPS fields added, `is_confirmed_crash` field distinguishes them)
- [x] FCM push notifications sent on confirmed crashes (with GPS location) (✅ GPS added to notification payload)
- [x] GPS location sent to loved ones when crash confirmed (✅ `notify_loved_ones_with_gps()` created)
- [x] Frontend displays AI analysis results (✅ CrashAlert component enhanced with AI display)
- [ ] User feedback mechanism working (⚠️ Not yet implemented)
- [ ] Complete end-to-end flow tested (⚠️ Testing needed)
- [ ] False positive reduction verified (⚠️ Testing needed - Note: false positives are now stored in database with `is_confirmed_crash=False` for analytics and model improvement)

---

## Phase 2: Tier 2 - Backend AI Analysis

> **Goal**: Add intelligent AI-powered crash confirmation to reduce false positives and provide detailed crash analysis.

### Backend Setup

#### Dependencies
- [x] Add `httpx` dependency (✅ Added to `pyproject.toml`)
  - [x] Used for Expo Push Notification API HTTP requests
  - [x] Version: `httpx>=0.27.0,<1.0.0`

#### Models
- [x] Create `device/models/sensor_data.py` (✅ Already exists)
  - [x] `SensorData` model for storing sensor readings
  - [x] Timestamp indexing for efficient queries
  - [x] Device relationship
  - [x] Fields: device_id, ax, ay, az, roll, pitch, tilt_detected, timestamp
  - [ ] Add GPS fields: latitude, longitude, altitude, gps_fix, satellites (optional - store GPS with sensor data)
- [x] Create `device/models/crash_event.py` (✅ Already exists)
  - [x] `CrashEvent` model with all required fields
  - [x] Database indexes for frequently queried fields
  - [x] Model Meta configuration
  - [x] Fields: device_id, user, crash_timestamp, is_confirmed_crash, confidence_score, severity, etc.
  - [x] Add GPS fields: crash_latitude, crash_longitude, crash_altitude, gps_accuracy_at_crash (✅ Added)
  - [x] Add speed fields: speed_at_crash (m/s), speed_change_at_crash (m/s²), max_speed_before_crash (m/s)
- [x] Create `device/models/device_token.py` (for FCM tokens) (✅ Already exists)
  - [x] `DeviceToken` model
  - [x] User/device relationship
  - [x] Token refresh mechanism
  - [x] Platform field (iOS/Android)
- [x] Create `core/models/user_settings.py` (✅ COMPLETED - Required for backend-stored crash alert interval)
  - [x] `UserSettings` model with OneToOneField to User
  - [x] `crash_alert_interval_seconds` field (IntegerField, default=15, range: 10-60)
  - [x] Validation: enforce 10-60 second range
  - [x] Index on user field for efficient queries
- [ ] Create and run migrations (⚠️ Run: `python manage.py makemigrations core --name add_user_settings` and `python manage.py makemigrations device --name add_gps_fields_to_crash_event`)

#### Schemas
- [x] Create `device/schemas/crash_schema.py` (✅ Already exists)
  - [x] `CrashAlertRequest` schema
    - [x] Add GPS data fields (latitude, longitude, altitude, accuracy, speed) (✅ Added GPSDataSchema)
    - [x] GPS data optional (may not have location permission or fix at crash time) (✅ Added as optional)
    - [x] Add speed fields to GPSDataSchema (speed, speed_change)
  - [x] `CrashAlertResponse` schema (✅ Already exists)
  - [x] Field validators (✅ Already implemented)
- [x] Create `device/schemas/fcm_schema.py` (✅ Implemented)
  - [x] `FCMTokenRequest` schema - For token registration
  - [x] `FCMTokenResponse` schema - Token registration response
  - [x] `TestNotificationRequest` schema - For test notifications
  - [x] `TestNotificationResponse` schema - Test notification response
- [ ] Create `device/schemas/device_schema.py` (if needed)
  - [ ] Device token registration schema

#### Controllers
- [x] Create `device/controllers/crash_controller.py` (✅ Already exists)
  - [x] `process_crash_alert()` function (✅ Already implemented)
  - [x] Follow backend guide conventions (import order, type hints, docstrings) (✅ Follows conventions)
  - [x] Error handling with proper HTTP errors (✅ Already implemented)
  - [x] Transaction management for multi-step operations (✅ Already implemented)
  - [x] Store GPS location in CrashEvent for all AI analyses (both confirmed crashes and false positives) (✅ Added GPS field storage)
  - [x] Store speed data in CrashEvent (speed_at_crash, speed_change_at_crash, max_speed_before_crash)
  - [x] Store all AI analysis results (confirmed crashes AND false positives) using `is_confirmed_crash` field to distinguish (✅ Implemented - all analyses stored)
  - [x] Send GPS location to loved ones when crash confirmed (via FCM notification) (✅ Added loved ones notification)
  - [x] **Fetch user's crash alert interval from UserSettings** (✅ COMPLETED - Required for dynamic context)
  - [x] **Calculate dynamic lookback seconds based on interval** (✅ COMPLETED - Higher interval = more context)
    - [x] Formula: `lookback_seconds = min(30 + (interval - 10) * 3, 180)`
    - [x] Example: 10s interval = 30s lookback, 30s interval = 90s lookback, 60s interval = 180s lookback
  - [x] **Retrieve recent crash events for AI context** (✅ COMPLETED - Include crash event history)
    - [x] Query recent crash events (1-3 events based on interval: `max(1, interval // 20)`)
    - [x] Include: is_confirmed_crash, confidence_score, severity, crash_type, max_g_force, crash_timestamp
- [x] Create `core/controllers/user_settings_controller.py` (✅ COMPLETED - Required for settings management)
  - [x] `get_user_settings()` function - Get user's crash alert interval
  - [x] `update_user_settings()` function - Update crash alert interval (validate 10-60 range)
  - [x] Error handling with proper HTTP errors
  - [x] Uses JWT authentication (via user router)
- [ ] Create `device/controllers/device_controller.py` (if not exists)
  - [ ] Device data reception endpoint
- [x] Create `device/controllers/fcm_controller.py` (✅ Implemented)
  - [x] `register_fcm_token()` function - Register Expo Push Token
  - [x] `send_test_notification()` function - Send test push notification
  - [x] Error handling with proper HTTP errors
  - [x] Uses JWT authentication (via mobile router)

#### Services
- [x] Create `device/services/crash_detector.py` (✅ Already exists)
  - [x] `get_recent_sensor_data()` function (✅ Implemented)
  - [x] Query last N seconds of sensor data from database (✅ Implemented)
  - [x] Format data for AI analysis (✅ Returns list of dicts)
  - [ ] Include GPS data in sensor data queries (if stored with sensor data)
- [x] Create `core/ai/gemini_service.py` (✅ Already exists)
  - [x] `GeminiService` class (✅ Implemented)
  - [x] `format_sensor_data_for_ai()` method (✅ Implemented)
  - [x] `analyze_crash_data()` method (✅ Implemented)
  - [x] Prompt engineering for crash detection (✅ Implemented)
  - [x] JSON response parsing (✅ Implemented)
  - [x] Error handling and retry logic (✅ Implemented)
  - [x] **Update `format_sensor_data_for_ai()` to accept crash events** (✅ COMPLETED - Required for enhanced analysis)
    - [x] Add `crash_events` parameter (list of crash event dicts)
    - [x] Format crash event history in prompt (show confirmed vs false positives, severity, confidence)
  - [x] **Update `analyze_crash_data()` to accept crash events** (✅ COMPLETED - Required for enhanced analysis)
    - [x] Add `crash_events` parameter
    - [x] Pass crash events to `format_sensor_data_for_ai()`
    - [x] Update prompt to mention crash event history context
    - [x] Instruct AI to consider recent crash patterns (many false positives = pattern, recent confirmed = follow-up impact)
  - [ ] **Update `format_sensor_data_for_ai()` to include speed data** (Required for enhanced analysis)
    - [ ] Include GPS speed in sensor data context
    - [ ] Include speed change calculations (sudden deceleration)
    - [ ] Update prompt to mention speed as additional indicator
- [x] Create `device/services/fcm_service.py` (✅ Implemented - using Expo Push API)
  - [x] `FCMService` class
  - [x] Expo Push Notification API implementation (using `httpx`)
  - [x] `send_crash_notification()` method
  - [x] `send_test_notification()` method
  - [x] `_get_expo_push_token()` method (retrieves Expo Push Token from DeviceToken model)
  - [x] `_send_expo_notification()` method (handles Expo API response parsing)
  - [x] Error handling and logging
  - [x] Support for nested response format: `{"data": {"status": "ok"}}`
  - [x] Update `send_crash_notification()` to include GPS location in notification payload (✅ Added GPS to notification data)
  - [x] Add method to send notifications to loved ones with GPS location (✅ Created `notify_loved_ones_with_gps()` in crash_utils.py)

#### Routers
- [x] Create `device/router/crash_router.py` (✅ Already exists)
  - [x] `crash_router` with proper auth (DeviceAPIKeyAuth) (✅ Already configured)
  - [x] `/alert` endpoint (✅ Already implemented)
  - [x] Follow backend guide conventions (✅ Follows conventions)
- [x] Update `device/router/device_router.py` (✅ Already registered)
  - [x] Register `crash_router` in device router (✅ Already registered)
- [x] Verify router registration in `api/v1/router.py` (✅ Already registered)
- [x] Mobile router endpoints (✅ Implemented for push notifications)
  - [x] `POST /api/v1/device/mobile/fcm/token` - Register Expo Push Token
  - [x] `POST /api/v1/device/mobile/fcm/test` - Send test push notification
  - [x] Both use JWT authentication (require logged-in user)
- [x] Update `core/router/user_router.py` (✅ COMPLETED - Required for settings endpoints)
  - [x] `GET /api/v1/core/user/settings` - Get user settings (crash alert interval)
  - [x] `PUT /api/v1/core/user/settings` - Update user settings (crash alert interval)
  - [x] Both use JWT authentication (require logged-in user)
  - [x] Validate interval range (10-60 seconds)

#### Utilities
- [x] Create `device/utils/crash_utils.py` (if complex logic needed) (✅ Created with `notify_loved_ones_with_gps()`)
- [ ] Create `device/utils/sensor_data_utils.py` (if complex logic needed)

#### Storage & Configuration
- [x] **Migrate crash alert interval to backend** (✅ COMPLETED - Replace SecureStore with backend API)
  - [x] Remove SecureStore functions (`storeCrashAlertInterval`, `getStoredCrashAlertInterval`) - Note: Functions still exist but are no longer used
  - [x] Create API service functions in `services/api/user.ts`:
    - [x] `getUserSettings()` - Fetch settings from backend
    - [x] `updateUserSettings()` - Update settings via backend API
  - [x] Update `useCrashDetection` hook to fetch interval from backend (or use default)
  - [x] **Note**: Frontend still needs to respect interval for rate limiting, but value comes from backend

#### Settings & Configuration
- [x] Add Gemini API settings to `sentry/settings/config.py` (✅ Already implemented)
  - [x] `gemini_api_key` field (✅ Already exists)
  - [x] `gemini_model` field (✅ Already exists)
  - [x] `gemini_analysis_lookback_seconds` field (✅ Already exists - Note: Now dynamically calculated based on user interval)
- [x] Add Push Notification settings to `sentry/settings/config.py` (✅ Implemented)
  - [x] `expo_push_api_url` field (default: "https://exp.host/--/api/v2/push/send")
  - [x] `fcm_credentials_path` field (deprecated - kept for backward compatibility)
- [x] Add crash detection settings (✅ Implemented)
  - [x] `crash_confidence_threshold` field
  - [x] `crash_high_severity_g_force` field
  - [x] `crash_medium_severity_g_force` field
- [x] **User Settings Model** (✅ COMPLETED - Required for backend-stored interval)
  - [x] `UserSettings.crash_alert_interval_seconds` field (IntegerField, default=15)
  - [x] Validation: Must be between 10 and 60 seconds
  - [x] OneToOneField relationship with User model

### ESP32 Device Configuration

- [ ] Setup ESP32 development environment
- [ ] Install MPU6050 library
- [ ] Configure BLE
  - [ ] Set BLE service UUID
  - [ ] Set sensor data characteristic UUID
  - [ ] Configure device name (e.g., "Sentry Device")
- [ ] Implement sensor reading
  - [ ] Read MPU6050 accelerometer data
  - [ ] Calculate roll, pitch, tilt_detected
  - [ ] Format data as JSON
- [ ] Implement BLE transmission
  - [ ] Send sensor data every 2 seconds
  - [ ] Handle BLE connection/disconnection
  - [ ] Error handling for sensor read failures
- [ ] Test BLE communication with mobile app
- [ ] Optimize battery usage

### Frontend Updates (Phase 2)

#### API Services
- [x] Create `lib/api.ts` (✅ Axios instances configured)
  - [x] Core API instance (for auth and user endpoints)
  - [x] Device API instance (for device endpoints)
  - [x] Request interceptors (JWT for core/mobile, API key for device endpoints)
  - [x] Response interceptors (401 handling, token refresh)
  - [x] **API key authentication** (✅ `X-API-Key` header added for device endpoints using `EXPO_PUBLIC_DEVICE_API_KEY`)
- [x] Create `services/api/crash.ts`
  - [x] `sendCrashAlert()` function
  - [x] Request/response type definitions
  - [x] Error handling
  - [x] **Update `CrashAlertRequest` interface in `types/api.ts` to include GPS data** (✅ Added `gps_data` field)
  - [x] **Update `sendCrashAlert()` to accept GPS data parameter** (✅ Already accepts full request object with GPS)

#### State Management (TanStack Query)
- [x] Setup TanStack Query (if not done in Phase 1)
  - [x] Install `@tanstack/react-query`
  - [x] Create `lib/queryClient.ts` with proper configuration (gcTime, staleTime)
  - [x] Setup `QueryClientProvider` in `app/_layout.tsx`
- [x] Create mutation hooks in `hooks/mutations/`
  - [x] `useSendCrashAlert.ts` - Mutation for sending crash alert to backend
  - [x] Handle AI response
  - [x] Update local state based on AI confirmation
- [ ] Create query hooks in `hooks/queries/`
  - [ ] `useCrashEvents.ts` - Query crash events from API
  - [ ] `useCrashHistory.ts` - Query crash history with date filters

#### Update Crash Detection Hook
- [x] Update `hooks/useCrashDetection.ts`
  - [x] Add mutation call to send alert to backend (✅ Enabled `useSendCrashAlert` mutation)
  - [x] **Import `useDevice` hook to access `currentGPSData`** (✅ Added)
  - [x] Include GPS data from DeviceContext in crash alert request (✅ Added `gps_data: currentGPSData`)
  - [x] Include speed data in crash alert request (speed, speed_change from GPS calculations)
  - [x] Handle AI confirmation response (✅ Added onSuccess/onError handlers)
  - [x] Update UI based on AI analysis (✅ CrashAlert component updated)
  - [x] Show AI reasoning and confidence (✅ Enhanced display with color coding)
  - [x] **Rate limiting/throttling implemented** (✅ Prevents multiple API calls within configurable interval)
  - [x] **Field name transformation** (✅ Transforms camelCase `threshold_result` to snake_case for backend)
  - [x] **Configurable interval** (✅ Loads crash alert interval from storage, refreshes every 5 seconds)

#### Push Notifications (Expo Push Notification Service)
- [x] Choose approach (✅ Expo Push Notifications - chosen)
- [x] Create `services/notifications/notificationService.ts` (✅ Implemented)
  - [x] `NotificationService` class
  - [x] `requestPermissions()` function
  - [x] `getPushToken()` function (gets Expo Push Token)
  - [x] `sendLocalNotification()` function (for testing)
  - [x] `startPeriodicNotifications()` function (for testing)
  - [x] `stopPeriodicNotifications()` function (for testing)
  - [x] `setupNotificationListeners()` function
  - [x] Handle foreground/background notifications
  - [x] Error handling for missing FCM configuration (Android)
- [x] Create `hooks/useFCM.ts` (✅ Implemented)
  - [x] FCM token management hook
  - [x] Token registration with backend (`/mobile/fcm/token`)
  - [x] Notification handling hook
  - [x] Test notification functions (local and backend)
  - [x] Periodic notification testing support
- [x] Register FCM token on app startup (✅ Implemented in useFCM hook)
- [x] Handle notification tap actions (✅ Implemented in notification listeners)

#### Update UI Components
- [x] Update `components/crash/CrashAlert.tsx`
  - [x] Display AI analysis results (✅ Enhanced display with status cards)
  - [x] Show confidence score and reasoning (✅ Added confidence display with color coding)
  - [x] Display key indicators (✅ Added formatted list of indicators)
  - [x] Show processing state (✅ Added loading spinner during AI analysis)
  - [x] Show crash confirmation status (✅ Added prominent crash confirmed/false alarm display)
  - [ ] Add user feedback buttons (true/false positive) (⚠️ Optional - can be added later)
- [x] Update `app/(tabs)/settings.tsx`
  - [x] **Crash Detection settings section** (✅ Added configurable crash alert interval)
  - [x] **Update to use backend API** (✅ COMPLETED - Replace SecureStore with backend)
    - [x] Fetch interval from backend on mount (`getUserSettings()`)
    - [x] Save interval to backend on change (`updateUserSettings()`)
    - [x] Number input for interval configuration (10-60 seconds range)
    - [x] Real-time validation (show error if outside 10-60 range)
    - [x] Visual feedback (current value display, range validation, loading states)
    - [x] Error handling (revert on save failure)
  - [x] **Location Services settings section** (Optional GPS tracking)
    - [x] Request location permission toggle
    - [x] Show current permission status
    - [x] Enable/disable GPS tracking toggle
    - [x] Show GPS accuracy indicator
    - [x] Display current speed (if GPS enabled)
- [ ] Create `components/crash/CrashHistory.tsx` (optional)
  - [ ] Display crash event history
  - [ ] Filter by date range

#### TypeScript Types (Update)
- [x] Update `types/api.ts`
  - [x] `CrashAlertRequest` interface
  - [x] `CrashAlertResponse` interface
  - [x] API response types
  - [x] **Field name compatibility** (✅ Frontend uses camelCase, transforms to snake_case for backend)

### Expo Push Notifications Setup

- [x] Setup Expo Push Notifications (✅ Chosen approach)
  - [x] Configure `app.json` with Expo project ID
  - [x] Install `expo-notifications` package
  - [x] Implement notification service using Expo Push Notification Service
  - [x] Configure backend to use Expo Push API (using `httpx`)
  - [x] Add `expo_push_api_url` to backend config
  - [x] Test push notification delivery (✅ Test endpoint implemented)
- [ ] Configure FCM credentials for Android (optional - only if using EAS Build or manual setup)
  - [ ] Use EAS Build (recommended - handles FCM automatically): `npx eas build --platform android`
  - [ ] Or configure FCM credentials manually: https://docs.expo.dev/push-notifications/fcm-credentials/
  - [ ] Note: Local notifications work without FCM configuration, but push notifications require it

### Integration (Phase 2)

- [ ] Integrate Tier 1 with Tier 2
  - [ ] Connect threshold detection to backend API
  - [ ] Handle AI response in frontend
  - [ ] Update notifications based on AI confirmation
- [ ] Test complete flow: BLE → Threshold → API → AI → FCM
- [ ] Test false positive handling
- [ ] Test offline queue (if implemented)

### Phase 2 Testing

#### Backend Testing
- [ ] Unit tests for Gemini service
- [ ] Unit tests for FCM service
- [ ] Unit tests for crash controller
- [ ] Integration tests for crash alert endpoint
- [ ] Integration tests with mock Gemini responses
- [ ] Test FCM token management
- [ ] Test sensor data retrieval
- [ ] Test GPS data storage in CrashEvent
- [ ] Test GPS location in FCM notifications
- [ ] Test loved ones notification with GPS location

#### Frontend Testing (Phase 2)
- [ ] Integration tests for API calls
- [ ] Integration tests for crash detection hook with backend
- [ ] Test AI response handling
- [ ] Test FCM token registration
- [ ] Test push notification handling

#### End-to-End Testing (Phase 2)
- [ ] Test complete flow: BLE → Threshold → API → AI → FCM
- [ ] Test GPS data flow: Phone → Location Service → Client (stored) → Backend (on crash) → Loved Ones
- [ ] Test false positive scenarios (AI correctly identifies false alarms)
- [ ] Test offline handling (queue alerts when offline)
- [ ] Test BLE disconnection during crash
- [ ] Test GPS data availability (with permission and without permission scenarios)
- [ ] Test speed calculation accuracy
- [ ] Test speed-based threshold detection
- [ ] Performance testing (response times)
- [ ] Load testing (multiple simultaneous alerts)
- [ ] Test AI confirmation accuracy
- [ ] Test loved ones receive GPS location in notifications

### Documentation

- [ ] Document BLE UUIDs and configuration
- [ ] Document threshold values and tuning
- [ ] Document API endpoints
- [ ] Document environment variables
- [ ] Document ESP32 setup and configuration
- [ ] Create user guide for mobile app
- [ ] Create developer guide for extending the system

### Security & Privacy

- [x] **Implement API rate limiting for crash alert endpoint** (✅ Client-side throttling with configurable interval)
  - [x] Rate limiting prevents multiple API calls within configured interval (default: 15 seconds)
  - [x] Configurable via Settings page (1-300 seconds range)
  - [x] Stored in SecureStore for persistence
  - [x] Automatically refreshes interval setting every 5 seconds
- [ ] Secure FCM token storage
- [ ] Implement token refresh mechanism
- [ ] Encrypt sensitive sensor data (if required)
- [ ] Review GDPR/privacy compliance
- [ ] Secure BLE communication (if needed)
- [ ] Validate all API inputs
- [x] **API key authentication** (✅ Device endpoints use `X-API-Key` header with `EXPO_PUBLIC_DEVICE_API_KEY`)
- [ ] **Location permissions**: GPS tracking is optional - users can deny permission, system works without GPS
- [ ] **GPS data privacy**: GPS data only sent to backend when crash detected, not continuously transmitted

### Deployment

- [ ] Configure production environment variables
- [ ] Setup production Firebase project
- [ ] Configure production FCM credentials
- [ ] Setup database indexes
- [ ] Configure logging
- [ ] Setup monitoring and alerts
- [ ] Performance optimization
- [ ] Load testing in production-like environment

---

## Overview

This document outlines the two-tier crash detection system that combines fast client-side threshold detection with intelligent backend AI analysis using Gemini API. This approach balances speed (immediate alerts) with accuracy (AI confirmation).

---

## Architecture Overview

```
┌─────────────────┐
│  ESP32 Device   │
│  (MPU6050)      │
│                 │
│  Sends sensor   │
│  data every 2s  │
│  via Bluetooth  │
│  Low Energy     │
└────────┬────────┘
         │
         │ BLE (Bluetooth Low Energy)
         │ Sensor Data (every 2 seconds)
         ▼
┌─────────────────┐
│  React Native   │
│  Mobile App     │
│                 │
│  Tier 1:        │
│  - BLE Receive  │
│  - Threshold    │
│    Detection    │
│  - Fast Alert   │
└────────┬────────┘
         │
         │ If threshold exceeded
         │ + Sensor data
         ▼
┌─────────────────┐
│  Django Backend │
│                 │
│  Tier 2:        │
│  - Gemini AI    │
│    Analysis     │
│  - Confirmation │
└────────┬────────┘
         │
         │ Push Notification
         ▼
┌─────────────────┐
│  Firebase Cloud │
│  Messaging      │
│  (FCM)          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Mobile App     │
│  (User)         │
└─────────────────┘
```

---

## Tier 1: Client-Side Fast Threshold Detection

### Purpose
Perform immediate crash detection on the mobile app using simple threshold calculations. This provides instant alerts (<100ms) without waiting for server response.

### Implementation Location
**Frontend**: `frontend/`

### Folder Structure (Industry Standard for React Native)

```
frontend/
├── app/                          # Expo Router pages (existing)
│   ├── (tabs)/
│   └── ...
├── services/                     # Business logic & API calls
│   ├── api/
│   │   └── crash.ts              # Crash analysis endpoints
│   ├── bluetooth/                # Bluetooth Low Energy (BLE) service
│   │   ├── bleManager.ts         # BLE connection management
│   │   └── deviceScanner.ts      # Device scanning & pairing
│   ├── crash/
│   │   ├── threshold.ts          # Threshold detection logic
│   │   └── calculator.ts         # G-force, tilt calculations
│   ├── auth.service.ts           # Authentication service
│   ├── device.service.ts         # Device service
│   └── ...                       # Other services
├── hooks/                        # Custom React hooks
│   ├── mutations/                # TanStack Query mutations
│   │   └── useSendCrashAlert.ts  # Mutation for sending crash alert
│   ├── useCrashDetection.ts      # Crash detection logic hook
│   ├── useAuth.ts                # Auth hook
│   └── ...                       # Other hooks
├── utils/                        # Utility functions
│   ├── validation.ts             # Data validation
│   └── constants.ts              # App constants
├── types/                        # TypeScript types
│   ├── device.ts                 # Device data types
│   ├── crash.ts                  # Crash detection types
│   └── api.ts                    # API response types
├── context/                      # React Context for local/client state
│   ├── DeviceContext.tsx         # Device BLE connection state (local)
│   ├── CrashContext.tsx          # Crash alert UI state (local)
│   ├── AuthContext.tsx           # Auth context
│   └── ...                       # Other contexts
├── lib/                          # Library setup & configuration
│   └── queryClient.ts            # TanStack Query client setup
├── components/                   # Reusable components
│   ├── crash/
│   │   ├── CrashAlert.tsx        # Crash alert component
│   │   └── CrashIndicator.tsx    # Crash indicator component
│   ├── device/
│   │   └── SensorDisplay.tsx     # Sensor display component
│   └── ToastContainer.tsx        # Toast component
├── constants/                    # App constants (existing)
├── assets/                       # Assets (existing)
└── package.json
```

### Bluetooth Low Energy (BLE) Communication

#### Purpose
The embedded ESP32 device communicates with the mobile app via Bluetooth Low Energy (BLE). The device sends MPU6050 sensor data every 2 seconds to the client app.

#### Why BLE?
- **Low Power**: BLE is designed for battery-efficient communication
- **Range**: Suitable for helmet-to-phone communication (typically 10-30 meters)
- **ESP32 Support**: ESP32 has built-in BLE support
- **Real-time**: 2-second intervals provide near real-time monitoring without excessive battery drain

#### Implementation

**Dependencies**:
```bash
npm install react-native-ble-plx
# Note: Requires native build (npx expo prebuild && npx expo run:android)
```

**File**: `frontend/services/bluetooth/bleManager.ts`

**Note**: The BLE manager is already fully implemented using `react-native-ble-plx`. Key features:
- GPS data subscription via `GPS_DATA_CHARACTERISTIC_UUID`
- Base64 decoding for BLE data packets
- Buffer management for chunked JSON messages
- Separate callbacks for sensor data and GPS data
- Proper cleanup and subscription management

See `frontend/services/bluetooth/bleManager.ts` for the complete implementation.

**Note**: Device scanning is handled directly in `BLEManager.scanForDevices()` and connection is managed via `DeviceContext`. No separate `DeviceScanner` class is needed.

#### ESP32 BLE Configuration

The ESP32 device should be configured to:
- Advertise as "Sentry Device" or similar name
- Send sensor data every 2 seconds via BLE characteristic
- Use a consistent service UUID and characteristic UUID
- Format data as JSON: `{"ax": 0.1, "ay": 0.2, "az": 0.98, "roll": 2.3, "pitch": 1.1, "tilt_detected": false}`

**Note**: 2-second intervals provide a good balance between:
- **Real-time monitoring**: Fast enough to detect crashes quickly
- **Battery efficiency**: Not too frequent to drain device battery
- **Data volume**: Manageable amount of data to process

### State Management (Hybrid Approach)

#### Purpose
Use a hybrid approach: **TanStack Query** for server state (API data) and **React Context** for local/client state (BLE connection, UI state).

#### Why This Approach?

**TanStack Query for Server State:**
- **Automatic caching**: Reduces unnecessary API calls
- **Background refetching**: Keeps data fresh automatically
- **Optimistic updates**: Better UX for mutations
- **Error handling**: Built-in retry and error states
- **Loading states**: Automatic loading state management

**React Context for Local State:**
- **Simple**: Perfect for BLE connection status, UI state
- **No dependencies**: Built into React
- **Lightweight**: No overhead for simple state

#### Setup TanStack Query

**Installation**:
```bash
npm install @tanstack/react-query
```

**File**: `frontend/lib/queryClient.ts`

```typescript
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10, // 10 minutes (garbage collection time)
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});
```

**File**: `frontend/app/_layout.tsx` (Update)

```typescript
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/queryClient';
import { DeviceProvider } from '@/context/DeviceContext';
import { CrashProvider } from '@/context/CrashContext';

export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <DeviceProvider>
        <CrashProvider>
          {/* Your app content */}
        </CrashProvider>
      </DeviceProvider>
    </QueryClientProvider>
  );
}
```

#### TanStack Query Hooks for Server State

**File**: `frontend/hooks/queries/useCrashEvents.ts`

```typescript
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api/client';
import { CrashEvent } from '@/types/crash';

export function useCrashEvents(deviceId: string) {
  return useQuery({
    queryKey: ['crashEvents', deviceId],
    queryFn: async () => {
      const response = await apiClient.get<CrashEvent[]>(
        `/api/v1/device/${deviceId}/crash-events`
      );
      return response.data;
    },
    enabled: !!deviceId,
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}
```

**File**: `frontend/hooks/queries/useCrashHistory.ts`

```typescript
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api/client';
import { CrashEvent } from '@/types/crash';

interface UseCrashHistoryOptions {
  deviceId: string;
  startDate?: string;
  endDate?: string;
}

export function useCrashHistory(options: UseCrashHistoryOptions) {
  const { deviceId, startDate, endDate } = options;

  return useQuery({
    queryKey: ['crashHistory', deviceId, startDate, endDate],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const response = await apiClient.get<CrashEvent[]>(
        `/api/v1/device/${deviceId}/crash-history?${params.toString()}`
      );
      return response.data;
    },
    enabled: !!deviceId,
  });
}
```

#### TanStack Query Mutations

> **Note**: This is Phase 2 implementation. Not needed in Phase 1.

**File**: `frontend/hooks/mutations/useSendCrashAlert.ts` (Phase 2)

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { sendCrashAlert, CrashAlertRequest, CrashAlertResponse } from '@/services/api/crash';
import { showLocalNotification } from '@/services/fcm/notifications';

export function useSendCrashAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CrashAlertRequest) => sendCrashAlert(data),
    onSuccess: (response: CrashAlertResponse) => {
      // Invalidate crash events query to refetch
      queryClient.invalidateQueries({ queryKey: ['crashEvents'] });

      // Show notification based on AI response
      if (response.is_crash) {
        showLocalNotification({
          title: '🚨 CRASH CONFIRMED',
          body: `Severity: ${response.severity} | ${response.reasoning}`,
          data: { type: 'crash_confirmed', ...response },
        });
      } else {
        showLocalNotification({
          title: '✅ False Alarm',
          body: 'AI analysis indicates no crash occurred.',
          data: { type: 'false_positive' },
        });
      }
    },
    onError: (error) => {
      console.error('Error sending crash alert:', error);
      // Keep threshold alert active if API fails
    },
  });
}
```

**File**: `frontend/hooks/mutations/useCrashFeedback.ts`

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api/client';

interface CrashFeedbackRequest {
  crashEventId: string;
  isCrash: boolean;
  falsePositive: boolean;
  comments?: string;
}

export function useCrashFeedback() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CrashFeedbackRequest) => {
      const response = await apiClient.post(
        `/api/v1/device/events/${data.crashEventId}/feedback`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      // Invalidate queries to refetch updated data
      queryClient.invalidateQueries({ queryKey: ['crashEvents'] });
      queryClient.invalidateQueries({ queryKey: ['crashHistory'] });
    },
  });
}
```

#### React Context for Local State

**File**: `frontend/context/DeviceContext.tsx`

```typescript
import React, { createContext, useContext, useState, useCallback } from 'react';
import { SensorReading } from '@/types/device';
import { BLEManager } from '@/services/bluetooth/bleManager';

interface DeviceContextType {
  isConnected: boolean;
  currentReading: SensorReading | null;
  connect: (deviceId: string) => Promise<boolean>;
  disconnect: () => Promise<void>;
  startReceiving: () => void;
  stopReceiving: () => void;
}

const DeviceContext = createContext<DeviceContextType | undefined>(undefined);

export function DeviceProvider({ children }: { children: React.ReactNode }) {
  const [isConnected, setIsConnected] = useState(false);
  const [currentReading, setCurrentReading] = useState<SensorReading | null>(null);
  const [bleManager] = useState(() => new BLEManager());

  const connect = useCallback(async (deviceId: string) => {
    const connected = await bleManager.connect(deviceId);
    setIsConnected(connected);
    return connected;
  }, [bleManager]);

  const disconnect = useCallback(async () => {
    await bleManager.disconnect();
    setIsConnected(false);
    setCurrentReading(null);
  }, [bleManager]);

  const startReceiving = useCallback(() => {
    bleManager.setDataCallback((data: SensorReading) => {
      setCurrentReading(data);
    });
  }, [bleManager]);

  const stopReceiving = useCallback(() => {
    bleManager.setDataCallback(() => {});
  }, [bleManager]);

  return (
    <DeviceContext.Provider
      value={{
        isConnected,
        currentReading,
        connect,
        disconnect,
        startReceiving,
        stopReceiving,
      }}
    >
      {children}
    </DeviceContext.Provider>
  );
}

export function useDevice() {
  const context = useContext(DeviceContext);
  if (!context) {
    throw new Error('useDevice must be used within DeviceProvider');
  }
  return context;
}
```

**File**: `frontend/context/CrashContext.tsx`

```typescript
import React, { createContext, useContext, useState, useCallback } from 'react';
import { ThresholdResult } from '@/types/crash';

interface CrashContextType {
  lastCrashAlert: ThresholdResult | null;
  isProcessing: boolean;
  setLastCrashAlert: (alert: ThresholdResult | null) => void;
  setProcessing: (processing: boolean) => void;
}

const CrashContext = createContext<CrashContextType | undefined>(undefined);

export function CrashProvider({ children }: { children: React.ReactNode }) {
  const [lastCrashAlert, setLastCrashAlert] = useState<ThresholdResult | null>(null);
  const [isProcessing, setProcessing] = useState(false);

  return (
    <CrashContext.Provider
      value={{
        lastCrashAlert,
        isProcessing,
        setLastCrashAlert,
        setProcessing,
      }}
    >
      {children}
    </CrashContext.Provider>
  );
}

export function useCrash() {
  const context = useContext(CrashContext);
  if (!context) {
    throw new Error('useCrash must be used within CrashProvider');
  }
  return context;
}
```

**Usage Example**:

```typescript
// In any component - Using TanStack Query for server state
import { useCrashEvents } from '@/hooks/queries/useCrashEvents';
import { useSendCrashAlert } from '@/hooks/mutations/useSendCrashAlert';
import { useDevice } from '@/context/DeviceContext'; // Local state

function CrashHistoryScreen() {
  const { isConnected } = useDevice(); // Local state from Context
  const { data: crashEvents, isLoading, error } = useCrashEvents('device-123'); // Server state from Query
  const sendCrashAlert = useSendCrashAlert();

  if (isLoading) return <Text>Loading...</Text>;
  if (error) return <Text>Error loading crash events</Text>;

  return (
    <View>
      <Text>Connected: {isConnected ? 'Yes' : 'No'}</Text>
      {crashEvents?.map((event) => (
        <CrashEventCard key={event.id} event={event} />
      ))}
    </View>
  );
}
```

#### Summary

- **TanStack Query**: Use for all API calls (GET requests, mutations)
  - Crash events, crash history, device data from server
  - Automatic caching, refetching, error handling
  
- **React Context**: Use for local/client-side state
  - BLE connection status
  - Current sensor reading from BLE
  - UI state (modals, alerts)
  - Temporary state that doesn't need persistence

### Threshold Detection Logic

**File**: `frontend/services/crash/threshold.ts`

```typescript
import { SensorReading } from '@/types/device';
import { calculateGForce, calculateTilt } from './calculator';

export interface ThresholdConfig {
  gForceThreshold: number;      // Default: 8g
  tiltThreshold: number;          // Default: 90 degrees
  consecutiveTriggers: number;     // Default: 2 (reduce false positives)
}

export interface ThresholdResult {
  isTriggered: boolean;
  triggerType: 'g_force' | 'tilt' | 'both' | null;
  severity: 'low' | 'medium' | 'high';
  gForce: number;
  tilt: { roll: number; pitch: number };
  timestamp: number;
}

const DEFAULT_CONFIG: ThresholdConfig = {
  gForceThreshold: 8.0,
  tiltThreshold: 90.0,
  consecutiveTriggers: 2,
};

export class ThresholdDetector {
  private config: ThresholdConfig;
  private triggerHistory: boolean[] = [];

  constructor(config: Partial<ThresholdConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Check if sensor reading exceeds thresholds
   */
  checkThreshold(reading: SensorReading): ThresholdResult {
    const gForce = calculateGForce(reading.ax, reading.ay, reading.az);
    const tilt = calculateTilt(reading.ax, reading.ay, reading.az);
    
    const gForceExceeded = gForce >= this.config.gForceThreshold;
    const tiltExceeded = Math.abs(tilt.roll) >= this.config.tiltThreshold || 
                        Math.abs(tilt.pitch) >= this.config.tiltThreshold;

    // Track trigger history to reduce false positives
    const isTriggered = gForceExceeded || tiltExceeded;
    this.triggerHistory.push(isTriggered);
    
    // Keep only last N triggers
    if (this.triggerHistory.length > this.config.consecutiveTriggers) {
      this.triggerHistory.shift();
    }

    // Require consecutive triggers at the end of history
    const recentTriggers = this.triggerHistory.slice(-this.config.consecutiveTriggers);
    const confirmed = recentTriggers.length === this.config.consecutiveTriggers && 
                      recentTriggers.every(Boolean);

    // Determine severity
    let severity: 'low' | 'medium' | 'high' = 'low';
    if (gForce >= 15 || (gForceExceeded && tiltExceeded)) {
      severity = 'high';
    } else if (gForce >= 12 || gForceExceeded || tiltExceeded) {
      severity = 'medium';
    }

    // Determine trigger type
    let triggerType: 'g_force' | 'tilt' | 'both' | null = null;
    if (gForceExceeded && tiltExceeded) {
      triggerType = 'both';
    } else if (gForceExceeded) {
      triggerType = 'g_force';
    } else if (tiltExceeded) {
      triggerType = 'tilt';
    }

    return {
      isTriggered: confirmed,
      triggerType,
      severity,
      gForce,
      tilt,
      timestamp: Date.now(),
    };
  }

  /**
   * Reset trigger history (call after alert sent)
   */
  reset(): void {
    this.triggerHistory = [];
  }
}
```

### Calculator Utilities

**File**: `frontend/services/crash/calculator.ts`

```typescript
/**
 * Calculate total G-force from acceleration components
 * Formula: sqrt(ax² + ay² + az²)
 * 
 * Note: This assumes ESP32 sends acceleration data in m/s².
 * If ESP32 already compensates for gravity, use the result directly.
 * Otherwise, you may need to subtract gravity (9.81 m/s²) from the vertical component.
 */
export function calculateGForce(ax: number, ay: number, az: number): number {
  const totalAccel = Math.sqrt(ax * ax + ay * ay + az * az);
  // Convert to G-force (divide by 9.81 m/s²)
  return totalAccel / 9.81;
}

/**
 * Calculate tilt angles (roll and pitch) from acceleration
 */
export function calculateTilt(
  ax: number,
  ay: number,
  az: number
): { roll: number; pitch: number } {
  // Roll: rotation around X-axis
  const roll = Math.atan2(ay, az) * (180 / Math.PI);
  
  // Pitch: rotation around Y-axis
  const pitch = Math.atan2(-ax, Math.sqrt(ay * ay + az * az)) * (180 / Math.PI);
  
  return { roll, pitch };
}

/**
 * Check if tilt exceeds threshold
 */
export function isTiltExceeded(
  roll: number,
  pitch: number,
  threshold: number = 90
): boolean {
  return Math.abs(roll) >= threshold || Math.abs(pitch) >= threshold;
}

/**
 * Calculate speed from GPS coordinates (distance/time)
 * Uses haversine formula to calculate distance between two GPS points
 * 
 * @param currentLat - Current latitude
 * @param currentLon - Current longitude
 * @param previousLat - Previous latitude
 * @param previousLon - Previous longitude
 * @param timeDelta - Time difference in seconds
 * @returns Speed in m/s (null if invalid data)
 */
export function calculateSpeed(
  currentLat: number,
  currentLon: number,
  previousLat: number | null,
  previousLon: number | null,
  timeDelta: number
): number | null {
  if (!previousLat || !previousLon || timeDelta <= 0) return null;

  // Haversine formula to calculate distance in meters
  const R = 6371000; // Earth radius in meters
  const dLat = (currentLat - previousLat) * Math.PI / 180;
  const dLon = (currentLon - previousLon) * Math.PI / 180;
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(previousLat * Math.PI / 180) * Math.cos(currentLat * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c; // Distance in meters

  const speed = distance / timeDelta; // Speed in m/s
  return speed;
}

/**
 * Calculate speed change (acceleration/deceleration) from speed values
 * 
 * @param currentSpeed - Current speed in m/s
 * @param previousSpeed - Previous speed in m/s
 * @param timeDelta - Time difference in seconds
 * @returns Speed change in m/s² (negative = deceleration, positive = acceleration)
 */
export function calculateSpeedChange(
  currentSpeed: number,
  previousSpeed: number,
  timeDelta: number
): number | null {
  if (timeDelta <= 0) return null;
  return (currentSpeed - previousSpeed) / timeDelta; // Speed change in m/s²
}

/**
 * Check if speed change indicates sudden deceleration (potential crash)
 * 
 * @param speedChange - Speed change in m/s²
 * @param threshold - Threshold for sudden deceleration (default: -10 m/s²)
 * @returns True if speed change exceeds threshold (sudden deceleration)
 */
export function isSuddenDeceleration(
  speedChange: number | null,
  threshold: number = -10.0
): boolean {
  if (speedChange === null) return false;
  return speedChange <= threshold; // Negative value = deceleration
}
```

### React Hook for Crash Detection

**File**: `frontend/hooks/useCrashDetection.ts`

**Note**: The implementation includes:
- Rate limiting/throttling to prevent excessive API calls
- Field name transformation (camelCase → snake_case) for backend compatibility
- Configurable interval loaded from SecureStore
- GPS data inclusion from DeviceContext

```typescript
import { useEffect, useRef, useState } from 'react';
import { ThresholdDetector } from '@/services/crash/threshold';
import { ThresholdResult } from '@/types/crash';
import { SensorReading } from '@/types/device';
import { useDevice } from '@/context/DeviceContext';
import { useCrash } from '@/context/CrashContext';
import { useSendCrashAlert } from '@/hooks/mutations/useSendCrashAlert';
import { CRASH_DETECTION_CONFIG } from '@/utils/constants';
import { getUserSettings } from '@/services/api/user';

interface UseCrashDetectionOptions {
  enabled?: boolean;
  onThresholdExceeded?: (result: ThresholdResult) => void;
  onAIConfirmation?: (confirmed: boolean) => void;
}

/**
 * Hook for crash detection using threshold analysis.
 * 
 * Phase 1: Receives sensor data from BLE connection (every 2 seconds from ESP32 device).
 * Performs fast threshold detection (Tier 1) and logs to console.
 * 
 * Phase 2: Will send to backend for AI analysis (Tier 2) using TanStack Query mutation.
 * 
 * @param sensorData - Sensor reading from BLE (received every 2 seconds)
 * @param options - Configuration options
 */
export function useCrashDetection(
  sensorData: SensorReading | null, // Received via BLE from ESP32 (every 2 seconds)
  options: UseCrashDetectionOptions = {}
) {
  const { enabled = true, onThresholdExceeded, onAIConfirmation } = options;
  const detectorRef = useRef(new ThresholdDetector());
  const [lastResult, setLastResult] = useState<ThresholdResult | null>(null);
  const isProcessingRef = useRef(false);
  const lastAlertTimeRef = useRef<number>(0);
  const alertIntervalRef = useRef<number>(CRASH_DETECTION_CONFIG.crashAlertIntervalSeconds * 1000);
  
  // Get GPS data from DeviceContext
  const { currentGPSData } = useDevice();
  
  // Get CrashContext to store AI response
  const { setAIResponse, setProcessing } = useCrash();
  
  // Phase 2: Use TanStack Query mutation for sending crash alert
  const sendCrashAlertMutation = useSendCrashAlert();

  // Load crash alert interval from storage on mount and periodically refresh
  useEffect(() => {
    const loadInterval = async () => {
      try {
        // Fetch from backend API instead of SecureStore
        const settings = await getUserSettings();
        if (settings.crash_alert_interval_seconds) {
          alertIntervalRef.current = settings.crash_alert_interval_seconds * 1000; // Convert to milliseconds
        } else {
          // Use default if no value
          alertIntervalRef.current = CRASH_DETECTION_CONFIG.crashAlertIntervalSeconds * 1000;
        }
      } catch (error) {
        console.error('Error loading crash alert interval:', error);
        // Use default on error
        alertIntervalRef.current = CRASH_DETECTION_CONFIG.crashAlertIntervalSeconds * 1000;
      }
    };
    loadInterval();
    
    // Refresh interval every 5 seconds to pick up changes from settings
    const intervalId = setInterval(loadInterval, 5000);
    return () => clearInterval(intervalId);
  }, []);

  useEffect(() => {
    // Process each sensor reading received via BLE (every 2 seconds)
    if (!enabled || !sensorData || isProcessingRef.current) return;

    const result = detectorRef.current.checkThreshold(sensorData);

    if (result.isTriggered && !isProcessingRef.current) {
      // Rate limiting: Check if enough time has passed since last alert
      const now = Date.now();
      const timeSinceLastAlert = now - lastAlertTimeRef.current;
      
      if (timeSinceLastAlert < alertIntervalRef.current) {
        // Too soon since last alert - skip this one
        const remainingSeconds = Math.ceil((alertIntervalRef.current - timeSinceLastAlert) / 1000);
        console.log(`⏱️ Rate limited: Skipping crash alert (wait ${remainingSeconds}s more)`);
        return;
      }

      isProcessingRef.current = true;
      lastAlertTimeRef.current = now; // Update last alert time
      setLastResult(result);
      setProcessing(true);
      setAIResponse(null); // Clear previous AI response

      // Phase 1: Console log threshold exceeded
      console.log('⚠️ THRESHOLD EXCEEDED - Potential Crash Detected', {
        timestamp: new Date().toISOString(),
        severity: result.severity,
        triggerType: result.triggerType,
        gForce: result.gForce,
        tilt: result.tilt,
        sensorData: sensorData,
        gpsData: currentGPSData,
      });

      // Phase 2: Send to backend for AI analysis using TanStack Query mutation
      // Transform camelCase to snake_case for backend compatibility
      sendCrashAlertMutation.mutate(
        {
          device_id: sensorData.device_id,
          sensor_reading: sensorData,
          threshold_result: {
            is_triggered: result.isTriggered,
            trigger_type: result.triggerType,
            severity: result.severity,
            g_force: result.gForce,
            tilt: result.tilt,
            timestamp: result.timestamp,
          },
          timestamp: new Date().toISOString(),
          gps_data: currentGPSData, // Include GPS data (may be null if no fix)
        },
        {
          onSuccess: (aiResponse) => {
            // AI confirmation received
            console.log('✅ AI Analysis Complete:', {
              is_crash: aiResponse.is_crash,
              confidence: aiResponse.confidence,
              severity: aiResponse.severity,
              reasoning: aiResponse.reasoning,
            });
            // Store AI response in context
            setAIResponse(aiResponse);
            setProcessing(false);
            onAIConfirmation?.(aiResponse.is_crash);
            // Reset detector after processing
            detectorRef.current.reset();
            isProcessingRef.current = false;
          },
          onError: (error) => {
            console.error('❌ Error sending crash alert:', error);
            setProcessing(false);
            setAIResponse(null);
            // Reset detector even on error to allow future detections
            detectorRef.current.reset();
            isProcessingRef.current = false;
          },
        }
      );

      onThresholdExceeded?.(result);
    }
  }, [sensorData, enabled, onThresholdExceeded, onAIConfirmation, currentGPSData, sendCrashAlertMutation, setAIResponse, setProcessing]);

  return {
    lastResult,
    isProcessing: sendCrashAlertMutation.isPending,
    reset: () => detectorRef.current.reset(),
  };
}
```

### API Service

**File**: `frontend/services/api/crash.ts`

```typescript
import { apiClient } from './client';
import { SensorReading } from '@/types/device';
import { ThresholdResult } from '@/types/crash';

export interface CrashAlertRequest {
  device_id: string;
  sensor_reading: SensorReading;
  threshold_result: ThresholdResult;
  timestamp: string;
}

export interface CrashAlertResponse {
  is_crash: boolean;
  confidence: number;
  severity: 'low' | 'medium' | 'high';
  crash_type: string;
  reasoning: string;
  key_indicators: string[];
  false_positive_risk: number;
}

export async function sendCrashAlert(
  data: CrashAlertRequest
): Promise<CrashAlertResponse> {
  const response = await apiClient.post<CrashAlertResponse>(
    '/api/v1/device/crash/alert',
    data
  );
  return response.data;
}
```

---

## GPS Integration

### Overview

GPS location data is integrated throughout the two-tier crash detection system to provide location information and speed calculations when crashes are detected. The GPS data is collected from the phone (React Native app) using `expo-location`, not from the ESP32 device. The GPS data flow is designed to:

1. **Tier 1 (Client)**: Collect GPS data from phone, calculate speed, store locally, only sending to backend when crash is detected
2. **Tier 2 (Backend)**: Store GPS location and speed with crash events, use in AI analysis, and send to loved ones when crash confirmed

### GPS Data Flow

```
Mobile Phone (React Native App)
    │
    │ Using expo-location
    │ Request location permission (optional)
    │
    │ Continuous GPS updates
    │ Calculate speed from coordinates
    ▼
Mobile App (Tier 1 - Client)
    │
    │ Store GPS data in DeviceContext (local only)
    │ Calculate speed: distance/time between coordinates
    │ Speed-based threshold detection (optional immediate alert)
    │
    │ When crash detected (threshold exceeded)
    ▼
Backend API (Tier 2)
    │
    │ Store GPS + speed in CrashEvent
    │ AI analysis uses speed data for better accuracy
    │ If crash confirmed by AI
    ▼
Loved Ones Notification
    │
    │ FCM Push Notification with GPS location + speed
    │ (latitude, longitude, speed, map link)
    ▼
Loved Ones (Emergency Contacts)
```

### Phase 1: GPS Data Collection and Storage (Client-Side Only)

#### Location Service Implementation

**Dependencies**:
```bash
npx expo install expo-location
```

**File**: `frontend/services/location/locationService.ts`

```typescript
import * as Location from 'expo-location';

export interface GPSData {
  latitude: number | null;
  longitude: number | null;
  altitude: number | null;
  accuracy: number | null; // GPS accuracy in meters
  speed: number | null; // Speed in m/s (calculated from GPS)
  timestamp: string;
}

export class LocationService {
  private watchPositionSubscription: Location.LocationSubscription | null = null;
  private lastLocation: Location.LocationObject | null = null;
  private lastTimestamp: number = 0;
  private onLocationUpdate?: (data: GPSData) => void;

  /**
   * Request location permissions (optional - user can deny)
   */
  async requestPermissions(): Promise<boolean> {
    const { status } = await Location.requestForegroundPermissionsAsync();
    return status === 'granted';
  }

  /**
   * Check if location permissions are granted
   */
  async checkPermissions(): Promise<boolean> {
    const { status } = await Location.getForegroundPermissionsAsync();
    return status === 'granted';
  }

  /**
   * Calculate speed from GPS coordinates (distance/time)
   */
  private calculateSpeed(
    currentLocation: Location.LocationObject,
    lastLocation: Location.LocationObject | null,
    timeDelta: number
  ): number | null {
    if (!lastLocation || timeDelta <= 0) return null;

    const distance = Location.distanceBetween(
      lastLocation.coords.latitude,
      lastLocation.coords.longitude,
      currentLocation.coords.latitude,
      currentLocation.coords.longitude
    ); // Distance in meters

    const speed = distance / timeDelta; // Speed in m/s
    return speed;
  }

  /**
   * Start location tracking
   */
  async startTracking(
    onUpdate: (data: GPSData) => void,
    options: Location.LocationOptions = {}
  ): Promise<boolean> {
    const hasPermission = await this.requestPermissions();
    if (!hasPermission) {
      console.warn('Location permission denied - GPS tracking disabled');
      return false;
    }

    this.onLocationUpdate = onUpdate;

    this.watchPositionSubscription = await Location.watchPositionAsync(
      {
        accuracy: Location.Accuracy.Balanced,
        timeInterval: 1000, // Update every 1 second
        distanceInterval: 1, // Update every 1 meter
        ...options,
      },
      (location) => {
        const now = Date.now();
        const timeDelta = this.lastTimestamp > 0 
          ? (now - this.lastTimestamp) / 1000 // Convert to seconds
          : 0;

        const speed = this.calculateSpeed(location, this.lastLocation, timeDelta);

        const gpsData: GPSData = {
          latitude: location.coords.latitude,
          longitude: location.coords.longitude,
          altitude: location.coords.altitude,
          accuracy: location.coords.accuracy,
          speed: speed, // Calculated speed in m/s
          timestamp: new Date(location.timestamp).toISOString(),
        };

        this.onLocationUpdate?.(gpsData);
        this.lastLocation = location;
        this.lastTimestamp = now;
      }
    );

    return true;
  }

  /**
   * Stop location tracking
   */
  stopTracking(): void {
    if (this.watchPositionSubscription) {
      this.watchPositionSubscription.remove();
      this.watchPositionSubscription = null;
    }
    this.lastLocation = null;
    this.lastTimestamp = 0;
  }

  /**
   * Get current location (one-time)
   */
  async getCurrentLocation(): Promise<GPSData | null> {
    const hasPermission = await this.checkPermissions();
    if (!hasPermission) return null;

    try {
      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });

      return {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        altitude: location.coords.altitude,
        accuracy: location.coords.accuracy,
        speed: location.coords.speed, // Use device-reported speed if available
        timestamp: new Date(location.timestamp).toISOString(),
      };
    } catch (error) {
      console.error('Error getting current location:', error);
      return null;
    }
  }
}
```

**2. Update DeviceContext to Store GPS Data**

File: `frontend/context/DeviceContext.tsx`

```typescript
import { LocationService } from '@/services/location/locationService';

interface DeviceContextType {
  // ... existing fields
  currentGPSData: GPSData | null;
  currentSpeed: number | null; // Speed in m/s (converted to km/h for display)
  isGPSEnabled: boolean;
  hasLocationPermission: boolean;
  startGPSTracking: () => Promise<void>;
  stopGPSTracking: () => void;
}

export function DeviceProvider({ children }: { children: React.ReactNode }) {
  const [currentGPSData, setCurrentGPSData] = useState<GPSData | null>(null);
  const [currentSpeed, setCurrentSpeed] = useState<number | null>(null);
  const [isGPSEnabled, setIsGPSEnabled] = useState(false);
  const [hasLocationPermission, setHasLocationPermission] = useState(false);
  const locationServiceRef = useRef(new LocationService());

  const startGPSTracking = useCallback(async () => {
    const hasPermission = await locationServiceRef.current.checkPermissions();
    setHasLocationPermission(hasPermission);
    
    if (!hasPermission) {
      const granted = await locationServiceRef.current.requestPermissions();
      setHasLocationPermission(granted);
      if (!granted) return;
    }

    const started = await locationServiceRef.current.startTracking((data) => {
      setCurrentGPSData(data);
      setCurrentSpeed(data.speed); // Speed in m/s
      setIsGPSEnabled(true);
    });

    if (!started) {
      setIsGPSEnabled(false);
    }
  }, []);

  const stopGPSTracking = useCallback(() => {
    locationServiceRef.current.stopTracking();
    setIsGPSEnabled(false);
    setCurrentGPSData(null);
    setCurrentSpeed(null);
  }, []);

  // ... rest of implementation
}
```

**3. TypeScript Types**

File: `frontend/types/device.ts`

```typescript
export interface GPSData {
  latitude: number | null;
  longitude: number | null;
  altitude: number | null;
  accuracy: number | null; // GPS accuracy in meters
  speed: number | null; // Speed in m/s (calculated from GPS coordinates)
  timestamp: string;
}
```

**Note**: In Phase 1, GPS data is stored locally only. It is NOT sent to the backend until a crash is detected (Phase 2). GPS tracking is optional - users can deny location permission.

### Phase 2: GPS Data Transmission and Notification

#### Frontend: Include GPS and Speed in Crash Alert

**Update Crash Detection Hook**

File: `frontend/hooks/useCrashDetection.ts`

**Status**: ⚠️ **Needs implementation** - This needs to be added in Phase 2.

```typescript
import { useDevice } from '@/context/DeviceContext';
import { calculateSpeedChange } from '@/services/crash/calculator';

export function useCrashDetection(
  sensorData: SensorReading | null,
  options: UseCrashDetectionOptions = {}
) {
  const { currentGPSData, currentSpeed } = useDevice(); // Get GPS data and speed from context
  const sendCrashAlertMutation = useSendCrashAlert();
  
  // ... existing code
  
  if (result.isTriggered) {
    // Calculate speed change (sudden deceleration)
    const speedChange = currentSpeed && previousSpeed 
      ? calculateSpeedChange(currentSpeed, previousSpeed, timeDelta)
      : null;

    // Include GPS data and speed in crash alert
    sendCrashAlertMutation.mutate({
      device_id: sensorData.device_id,
      sensor_reading: sensorData,
      threshold_result: result,
      timestamp: new Date().toISOString(),
      gps_data: currentGPSData ? {
        ...currentGPSData,
        speed: currentSpeed, // Speed in m/s
        speed_change: speedChange, // Speed change in m/s²
      } : null, // GPS data is optional (may be null if permission denied or no fix)
    });
  }
}
```

**Note**: GPS data is optional. If location permission is denied or GPS is unavailable, the crash alert will still be sent without GPS data.

**Update API Types**

File: `frontend/types/api.ts`

**Status**: ⚠️ **Not yet implemented** - This needs to be added in Phase 2.

```typescript
import { GPSData } from './device';

export interface CrashAlertRequest {
  device_id: string;
  sensor_reading: SensorReading;
  threshold_result: ThresholdResult;
  timestamp: string;
  gps_data: GPSData | null; // GPS data (may be null if no fix)
}
```

**Note**: Currently, `CrashAlertRequest` doesn't include GPS data. This needs to be updated when implementing Phase 2.

#### Backend: Store GPS in CrashEvent

**1. Update CrashEvent Model**

File: `backend/sentry/device/models/crash_event.py`

**Status**: ⚠️ **Not yet implemented** - This needs to be added in Phase 2.

```python
class CrashEvent(models.Model):
    # ... existing fields
    
    # GPS Location at Crash Time
    crash_latitude = models.FloatField(null=True, blank=True)
    crash_longitude = models.FloatField(null=True, blank=True)
    crash_altitude = models.FloatField(null=True, blank=True)
    gps_accuracy_at_crash = models.FloatField(null=True, blank=True)  # GPS accuracy in meters
    
    # Speed Data at Crash Time
    speed_at_crash = models.FloatField(null=True, blank=True)  # Speed in m/s
    speed_change_at_crash = models.FloatField(null=True, blank=True)  # Speed change in m/s² (sudden deceleration)
    max_speed_before_crash = models.FloatField(null=True, blank=True)  # Maximum speed in last 30 seconds before crash (m/s)
    
    # ... rest of model
```

**Note**: Currently, `CrashEvent` model doesn't have GPS fields. These need to be added via migration in Phase 2.

**2. Update Crash Alert Schema**

File: `backend/sentry/device/schemas/crash_schema.py`

**Status**: ⚠️ **Not yet implemented** - This needs to be added in Phase 2.

```python
"""Crash detection schemas."""

from ninja import Schema

class GPSDataSchema(Schema):
    """GPS data schema."""

    latitude: float | None
    longitude: float | None
    altitude: float | None
    accuracy: float | None  # GPS accuracy in meters
    speed: float | None  # Speed in m/s (calculated from GPS)
    speed_change: float | None  # Speed change in m/s² (sudden deceleration)
    timestamp: str

class CrashAlertRequest(Schema):
    """Crash alert request schema."""

    device_id: str
    sensor_reading: SensorReadingSchema
    threshold_result: ThresholdResultSchema
    timestamp: str
    gps_data: GPSDataSchema | None = None  # Optional GPS data
```

**Note**: Currently, `CrashAlertRequest` schema doesn't include GPS data. This needs to be added in Phase 2.

**3. Update Crash Controller**

File: `backend/sentry/device/controllers/crash_controller.py`

**Status**: ⚠️ **Partially implemented** - GPS fields need to be added when GPS schema is updated.

```python
"""Crash controller."""

import logging

from core.ai.gemini_service import GeminiService
from django.db import transaction
from django.http import HttpRequest
from ninja.errors import HttpError

from device.models import CrashEvent
from device.schemas.crash_schema import CrashAlertRequest, CrashAlertResponse
from device.services.crash_detector import CrashDetectorService
from device.services.fcm_service import FCMService

logger = logging.getLogger("device")

def process_crash_alert(
    request: HttpRequest,
    data: CrashAlertRequest,
) -> CrashAlertResponse:
    """Process crash alert from mobile app (Tier 1 trigger).

    Args:
        request: The HTTP request object
        data: The crash alert request data

    Returns:
        CrashAlertResponse containing AI analysis results

    Raises:
        HttpError: If processing fails
    """
    try:
        # Initialize services
        gemini_service = GeminiService()
        crash_detector = CrashDetectorService()
        fcm_service = FCMService()
        
        # ... existing AI analysis code (retrieve sensor data, call Gemini AI)
        
        if ai_analysis["is_crash"]:
            with transaction.atomic():
                crash_event = CrashEvent.objects.create(
                    # ... existing fields
                    # GPS and speed fields
                    crash_latitude=data.gps_data.latitude if data.gps_data else None,
                    crash_longitude=data.gps_data.longitude if data.gps_data else None,
                    crash_altitude=data.gps_data.altitude if data.gps_data else None,
                    gps_accuracy_at_crash=data.gps_data.accuracy if data.gps_data else None,
                    speed_at_crash=data.gps_data.speed if data.gps_data else None,  # Speed in m/s
                    speed_change_at_crash=data.gps_data.speed_change if data.gps_data else None,  # Speed change in m/s²
                    max_speed_before_crash=None,  # Will be calculated from recent sensor data if available
                )
                
                # Send notifications to loved ones with GPS location
                if ai_analysis["severity"] in ["high", "medium"]:
                    fcm_service.send_crash_notification(
                        device_id=data.device_id,
                        crash_event=crash_event,
                        ai_analysis=ai_analysis,
                    )
                    # TODO: Send GPS location to loved ones when GPS is implemented
                    # notify_loved_ones_with_gps(device_id=data.device_id, crash_event=crash_event)
        
        return CrashAlertResponse(...)
        
    except Exception as e:
        logger.error(f"Error processing crash alert: {e}", exc_info=True)
        raise HttpError(status_code=500, message="Failed to process crash alert")
```

**Note**: The controller exists but needs GPS field updates when GPS schema is added in Phase 2.

#### Backend: Notify Loved Ones with GPS Location

**1. Update FCM Service**

File: `backend/sentry/device/services/fcm_service.py`

```python
def send_crash_notification(
    self,
    device_id: str,
    crash_event: CrashEvent,
    ai_analysis: dict,
) -> None:
    """Send crash notification with GPS location."""
    
    # Get GPS location
    gps_location = None
    if crash_event.crash_latitude and crash_event.crash_longitude:
        gps_location = {
            "latitude": crash_event.crash_latitude,
            "longitude": crash_event.crash_longitude,
            "altitude": crash_event.crash_altitude,
        }
        # Create map link (Google Maps)
        map_link = f"https://www.google.com/maps?q={crash_event.crash_latitude},{crash_event.crash_longitude}"
    else:
        map_link = None
    
    # Build notification message
    message = {
        "title": f"🚨 Crash Detected - {ai_analysis['severity'].upper()}",
        "body": f"{ai_analysis['crash_type']} - {ai_analysis['reasoning'][:100]}...",
        "data": {
            "type": "crash_confirmed",
            "crash_event_id": str(crash_event.id),
            "severity": ai_analysis["severity"],
            "gps_location": gps_location,
            "map_link": map_link,
        },
    }
    
    # Send to device owner
    # ... existing notification code
    
**Note**: The `notify_loved_ones_with_gps()` function should be placed in a utility file, not in the controller or service. Create `device/utils/crash_utils.py`:

File: `backend/sentry/device/utils/crash_utils.py`

**Status**: ⚠️ **Not yet implemented** - This needs to be created in Phase 2.

```python
"""Crash utilities."""

import logging

from device.models.crash_event import CrashEvent
from device.models.device_token import DeviceToken
from device.services.fcm_service import FCMService

logger = logging.getLogger("device")

def notify_loved_ones_with_gps(
    device_id: str,
    crash_event: CrashEvent,
) -> None:
    """Send GPS location to all active loved ones for the device owner.

    Args:
        device_id: The device ID
        crash_event: The crash event with GPS location
    """
    from core.models import LovedOne
    
    # Get device owner (user)
    user = crash_event.user
    if not user:
        logger.warning(f"No user associated with crash event {crash_event.id}")
        return
    
    # Get all active loved ones (use select_related to avoid N+1 queries)
    loved_ones = LovedOne.objects.filter(
        user=user,
        is_active=True
    ).select_related("loved_one")
    
    # Get GPS location
    if not (crash_event.crash_latitude and crash_event.crash_longitude):
        logger.warning(f"No GPS location for crash event {crash_event.id}")
        return
    
    map_link = f"https://www.google.com/maps?q={crash_event.crash_latitude},{crash_event.crash_longitude}"
    
    # Initialize FCM service
    fcm_service = FCMService()
    
    # Send notification to each loved one
    for loved_one_rel in loved_ones:
        loved_one_user = loved_one_rel.loved_one
        
        # Get loved one's device tokens
        device_tokens = DeviceToken.objects.filter(
            user=loved_one_user,
            is_active=True
        )
        
        for device_token in device_tokens:
            message = {
                "title": f"🚨 Emergency: {user.email} - Crash Detected",
                "body": f"Location: {map_link}",
                "data": {
                    "type": "loved_one_crash_alert",
                    "crash_event_id": str(crash_event.id),
                    "user_email": user.email,
                    "gps_location": {
                        "latitude": crash_event.crash_latitude,
                        "longitude": crash_event.crash_longitude,
                        "altitude": crash_event.crash_altitude,
                    },
                    "map_link": map_link,
                },
            }
            
            fcm_service._send_expo_notification(
                expo_push_token=device_token.fcm_token,
                message=message,
            )
```

**Note**: This utility function needs to be created in Phase 2. Follow BACKEND_GUIDE.md conventions:
- Place in `device/utils/crash_utils.py`
- Use `logging.getLogger("device")` for logger
- Use Google-style docstrings with Args, Returns, Raises sections

### GPS Data Storage Strategy

**Option 1: Store GPS with Sensor Data (Recommended)**
- Store GPS data and speed in `SensorData` model alongside sensor readings
- Allows historical GPS tracking and speed analysis
- Useful for AI analysis context (speed patterns, sudden deceleration)
- GPS data collected from phone (React Native app), not ESP32

**Option 2: Store GPS Only in CrashEvent**
- Store GPS and speed only when crash detected
- Simpler, less storage
- Sufficient for crash notifications and AI analysis

**Recommendation**: Use Option 1 for comprehensive tracking, but ensure GPS and speed are always included in CrashEvent for emergency notifications and AI analysis. Speed data helps AI distinguish between crashes and false positives (sudden deceleration = crash indicator).

### Testing GPS Integration

1. **Test GPS Data Collection (Phase 1)**
   - Verify location permission request works
   - Verify GPS data collected from phone using `expo-location`
   - Verify GPS data stored in DeviceContext
   - Verify speed calculation from GPS coordinates
   - Test with location permission granted and denied
   - Test with GPS fix and without fix
   - Test speed calculation accuracy

2. **Test Speed Calculation (Phase 1)**
   - Verify speed calculated correctly from GPS coordinates
   - Verify speed change (sudden deceleration) detection
   - Test speed-based threshold detection (optional)

3. **Test GPS in Crash Alert (Phase 2)**
   - Verify GPS and speed included in crash alert request
   - Verify GPS and speed stored in CrashEvent
   - Test with null GPS data (permission denied or no fix)
   - Verify AI analysis uses speed data for better accuracy

4. **Test Loved Ones Notification**
   - Verify loved ones receive GPS location and speed
   - Verify map link works correctly
   - Test with multiple loved ones

---

## Tier 2: Backend AI Analysis with Gemini

### Purpose
Perform intelligent crash analysis using Gemini AI API to confirm or deny threshold triggers, reducing false positives and providing detailed crash insights.

**Important**: All AI analysis results (both confirmed crashes and false positives) are stored in the database using the `CrashEvent` model. The `is_confirmed_crash` field distinguishes between confirmed crashes (`True`) and false positives (`False`). This approach enables:
- **Analytics**: Track false positive rates over time
- **Model Improvement**: Historical data for training/refining AI models and thresholds
- **User Feedback**: Correlate user feedback with stored false positive determinations
- **System Monitoring**: Monitor AI accuracy and system performance

### Implementation Location
**Backend**: `backend/sentry/`

### Flow

1. **Receive Threshold Alert from Mobile App**
   - Endpoint: `POST /api/v1/device/crash/alert`
   - Receives sensor data + threshold result

2. **Retrieve Recent Context**
   - Fetch last 30 seconds of sensor data from database
   - Format for Gemini AI analysis

3. **Call Gemini AI**
   - Create optimized prompt
   - Send to Gemini API
   - Parse JSON response

5. **Process AI Response**
   - Create CrashEvent for ALL AI analyses (both confirmed crashes AND false positives)
   - Set `is_confirmed_crash=True` for confirmed crashes, `False` for false positives
   - If confirmed crash → Send FCM push notification, notify loved ones
   - If false positive → Store in database for analytics/improvement (no notifications sent)

5. **Send Push Notification via FCM**
   - High severity → Immediate notification
   - Medium severity → Delayed notification
   - Low severity → Log only

### Backend Endpoint

**Note**: Following the backend guide conventions:
- Controllers contain business logic
- Services (like `FCMService`, `GeminiService`) are used for external integrations
- Complex model-specific logic should go in `utils/{model_name}_utils.py`
- Import organization: standard library → third-party → Django → local imports
- Use `Schema` from `ninja` (not `BaseModel` from `pydantic` directly)
- Use Google-style docstrings with Args, Returns, Raises sections
- Use `transaction.atomic()` for multi-step database operations
- Use `logging.getLogger("device")` for logger naming (app name, not `__name__`)
- Place utility functions in `utils/{model_name}_utils.py` files

**File**: `backend/sentry/device/controllers/crash_controller.py`

**Note**: Following BACKEND_GUIDE.md conventions:
- Import order: standard library → third-party → Django → local imports
- Use `logging.getLogger("device")` (app name, not `__name__`)
- Use Google-style docstrings with Args, Returns, Raises sections
- Use `transaction.atomic()` for multi-step database operations

```python
"""Crash controller."""

import logging

from django.db import transaction
from django.http import HttpRequest
from ninja.errors import HttpError

from core.ai.gemini_service import GeminiService
from device.models import CrashEvent
from device.schemas.crash_schema import CrashAlertRequest, CrashAlertResponse
from device.services.crash_detector import CrashDetectorService
from device.services.fcm_service import FCMService
from device.utils.crash_utils import notify_loved_ones_with_gps

logger = logging.getLogger("device")

def process_crash_alert(
    request: HttpRequest,
    data: CrashAlertRequest,
) -> CrashAlertResponse:
    """Process crash alert from mobile app (Tier 1 trigger).

    Args:
        request: The HTTP request object
        data: The crash alert request data

    Returns:
        CrashAlertResponse containing AI analysis results

    Raises:
        HttpError: If processing fails
    """
    try:
        # Initialize services
        gemini_service = GeminiService()
        crash_detector = CrashDetectorService()
        fcm_service = FCMService()
        
        # Retrieve recent sensor data (last 30 seconds)
        recent_data = crash_detector.get_recent_sensor_data(
            device_id=data.device_id,
            lookback_seconds=30
        )
        
        # Format data for Gemini AI
        formatted_data = gemini_service.format_sensor_data_for_ai(
            sensor_data=recent_data,
            current_reading=data.sensor_reading,
            include_metrics=True
        )
        
        # Call Gemini AI for analysis
        ai_analysis = gemini_service.analyze_crash_data(
            sensor_data=recent_data,
            current_reading=data.sensor_reading,
            context_seconds=30
        )
        
        # Create CrashEvent for ALL AI analyses (both confirmed crashes and false positives)
        # This allows tracking false positive rates, model improvement, and user feedback correlation
        # Use is_confirmed_crash field to distinguish confirmed crashes from false positives
        with transaction.atomic():
            crash_event = CrashEvent.objects.create(
                device_id=data.device_id,
                user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                crash_timestamp=data.timestamp,
                is_confirmed_crash=ai_analysis['is_crash'],  # False for false positives, True for confirmed crashes
                confidence_score=ai_analysis['confidence'],
                severity=ai_analysis['severity'],
                crash_type=ai_analysis['crash_type'],
                ai_reasoning=ai_analysis['reasoning'],
                key_indicators=ai_analysis['key_indicators'],
                false_positive_risk=ai_analysis['false_positive_risk'],
                max_g_force=data.threshold_result.g_force,
                impact_acceleration={
                    'ax': data.sensor_reading.ax,
                    'ay': data.sensor_reading.ay,
                    'az': data.sensor_reading.az,
                },
                final_tilt={
                    'roll': data.sensor_reading.roll,
                    'pitch': data.sensor_reading.pitch,
                },
                # GPS fields
                crash_latitude=data.gps_data.latitude if data.gps_data and data.gps_data.fix else None,
                crash_longitude=data.gps_data.longitude if data.gps_data and data.gps_data.fix else None,
                crash_altitude=data.gps_data.altitude if data.gps_data and data.gps_data.fix else None,
                gps_fix_at_crash=data.gps_data.fix if data.gps_data else False,
                satellites_at_crash=data.gps_data.satellites if data.gps_data else None,
            )
            
            # Only send FCM push notifications for CONFIRMED crashes (not false positives)
            if ai_analysis['is_crash'] and ai_analysis['severity'] in ['high', 'medium']:
                fcm_service.send_crash_notification(
                    device_id=data.device_id,
                    crash_event=crash_event,
                    ai_analysis=ai_analysis
                )
                # Send GPS location to loved ones for confirmed crashes
                notify_loved_ones_with_gps(
                    device_id=data.device_id,
                    crash_event=crash_event,
                )
        
        return CrashAlertResponse(
            is_crash=ai_analysis['is_crash'],
            confidence=ai_analysis['confidence'],
            severity=ai_analysis['severity'],
            crash_type=ai_analysis['crash_type'],
            reasoning=ai_analysis['reasoning'],
            key_indicators=ai_analysis['key_indicators'],
            false_positive_risk=ai_analysis['false_positive_risk'],
        )
        
    except Exception as e:
        logger.error(f"Error processing crash alert: {e}", exc_info=True)
        raise HttpError(status_code=500, message="Failed to process crash alert")
```

### Router

**File**: `backend/sentry/device/router/crash_router.py`

```python
"""Crash router."""

from typing import Any

from django.http import HttpRequest
from ninja import Router

from core.auth.api_key import DeviceAPIKeyAuth
from device.controllers.crash_controller import process_crash_alert
from device.schemas.crash_schema import CrashAlertRequest, CrashAlertResponse

crash_router = Router(tags=["crash"], auth=DeviceAPIKeyAuth())

@crash_router.post("/alert", response=CrashAlertResponse)
def crash_alert_endpoint(
    request: HttpRequest,
    payload: CrashAlertRequest,
) -> CrashAlertResponse:
    """Endpoint for mobile app to send threshold-triggered crash alerts.

    This is called when Tier 1 (client-side) detects threshold exceeded.
    Backend performs Tier 2 (AI analysis) and responds with confirmation.

    Args:
        request: The HTTP request object
        payload: The crash alert request payload

    Returns:
        CrashAlertResponse containing AI analysis results
    """
    return process_crash_alert(request, payload)
```

**Note**: The `crash_router` should be registered in the device router:

**File**: `backend/sentry/device/router/device_router.py` (update)

```python
"""Device router."""

from typing import Any

from django.http import HttpRequest
from ninja import Router

from core.auth.api_key import DeviceAPIKeyAuth
from device.controllers.device_controller import receive_device_data
from device.schemas import DeviceDataRequest, DeviceDataResponse
from .crash_router import crash_router

device_router = Router(tags=["device"], auth=DeviceAPIKeyAuth())

# Existing endpoint
@device_router.post("/data", response=DeviceDataResponse)
def receive_device_data_endpoint(
    request: HttpRequest,
    payload: DeviceDataRequest,
) -> DeviceDataResponse:
    """Endpoint the embedded device can POST MPU6050 data to.

    Args:
        request: The HTTP request object
        payload: The device data request payload

    Returns:
        DeviceDataResponse containing processing result
    """
    return receive_device_data(request, payload)

# Register crash router
device_router.add_router("crash", crash_router)
```

The `device_router` is already registered in `api/v1/router.py`, so the crash endpoint will be available at `/api/v1/device/crash/alert`.

---

## Firebase Cloud Messaging (FCM) Integration

### Purpose
Send push notifications to mobile app users when crashes are detected and confirmed by AI.

### Backend Setup

#### 1. Install Dependencies

```bash
pip install httpx>=0.27.0
```

#### 2. FCM Service (Using Expo Push Notification API)

**File**: `backend/sentry/device/services/fcm_service.py`

**Note**: The implementation uses Expo Push Notification Service API instead of Firebase Admin SDK directly. This approach:
- Works with Expo Push Tokens (returned by `expo-notifications` library)
- No need for Firebase Admin SDK or service account credentials
- Simpler setup for Expo-based apps
- Uses `httpx` library to make HTTP POST requests to Expo's API

Key implementation details:
- `send_crash_notification()`: Sends crash notification via Expo Push API
- `send_test_notification()`: Sends test notification for testing purposes
- `_get_expo_push_token()`: Retrieves Expo Push Token from `DeviceToken` model
- `_send_expo_notification()`: Handles HTTP POST to Expo API with proper response parsing
- Supports nested response format: `{"data": {"status": "ok", "id": "..."}}`
- Error handling with proper logging

**Dependencies**:
- `httpx` library for HTTP requests
- `DeviceToken` model (stores Expo Push Tokens in `fcm_token` field)

#### 3. Configuration

**File**: `backend/sentry/sentry/settings/config.py`

Add to the `Settings` class:
```python
# Push notification settings (Expo)
expo_push_api_url: str = Field(
    default="https://exp.host/--/api/v2/push/send",
    description="Expo Push Notification API endpoint URL",
)
# FCM settings (deprecated - using Expo Push API now)
fcm_credentials_path: str | None = Field(
    default=None,
    description="Path to Firebase service account JSON file (deprecated - not used with Expo Push API)",
)
```

**Note**: `fcm_credentials_path` is kept for backward compatibility but is not used with Expo Push API implementation.

### Frontend Setup

#### 1. Install Dependencies

```bash
cd frontend
npx expo install expo-notifications expo-device expo-constants
```

**Note**: No need for `@react-native-firebase/app` or `@react-native-firebase/messaging` when using Expo Push Notification Service.

#### 2. Notification Service

**File**: `frontend/services/notifications/notificationService.ts`

**Note**: This is implemented using `expo-notifications` library and Expo Push Notification Service.

**Implementation Notes**:
- Uses `expo-notifications` for Expo Push Token generation
- Token is sent to backend endpoint: `/api/v1/device/mobile/fcm/token`
- Backend uses Expo Push API to send notifications using the Expo Push Token
- Handles both local notifications and push notifications
- Supports periodic notifications for testing
- Error handling for missing FCM configuration on Android

**Key Methods**:
- `getPushToken()`: Gets Expo Push Token (format: `ExponentPushToken[...]`)
- `sendLocalNotification()`: Sends immediate local notification
- `startPeriodicNotifications()`: Starts periodic test notifications
- `setupNotificationListeners()`: Sets up foreground/background notification handlers

#### 3. useFCM Hook

**File**: `frontend/hooks/useFCM.ts`

**Implementation Notes**:
- Automatically registers for push notifications on mount
- Sends Expo Push Token to backend on registration
- Provides test notification functions (local and backend)
- Manages notification state (token, registration status, periodic notifications)
- Handles notification listeners setup and cleanup

#### 4. Backend Test Notification Endpoint

**File**: `backend/sentry/device/router/mobile_router.py`

**Endpoints**:
- `POST /api/v1/device/mobile/fcm/token` - Register Expo Push Token
- `POST /api/v1/device/mobile/fcm/test` - Send test push notification

**Note**: Both endpoints require JWT authentication.

#### 5. Notification Component

> **Note**: This is Phase 2 implementation. In Phase 1, use `console.log()` instead of notifications.

**Note**: Local notification functionality is implemented in `notificationService.ts` via `sendLocalNotification()` method. The `useFCM` hook provides convenient wrapper functions for testing.

#### 6. App Initialization

**File**: `frontend/app/(tabs)/home.tsx` (update)

**Note**: Push notification registration happens automatically in the `useFCM` hook when components mount. The hook:
- Registers for push notifications
- Sends token to backend
- Sets up notification listeners
- Provides test notification functions

Example usage:
```typescript
const { 
  pushToken, 
  isRegistered, 
  sendTestNotification,
  sendBackendTestNotification,
} = useFCM();
```

---

## Data Flow Summary

### Complete Flow

1. **ESP32 Device (Embedded)**
   - Reads MPU6050 sensor data (accelerometer + gyroscope)
   - Calculates roll, pitch, and tilt detection
   - Sends sensor data via **Bluetooth Low Energy (BLE)** to mobile app
   - **Transmission interval: Every 2 seconds** (good balance between real-time monitoring and battery efficiency)
   - Sensor data format: `{ax, ay, az, roll, pitch, tilt_detected, timestamp}`

2. **Mobile App (Tier 1 - Client-Side)**
   - Receives sensor data via BLE connection
   - Collects GPS data from phone using `expo-location` (optional - requires permission)
   - Calculates speed from GPS coordinates (distance/time between updates)
   - Calculates G-force: `sqrt(ax² + ay² + az²)`
   - Checks thresholds:
     - G-force ≥ 8g (configurable)
     - Tilt ≥ 90° (configurable)
     - Speed change (sudden deceleration) - optional immediate alert
   - If threshold exceeded:
     - **Phase 1**: Logs to console with threshold details (<100ms)
     - **Phase 2**: Sends alert to backend API with sensor data + GPS location + speed
   - GPS data stored locally only (not sent to backend until crash detected)
   - Continues receiving sensor data every 2 seconds
   - GPS updates continuously (every 1 second or 1 meter movement)

3. **Backend (Tier 2 - AI Analysis)**
   - Receives threshold alert from mobile app (with GPS location and speed if available)
   - Retrieves recent sensor data context (last 30 seconds from database)
   - Formats data for Gemini AI (includes sensor data, GPS location, and speed)
   - Calls Gemini AI API for intelligent analysis
     - AI considers: G-force, tilt, speed, speed change, GPS location
     - More accurate analysis with speed data (sudden deceleration = crash indicator)
  - Processes AI response (is_crash, confidence, severity, reasoning)
  - Creates CrashEvent in database for ALL AI analyses (both confirmed crashes AND false positives)
    - Uses `is_confirmed_crash` field to distinguish: `True` for confirmed crashes, `False` for false positives
    - Stores all AI analysis data (confidence, reasoning, key_indicators, false_positive_risk)
    - Includes GPS location and speed if available (both confirmed and false positive events)
    - **Benefits**: Enables tracking false positive rates, model improvement, analytics, and user feedback correlation
  - If confirmed crash (`is_confirmed_crash=True`):
    - Sends FCM push notification to mobile app (with GPS location and speed)
    - Sends GPS location and speed to all active loved ones (emergency contacts)
  - If false positive (`is_confirmed_crash=False`):
    - Event is still stored in database for analytics and improvement
    - No push notifications sent (prevents user fatigue from false alarms)

4. **Firebase Cloud Messaging (FCM)**
   - Delivers push notification to mobile app (device owner)
   - Delivers push notification to loved ones (emergency contacts)
   - App receives notification (foreground/background/quit state)
   - Notification includes: severity, crash type, AI reasoning, GPS location, map link

5. **Mobile App (User Notification)**
   - Receives FCM push notification
   - Shows enhanced alert with AI analysis details
   - User can:
     - View crash details
     - Dismiss alert
     - Send emergency SOS
     - Provide feedback (true crash / false positive)

### Timing Breakdown

- **BLE Data Transmission**: Every 2 seconds (from ESP32 to mobile app)
- **Tier 1 (Client Threshold Check)**: <100ms (immediate, on-device calculation)
- **Rate Limiting Check**: <1ms (client-side throttling prevents excessive calls)
- **Tier 2 (Backend AI Analysis)**: 1-3 seconds (Gemini API call + processing)
  - **Context Retrieval**: Varies based on user's crash alert interval
    - 10s interval: 30s sensor data, 1 crash event
    - 30s interval: 90s sensor data, 1 crash event
    - 60s interval: 180s sensor data, 3 crash events
- **FCM Delivery**: <1 second (push notification delivery)
- **Total Alert Time**: ~2-4 seconds from threshold trigger to user notification
- **Maximum Detection Latency**: ~4-6 seconds (2s data interval + 2-4s processing)
- **Minimum Interval Between Alerts**: Configurable in backend (10-60 seconds, default: 15 seconds) - prevents API spam

**Note**: The 2-second sensor data transmission interval is a good balance:
- **Fast enough** to detect crashes quickly (within 2-4 seconds)
- **Battery efficient** for ESP32 device (BLE is low power)
- **Manageable data volume** for processing and storage

**Note**: GPS data is collected from the phone continuously (every 1 second or 1 meter movement) using `expo-location`. This provides more accurate location data and enables speed calculation. GPS tracking is optional - users can deny location permission, and the system will still work with sensor data only.

---

## Configuration

### Threshold Configuration

**File**: `frontend/utils/constants.ts`

```typescript
export const CRASH_DETECTION_CONFIG = {
  gForceThreshold: 8.0,        // G-force threshold (8g)
  tiltThreshold: 90.0,         // Tilt threshold (90 degrees)
  consecutiveTriggers: 2,      // Require 2 consecutive triggers
  lookbackSeconds: 30,         // Context window for AI (30 seconds)
  crashAlertIntervalSeconds: 15, // Minimum interval between crash alert API calls (configurable)
  speedChangeThreshold: 10.0,  // Speed change threshold (m/s²) for sudden deceleration detection (optional)
  enableSpeedBasedDetection: false, // Enable speed-based threshold detection (optional)
} as const;
```

### Rate Limiting Configuration

**File**: `backend/sentry/core/models/user_settings.py`

The crash alert interval is stored in the `UserSettings` model and can be configured via the Settings page:
- **Default**: 15 seconds
- **Range**: 10-60 seconds (enforced validation)
- **Storage**: Backend database (OneToOneField with User)
- **API Endpoints**:
  - `GET /api/v1/core/user/settings` - Get user's crash alert interval
  - `PUT /api/v1/core/user/settings` - Update crash alert interval
- **Dynamic Context**: Higher interval values allow more sensor data and crash events to be analyzed:
  - **10 seconds**: 30s sensor lookback, 1 crash event
  - **30 seconds**: 90s sensor lookback, 1 crash event
  - **60 seconds**: 180s sensor lookback, 3 crash events
- **Formula**: 
  - Sensor lookback: `min(30 + (interval - 10) * 3, 180)` seconds
  - Crash events: `max(1, interval // 20)` events

**File**: `frontend/app/(tabs)/settings.tsx`

Users can configure the crash alert interval in the Settings page under "Crash Detection" section.

### API Authentication Configuration

**File**: `frontend/lib/api.ts`

Device API endpoints use API key authentication:
- **Header**: `X-API-Key`
- **Environment Variable**: `EXPO_PUBLIC_DEVICE_API_KEY`
- **Scope**: Applied to all device endpoints except `/mobile/*` (which use JWT)
- **Warning**: Shows console warning if API key is not configured

### Backend Configuration

**File**: `backend/sentry/sentry/settings/config.py`

```python
# Gemini AI
gemini_api_key: str | None = None
gemini_model: str = "gemini-pro"
gemini_analysis_lookback_seconds: int = 30  # Note: Now dynamically calculated based on user interval

# FCM
fcm_credentials_path: str | None = None

# Crash Detection
crash_confidence_threshold: float = 0.7  # Minimum confidence for alert
crash_high_severity_g_force: float = 15.0
crash_medium_severity_g_force: float = 12.0
```

**File**: `backend/sentry/core/models/user_settings.py`

```python
# User Settings Model
class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    crash_alert_interval_seconds = models.IntegerField(
        default=15,
        help_text="Minimum time between crash alert API calls (10-60 seconds)",
    )
    # Validation: 10 <= crash_alert_interval_seconds <= 60
```

**Dynamic Context Calculation**:
- **Sensor Data Lookback**: `min(30 + (interval - 10) * 3, 180)` seconds
  - 10s interval → 30s lookback
  - 30s interval → 90s lookback
  - 60s interval → 180s lookback
- **Crash Event History**: `max(1, interval // 20)` events
  - 10s interval → 1 event
  - 30s interval → 1 event
  - 60s interval → 3 events

---

## Testing Strategy

### Tier 1 Testing (Client)

1. **Unit Tests**
   - Test threshold calculations
   - Test G-force and tilt calculations
   - Test consecutive trigger logic

2. **Integration Tests**
   - Test API calls to backend (Phase 2)
   - Test console logging on threshold (Phase 1)
   - Test hook behavior

### Tier 2 Testing (Backend)

1. **Unit Tests**
   - Test Gemini service
   - Test FCM service
   - Test crash event creation

2. **Integration Tests**
   - Test full flow: alert → AI → notification
   - Test with mock Gemini responses
   - Test FCM token management

### End-to-End Testing

1. **Simulate Crash**
   - Send high G-force data from mobile app
   - **Phase 1**: Verify console log shows threshold exceeded
   - **Phase 2**: Verify backend AI analysis
   - **Phase 2**: Verify FCM push notification

2. **False Positive Testing**
   - Send normal sensor data
   - Verify no alerts triggered
   - Verify AI correctly identifies false positive

---

## Performance Considerations

### Client-Side (Tier 1)

- **CPU Usage**: Minimal (simple math calculations)
- **Battery Impact**: Low (no network calls for threshold check)
- **Memory**: Minimal (only stores recent trigger history)

### Backend (Tier 2)

- **Response Time**: 1-3 seconds (Gemini API latency)
- **Cost**: Only calls Gemini when threshold triggered (cost optimization)
- **Scalability**: Use async task queue (Celery) for high volume

### Optimization Strategies

1. **Client-Side**
   - Debounce threshold checks (check every N readings, not every reading)
   - Use Web Workers for calculations if needed
   - Cache threshold config

2. **Backend**
   - Cache recent sensor data queries
   - Use connection pooling for database
   - Batch FCM notifications if multiple devices

---

## Security Considerations

1. **API Authentication**
   - Use device API key for device endpoints
   - Use JWT for user endpoints

2. **FCM Token Security**
   - Store tokens securely in database
   - Validate tokens before sending notifications
   - Implement token refresh mechanism

3. **Data Privacy**
   - Encrypt sensitive sensor data
   - Anonymize data for AI analysis if needed
   - Comply with GDPR/privacy regulations

---

## Future Enhancements

1. **Offline Support**
   - Queue threshold alerts when offline
   - Sync when connection restored

2. **Machine Learning**
   - Train custom model on collected data
   - Improve threshold accuracy

3. **Multi-Device Support**
   - Aggregate analysis across multiple devices
   - Fleet-level insights

4. **Emergency Services Integration**
   - Auto-dial emergency services for high-severity crashes
   - Include location data

---

## Conclusion

This two-tier approach provides:
- **Speed**: Immediate alerts via client-side threshold detection
- **Accuracy**: AI confirmation reduces false positives
- **User Experience**: Fast response with intelligent analysis
- **Cost Efficiency**: Only calls Gemini API when needed

The hybrid system balances the need for immediate alerts with intelligent analysis, providing the best of both worlds.

