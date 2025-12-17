# Bluetooth Management Strategy: Client ↔ Device Communication

## Overview

This document outlines the recommended approach for managing bidirectional Bluetooth Low Energy (BLE) communication between the React Native mobile app (client) and the ESP32 embedded device.

## Architecture

### Communication Flow

```
┌─────────────────┐                    ┌─────────────────┐
│  Mobile App     │                    │  ESP32 Device   │
│  (React Native) │                    │                 │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         │         BLE Connection               │
         │◄────────────────────────────────────►│
         │                                      │
         │  Sensor Data (Notifications)         │
         │◄─────────────────────────────────────│
         │  Every 2 seconds                     │
         │  {ax, ay, az, roll, pitch, tilt}    │
         │                                      │
         │  Commands (Write)                    │
         │─────────────────────────────────────►│
         │  WiFi config, settings, etc.         │
         │                                      │
```

## Communication Patterns

### 1. **Sensor Data: ESP32 → Mobile App (Read/Notify)**

**Pattern**: ESP32 sends sensor data via BLE Characteristic Notifications
- **Frequency**: Every 2 seconds
- **Direction**: Device → Client (one-way, initiated by device)
- **Method**: Subscribe to characteristic notifications

**Implementation**:
```typescript
// Client subscribes to sensor data characteristic
await bleManager.startNotification(
  deviceId,
  SENSOR_SERVICE_UUID,
  SENSOR_DATA_CHARACTERISTIC_UUID
);

// Device pushes data every 2 seconds via BLE notification
// Client receives via notification listener
```

**Data Format**:
```json
{
  "ax": 0.1,
  "ay": 0.2,
  "az": 9.81,
  "roll": 2.3,
  "pitch": 1.1,
  "tilt_detected": false,
  "timestamp": "2025-12-17T10:30:00Z"
}
```

### 2. **Commands: Mobile App → ESP32 (Write)**

**Pattern**: Mobile app writes commands/configuration via BLE Characteristic Write
- **Frequency**: On-demand (user-initiated)
- **Direction**: Client → Device (one-way, initiated by client)
- **Method**: Write to characteristic

**Use Cases**:
- WiFi configuration (SSID + password)
- Device settings (thresholds, sampling rate)
- Device control (reset, calibration)
- OTA updates (firmware)

**Implementation**:
```typescript
// Client writes WiFi credentials
await bleManager.write(
  deviceId,
  CONFIG_SERVICE_UUID,
  WIFI_CONFIG_CHARACTERISTIC_UUID,
  JSON.stringify({
    ssid: "MyWiFi",
    password: "password123"
  })
);
```

## Recommended BLE Service Structure

### ESP32 BLE Services & Characteristics

```
Sentry Device (BLE Peripheral)
├── Service 1: Sensor Data Service (UUID: SENSOR_SERVICE_UUID)
│   ├── Characteristic: Sensor Data (Notify, Read)
│   │   └── Sends sensor readings every 2 seconds
│   └── Characteristic: Sensor Config (Write, Read)
│       └── Configure sensor sampling rate, thresholds
│
├── Service 2: Configuration Service (UUID: CONFIG_SERVICE_UUID)
│   ├── Characteristic: WiFi Config (Write)
│   │   └── Send WiFi SSID + password
│   ├── Characteristic: Device Settings (Write, Read)
│   │   └── Device name, thresholds, etc.
│   └── Characteristic: Device Status (Notify, Read)
│       └── Device connection status, WiFi status, etc.
│
└── Service 3: Device Control Service (UUID: CONTROL_SERVICE_UUID)
    ├── Characteristic: Commands (Write)
    │   └── Reset, calibrate, OTA update commands
    └── Characteristic: Command Response (Notify, Read)
        └── Response/acknowledgment for commands
```

## Implementation Strategy

### Phase 1: Basic Communication (Current)

1. **ESP32 → Mobile**: Sensor data notifications (every 2 seconds)
   - Implemented via BLE characteristic notifications
   - Mobile app subscribes and receives data

2. **Mobile → ESP32**: WiFi configuration (on-demand)
   - Implemented via BLE characteristic write
   - Send WiFi SSID + password when user submits form

### Phase 2: Enhanced Communication (Future)

1. **Bidirectional Status Updates**
   - Device sends connection status, WiFi connection status
   - Mobile app can query device status on demand

2. **Command-Response Pattern**
   - Mobile app sends command via Write
   - Device responds via Notification or Read
   - Acknowledge successful WiFi connection, etc.

## Code Structure Recommendations

### Current Structure (Good Foundation)

```
frontend/
├── services/
│   └── bluetooth/
│       ├── bleManager.ts          # Core BLE manager
│       └── deviceScanner.ts       # Device discovery
│
├── context/
│   └── DeviceContext.tsx          # Device connection state
│
└── types/
    └── device.ts                  # SensorReading, BLEDevice types
```

