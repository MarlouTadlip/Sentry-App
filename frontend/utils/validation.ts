/** Data validation utilities. */

import { SensorReading } from '@/types/device';

/**
 * Validate sensor reading data
 */
export function validateSensorReading(data: unknown): data is SensorReading {
  if (!data || typeof data !== 'object') {
    return false;
  }

  const reading = data as Partial<SensorReading>;

  return (
    typeof reading.device_id === 'string' &&
    typeof reading.ax === 'number' &&
    !Number.isNaN(reading.ax) &&
    typeof reading.ay === 'number' &&
    !Number.isNaN(reading.ay) &&
    typeof reading.az === 'number' &&
    !Number.isNaN(reading.az) &&
    typeof reading.roll === 'number' &&
    !Number.isNaN(reading.roll) &&
    typeof reading.pitch === 'number' &&
    !Number.isNaN(reading.pitch) &&
    typeof reading.tilt_detected === 'boolean' &&
    typeof reading.timestamp === 'string'
  );
}

/**
 * Validate G-force value is within reasonable range
 */
export function isValidGForce(gForce: number): boolean {
  return gForce >= 0 && gForce <= 100; // Reasonable range for crash detection
}

/**
 * Validate tilt angle is within valid range
 */
export function isValidTiltAngle(angle: number): boolean {
  return angle >= -180 && angle <= 180; // Valid angle range in degrees
}

