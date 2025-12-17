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

export interface GPSData {
  fix: boolean;
  satellites: number;
  latitude: number | null;
  longitude: number | null;
  altitude: number | null;
  timestamp: string;
}

export interface BLEDevice {
  id: string;
  name: string;
  rssi: number;
  connected: boolean;
}

