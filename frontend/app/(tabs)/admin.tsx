import { useThemeColors } from "@/hooks/useThemeColors";
import {
  Bell,
  BellOff,
  AlertTriangle,
  Shield,
} from "@tamagui/lucide-icons";
import React from "react";
import {
  Button,
  Card,
  ScrollView,
  Text,
  XStack,
  YStack,
  Spinner,
} from "tamagui";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/hooks/useToast";
import { useFCM } from "@/hooks/useFCM";
import { useRouter } from "expo-router";
import { Redirect } from "expo-router";

const admin = () => {
  const colors = useThemeColors();
  const { user } = useAuth();
  const toast = useToast();
  const router = useRouter();

  // Redirect non-admin users
  if (!user?.is_superuser) {
    return <Redirect href="/(tabs)/home" />;
  }

  // Notification setup
  const { 
    pushToken, 
    isRegistered, 
    isPeriodicActive,
    hasNotificationPermission,
    sendTestNotification,
    sendBackendTestNotification, 
    startPeriodicTest, 
    stopPeriodicTest,
    requestNotificationPermission,
    isSendingBackendTest,
  } = useFCM();
  
  return (
    <ScrollView 
      style={{ backgroundColor: colors.background }}
    >
      <YStack padding={"$4"} gap={"$4"}>
        {/* Admin Header */}
        <Card
          elevate
          bordered
          borderColor={colors.primary}
          padded
          gap={"$3"}
          backgroundColor={colors.cardBackground}
        >
          <XStack gap={"$2"} alignItems="center" marginBottom={"$2"}>
            <Shield color={colors.primary} />
            <Text color={colors.text} fontSize={"$6"} fontWeight="bold">
              Admin Panel
            </Text>
          </XStack>
          <Text color={colors.gray[200]} fontSize={"$4"}>
            Administrative functions and testing tools
          </Text>
        </Card>

        {/* Notification Test Card */}
        <Card
          elevate
          bordered
          borderColor={colors.border}
          padded
          gap={"$4"}
          enterStyle={{ opacity: 0, y: 10 }}
          opacity={1}
          animation={"bouncy"}
          backgroundColor={colors.cardBackground}
        >
          <XStack gap={"$2"} alignItems="center" marginBottom={"$2"}>
            <Bell color={colors.primary} />
            <Text color={colors.text} fontSize={"$5"} fontWeight="bold">
              Notification Testing
            </Text>
          </XStack>

          <Text color={colors.gray[200]} fontSize={"$3"} marginBottom={"$2"}>
            Test Firebase Cloud Messaging notifications
          </Text>

          <YStack gap={"$3"}>
            {/* Permission Warning */}
            {!hasNotificationPermission && !isRegistered && (
              <Card
                bordered
                borderColor={colors.red}
                backgroundColor={colors.cardBackground}
                padding={"$3"}
                marginBottom={"$2"}
              >
                <XStack gap={"$2"} alignItems="center" marginBottom={"$2"}>
                  <AlertTriangle color={colors.red} size={20} />
                  <Text color={colors.red} fontWeight="bold" fontSize={"$4"}>
                    Notification Permission Required
                  </Text>
                </XStack>
                <Text color={colors.text} fontSize={"$3"} marginBottom={"$2"}>
                  Please grant notification permission to receive crash alerts and test notifications.
                </Text>
                <Button
                  backgroundColor={colors.primary}
                  onPress={async () => {
                    const granted = await requestNotificationPermission();
                    if (granted) {
                      toast.showSuccess("Permission Granted", "Notification permission has been granted.");
                    } else {
                      toast.showError("Permission Denied", "Please enable notifications in app settings.");
                    }
                  }}
                >
                  <XStack gap={"$2"} alignItems="center">
                    <Bell size={16} color="#ffffff" />
                    <Text color="#ffffff" fontWeight="semibold">
                      Grant Notification Permission
                    </Text>
                  </XStack>
                </Button>
              </Card>
            )}

            {/* Token Status */}
            <XStack justifyContent="space-between" paddingBottom={"$2"}>
              <Text color={colors.text} fontSize={"$4"} fontWeight="600">
                Push Token Status:
              </Text>
              <Text 
                color={isRegistered ? colors.green[500] : colors.red} 
                fontSize={"$4"} 
                fontWeight="bold"
              >
                {isRegistered ? "Registered" : "Not Registered"}
              </Text>
            </XStack>

            {pushToken && (
              <YStack gap={"$2"} paddingBottom={"$2"}>
                <Text color={colors.text} fontSize={"$3"} fontWeight="600">
                  Token:
                </Text>
                <Text color={colors.gray[200]} fontSize={"$2"} numberOfLines={2}>
                  {pushToken}
                </Text>
              </YStack>
            )}

            {/* Periodic Notification Button */}
            <Button
              backgroundColor={isPeriodicActive ? colors.red : colors.primary}
              onPress={() => {
                if (isPeriodicActive) {
                  stopPeriodicTest();
                } else {
                  startPeriodicTest(5); // Every 5 seconds
                }
              }}
            >
              <XStack gap={"$2"} alignItems="center">
                {isPeriodicActive ? (
                  <>
                    <BellOff size={16} color="#ffffff" />
                    <Text color="#ffffff" fontWeight="semibold">
                      Stop Periodic Notifications
                    </Text>
                  </>
                ) : (
                  <>
                    <Bell size={16} color="#ffffff" />
                    <Text color="#ffffff" fontWeight="semibold">
                      Start Periodic Notifications (Every 5s)
                    </Text>
                  </>
                )}
              </XStack>
            </Button>

            {/* Single Local Test Notification Button */}
            <Button
              variant="outlined"
              borderColor={colors.border}
              borderWidth={1}
              backgroundColor="transparent"
              onPress={sendTestNotification}
            >
              <XStack gap={"$2"} alignItems="center">
                <Bell size={16} color={colors.primary} />
                <Text color={colors.primary} fontWeight="semibold">
                  Send Local Test Notification
                </Text>
              </XStack>
            </Button>

            {/* Backend FCM Test Notification Button */}
            <Button
              variant="outlined"
              borderColor={colors.primary}
              borderWidth={2}
              backgroundColor={isSendingBackendTest ? colors.gray[200] : "transparent"}
              onPress={async () => {
                try {
                  const result = await sendBackendTestNotification();
                  if (result.success) {
                    toast.showSuccess("Test Sent", "Backend push notification sent successfully! Check your device.");
                  } else {
                    toast.showError("Test Failed", result.message || "Failed to send test notification");
                  }
                } catch (error: any) {
                  const errorMessage = error?.response?.data?.message || error?.message || "Failed to send test notification";
                  toast.showError("Test Failed", errorMessage);
                }
              }}
              disabled={isSendingBackendTest || !isRegistered}
              opacity={(!isRegistered || isSendingBackendTest) ? 0.6 : 1}
            >
              <XStack gap={"$2"} alignItems="center">
                <Bell size={16} color={colors.primary} />
                <Text color={colors.primary} fontWeight="semibold">
                  {isSendingBackendTest ? "Sending..." : "Test Backend FCM Push"}
                </Text>
              </XStack>
            </Button>

            {!isRegistered && (
              <Text color={colors.red} fontSize={"$3"} textAlign="center" fontWeight="600">
                ⚠️ Push token not registered. Please ensure notifications are enabled.
              </Text>
            )}

            {isPeriodicActive && (
              <Text color={colors.green[500]} fontSize={"$3"} textAlign="center" fontWeight="600">
                ✓ Periodic notifications active (every 5 seconds)
              </Text>
            )}
          </YStack>
        </Card>
      </YStack>
    </ScrollView>
  );
};

export default admin;

