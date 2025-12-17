/** API service for crash alerts. */

import { deviceApi } from '@/lib/api';
import { CrashAlertRequest, CrashAlertResponse } from '@/types/api';

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

