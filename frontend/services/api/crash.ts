/** API service for crash alerts. */

import { deviceApi } from '@/lib/api';
import { CrashAlertRequest, CrashAlertResponse, CrashEvent, CrashFeedbackRequest, CrashFeedbackResponse } from '@/types/api';

/**
 * Send crash alert to backend for AI analysis
 */
export async function sendCrashAlert(
  data: CrashAlertRequest
): Promise<CrashAlertResponse> {
  const response = await deviceApi.post<CrashAlertResponse>(
    '/crash/alert',
    data
  );
  return response.data;
}

/**
 * Get crash events for a device or user
 */
export async function getCrashEvents(
  deviceId?: string,
  limit: number = 50,
  offset: number = 0
): Promise<CrashEvent[]> {
  const params = new URLSearchParams();
  if (deviceId) params.append('device_id', deviceId);
  params.append('limit', limit.toString());
  params.append('offset', offset.toString());
  
  const response = await deviceApi.get<CrashEvent[]>(
    `/crash/events?${params.toString()}`
  );
  return response.data;
}

/**
 * Submit user feedback for a crash event
 */
export async function submitCrashFeedback(
  eventId: number,
  data: CrashFeedbackRequest
): Promise<CrashFeedbackResponse> {
  const response = await deviceApi.post<CrashFeedbackResponse>(
    `/crash/events/${eventId}/feedback`,
    data
  );
  return response.data;
}
