# Two-Tier Crash Detection Approach

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
├── src/                          # New: Source code organization
│   ├── services/                 # Business logic & API calls
│   │   ├── api/
│   │   │   ├── client.ts         # Axios/API client setup
│   │   │   ├── device.ts         # Device data endpoints
│   │   │   └── crash.ts           # Crash analysis endpoints
│   │   ├── crash/
│   │   │   ├── threshold.ts      # Threshold detection logic
│   │   │   └── calculator.ts     # G-force, tilt calculations
│   │   └── fcm/
│   │       ├── messaging.ts      # FCM service
│   │       └── notifications.ts  # Notification handling
│   ├── hooks/                    # Custom React hooks
│   │   ├── useCrashDetection.ts  # Crash detection hook
│   │   ├── useDeviceData.ts      # Device data hook
│   │   └── useFCM.ts              # FCM hook
│   ├── utils/                    # Utility functions
│   │   ├── math.ts               # Math utilities (G-force calc)
│   │   ├── validation.ts         # Data validation
│   │   └── constants.ts          # App constants
│   ├── types/                    # TypeScript types
│   │   ├── device.ts             # Device data types
│   │   ├── crash.ts               # Crash detection types
│   │   └── api.ts                 # API response types
│   ├── context/                  # React Context for local/client state
│   │   ├── DeviceContext.tsx     # Device BLE connection state (local)
│   │   └── CrashContext.tsx      # Crash alert UI state (local)
│   ├── lib/                      # Library setup & configuration
│   │   └── queryClient.ts        # TanStack Query client setup
│   ├── hooks/                    # Custom React hooks
│   │   ├── queries/              # TanStack Query hooks for server state
│   │   │   ├── useCrashEvents.ts # Query crash events from API
│   │   │   ├── useDeviceData.ts  # Query device data from API
│   │   │   └── useCrashHistory.ts
│   │   ├── mutations/            # TanStack Query mutations
│   │   │   ├── useSendCrashAlert.ts # Mutation for sending crash alert
│   │   │   └── useCrashFeedback.ts  # Mutation for user feedback
│   │   ├── useCrashDetection.ts  # Crash detection logic hook
│   │   └── useFCM.ts              # FCM hook
│   ├── services/
│   │   └── bluetooth/           # Bluetooth Low Energy (BLE) service
│   │       ├── bleManager.ts     # BLE connection management
│   │       └── deviceScanner.ts  # Device scanning & pairing
│   └── components/               # Reusable components
│       ├── crash/
│       │   ├── CrashAlert.tsx    # Crash alert component
│       │   └── CrashIndicator.tsx
│       └── device/
│           └── SensorDisplay.tsx
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
npm install react-native-ble-manager
# or for Expo
npx expo install expo-bluetooth
```

**File**: `frontend/src/services/bluetooth/bleManager.ts`

```typescript
import { BleManager, Device, Characteristic } from 'react-native-ble-manager';
import { SensorReading } from '@/types/device';

export interface BLEDevice {
  id: string;
  name: string;
  rssi: number;
  connected: boolean;
}

// ESP32 BLE Service UUID (configure in ESP32 code)
const SENTRY_SERVICE_UUID = '12345678-1234-1234-1234-123456789abc';
const SENSOR_DATA_CHARACTERISTIC_UUID = '12345678-1234-1234-1234-123456789abd';

export class BLEManager {
  private manager: BleManager;
  private connectedDevice: Device | null = null;
  private onDataReceived?: (data: SensorReading) => void;

  constructor() {
    this.manager = new BleManager();
  }

  /**
   * Initialize BLE manager
   */
  async initialize(): Promise<void> {
    await this.manager.start({ showAlert: false });
  }

