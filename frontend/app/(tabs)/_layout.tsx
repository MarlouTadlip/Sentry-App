import { History, Home, Settings, Users } from "@tamagui/lucide-icons";
import { Tabs, Redirect, useRouter } from "expo-router";
import React, { useEffect } from "react";
import { useThemeColors } from "@/hooks/useThemeColors";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/hooks/useToast";

const _layout = () => {
  const colors = useThemeColors();
  const { isAuthenticated, isVerified, isInitializing } = useAuth();
  const toast = useToast();
  const router = useRouter();

  // Redirect to landing page if not authenticated
  useEffect(() => {
    if (!isInitializing && !isAuthenticated) {
      router.replace("/");
    }
  }, [isAuthenticated, isInitializing, router]);

  // Show nothing while initializing (or a loading spinner)
  if (isInitializing) {
    return null;
  }

  // Redirect unauthenticated users to landing page
  if (!isAuthenticated) {
    return <Redirect href="/" />;
  }
  
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.gray[200],
        headerStyle: { backgroundColor: colors.green[400] },
        headerTintColor: "#ffffff",
        tabBarStyle: {
          backgroundColor: colors.background,
        },
        sceneStyle: {
          backgroundColor: colors.background,
        },
      }}
    >
      <Tabs.Screen
        name="home"
        options={{
          title: "Home",
          headerTitle: "Sentry",
          headerTitleAlign: "center",
          tabBarIcon: () => <Home />,
        }}
      ></Tabs.Screen>
      <Tabs.Screen
        name="contacts"
        options={{
          title: "Contacts",
          headerTitle: "Sentry",
          headerTitleAlign: "center",
          tabBarIcon: () => <Users />,
          tabBarStyle: !isVerified ? { opacity: 0.5 } : undefined,
        }}
        listeners={{
          tabPress: (e) => {
            if (!isVerified) {
              e.preventDefault();
              toast.showWarning("Verification Required", "You must be verified before you can access this feature.");
            }
          },
        }}
      ></Tabs.Screen>
      <Tabs.Screen
        name="history"
        options={{
          title: "History",
          headerTitle: "Sentry",
          headerTitleAlign: "center",
          tabBarIcon: () => <History />,
          tabBarStyle: !isVerified ? { opacity: 0.5 } : undefined,
        }}
        listeners={{
          tabPress: (e) => {
            if (!isVerified) {
              e.preventDefault();
              toast.showWarning("Verification Required", "You must be verified before you can access this feature.");
            }
          },
        }}
      ></Tabs.Screen>
      <Tabs.Screen
        name="settings"
        options={{
          title: "Settings",
          headerTitle: "Sentry",
          headerTitleAlign: "center",
          tabBarIcon: () => <Settings />,
        }}
      ></Tabs.Screen>
    </Tabs>
  );
};

export default _layout;
