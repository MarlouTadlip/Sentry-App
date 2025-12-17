import { coreApi } from '@/lib/api';

export interface UserSettings {
  crash_alert_interval_seconds: number;
}

export interface UserSettingsUpdateRequest {
  crash_alert_interval_seconds: number;
}

/**
 * Get user settings from backend
 */
export async function getUserSettings(): Promise<UserSettings> {
  const response = await coreApi.get<UserSettings>('/user/settings');
  return response.data;
}

/**
 * Update user settings via backend API
 */
export async function updateUserSettings(
  data: UserSettingsUpdateRequest
): Promise<UserSettings> {
  const response = await coreApi.put<UserSettings>('/user/settings', data);
  return response.data;
}

