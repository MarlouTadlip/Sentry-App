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
  latitude: number | null;
  longitude: number | null;
  altitude: number | null;
  accuracy: number | null; // GPS accuracy in meters
  speed: number | null; // Speed in m/s (calculated from GPS coordinates)
  speed_change: number | null; // Speed change in m/s² (sudden deceleration)
  timestamp: string;
}

export interface BLEDevice {
  id: string;
  name: string;
  rssi: number;
  connected: boolean;
}

