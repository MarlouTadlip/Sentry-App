/** API-related TypeScript types. */

import { SensorReading, GPSData } from './device';
import { ThresholdResult } from './crash';

export interface CrashAlertRequest {
  device_id: string;
  sensor_reading: SensorReading;
  threshold_result: ThresholdResult;
  timestamp: string;
  gps_data: GPSData | null; // GPS data (may be null if no fix)
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

