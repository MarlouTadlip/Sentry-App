/** Device-related TypeScript types. */

export interface SensorReading {
  device_id: string;
  ax: number;
  ay: number;
  az: number;
  roll: number;
  pitch: number;
  tilt_detected: boolean;
  timestamp: string;
}

export interface BLEDevice {
  id: string;
  name: string;
  rssi: number;
  connected: boolean;
}

