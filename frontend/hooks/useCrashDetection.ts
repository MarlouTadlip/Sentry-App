/** Hook for crash detection using threshold analysis. */

import { useEffect, useRef, useState } from 'react';
import { ThresholdDetector } from '@/services/crash/threshold';
import { ThresholdResult } from '@/types/crash';
import { SensorReading } from '@/types/device';

interface UseCrashDetectionOptions {
  enabled?: boolean;
  onThresholdExceeded?: (result: ThresholdResult) => void;
  onAIConfirmation?: (confirmed: boolean) => void;
}

/**
 * Hook for crash detection using threshold analysis.
 *
 * Phase 1: Receives sensor data from BLE connection (every 2 seconds from ESP32 device).
 * Performs fast threshold detection (Tier 1) and logs to console.
 *
 * Phase 2: Will send to backend for AI analysis (Tier 2) using TanStack Query mutation.
 *
 * @param sensorData - Sensor reading from BLE (received every 2 seconds)
 * @param options - Configuration options
 */
export function useCrashDetection(
  sensorData: SensorReading | null, // Received via BLE from ESP32 (every 2 seconds)
  options: UseCrashDetectionOptions = {}
) {
  const { enabled = true, onThresholdExceeded, onAIConfirmation } = options;
  const detectorRef = useRef(new ThresholdDetector());
  const [lastResult, setLastResult] = useState<ThresholdResult | null>(null);
  const isProcessingRef = useRef(false);

  // Phase 2: Use TanStack Query mutation for sending crash alert
  // Uncomment when ready to enable backend integration:
  // import { useSendCrashAlert } from '@/hooks/mutations/useSendCrashAlert';
  // const sendCrashAlertMutation = useSendCrashAlert();

  useEffect(() => {
    // Process each sensor reading received via BLE (every 2 seconds)
    if (!enabled || !sensorData || isProcessingRef.current) return;

    const result = detectorRef.current.checkThreshold(sensorData);

    if (result.isTriggered && !isProcessingRef.current) {
      isProcessingRef.current = true;
      setLastResult(result);

      // Phase 1: Console log threshold exceeded (no notifications yet)
      console.log('⚠️ THRESHOLD EXCEEDED - Potential Crash Detected', {
        timestamp: new Date().toISOString(),
        severity: result.severity,
        triggerType: result.triggerType,
        gForce: result.gForce,
        tilt: result.tilt,
        sensorData: sensorData,
      });

      // Phase 2: Send to backend for AI analysis using TanStack Query mutation
      // Uncomment when ready to enable backend integration:
      // sendCrashAlertMutation.mutate(
      //   {
      //     device_id: sensorData.device_id,
      //     sensor_reading: sensorData,
      //     threshold_result: result,
      //     timestamp: new Date().toISOString(),
      //   },
      //   {
      //     onSuccess: (aiResponse) => {
      //       // AI confirmation received
      //       onAIConfirmation?.(aiResponse.is_crash);
      //       // Reset detector after processing
      //       detectorRef.current.reset();
      //       isProcessingRef.current = false;
      //     },
      //     onError: (error) => {
      //       console.error('Error sending crash alert:', error);
      //       detectorRef.current.reset();
      //       isProcessingRef.current = false;
      //     },
      //   }
      // );

      // Phase 1: Reset after logging (no backend call yet)
      setTimeout(() => {
        detectorRef.current.reset();
        isProcessingRef.current = false;
      }, 1000); // Reset after 1 second

      onThresholdExceeded?.(result);
    }
  }, [sensorData, enabled, onThresholdExceeded, onAIConfirmation]);

  return {
    lastResult,
    isProcessing: false, // Phase 2: sendCrashAlertMutation.isPending,
    reset: () => detectorRef.current.reset(),
  };
}

