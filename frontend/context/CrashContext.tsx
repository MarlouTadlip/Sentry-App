/** Crash context for crash alert UI state. */

import React, { createContext, useContext, useState } from 'react';
import { ThresholdResult } from '@/types/crash';
import { CrashAlertResponse } from '@/types/api';

interface CrashContextType {
  lastCrashAlert: ThresholdResult | null;
  aiResponse: CrashAlertResponse | null;
  crashEventId: number | null;
  isProcessing: boolean;
  setLastCrashAlert: (alert: ThresholdResult | null) => void;
  setAIResponse: (response: CrashAlertResponse | null) => void;
  setCrashEventId: (id: number | null) => void;
  setProcessing: (processing: boolean) => void;
}

const CrashContext = createContext<CrashContextType | undefined>(undefined);

export function CrashProvider({ children }: { children: React.ReactNode }) {
  const [lastCrashAlert, setLastCrashAlert] = useState<ThresholdResult | null>(null);
  const [aiResponse, setAIResponse] = useState<CrashAlertResponse | null>(null);
  const [crashEventId, setCrashEventId] = useState<number | null>(null);
  const [isProcessing, setProcessing] = useState(false);

  return (
    <CrashContext.Provider
      value={{
        lastCrashAlert,
        aiResponse,
        crashEventId,
        isProcessing,
        setLastCrashAlert,
        setAIResponse,
        setCrashEventId,
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

