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
  crash_event_id?: number | null; // ID of created crash event (if any)
}

export interface CrashEvent {
  id: number;
  device_id: string;
  crash_timestamp: string;
  is_confirmed_crash: boolean;
  confidence_score: number | null;
  severity: 'low' | 'medium' | 'high';
  crash_type: string;
  ai_reasoning: string;
  key_indicators: string[];
  false_positive_risk: number | null;
  max_g_force: number | null;
  crash_latitude: number | null;
  crash_longitude: number | null;
  crash_altitude: number | null;
  gps_fix_at_crash: boolean;
  satellites_at_crash: number | null;
  user_feedback: 'true_positive' | 'false_positive' | null;
  user_comments: string | null;
  created_at: string;
  updated_at: string;
}

export interface CrashFeedbackRequest {
  user_feedback: 'true_positive' | 'false_positive';
  user_comments?: string;
}

export interface CrashFeedbackResponse {
  success: boolean;
  message: string;
}

