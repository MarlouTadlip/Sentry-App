/** Mutation hook for sending crash alerts to backend. */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { sendCrashAlert } from '@/services/api/crash';
import { CrashAlertRequest, CrashAlertResponse } from '@/types/api';

export function useSendCrashAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CrashAlertRequest) => sendCrashAlert(data),
    onSuccess: (response: CrashAlertResponse) => {
      // Invalidate crash events query to refetch
      queryClient.invalidateQueries({ queryKey: ['crashEvents'] });

      // Show notification based on AI response
      if (response.is_crash) {
        console.log('🚨 CRASH CONFIRMED', {
          severity: response.severity,
          confidence: response.confidence,
          reasoning: response.reasoning,
        });
        // Phase 2: Show local notification
        // showLocalNotification({
        //   title: '🚨 CRASH CONFIRMED',
        //   body: `Severity: ${response.severity} | ${response.reasoning}`,
        //   data: { type: 'crash_confirmed', ...response },
        // });
      } else {
        console.log('✅ False Alarm', {
          reasoning: response.reasoning,
        });
        // Phase 2: Show local notification
        // showLocalNotification({
        //   title: '✅ False Alarm',
        //   body: 'AI analysis indicates no crash occurred.',
        //   data: { type: 'false_positive' },
        // });
      }
    },
    onError: (error) => {
      console.error('Error sending crash alert:', error);
      // Keep threshold alert active if API fails
    },
  });
}

