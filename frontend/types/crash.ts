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

export interface CrashEvent {
  id: string;
  device_id: string;
  crash_timestamp: string;
  is_confirmed_crash: boolean;
  confidence_score: number | null;
  severity: 'low' | 'medium' | 'high';
  crash_type: string;
  ai_reasoning: string;
  key_indicators: string[];
  false_positive_risk: number | null;
}

