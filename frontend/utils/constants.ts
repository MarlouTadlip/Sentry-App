/** Application constants. */

export const CRASH_DETECTION_CONFIG = {
  gForceThreshold: 8.0,
  tiltThreshold: 90.0,
  consecutiveTriggers: 2,
  lookbackSeconds: 30,
} as const;

// ESP32 BLE Service UUID (configure in ESP32 code)
export const SENTRY_SERVICE_UUID = '12345678-1234-1234-1234-123456789abc';
export const SENSOR_DATA_CHARACTERISTIC_UUID = '12345678-1234-1234-1234-123456789abd';

