/** Location service for GPS tracking and speed calculation. */

import { GPSData } from '@/types/device';

// Dynamically import expo-location to handle cases where native module isn't available
// Use lazy loading to prevent errors when native module isn't available
// Note: expo-location requires native build - run "npx expo prebuild && npx expo run:android" to enable
let LocationModule: typeof import('expo-location') | null = null;
let locationModuleLoaded = false;
let locationModuleError: Error | null = null;

function getLocationModule(): typeof import('expo-location') | null {
  if (locationModuleLoaded) {
    return LocationModule;
  }
  
  locationModuleLoaded = true;
  try {
    // Use dynamic require to prevent Metro from resolving at build time
    LocationModule = require('expo-location');
    locationModuleError = null;
    return LocationModule;
  } catch (error) {
    locationModuleError = error as Error;
    LocationModule = null;
    if (__DEV__) {
      console.warn('⚠️ expo-location not available. GPS features will be disabled.');
      console.warn('💡 To enable GPS: Run "npx expo prebuild && npx expo run:android" to rebuild with native modules.');
      console.warn('   Error:', locationModuleError.message);
    }
    return null;
  }
}

// Type definitions for Location when available
type LocationSubscription = import('expo-location').LocationSubscription;
type LocationObject = import('expo-location').LocationObject;

export class LocationService {
  private watchPositionSubscription: LocationSubscription | null = null;
  private lastLocation: LocationObject | null = null;
  private lastTimestamp: number = 0;
  private onLocationUpdate?: (data: GPSData) => void;
  private lastSpeed: number | null = null;

  /**
   * Request location permissions (optional - user can deny)
   */
  async requestPermissions(): Promise<boolean> {
    const Location = getLocationModule();
    if (!Location) {
      console.warn('expo-location not available - cannot request permissions');
      return false;
    }
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('Error requesting location permissions:', error);
      return false;
    }
  }

  /**
   * Check if location permissions are granted
   */
  async checkPermissions(): Promise<boolean> {
    const Location = getLocationModule();
    if (!Location) {
      return false;
    }
    try {
      const { status } = await Location.getForegroundPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('Error checking location permissions:', error);
      return false;
    }
  }

  /**
   * Calculate speed from GPS coordinates (distance/time)
   * Uses haversine formula to calculate distance between two GPS points
   */
  private calculateSpeed(
    currentLocation: LocationObject,
    lastLocation: LocationObject | null,
    timeDelta: number
  ): number | null {
    if (!lastLocation || timeDelta <= 0) {
      // Use device-reported speed if available
      return currentLocation.coords.speed ?? null;
    }

    // Haversine formula to calculate distance in meters
    const R = 6371000; // Earth radius in meters
    const dLat = (currentLocation.coords.latitude - lastLocation.coords.latitude) * Math.PI / 180;
    const dLon = (currentLocation.coords.longitude - lastLocation.coords.longitude) * Math.PI / 180;
    const a = 
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lastLocation.coords.latitude * Math.PI / 180) * Math.cos(currentLocation.coords.latitude * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c; // Distance in meters

    const speed = distance / timeDelta; // Speed in m/s
    return speed;
  }

  /**
   * Calculate speed change (acceleration/deceleration) from speed values
   */
  private calculateSpeedChange(
    currentSpeed: number | null,
    previousSpeed: number | null,
    timeDelta: number
  ): number | null {
    if (!currentSpeed || previousSpeed === null || timeDelta <= 0) return null;
    return (currentSpeed - previousSpeed) / timeDelta; // Speed change in m/s²
  }

  /**
   * Start location tracking
   */
  async startTracking(
    onUpdate: (data: GPSData) => void,
    options: any = {}
  ): Promise<boolean> {
    const Location = getLocationModule();
    if (!Location) {
      console.warn('expo-location not available - GPS tracking disabled');
      return false;
    }

    const hasPermission = await this.requestPermissions();
    if (!hasPermission) {
      console.warn('Location permission denied - GPS tracking disabled');
      return false;
    }

    this.onLocationUpdate = onUpdate;

    try {
      this.watchPositionSubscription = await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.Balanced,
          timeInterval: 1000, // Update every 1 second
          distanceInterval: 1, // Update every 1 meter
          ...options,
        },
        (location) => {
          const now = Date.now();
          const timeDelta = this.lastTimestamp > 0 
            ? (now - this.lastTimestamp) / 1000 // Convert to seconds
            : 0;

          const speed = this.calculateSpeed(location, this.lastLocation, timeDelta);
          const speedChange = this.calculateSpeedChange(speed, this.lastSpeed, timeDelta);

          const gpsData: GPSData = {
            latitude: location.coords.latitude,
            longitude: location.coords.longitude,
            altitude: location.coords.altitude,
            accuracy: location.coords.accuracy,
            speed: speed, // Calculated speed in m/s
            speed_change: speedChange, // Speed change in m/s²
            timestamp: new Date(location.timestamp).toISOString(),
          };

          this.onLocationUpdate?.(gpsData);
          this.lastLocation = location;
          this.lastTimestamp = now;
          this.lastSpeed = speed;
        }
      );

      return true;
    } catch (error) {
      console.error('Error starting location tracking:', error);
      return false;
    }
  }

  /**
   * Stop location tracking
   */
  stopTracking(): void {
    if (this.watchPositionSubscription) {
      this.watchPositionSubscription.remove();
      this.watchPositionSubscription = null;
    }
    this.lastLocation = null;
    this.lastTimestamp = 0;
    this.lastSpeed = null;
  }

  /**
   * Get current location (one-time)
   */
  async getCurrentLocation(): Promise<GPSData | null> {
    const Location = getLocationModule();
    if (!Location) {
      return null;
    }

    const hasPermission = await this.checkPermissions();
    if (!hasPermission) return null;

    try {
      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });

      return {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        altitude: location.coords.altitude,
        accuracy: location.coords.accuracy,
        speed: location.coords.speed ?? null, // Use device-reported speed if available
        speed_change: null, // Cannot calculate speed change from single reading
        timestamp: new Date(location.timestamp).toISOString(),
      };
    } catch (error) {
      console.error('Error getting current location:', error);
      return null;
    }
  }
}

