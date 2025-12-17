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

