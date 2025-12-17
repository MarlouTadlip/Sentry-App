import { useThemeColors } from "@/hooks/useThemeColors";
import { useThemeContext } from "@/context/ThemeContext";
import { useToast } from "@/hooks/useToast";
import { useAuth } from "@/context/AuthContext";
import { useDevice } from "@/context/DeviceContext";
import { LogOut, Moon, Palette, Settings, Sun, User, AlertTriangle, Shield, MapPin } from "@tamagui/lucide-icons";
import { useRouter } from "expo-router";
import React, { useEffect, useState } from "react";
import { Card, ScrollView, Text, XStack, YStack, Button, Slider } from "tamagui";
import { Pressable, StyleSheet } from "react-native";
import { getUserSettings, updateUserSettings } from "@/services/api/user";
import { CRASH_DETECTION_CONFIG } from "@/utils/constants";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from "react-native-reanimated";

const settings = () => {
  const colors = useThemeColors();
  const { themePreference, toggleTheme, activeTheme } = useThemeContext();
  const toast = useToast();
  const router = useRouter();
  const { logout, user } = useAuth();
  const { 
    isGPSEnabled, 
    hasLocationPermission, 
    currentSpeed, 
    currentGPSData,
    startGPSTracking, 
    stopGPSTracking, 
    requestLocationPermission 
  } = useDevice();
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [crashAlertInterval, setCrashAlertInterval] = useState<number>(
    CRASH_DETECTION_CONFIG.crashAlertIntervalSeconds
  );
  const [isLoadingSettings, setIsLoadingSettings] = useState(true);
  const [isSavingSettings, setIsSavingSettings] = useState(false);
  const isDark = activeTheme === "dark";
  
  // Animated value for switch position (0 = left, 24 = right)
  const translateX = useSharedValue(isDark ? 24 : 0);

  // Load crash alert interval from backend
  useEffect(() => {
    const loadInterval = async () => {
      setIsLoadingSettings(true);
      try {
        const settings = await getUserSettings();
        if (settings.crash_alert_interval_seconds) {
          setCrashAlertInterval(settings.crash_alert_interval_seconds);
        }
      } catch (error) {
        console.error("Error loading user settings:", error);
        toast.showError("Load Failed", "Failed to load crash alert interval");
      } finally {
        setIsLoadingSettings(false);
      }
    };
    loadInterval();
  }, [toast]);

  // Update animation when theme changes
  useEffect(() => {
    translateX.value = withSpring(isDark ? 24 : 0, {
      damping: 15,
      stiffness: 150,
      mass: 1,
    });
  }, [isDark, translateX]);

  // Animated style for the thumb
  const animatedThumbStyle = useAnimatedStyle(() => {
    return {
      transform: [{ translateX: translateX.value }],
    };
  });

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
      toast.showSuccess("Logged Out", "You have been successfully logged out");
      // Navigate to login page
      router.replace("/(auth)/login");
    } catch (error: any) {
      const errorMessage = error?.message || "Failed to logout. Please try again.";
      toast.showError("Logout Failed", errorMessage);
    } finally {
      setIsLoggingOut(false);
    }
  };

  const handleIntervalChange = async (value: string) => {
    const numValue = parseInt(value, 10);
    
    // Validate range: 10-60 seconds (backend enforced range)
    if (isNaN(numValue) || numValue < 10 || numValue > 60) {
      // Invalid value - don't save
      return;
    }
    
    // Valid value - save to backend
    setIsSavingSettings(true);
    try {
      const updatedSettings = await updateUserSettings({
        crash_alert_interval_seconds: numValue,
      });
      setCrashAlertInterval(updatedSettings.crash_alert_interval_seconds);
      toast.showSuccess(
        "Setting Saved",
        `Crash alert interval set to ${updatedSettings.crash_alert_interval_seconds} seconds`
      );
    } catch (error: any) {
      console.error("Error saving crash alert interval:", error);
      const errorMessage = error?.response?.data?.message || error?.message || "Failed to save crash alert interval";
      toast.showError("Save Failed", errorMessage);
      // Revert to previous value on error - reload from backend
      try {
        const settings = await getUserSettings();
        if (settings.crash_alert_interval_seconds) {
          setCrashAlertInterval(settings.crash_alert_interval_seconds);
        }
      } catch (reloadError) {
        console.error("Error reloading settings:", reloadError);
      }
    } finally {
      setIsSavingSettings(false);
    }
  };
  
  return (
    <ScrollView style={{ backgroundColor: colors.background }}>
      <YStack padding={"$4"} gap={"$4"}>
        {/* Profile Card - Topmost */}
        <Card
          elevate
          bordered
          animation="bouncy"
          borderColor={colors.border}
          padded
          gap={"$4"}
          enterStyle={{ opacity: 0, y: 10 }}
          opacity={1}
          y={0}
          backgroundColor={colors.cardBackground}
        >
          <YStack gap={"$4"}>
            <XStack alignItems="center" gap={"$2"}>
              <User color={colors.primary} />
              <Text color={colors.text} fontSize={"$5"} fontWeight={"500"}>
                Profile
              </Text>
            </XStack>
            <Button
              onPress={() => router.push("/(app)/profile")}
              backgroundColor={colors.primary}
              color="white"
              fontWeight="600"
            >
              <User size={20} color="#ffffff" />
              <Text color="#ffffff" fontWeight="600" marginLeft="$2">
                View Profile
              </Text>
            </Button>
          </YStack>
        </Card>

        {/* App Settings Card - Contains Theme and Account */}
        <Card
          elevate
          bordered
          animation="bouncy"
          borderColor={colors.border}
          padded
          gap={"$4"}
          enterStyle={{ opacity: 0, y: 10 }}
          opacity={1}
          y={0}
          backgroundColor={colors.cardBackground}
        >
          <YStack gap={"$4"}>
            <XStack alignItems="center" gap={"$2"}>
              <Settings color={colors.primary} />
              <Text color={colors.text} fontSize={"$6"} fontWeight={"600"}>
                App Settings
              </Text>
            </XStack>

            {/* Theme Section */}
            <YStack gap={"$3"} paddingTop={"$2"}>
              <XStack alignItems="center" justifyContent="space-between">
                <XStack alignItems="center" gap={"$3"} flex={1}>
                  <Palette color={colors.primary} size={20} />
                  <YStack flex={1}>
                    <Text color={colors.text} fontSize={"$5"} fontWeight={"500"}>
                      Theme
                    </Text>
                    <Text color={colors.gray[200]} fontSize={"$3"}>
                      {themePreference === "system"
                        ? "System Default"
                        : isDark
                        ? "Dark Mode"
                        : "Light Mode"}
                    </Text>
                  </YStack>
                </XStack>
                <Pressable
                  onPress={toggleTheme}
                  style={[
                    styles.switchContainer,
                    {
                      backgroundColor: isDark ? colors.primary : colors.gray[200],
                    },
                  ]}
                >
                  <Animated.View style={[styles.switchThumb, animatedThumbStyle]}>
                    {isDark ? (
                      <Moon size={14} color={colors.primary} />
                    ) : (
                      <Sun size={14} color="#FFA500" />
                    )}
                  </Animated.View>
                </Pressable>
              </XStack>
            </YStack>

            {/* Divider */}
            <XStack
              height={1}
              backgroundColor={colors.border}
              marginVertical={"$2"}
            />

            {/* Crash Detection Section */}
            <YStack gap={"$3"}>
              <XStack alignItems="center" gap={"$2"}>
                <AlertTriangle color={colors.emerald[500]} size={20} />
                <Text color={colors.text} fontSize={"$5"} fontWeight={"500"}>
                  Crash Detection
                </Text>
              </XStack>
              <YStack gap={"$2"}>
                <Text color={colors.gray[200]} fontSize={"$3"}>
                  Alert Interval (seconds)
                </Text>
                <Text color={colors.gray[200]} fontSize={"$2"}>
                  Minimum time between crash alert API calls. Prevents excessive requests.
                </Text>
                <YStack gap={"$2"} paddingVertical={"$2"}>
                  <XStack alignItems="center" gap={"$3"} width="100%">
                    <Text color={colors.text} fontSize={"$3"} minWidth={30}>
                      10
                    </Text>
                    <Slider
                      value={[crashAlertInterval]}
                      onValueChange={(values) => {
                        const value = Array.isArray(values) ? values[0] : values;
                        const roundedValue = Math.round(value);
                        setCrashAlertInterval(roundedValue);
                      }}
                      onSlideEnd={(values) => {
                        const value = Array.isArray(values) ? values[0] : values;
                        const roundedValue = Math.round(value);
                        handleIntervalChange(roundedValue.toString());
                      }}
                      min={10}
                      max={60}
                      step={1}
                      disabled={isLoadingSettings || isSavingSettings}
                      opacity={isLoadingSettings || isSavingSettings ? 0.6 : 1}
                      flex={1}
                    >
                      <Slider.Track>
                        <Slider.TrackActive backgroundColor={colors.primary} />
                      </Slider.Track>
                      <Slider.Thumb
                        index={0}
                        circular
                        backgroundColor={colors.primary}
                        borderColor={colors.border}
                        borderWidth={2}
                        size={20}
                      />
                    </Slider>
                    <Text color={colors.text} fontSize={"$3"} minWidth={30}>
                      60
                    </Text>
                  </XStack>
                  <XStack justifyContent="center" alignItems="center" gap={"$2"}>
                    <Text color={colors.text} fontSize={"$5"} fontWeight={"600"}>
                      {crashAlertInterval}
                    </Text>
                    <Text color={colors.gray[200]} fontSize={"$3"}>
                      seconds
                    </Text>
                  </XStack>
                </YStack>
                <Text color={colors.gray[200]} fontSize={"$2"}>
                  {isLoadingSettings
                    ? "Loading..."
                    : isSavingSettings
                    ? "Saving..."
                    : `Range: 10-60 seconds`}
                </Text>
              </YStack>
            </YStack>

            {/* Divider */}
            <XStack
              height={1}
              backgroundColor={colors.border}
              marginVertical={"$2"}
            />

            {/* Location Services Section */}
            <YStack gap={"$3"}>
              <XStack alignItems="center" gap={"$2"}>
                <MapPin color={colors.primary} size={20} />
                <Text color={colors.text} fontSize={"$5"} fontWeight={"500"}>
                  Location Services
                </Text>
              </XStack>
              <YStack gap={"$2"}>
                <Text color={colors.gray[200]} fontSize={"$3"}>
                  GPS tracking is optional and provides more accurate crash detection with speed calculations.
                </Text>
                
                {/* Permission Status */}
                <YStack gap={"$2"} paddingVertical={"$2"}>
                  <XStack justifyContent="space-between" alignItems="center">
                    <Text color={colors.text} fontSize={"$3"}>
                      Location Permission
                    </Text>
                    <XStack alignItems="center" gap={"$2"}>
                      <Text 
                        color={hasLocationPermission ? colors.emerald[500] : colors.red[500]} 
                        fontSize={"$3"}
                        fontWeight={"500"}
                      >
                        {hasLocationPermission ? "Granted" : "Denied"}
                      </Text>
                      {!hasLocationPermission && (
                        <Button
                          size="$2"
                          onPress={async () => {
                            const granted = await requestLocationPermission();
                            if (granted) {
                              toast.showSuccess("Permission Granted", "Location permission enabled");
                            } else {
                              toast.showError("Permission Denied", "Location permission is required for GPS tracking");
                            }
                          }}
                          backgroundColor={colors.primary}
                          color="white"
                        >
                          Request
                        </Button>
                      )}
                    </XStack>
                  </XStack>

                  {/* GPS Tracking Status */}
                  <XStack justifyContent="space-between" alignItems="center">
                    <Text color={colors.text} fontSize={"$3"}>
                      GPS Tracking
                    </Text>
                    <XStack alignItems="center" gap={"$2"}>
                      <Text 
                        color={isGPSEnabled ? colors.emerald[500] : colors.gray[200]} 
                        fontSize={"$3"}
                        fontWeight={"500"}
                      >
                        {isGPSEnabled ? "Enabled" : "Disabled"}
                      </Text>
                      <Pressable
                        onPress={async () => {
                          if (isGPSEnabled) {
                            stopGPSTracking();
                            toast.showSuccess("GPS Disabled", "GPS tracking stopped");
                          } else {
                            if (!hasLocationPermission) {
                              const granted = await requestLocationPermission();
                              if (!granted) {
                                toast.showError("Permission Required", "Location permission is required");
                                return;
                              }
                            }
                            await startGPSTracking();
                            toast.showSuccess("GPS Enabled", "GPS tracking started");
                          }
                        }}
                        style={[
                          styles.switchContainer,
                          {
                            backgroundColor: isGPSEnabled ? colors.primary : colors.gray[200],
                          },
                        ]}
                      >
                        <Animated.View 
                          style={[
                            styles.switchThumb, 
                            { transform: [{ translateX: isGPSEnabled ? 24 : 0 }] }
                          ]}
                        >
                          {isGPSEnabled ? (
                            <MapPin size={14} color={colors.primary} />
                          ) : (
                            <MapPin size={14} color={colors.gray[200]} />
                          )}
                        </Animated.View>
                      </Pressable>
                    </XStack>
                  </XStack>

                  {/* Current Speed Display */}
                  {isGPSEnabled && currentSpeed !== null && (
                    <XStack justifyContent="space-between" alignItems="center">
                      <Text color={colors.text} fontSize={"$3"}>
                        Current Speed
                      </Text>
                      <Text color={colors.primary} fontSize={"$4"} fontWeight={"600"}>
                        {(currentSpeed * 3.6).toFixed(1)} km/h
                      </Text>
                    </XStack>
                  )}

                  {/* GPS Accuracy Display */}
                  {isGPSEnabled && currentGPSData && currentGPSData.accuracy !== null && (
                    <XStack justifyContent="space-between" alignItems="center">
                      <Text color={colors.text} fontSize={"$3"}>
                        GPS Accuracy
                      </Text>
                      <Text color={colors.gray[200]} fontSize={"$3"}>
                        {currentGPSData.accuracy.toFixed(0)} m
                      </Text>
                    </XStack>
                  )}
                </YStack>
              </YStack>
            </YStack>

            {/* Divider */}
            <XStack
              height={1}
              backgroundColor={colors.border}
              marginVertical={"$2"}
            />

            {/* Admin Section - Only show for superusers */}
            {user?.is_superuser && (
              <>
                <YStack gap={"$3"}>
                  <XStack alignItems="center" gap={"$2"}>
                    <Shield color={colors.primary} size={20} />
                    <Text color={colors.text} fontSize={"$5"} fontWeight={"500"}>
                      Admin
                    </Text>
                  </XStack>
                  <Button
                    onPress={() => router.push("/(tabs)/admin")}
                    backgroundColor={colors.primary}
                    color="white"
                    fontWeight="600"
                  >
                    <Shield size={20} color="#ffffff" />
                    <Text color="#ffffff" fontWeight="600" marginLeft="$2">
                      Admin Panel
                    </Text>
                  </Button>
                </YStack>
                {/* Divider */}
                <XStack
                  height={1}
                  backgroundColor={colors.border}
                  marginVertical={"$2"}
                />
              </>
            )}

            {/* Account Section */}
            <YStack gap={"$3"}>
              <XStack alignItems="center" gap={"$2"}>
                <LogOut color={colors.red} size={20} />
                <Text color={colors.text} fontSize={"$5"} fontWeight={"500"}>
                  Account
                </Text>
              </XStack>
              <Button
                onPress={handleLogout}
                backgroundColor={colors.red}
                color="white"
                fontWeight="600"
                disabled={isLoggingOut}
                opacity={isLoggingOut ? 0.6 : 1}
              >
                <LogOut size={20} color="#ffffff" />
                <Text color="#ffffff" fontWeight="600">
                  {isLoggingOut ? "Logging out..." : "Logout"}
                </Text>
              </Button>
            </YStack>
          </YStack>
        </Card>
      </YStack>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  switchContainer: {
    width: 56,
    height: 32,
    borderRadius: 16,
    justifyContent: "center",
    paddingHorizontal: 4,
    position: "relative",
  },
  switchThumb: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: "#ffffff",
    alignItems: "center",
    justifyContent: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
});

export default settings;
