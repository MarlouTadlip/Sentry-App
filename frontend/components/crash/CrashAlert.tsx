/** Crash alert component for displaying crash detection results. */

import React, { useState } from 'react';
import { Card, Text, XStack, YStack, Spinner, Button, Input } from 'tamagui';
import { ThresholdResult } from '@/types/crash';
import { CrashAlertResponse } from '@/types/api';
import { useThemeColors } from '@/hooks/useThemeColors';
import { useCrashFeedback } from '@/hooks/mutations/useCrashFeedback';
import { useCrash } from '@/context/CrashContext';

interface CrashAlertProps {
  thresholdResult: ThresholdResult;
  aiResponse?: CrashAlertResponse | null;
  isProcessing?: boolean;
}

export function CrashAlert({ thresholdResult, aiResponse, isProcessing = false }: CrashAlertProps) {
  const colors = useThemeColors();
  const { crashEventId } = useCrash();
  const feedbackMutation = useCrashFeedback();
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackComments, setFeedbackComments] = useState('');
  const [submittedFeedback, setSubmittedFeedback] = useState<'true_positive' | 'false_positive' | null>(null);

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

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return colors.green[500];
    if (confidence >= 0.6) return colors.emerald[500];
    return colors.emerald[500];
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

      {/* AI Analysis Section */}
      <YStack
        height={1}
        backgroundColor={colors.border}
        marginVertical="$3"
      />

      <XStack alignItems="center" gap="$2" marginBottom="$2">
        <Text fontSize="$6" fontWeight="bold" color={colors.text}>
          🤖 AI Analysis
        </Text>
        {isProcessing && (
          <XStack alignItems="center" gap="$2">
            <Spinner size="small" color={colors.green[500]} />
            <Text fontSize="$3" color={colors.gray[200]}>
              Analyzing...
            </Text>
          </XStack>
        )}
      </XStack>

      {isProcessing && !aiResponse && (
        <YStack gap="$3" padding="$3" backgroundColor={colors.cardBackground} borderRadius="$2">
          <Text fontSize="$4" color={colors.gray[200]} textAlign="center">
            Sending crash data to AI for analysis...
          </Text>
        </YStack>
      )}

      {aiResponse && (
        <YStack gap="$3">
          {/* Crash Confirmation Status */}
          <Card
            bordered
            borderColor={aiResponse.is_crash ? colors.red : colors.green[500]}
            borderWidth={2}
            padding="$3"
            backgroundColor={aiResponse.is_crash ? colors.red + '20' : colors.green[500] + '20'}
          >
            <XStack justifyContent="space-between" alignItems="center" flexWrap="wrap">
              <XStack alignItems="center" gap="$2">
                <Text fontSize="$5" fontWeight="bold" color={colors.text}>
                  {aiResponse.is_crash ? '🚨 CRASH CONFIRMED' : '✅ False Alarm'}
                </Text>
              </XStack>
              <Text
                fontSize="$5"
                fontWeight="bold"
                color={getConfidenceColor(aiResponse.confidence)}
              >
                {(aiResponse.confidence * 100).toFixed(0)}% Confidence
              </Text>
            </XStack>
          </Card>

          {/* Crash Details */}
          <YStack gap="$2">
            <XStack justifyContent="space-between" flexWrap="wrap">
              <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
                AI Severity:
              </Text>
              <Text
                fontSize="$4"
                fontWeight="bold"
                color={getSeverityColor(aiResponse.severity)}
              >
                {aiResponse.severity.toUpperCase()}
              </Text>
            </XStack>

            {aiResponse.crash_type && (
              <XStack justifyContent="space-between" flexWrap="wrap">
                <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
                  Crash Type:
                </Text>
                <Text fontSize="$4" color={colors.text}>
                  {aiResponse.crash_type}
                </Text>
              </XStack>
            )}

            <XStack justifyContent="space-between" flexWrap="wrap">
              <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
                False Positive Risk:
              </Text>
              <Text
                fontSize="$4"
                color={aiResponse.false_positive_risk > 0.5 ? colors.emerald[500] : colors.green[500]}
              >
                {(aiResponse.false_positive_risk * 100).toFixed(0)}%
              </Text>
            </XStack>
          </YStack>

          {/* AI Reasoning */}
          <YStack gap="$2">
            <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
              AI Reasoning:
            </Text>
            <Card padding="$3" backgroundColor={colors.cardBackground} borderRadius="$2">
              <Text fontSize="$4" color={colors.text} lineHeight="$1">
                {aiResponse.reasoning}
              </Text>
            </Card>
          </YStack>

          {/* Key Indicators */}
          {aiResponse.key_indicators && aiResponse.key_indicators.length > 0 && (
            <YStack gap="$2">
              <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
                Key Indicators:
              </Text>
              <YStack gap="$1">
                {aiResponse.key_indicators.map((indicator, index) => (
                  <XStack key={index} alignItems="flex-start" gap="$2">
                    <Text fontSize="$4" color={colors.green[500]} marginTop="$1">
                      •
                    </Text>
                    <Text fontSize="$4" color={colors.text} flex={1}>
                      {indicator}
                    </Text>
                  </XStack>
                ))}
              </YStack>
            </YStack>
          )}
        </YStack>
      )}

      {!isProcessing && !aiResponse && (
        <YStack gap="$2" padding="$3" backgroundColor={colors.cardBackground} borderRadius="$2">
          <Text fontSize="$4" color={colors.gray[200]} textAlign="center">
            Waiting for AI analysis...
          </Text>
        </YStack>
      )}

      {/* User Feedback Section */}
      {aiResponse && crashEventId && !submittedFeedback && (
        <>
          <YStack
            height={1}
            backgroundColor={colors.border}
            marginVertical="$3"
          />
          <YStack gap="$3">
            <Text fontSize="$5" fontWeight="bold" color={colors.text}>
              💬 Help Improve Detection
            </Text>
            <Text fontSize="$4" color={colors.gray[200]}>
              Was this a real crash or a false alarm?
            </Text>
            
            {!showFeedback ? (
              <XStack gap="$2" flexWrap="wrap">
                <Button
                  flex={1}
                  minWidth={120}
                  backgroundColor={colors.green[500]}
                  color="white"
                  onPress={() => {
                    setShowFeedback(true);
                    setSubmittedFeedback('true_positive');
                    feedbackMutation.mutate({
                      eventId: crashEventId,
                      data: {
                        user_feedback: 'true_positive',
                      },
                    });
                  }}
                  disabled={feedbackMutation.isPending}
                >
                  {feedbackMutation.isPending ? (
                    <Spinner size="small" color="white" />
                  ) : (
                    '✅ Real Crash'
                  )}
                </Button>
                <Button
                  flex={1}
                  minWidth={120}
                  backgroundColor={colors.emerald[500]}
                  color="white"
                  onPress={() => {
                    setShowFeedback(true);
                    setSubmittedFeedback('false_positive');
                    feedbackMutation.mutate({
                      eventId: crashEventId,
                      data: {
                        user_feedback: 'false_positive',
                      },
                    });
                  }}
                  disabled={feedbackMutation.isPending}
                >
                  {feedbackMutation.isPending ? (
                    <Spinner size="small" color="white" />
                  ) : (
                    '❌ False Alarm'
                  )}
                </Button>
              </XStack>
            ) : (
              <YStack gap="$2">
                <Card
                  bordered
                  borderColor={submittedFeedback === 'true_positive' ? colors.green[500] : colors.emerald[500]}
                  borderWidth={2}
                  padding="$3"
                  backgroundColor={
                    submittedFeedback === 'true_positive'
                      ? colors.green[500] + '20'
                      : colors.emerald[500] + '20'
                  }
                >
                  <Text fontSize="$4" fontWeight="600" color={colors.text}>
                    {submittedFeedback === 'true_positive'
                      ? '✅ Thank you! Marked as real crash.'
                      : '❌ Thank you! Marked as false alarm.'}
                  </Text>
                  {feedbackMutation.isSuccess && (
                    <Text fontSize="$3" color={colors.gray[200]} marginTop="$2">
                      Your feedback helps improve crash detection accuracy.
                    </Text>
                  )}
                </Card>
              </YStack>
            )}
          </YStack>
        </>
      )}
    </Card>
  );
}

