/** Threshold detection logic for crash detection. */

import { SensorReading } from '@/types/device';
import { ThresholdConfig, ThresholdResult } from '@/types/crash';
import { calculateGForce, calculateTilt } from './calculator';
import { CRASH_DETECTION_CONFIG } from '@/utils/constants';

const DEFAULT_CONFIG: ThresholdConfig = {
  gForceThreshold: CRASH_DETECTION_CONFIG.gForceThreshold,
  tiltThreshold: CRASH_DETECTION_CONFIG.tiltThreshold,
  consecutiveTriggers: CRASH_DETECTION_CONFIG.consecutiveTriggers,
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
    const tiltExceeded =
      Math.abs(tilt.roll) >= this.config.tiltThreshold ||
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
    const confirmed =
      recentTriggers.length === this.config.consecutiveTriggers &&
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

