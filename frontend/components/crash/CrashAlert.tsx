/** Crash alert component for displaying crash detection results. */

import React from 'react';
import { Card, Text, XStack, YStack } from 'tamagui';
import { ThresholdResult } from '@/types/crash';
import { CrashAlertResponse } from '@/types/api';
import { useThemeColors } from '@/hooks/useThemeColors';

interface CrashAlertProps {
  thresholdResult: ThresholdResult;
  aiResponse?: CrashAlertResponse;
}

export function CrashAlert({ thresholdResult, aiResponse }: CrashAlertProps) {
  const colors = useThemeColors();

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return colors.red;
      case 'medium':
        return colors.emerald[500];
      case 'low':
        return colors.green[500];
      default:
        return colors.gray[200];
    }
  };

  const borderColor = getSeverityColor(thresholdResult.severity);

  return (
    <Card
      elevate
      bordered
      borderColor={borderColor}
      borderWidth={2}
      padding="$4"
      margin="$4"
      backgroundColor={colors.cardBackground}
      gap="$3"
    >
      <Text fontSize="$7" fontWeight="bold" color={colors.text} marginBottom="$2">
        🚨 Crash Alert
      </Text>

      <YStack gap="$2">
        <XStack justifyContent="space-between" flexWrap="wrap">
          <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
            Severity:
          </Text>
          <Text fontSize="$5" fontWeight="bold" color={borderColor}>
            {thresholdResult.severity.toUpperCase()}
          </Text>
        </XStack>

        <XStack justifyContent="space-between" flexWrap="wrap">
          <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
            Trigger Type:
          </Text>
          <Text fontSize="$4" color={colors.text}>
            {thresholdResult.triggerType || 'None'}
          </Text>
        </XStack>

        <XStack justifyContent="space-between" flexWrap="wrap">
          <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
            G-Force:
          </Text>
          <Text fontSize="$4" color={colors.text}>
            {thresholdResult.gForce.toFixed(2)}g
          </Text>
        </XStack>

        <XStack justifyContent="space-between" flexWrap="wrap">
          <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
            Tilt:
          </Text>
          <Text fontSize="$4" color={colors.text}>
            Roll: {thresholdResult.tilt.roll.toFixed(1)}° | Pitch:{' '}
            {thresholdResult.tilt.pitch.toFixed(1)}°
          </Text>
        </XStack>
      </YStack>

      {aiResponse && (
        <>
          <YStack
            height={1}
            backgroundColor={colors.border}
            marginVertical="$3"
          />

          <Text fontSize="$6" fontWeight="bold" color={colors.text} marginBottom="$2">
            AI Analysis
          </Text>

          <YStack gap="$2">
            <XStack justifyContent="space-between" flexWrap="wrap">
              <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
                Confirmed:
              </Text>
              <Text fontSize="$4" color={colors.text}>
                {aiResponse.is_crash ? '✅ YES' : '❌ NO'}
              </Text>
            </XStack>

            <XStack justifyContent="space-between" flexWrap="wrap">
              <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
                Confidence:
              </Text>
              <Text fontSize="$4" color={colors.text}>
                {(aiResponse.confidence * 100).toFixed(1)}%
              </Text>
            </XStack>

            <YStack gap="$2">
              <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
                Reasoning:
              </Text>
              <Text fontSize="$4" color={colors.gray[200]} fontStyle="italic">
                {aiResponse.reasoning}
              </Text>
            </YStack>

            {aiResponse.key_indicators.length > 0 && (
              <YStack gap="$2">
                <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
                  Key Indicators:
                </Text>
                {aiResponse.key_indicators.map((indicator, index) => (
                  <Text key={index} fontSize="$4" color={colors.gray[200]} marginLeft="$2">
                    • {indicator}
                  </Text>
                ))}
              </YStack>
            )}
          </YStack>
        </>
      )}
    </Card>
  );
}

