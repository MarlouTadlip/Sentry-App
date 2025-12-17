/** Sensor display component for showing real-time sensor data. */

import React from 'react';
import { Card, Text, XStack, YStack } from 'tamagui';
import { SensorReading } from '@/types/device';
import { useThemeColors } from '@/hooks/useThemeColors';

interface SensorDisplayProps {
  sensorData: SensorReading | null;
  isConnected: boolean;
}

export function SensorDisplay({ sensorData, isConnected }: SensorDisplayProps) {
  const colors = useThemeColors();

  if (!isConnected) {
    return (
      <Card
        elevate
        bordered
        borderColor={colors.red}
        padding="$4"
        margin="$4"
        backgroundColor={colors.cardBackground}
      >
        <Text color={colors.red} textAlign="center" fontSize="$5">
          Device not connected
        </Text>
      </Card>
    );
  }

  if (!sensorData) {
    return (
      <Card
        elevate
        bordered
        borderColor={colors.border}
        padding="$4"
        margin="$4"
        backgroundColor={colors.cardBackground}
      >
        <Text color={colors.gray[200]} textAlign="center" fontSize="$4">
          Waiting for sensor data...
        </Text>
      </Card>
    );
  }

  return (
    <Card
      elevate
      bordered
      borderColor={colors.border}
      padding="$4"
      margin="$4"
      backgroundColor={colors.cardBackground}
      gap="$3"
    >
      <Text fontSize="$6" fontWeight="bold" color={colors.text} marginBottom="$2">
        Sensor Data
      </Text>

      <XStack justifyContent="space-between" flexWrap="wrap" marginBottom="$2">
        <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
          Acceleration (m/s²):
        </Text>
        <Text fontSize="$4" color={colors.text}>
          X: {sensorData.ax.toFixed(2)} | Y: {sensorData.ay.toFixed(2)} | Z:{' '}
          {sensorData.az.toFixed(2)}
        </Text>
      </XStack>

      <XStack justifyContent="space-between" flexWrap="wrap" marginBottom="$2">
        <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
          Orientation:
        </Text>
        <Text fontSize="$4" color={colors.text}>
          Roll: {sensorData.roll.toFixed(1)}° | Pitch: {sensorData.pitch.toFixed(1)}°
        </Text>
      </XStack>

      <XStack justifyContent="space-between" flexWrap="wrap" marginBottom="$2">
        <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
          Tilt Detected:
        </Text>
        <Text
          fontSize="$4"
          color={sensorData.tilt_detected ? colors.red : colors.text}
          fontWeight={sensorData.tilt_detected ? 'bold' : 'normal'}
        >
          {sensorData.tilt_detected ? '⚠️ YES' : '✓ NO'}
        </Text>
      </XStack>

      <XStack justifyContent="space-between" flexWrap="wrap" marginBottom="$2">
        <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
          Device ID:
        </Text>
        <Text fontSize="$4" color={colors.text}>
          {sensorData.device_id}
        </Text>
      </XStack>

      <XStack justifyContent="space-between" flexWrap="wrap">
        <Text fontSize="$4" fontWeight="600" color={colors.gray[200]}>
          Timestamp:
        </Text>
        <Text fontSize="$3" color={colors.gray[200]}>
          {new Date(sensorData.timestamp).toLocaleTimeString()}
        </Text>
      </XStack>
    </Card>
  );
}

