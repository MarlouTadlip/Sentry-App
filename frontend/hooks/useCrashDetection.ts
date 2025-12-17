/** Hook for crash detection using threshold analysis. */

import { useEffect, useRef, useState } from 'react';
import { ThresholdDetector } from '@/services/crash/threshold';
import { ThresholdResult } from '@/types/crash';
import { SensorReading } from '@/types/device';
import { useDevice } from '@/context/DeviceContext';
import { useCrash } from '@/context/CrashContext';
import { useSendCrashAlert } from '@/hooks/mutations/useSendCrashAlert';

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
 * Phase 2: Sends to backend for AI analysis (Tier 2) using TanStack Query mutation.
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
  
  // Get GPS data from DeviceContext
  const { currentGPSData } = useDevice();
  
  // Get CrashContext to store AI response
  const { setAIResponse, setProcessing } = useCrash();
  
  // Phase 2: Use TanStack Query mutation for sending crash alert
  const sendCrashAlertMutation = useSendCrashAlert();

  useEffect(() => {
    // Process each sensor reading received via BLE (every 2 seconds)
    if (!enabled || !sensorData || isProcessingRef.current) return;

    const result = detectorRef.current.checkThreshold(sensorData);

    if (result.isTriggered && !isProcessingRef.current) {
      isProcessingRef.current = true;
      setLastResult(result);
      setProcessing(true);
      setAIResponse(null); // Clear previous AI response

      // Phase 1: Console log threshold exceeded
      console.log('⚠️ THRESHOLD EXCEEDED - Potential Crash Detected', {
        timestamp: new Date().toISOString(),
        severity: result.severity,
        triggerType: result.triggerType,
        gForce: result.gForce,
        tilt: result.tilt,
        sensorData: sensorData,
        gpsData: currentGPSData,
      });

      // Phase 2: Send to backend for AI analysis using TanStack Query mutation
      sendCrashAlertMutation.mutate(
        {
          device_id: sensorData.device_id,
          sensor_reading: sensorData,
          threshold_result: result,
          timestamp: new Date().toISOString(),
          gps_data: currentGPSData, // Include GPS data (may be null if no fix)
        },
        {
          onSuccess: (aiResponse) => {
            // AI confirmation received
            console.log('✅ AI Analysis Complete:', {
              is_crash: aiResponse.is_crash,
              confidence: aiResponse.confidence,
              severity: aiResponse.severity,
              reasoning: aiResponse.reasoning,
            });
            // Store AI response in context
            setAIResponse(aiResponse);
            setProcessing(false);
            onAIConfirmation?.(aiResponse.is_crash);
            // Reset detector after processing
            detectorRef.current.reset();
            isProcessingRef.current = false;
          },
          onError: (error) => {
            console.error('❌ Error sending crash alert:', error);
            setProcessing(false);
            setAIResponse(null);
            // Reset detector even on error to allow future detections
            detectorRef.current.reset();
            isProcessingRef.current = false;
          },
        }
      );

      onThresholdExceeded?.(result);
    }
  }, [sensorData, enabled, onThresholdExceeded, onAIConfirmation]);

  return {
    lastResult,
    isProcessing: sendCrashAlertMutation.isPending,
    reset: () => detectorRef.current.reset(),
  };
}

