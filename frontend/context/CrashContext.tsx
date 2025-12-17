/** Crash context for crash alert UI state. */

import React, { createContext, useContext, useState } from 'react';
import { ThresholdResult } from '@/types/crash';

interface CrashContextType {
  lastCrashAlert: ThresholdResult | null;
  isProcessing: boolean;
  setLastCrashAlert: (alert: ThresholdResult | null) => void;
  setProcessing: (processing: boolean) => void;
}

const CrashContext = createContext<CrashContextType | undefined>(undefined);

export function CrashProvider({ children }: { children: React.ReactNode }) {
  const [lastCrashAlert, setLastCrashAlert] = useState<ThresholdResult | null>(null);
  const [isProcessing, setProcessing] = useState(false);

  return (
    <CrashContext.Provider
      value={{
        lastCrashAlert,
        isProcessing,
        setLastCrashAlert,
        setProcessing,
      }}
    >
      {children}
    </CrashContext.Provider>
  );
}

export function useCrash() {
  const context = useContext(CrashContext);
  if (!context) {
    throw new Error('useCrash must be used within CrashProvider');
  }
  return context;
}

