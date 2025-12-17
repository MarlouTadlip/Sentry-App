/** Crash detection TypeScript types. */

export interface ThresholdConfig {
  gForceThreshold: number;
  tiltThreshold: number;
  consecutiveTriggers: number;
}

export interface ThresholdResult {
  isTriggered: boolean;
  triggerType: 'g_force' | 'tilt' | 'both' | null;
  severity: 'low' | 'medium' | 'high';
  gForce: number;
  tilt: { roll: number; pitch: number };
  timestamp: number;
}

// Note: CrashEvent type moved to types/api.ts to match backend schema