  /**
   * Scan for ESP32 devices
   */
  async scanForDevices(): Promise<BLEDevice[]> {
    await this.manager.scan([], 5, true); // Scan for 5 seconds
    
    return new Promise((resolve) => {
      const devices: BLEDevice[] = [];
      
      this.manager.addListener('BleManagerDiscoverPeripheral', (device: Device) => {
        // Filter for Sentry devices (check name or service UUID)
        if (device.name?.includes('Sentry') || device.advertising?.serviceUUIDs?.includes(SENTRY_SERVICE_UUID)) {
          devices.push({
            id: device.id,
            name: device.name || 'Unknown Device',
            rssi: device.rssi || 0,
            connected: false,
          });
        }
      });

      setTimeout(() => {
        this.manager.stopScan();
        resolve(devices);
      }, 5000);
    });
  }

  /**
   * Connect to ESP32 device
   */
  async connect(deviceId: string): Promise<boolean> {
    try {
      await this.manager.connect(deviceId);
      await this.manager.retrieveServices(deviceId);
      
      // Subscribe to sensor data characteristic
      await this.manager.startNotification(
        deviceId,
        SENTRY_SERVICE_UUID,
        SENSOR_DATA_CHARACTERISTIC_UUID
      );

      // Listen for data updates
      this.manager.addListener(
        'BleManagerDidUpdateValueForCharacteristic',
        ({ value }: { value: number[] }) => {
          const sensorData = this.parseSensorData(value);
          this.onDataReceived?.(sensorData);
        }
      );

      this.connectedDevice = { id: deviceId } as Device;
      return true;
    } catch (error) {
      console.error('BLE connection error:', error);
      return false;
    }
  }

  /**
   * Disconnect from device
   */
  async disconnect(): Promise<void> {
    if (this.connectedDevice) {
      await this.manager.stopNotification(
        this.connectedDevice.id,
        SENTRY_SERVICE_UUID,
        SENSOR_DATA_CHARACTERISTIC_UUID
      );
      await this.manager.disconnect(this.connectedDevice.id);
      this.connectedDevice = null;
    }
  }

  /**
   * Set callback for received sensor data
   */
  setDataCallback(callback: (data: SensorReading) => void): void {
    this.onDataReceived = callback;
  }

