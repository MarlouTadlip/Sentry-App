/** Visual indicator for crash detection status. */

import React from 'react';
import { Card, Text, YStack } from 'tamagui';

interface CrashIndicatorProps {
  isActive: boolean;
  severity?: 'low' | 'medium' | 'high';
}

export function CrashIndicator({ isActive, severity }: CrashIndicatorProps) {
  const getSeverityColor = (sev: string) => {
    switch (sev) {
      case 'high':
        return '#ef4444'; // red
      case 'medium':
        return '#f59e0b'; // orange
      case 'low':
        return '#3b82f6'; // blue
      default:
        return '#6b7280'; // gray
    }
  };

  const backgroundColor = isActive
    ? getSeverityColor(severity || 'low')
    : '#10b981'; // green when inactive

  return (
    <Card
      elevate
      bordered
      backgroundColor={backgroundColor}
      padding="$3"
      margin="$4"
      borderRadius="$4"
    >
      <YStack alignItems="center" justifyContent="center">
        <Text color="#ffffff" fontSize="$5" fontWeight="bold">
          {isActive
            ? `🔴 Alert: ${severity?.toUpperCase() || 'CRASH'}`
            : '🟢 Monitoring'}
        </Text>
      </YStack>
    </Card>
  );
}

