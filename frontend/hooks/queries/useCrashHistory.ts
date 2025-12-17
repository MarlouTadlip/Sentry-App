/** Query hook for fetching crash history with date filters. */

import { useQuery } from '@tanstack/react-query';
import { getCrashEvents } from '@/services/api/crash';
import { CrashEvent } from '@/types/api';

interface UseCrashHistoryOptions {
  deviceId?: string;
  startDate?: string; // ISO date string
  endDate?: string; // ISO date string
  limit?: number;
  offset?: number;
  enabled?: boolean;
}

/**
 * Hook for fetching crash history with optional date filters
 */
export function useCrashHistory(options: UseCrashHistoryOptions = {}) {
  const { deviceId, startDate, endDate, limit = 50, offset = 0, enabled = true } = options;

  return useQuery<CrashEvent[]>({
    queryKey: ['crashHistory', deviceId, startDate, endDate, limit, offset],
    queryFn: async () => {
      // Fetch all events and filter by date on client side
      // (Backend could be enhanced to support date filtering)
      const events = await getCrashEvents(deviceId, limit * 2, offset); // Fetch more to account for filtering
      
      // Filter by date range if provided
      if (startDate || endDate) {
        return events.filter((event) => {
          const eventDate = new Date(event.crash_timestamp);
          if (startDate && eventDate < new Date(startDate)) return false;
          if (endDate && eventDate > new Date(endDate)) return false;
          return true;
        }).slice(0, limit); // Apply limit after filtering
      }
      
      return events;
    },
    enabled: enabled && !!deviceId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