  /**
   * Parse BLE data to SensorReading format
   * ESP32 sends data as: {ax, ay, az, roll, pitch, tilt_detected, timestamp}
   */
  private parseSensorData(value: number[]): SensorReading {
    // Convert byte array to sensor reading
    // Format depends on ESP32 implementation
    // Example: JSON string or binary format
    const dataString = String.fromCharCode(...value);
    const data = JSON.parse(dataString);
    
    return {
      device_id: this.connectedDevice?.id || 'unknown',
      ax: data.ax,
      ay: data.ay,
      az: data.az,
      roll: data.roll,
      pitch: data.pitch,
      tilt_detected: data.tilt_detected || false,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Check if device is connected
   */
  isConnected(): boolean {
    return this.connectedDevice !== null;
  }
}
```

**File**: `frontend/src/services/bluetooth/deviceScanner.ts`

```typescript
import { BLEManager, BLEDevice } from './bleManager';

export class DeviceScanner {
  private bleManager: BLEManager;

  constructor() {
    this.bleManager = new BLEManager();
  }

  /**
   * Scan and connect to Sentry device
   */
  async scanAndConnect(): Promise<BLEDevice | null> {
    await this.bleManager.initialize();
    const devices = await this.bleManager.scanForDevices();
    
    if (devices.length > 0) {
      // Connect to first found device (or let user choose)
      const device = devices[0];
      const connected = await this.bleManager.connect(device.id);
      
      if (connected) {
        return { ...device, connected: true };
      }
    }
    
    return null;
  }

  /**
   * Get BLE manager instance
   */
  getBLEManager(): BLEManager {
    return this.bleManager;
  }
}
```

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

**File**: `frontend/src/lib/queryClient.ts`

```typescript
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 10, // 10 minutes
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

**File**: `frontend/src/hooks/queries/useCrashEvents.ts`

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

**File**: `frontend/src/hooks/queries/useCrashHistory.ts`

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

**File**: `frontend/src/hooks/mutations/useSendCrashAlert.ts`

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

**File**: `frontend/src/hooks/mutations/useCrashFeedback.ts`

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

**File**: `frontend/src/context/DeviceContext.tsx`

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

**File**: `frontend/src/context/CrashContext.tsx`

```typescript
import React, { createContext, useContext, useState, useCallback } from 'react';
import { ThresholdResult } from '@/services/crash/threshold';

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

**File**: `frontend/src/services/crash/threshold.ts`

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

    // Require consecutive triggers
    const consecutiveCount = this.triggerHistory.filter(Boolean).length;
    const confirmed = consecutiveCount >= this.config.consecutiveTriggers;

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

**File**: `frontend/src/services/crash/calculator.ts`

```typescript
/**
 * Calculate total G-force from acceleration components
 * Formula: sqrt(ax² + ay² + az²)
 */
export function calculateGForce(ax: number, ay: number, az: number): number {
  return Math.sqrt(ax * ax + ay * ay + az * az);
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
```

### React Hook for Crash Detection

**File**: `frontend/src/hooks/useCrashDetection.ts`

```typescript
import { useEffect, useRef, useState } from 'react';
import { ThresholdDetector, ThresholdResult } from '@/services/crash/threshold';
import { SensorReading } from '@/types/device';
import { useSendCrashAlert } from '@/hooks/mutations/useSendCrashAlert';
import { showLocalNotification } from '@/services/fcm/notifications';

interface UseCrashDetectionOptions {
  enabled?: boolean;
  onThresholdExceeded?: (result: ThresholdResult) => void;
  onAIConfirmation?: (confirmed: boolean) => void;
}

/**
 * Hook for crash detection using threshold analysis.
 * 
 * Receives sensor data from BLE connection (every 2 seconds from ESP32 device).
 * Performs fast threshold detection (Tier 1) and sends to backend for AI analysis (Tier 2).
 * Uses TanStack Query mutation for server state management.
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
  
  // Use TanStack Query mutation for sending crash alert
  const sendCrashAlertMutation = useSendCrashAlert();

  useEffect(() => {
    // Process each sensor reading received via BLE (every 2 seconds)
    if (!enabled || !sensorData || sendCrashAlertMutation.isPending) return;

    const result = detectorRef.current.checkThreshold(sensorData);

    if (result.isTriggered) {
      setLastResult(result);

      // Immediate local alert
      showLocalNotification({
        title: '⚠️ Potential Crash Detected',
        body: 'Analyzing with AI...',
        data: { type: 'crash_detected', severity: result.severity },
      });

      // Send to backend for AI analysis using TanStack Query mutation
      sendCrashAlertMutation.mutate(
        {
          device_id: sensorData.device_id,
          sensor_reading: sensorData,
          threshold_result: result,
          timestamp: new Date().toISOString(),
        },
        {
          onSuccess: (aiResponse) => {
            // AI confirmation received
            onAIConfirmation?.(aiResponse.is_crash);
            
            // Notifications are handled in useSendCrashAlert mutation
            // (see hooks/mutations/useSendCrashAlert.ts)
            
            // Reset detector after processing
            detectorRef.current.reset();
          },
          onError: (error) => {
            console.error('Error sending crash alert:', error);
            // Keep threshold alert active if AI fails
            detectorRef.current.reset();
          },
        }
      );

      onThresholdExceeded?.(result);
    }
  }, [sensorData, enabled, sendCrashAlertMutation, onThresholdExceeded, onAIConfirmation]);

  return {
    lastResult,
    isProcessing: sendCrashAlertMutation.isPending,
    reset: () => detectorRef.current.reset(),
  };
}
```

### API Service

**File**: `frontend/src/services/api/crash.ts`

```typescript
import { apiClient } from './client';
import { SensorReading } from '@/types/device';
import { ThresholdResult } from '@/services/crash/threshold';

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

## Tier 2: Backend AI Analysis with Gemini

### Purpose
Perform intelligent crash analysis using Gemini AI API to confirm or deny threshold triggers, reducing false positives and providing detailed crash insights.

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

4. **Process AI Response**
   - If confirmed crash → Create CrashEvent, send FCM push notification
   - If false positive → Log for learning, optionally notify user

5. **Send Push Notification via FCM**
   - High severity → Immediate notification
   - Medium severity → Delayed notification
   - Low severity → Log only

### Backend Endpoint

**File**: `backend/sentry/device/controllers/crash_controller.py`

```python
from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError
from device.schemas.crash_schema import CrashAlertRequest, CrashAlertResponse
from device.services.crash_detector import CrashDetectorService
from device.services.fcm_service import FCMService
from device.models.crash_event import CrashEvent
from core.ai.gemini_service import GeminiService
import logging

logger = logging.getLogger(__name__)

def process_crash_alert(
    request: HttpRequest,
    data: CrashAlertRequest,
) -> CrashAlertResponse:
    """Process crash alert from mobile app (Tier 1 trigger).
    
    Flow:
    1. Receive threshold alert from mobile app
    2. Retrieve recent sensor data context
    3. Call Gemini AI for analysis
    4. Create CrashEvent if confirmed
    5. Send FCM push notification
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
        
        # Create CrashEvent if confirmed
        crash_event = None
        if ai_analysis['is_crash']:
            crash_event = CrashEvent.objects.create(
                device_id=data.device_id,
                user=request.user if hasattr(request, 'user') else None,
                crash_timestamp=data.timestamp,
                is_confirmed_crash=True,
                confidence_score=ai_analysis['confidence'],
                severity=ai_analysis['severity'],
                crash_type=ai_analysis['crash_type'],
                ai_reasoning=ai_analysis['reasoning'],
                key_indicators=ai_analysis['key_indicators'],
                false_positive_risk=ai_analysis['false_positive_risk'],
                max_g_force=data.threshold_result['gForce'],
                impact_acceleration={
                    'ax': data.sensor_reading['ax'],
                    'ay': data.sensor_reading['ay'],
                    'az': data.sensor_reading['az'],
                },
                final_tilt=data.threshold_result['tilt'],
            )
            
            # Send FCM push notification
            if ai_analysis['severity'] in ['high', 'medium']:
                fcm_service.send_crash_notification(
                    device_id=data.device_id,
                    crash_event=crash_event,
                    ai_analysis=ai_analysis
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
from ninja import Router
from django.http import HttpRequest
from device.controllers.crash_controller import process_crash_alert
from device.schemas.crash_schema import CrashAlertRequest, CrashAlertResponse
from device.auth import DeviceAPIKeyAuth

crash_router = Router(tags=["crash"], auth=DeviceAPIKeyAuth())

@crash_router.post("/alert", response=CrashAlertResponse)
def crash_alert_endpoint(
    request: HttpRequest,
    payload: CrashAlertRequest,
) -> CrashAlertResponse:
    """Endpoint for mobile app to send threshold-triggered crash alerts.
    
    This is called when Tier 1 (client-side) detects threshold exceeded.
    Backend performs Tier 2 (AI analysis) and responds with confirmation.
    """
    return process_crash_alert(request, payload)
```

---

## Firebase Cloud Messaging (FCM) Integration

### Purpose
Send push notifications to mobile app users when crashes are detected and confirmed by AI.

### Backend Setup

#### 1. Install Dependencies

```bash
pip install firebase-admin>=6.0.0
```

#### 2. FCM Service

**File**: `backend/sentry/device/services/fcm_service.py`

```python
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from device.models.crash_event import CrashEvent
import logging

logger = logging.getLogger(__name__)

class FCMService:
    """Firebase Cloud Messaging service for push notifications."""
    
    def __init__(self):
        if not firebase_admin._apps:
            # Initialize Firebase Admin SDK
            cred_path = getattr(settings, 'FCM_CREDENTIALS_PATH', None)
            if cred_path:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Use default credentials (for production)
                firebase_admin.initialize_app()
    
    def send_crash_notification(
        self,
        device_id: str,
        crash_event: CrashEvent,
        ai_analysis: dict,
    ) -> bool:
        """Send crash notification to user's mobile device.
        
        Args:
            device_id: Device identifier
            crash_event: CrashEvent model instance
            ai_analysis: AI analysis results from Gemini
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            # Get FCM token for device/user
            # TODO: Implement device token storage/retrieval
            fcm_token = self._get_fcm_token(device_id)
            if not fcm_token:
                logger.warning(f"No FCM token found for device {device_id}")
                return False
            
            # Build notification message
            message = messaging.Message(
                notification=messaging.Notification(
                    title="🚨 Crash Detected",
                    body=f"Severity: {ai_analysis['severity'].upper()} | {ai_analysis['reasoning'][:100]}",
                ),
                data={
                    'type': 'crash_detected',
                    'crash_event_id': str(crash_event.id),
                    'severity': ai_analysis['severity'],
                    'confidence': str(ai_analysis['confidence']),
                    'crash_type': ai_analysis['crash_type'],
                    'timestamp': crash_event.crash_timestamp.isoformat(),
                },
                token=fcm_token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        channel_id='crash_alerts',
                        sound='default',
                        priority='max',
                    ),
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1,
                            content_available=True,
                        ),
                    ),
                ),
            )
            
            # Send notification
            response = messaging.send(message)
            logger.info(f"FCM notification sent: {response}")
            
            # Update crash event
            crash_event.alert_sent = True
            crash_event.save(update_fields=['alert_sent'])
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending FCM notification: {e}", exc_info=True)
            return False
    
    def _get_fcm_token(self, device_id: str) -> str | None:
        """Get FCM token for device.
        
        TODO: Implement device token storage model.
        For now, return None (placeholder).
        """
        # Example: DeviceToken.objects.get(device_id=device_id).fcm_token
        return None
```

#### 3. Configuration

**File**: `backend/sentry/sentry/settings/config.py`

Add:
```python
fcm_credentials_path: str | None = Field(
    default=None,
    description="Path to Firebase service account JSON file",
)
```

### Frontend Setup

#### 1. Install Dependencies

```bash
cd frontend
npx expo install expo-notifications
npm install @react-native-firebase/app @react-native-firebase/messaging
```

#### 2. FCM Service

**File**: `frontend/src/services/fcm/messaging.ts`

```typescript
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import { apiClient } from '@/services/api/client';

// Configure notification handler
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export interface FCMToken {
  token: string;
  device_id: string;
}

/**
 * Register device for push notifications
 */
export async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) {
    console.warn('Must use physical device for Push Notifications');
    return null;
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    console.warn('Failed to get push token for push notification!');
    return null;
  }

  const tokenData = await Notifications.getExpoPushTokenAsync({
    projectId: 'your-expo-project-id', // Get from app.json or env
  });

  const token = tokenData.data;
  
  // Send token to backend
  await saveFCMToken(token);

  return token;
}

/**
 * Save FCM token to backend
 */
async function saveFCMToken(token: string): Promise<void> {
  try {
    await apiClient.post('/api/v1/device/fcm/token', {
      token,
      device_id: await getDeviceId(),
      platform: Platform.OS,
    });
  } catch (error) {
    console.error('Error saving FCM token:', error);
  }
}

/**
 * Get device ID (implement based on your device identification logic)
 */
async function getDeviceId(): Promise<string> {
  // TODO: Implement device ID retrieval
  // Could use expo-device, or store in AsyncStorage
  return 'device-id-placeholder';
}

/**
 * Setup notification listeners
 */
export function setupNotificationListeners(
  onNotificationReceived: (notification: Notifications.Notification) => void
): () => void {
  // Foreground notifications
  const foregroundSubscription = Notifications.addNotificationReceivedListener(
    onNotificationReceived
  );

  // Background/quit state notifications
  const responseSubscription = Notifications.addNotificationResponseReceivedListener(
    (response) => {
      const data = response.notification.request.content.data;
      if (data?.type === 'crash_detected') {
        // Navigate to crash details screen
        // navigation.navigate('CrashDetails', { crashEventId: data.crash_event_id });
      }
    }
  );

  // Cleanup function
  return () => {
    foregroundSubscription.remove();
    responseSubscription.remove();
  };
}
```

#### 3. Notification Component

**File**: `frontend/src/services/fcm/notifications.ts`

```typescript
import * as Notifications from 'expo-notifications';

export interface NotificationOptions {
  title: string;
  body: string;
  data?: Record<string, any>;
  sound?: boolean;
}

/**
 * Show local notification
 */
export async function showLocalNotification(
  options: NotificationOptions
): Promise<void> {
  await Notifications.scheduleNotificationAsync({
    content: {
      title: options.title,
      body: options.body,
      data: options.data,
      sound: options.sound ?? true,
    },
    trigger: null, // Show immediately
  });
}
```

#### 4. App Initialization

**File**: `frontend/app/_layout.tsx` (update)

```typescript
import { useEffect } from 'react';
import { registerForPushNotifications, setupNotificationListeners } from '@/services/fcm/messaging';

export default function RootLayout() {
  useEffect(() => {
    // Register for push notifications on app start
    registerForPushNotifications();

    // Setup notification listeners
    const cleanup = setupNotificationListeners((notification) => {
      console.log('Notification received:', notification);
      // Handle notification
    });

    return cleanup;
  }, []);

  // ... rest of layout
}
```

---

## Data Flow Summary

### Complete Flow

1. **ESP32 Device (Embedded)**
   - Reads MPU6050 sensor data (accelerometer + gyroscope)
   - Calculates roll, pitch, and tilt detection
   - Sends sensor data via **Bluetooth Low Energy (BLE)** to mobile app
   - **Transmission interval: Every 2 seconds** (good balance between real-time monitoring and battery efficiency)
   - Data format: `{ax, ay, az, roll, pitch, tilt_detected, timestamp}`

2. **Mobile App (Tier 1 - Client-Side)**
   - Receives sensor data via BLE connection
   - Calculates G-force: `sqrt(ax² + ay² + az²)`
   - Checks thresholds:
     - G-force ≥ 8g (configurable)
     - Tilt ≥ 90° (configurable)
   - If threshold exceeded:
     - Shows **immediate local notification** (<100ms)
     - Sends alert to backend API with sensor data
   - Continues receiving data every 2 seconds

3. **Backend (Tier 2 - AI Analysis)**
   - Receives threshold alert from mobile app
   - Retrieves recent sensor data context (last 30 seconds from database)
   - Formats data for Gemini AI
   - Calls Gemini AI API for intelligent analysis
   - Processes AI response (is_crash, confidence, severity, reasoning)
   - If confirmed crash:
     - Creates CrashEvent in database
     - Sends FCM push notification to mobile app
   - If false positive:
     - Logs for learning/improvement
     - Optionally notifies user of false alarm

4. **Firebase Cloud Messaging (FCM)**
   - Delivers push notification to mobile app
   - App receives notification (foreground/background/quit state)
   - Notification includes: severity, crash type, AI reasoning

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
- **Tier 2 (Backend AI Analysis)**: 1-3 seconds (Gemini API call + processing)
- **FCM Delivery**: <1 second (push notification delivery)
- **Total Alert Time**: ~2-4 seconds from threshold trigger to user notification
- **Maximum Detection Latency**: ~4-6 seconds (2s data interval + 2-4s processing)

**Note**: The 2-second data transmission interval is a good balance:
- **Fast enough** to detect crashes quickly (within 2-4 seconds)
- **Battery efficient** for ESP32 device (BLE is low power)
- **Manageable data volume** for processing and storage

---

## Configuration

### Threshold Configuration

**File**: `frontend/src/utils/constants.ts`

```typescript
export const CRASH_DETECTION_CONFIG = {
  gForceThreshold: 8.0,        // G-force threshold (8g)
  tiltThreshold: 90.0,         // Tilt threshold (90 degrees)
  consecutiveTriggers: 2,      // Require 2 consecutive triggers
  lookbackSeconds: 30,         // Context window for AI (30 seconds)
} as const;
```

### Backend Configuration

**File**: `backend/sentry/sentry/settings/config.py`

```python
# Gemini AI
gemini_api_key: str | None = None
gemini_model: str = "gemini-pro"
gemini_analysis_lookback_seconds: int = 30

# FCM
fcm_credentials_path: str | None = None

# Crash Detection
crash_confidence_threshold: float = 0.7  # Minimum confidence for alert
crash_high_severity_g_force: float = 15.0
crash_medium_severity_g_force: float = 12.0
```

---

## Testing Strategy

### Tier 1 Testing (Client)

1. **Unit Tests**
   - Test threshold calculations
   - Test G-force and tilt calculations
   - Test consecutive trigger logic

2. **Integration Tests**
   - Test API calls to backend
   - Test local notifications
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
   - Verify immediate local notification
   - Verify backend AI analysis
   - Verify FCM push notification

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

## Implementation Checklist

### Frontend
- [ ] Create folder structure (`src/services`, `src/hooks`, `src/context`, `src/lib`, etc.)
- [ ] Setup TanStack Query
  - [ ] Install `@tanstack/react-query`
  - [ ] Create query client configuration
  - [ ] Setup QueryClientProvider in app root
  - [ ] Create query hooks (`useCrashEvents`, `useCrashHistory`)
  - [ ] Create mutation hooks (`useSendCrashAlert`, `useCrashFeedback`)
- [ ] Setup Bluetooth Low Energy (BLE) service
  - [ ] Install BLE library (`react-native-ble-manager` or `expo-bluetooth`)
  - [ ] Implement BLE manager for ESP32 connection
  - [ ] Implement device scanner and pairing
  - [ ] Configure data reception (every 2 seconds)
- [ ] Implement React Context for local state management
  - [ ] Create DeviceContext for BLE connection state (local)
  - [ ] Create CrashContext for crash alert UI state (local)
- [ ] Implement threshold detection logic
- [ ] Implement calculator utilities (G-force, tilt)
- [ ] Create `useCrashDetection` hook (using TanStack Query mutation)
- [ ] Setup FCM service
- [ ] Create notification components
- [ ] Integrate BLE data flow with crash detection
- [ ] Integrate with existing app

### Backend
- [ ] Create crash alert endpoint
- [ ] Implement Gemini AI integration
- [ ] Create CrashEvent model
- [ ] Setup FCM service
- [ ] Implement device token storage
- [ ] Add async task processing (optional)

### Configuration
- [ ] Setup Firebase project
- [ ] Download service account JSON
- [ ] Configure FCM credentials
- [ ] Setup Expo push notifications
- [ ] Configure threshold values
- [ ] Configure ESP32 BLE
  - [ ] Set BLE service UUID and characteristic UUID
  - [ ] Configure data transmission interval (2 seconds)
  - [ ] Format sensor data as JSON
  - [ ] Test BLE connection with mobile app

### Testing
- [ ] Unit tests for threshold logic
- [ ] Integration tests for API
- [ ] End-to-end crash simulation
- [ ] Performance testing

---

## Conclusion

This two-tier approach provides:
- **Speed**: Immediate alerts via client-side threshold detection
- **Accuracy**: AI confirmation reduces false positives
- **User Experience**: Fast response with intelligent analysis
- **Cost Efficiency**: Only calls Gemini API when needed

The hybrid system balances the need for immediate alerts with intelligent analysis, providing the best of both worlds.