### Recommended Enhancements

```typescript
// services/bluetooth/bleManager.ts

export class BLEManager {
  // Current: Receive sensor data
  async subscribeToSensorData(callback: (data: SensorReading) => void): Promise<void>
  
  // New: Send WiFi configuration
  async sendWiFiConfig(ssid: string, password: string): Promise<boolean>
  
  // New: Send device command
  async sendCommand(command: DeviceCommand): Promise<CommandResponse>
  
  // New: Read device status
  async readDeviceStatus(): Promise<DeviceStatus>
  
  // New: Subscribe to device status updates
  async subscribeToDeviceStatus(callback: (status: DeviceStatus) => void): Promise<void>
}

// types/device.ts

export interface DeviceCommand {
  type: 'wifi_config' | 'reset' | 'calibrate' | 'ota_update';
  payload?: any;
}

export interface CommandResponse {
  success: boolean;
  message?: string;
  data?: any;
}

export interface DeviceStatus {
  wifi_connected: boolean;
  wifi_ssid?: string;
  battery_level?: number;
  firmware_version?: string;
}
```

## Best Practices

### 1. **Error Handling**

- Always handle BLE disconnections gracefully
- Implement reconnection logic with exponential backoff
- Show user-friendly error messages
- Log errors for debugging

### 2. **Connection Management**

- Maintain connection state in React Context (`DeviceContext`)
- Auto-reconnect on disconnection (optional, with user preference)
- Allow manual connect/disconnect via UI

### 3. **Data Validation**

- Validate sensor data format before processing
- Validate WiFi credentials before sending
- Handle malformed data gracefully

### 4. **Security**

- **WiFi Password**: Send over BLE (encrypted by BLE layer)
- Consider additional encryption for sensitive data
- Validate device identity (avoid connecting to wrong device)

### 5. **Performance**

- Use characteristic notifications (not polling) for sensor data
- Batch multiple writes if needed
- Implement timeout for write operations

## Example: WiFi Configuration Flow

```typescript
// In home.tsx or a dedicated WiFi config hook

const handleSendWiFiCredentials = async () => {
  if (!isConnected) {
    toast.showError("Error", "Device not connected");
    return;
  }

  if (!wifiSSID.trim() || !wifiPassword.trim()) {
    toast.showError("Error", "Please enter WiFi credentials");
    return;
  }

  setIsConnectingWifi(true);
  
  try {
    const success = await bleManager.sendWiFiConfig(wifiSSID, wifiPassword);
    
    if (success) {
      toast.showSuccess("WiFi Config Sent", "Device is connecting to WiFi...");
      // Optionally wait for device status update confirming WiFi connection
    } else {
      toast.showError("Failed", "Could not send WiFi configuration");
    }
  } catch (error) {
    toast.showError("Error", "Failed to send WiFi credentials");
  } finally {
    setIsConnectingWifi(false);
  }
};
```

## ESP32 Implementation Notes

### For ESP32 Developer

1. **BLE Characteristic Setup**:
   ```cpp
   // Sensor Data Characteristic (Notify)
   BLECharacteristic *pSensorDataCharacteristic;
   pSensorDataCharacteristic->setCallbacks(new SensorDataCallbacks());
   
   // WiFi Config Characteristic (Write)
   BLECharacteristic *pWiFiConfigCharacteristic;
   pWiFiConfigCharacteristic->setCallbacks(new WiFiConfigCallbacks());
   ```

2. **Send Sensor Data** (every 2 seconds):
   ```cpp
   // Create JSON payload
   String sensorData = createSensorJSON();
   
   // Send via notification
   pSensorDataCharacteristic->setValue(sensorData.c_str());
   pSensorDataCharacteristic->notify();
   ```

3. **Receive WiFi Config**:
   ```cpp
   void WiFiConfigCallbacks::onWrite(BLECharacteristic *pCharacteristic) {
     std::string value = pCharacteristic->getValue();
     // Parse JSON: {"ssid": "...", "password": "..."}
     // Connect to WiFi
   }
   ```

## Summary

**Recommended Approach**:

1. **ESP32 → Mobile**: Use BLE Notifications for sensor data (every 2 seconds)
   - Efficient, real-time, low battery impact
   - Mobile app subscribes once, receives continuously

2. **Mobile → ESP32**: Use BLE Write for commands/configuration
   - Send WiFi credentials, settings, commands
   - Can add command-response pattern for acknowledgments

3. **State Management**: Use React Context for connection state
   - `DeviceContext` manages BLE connection, sensor data
   - UI components consume context via hooks

4. **Error Handling**: Implement robust error handling
   - Handle disconnections, invalid data, timeouts
   - User-friendly error messages

This approach provides a clean separation of concerns, efficient communication, and scalable architecture for bidirectional BLE communication.

