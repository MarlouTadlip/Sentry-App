/** API-related TypeScript types. */

import { SensorReading } from './device';
import { ThresholdResult } from './crash';

export interface CrashAlertRequest {
  device_id: string;
  sensor_reading: SensorReading;
  threshold_result: ThresholdResult;
  timestamp: string;
}

export interface CrashAlertResponse {
  is_crash: boolean;
  confidence: number;
  severity: 'low' | 'medium' | 'high';
  crash_type: string;
  reasoning: string;
  key_indicators: string[];
  false_positive_risk: number;
}

