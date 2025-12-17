/** Device context for BLE connection state. */

import React, { createContext, useContext, useState, useCallback, useRef } from 'react';
import { SensorReading } from '@/types/device';
import { BLEManager } from '@/services/bluetooth/bleManager';

interface DeviceContextType {
  isConnected: boolean;
  currentReading: SensorReading | null;
  connect: (deviceId: string) => Promise<boolean>;
  disconnect: () => Promise<void>;
  startReceiving: () => void;
  stopReceiving: () => void;
}

const DeviceContext = createContext<DeviceContextType | undefined>(undefined);

export function DeviceProvider({ children }: { children: React.ReactNode }) {
  const [isConnected, setIsConnected] = useState(false);
  const [currentReading, setCurrentReading] = useState<SensorReading | null>(null);
  const bleManagerRef = useRef<BLEManager | null>(null);

  // Initialize BLE manager
  if (!bleManagerRef.current) {
    bleManagerRef.current = new BLEManager();
  }

  const connect = useCallback(async (deviceId: string) => {
    if (!bleManagerRef.current) return false;
    
    const connected = await bleManagerRef.current.connect(deviceId);
    setIsConnected(connected);
    return connected;
  }, []);

  const disconnect = useCallback(async () => {
    if (!bleManagerRef.current) return;
    
    await bleManagerRef.current.disconnect();
    setIsConnected(false);
    setCurrentReading(null);
  }, []);

  const startReceiving = useCallback(() => {
    if (!bleManagerRef.current) return;
    
    bleManagerRef.current.setDataCallback((data: SensorReading) => {
      setCurrentReading(data);
    });
  }, []);

  const stopReceiving = useCallback(() => {
    if (!bleManagerRef.current) return;
    
    bleManagerRef.current.setDataCallback(() => {});
  }, []);

  return (
    <DeviceContext.Provider
      value={{
        isConnected,
        currentReading,
        connect,
        disconnect,
        startReceiving,
        stopReceiving,
      }}
    >
      {children}
    </DeviceContext.Provider>
  );
}

export function useDevice() {
  const context = useContext(DeviceContext);
  if (!context) {
    throw new Error('useDevice must be used within DeviceProvider');
  }
  return context;
}

