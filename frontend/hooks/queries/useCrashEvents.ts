/** Query hook for fetching crash events. */

import { useQuery } from '@tanstack/react-query';
import { getCrashEvents } from '@/services/api/crash';
import { CrashEvent } from '@/types/api';

interface UseCrashEventsOptions {
  deviceId?: string;
  limit?: number;
  offset?: number;
  enabled?: boolean;
}

/**
 * Hook for fetching crash events from the API
 */
export function useCrashEvents(options: UseCrashEventsOptions = {}) {
  const { deviceId, limit = 50, offset = 0, enabled = true } = options;

  return useQuery<CrashEvent[]>({
    queryKey: ['crashEvents', deviceId, limit, offset],
    queryFn: () => getCrashEvents(deviceId, limit, offset),
    enabled: enabled && !!deviceId, // Only fetch if deviceId is provided
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

