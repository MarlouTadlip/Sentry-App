/** Mutation hook for submitting crash event feedback. */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { submitCrashFeedback } from '@/services/api/crash';
import { CrashFeedbackRequest } from '@/types/api';

/**
 * Hook for submitting user feedback on crash events
 */
export function useCrashFeedback() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ eventId, data }: { eventId: number; data: CrashFeedbackRequest }) =>
      submitCrashFeedback(eventId, data),
    onSuccess: () => {
      // Invalidate queries to refetch updated data
      queryClient.invalidateQueries({ queryKey: ['crashEvents'] });
      queryClient.invalidateQueries({ queryKey: ['crashHistory'] });
    },
  });
}

