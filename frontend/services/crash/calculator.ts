/** Calculator utilities for crash detection. */

/**
 * Calculate total G-force from acceleration components
 * Formula: sqrt(ax² + ay² + az²) / 9.81
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

