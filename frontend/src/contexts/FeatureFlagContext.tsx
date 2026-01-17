'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import fetchApi from '@/services/api';

interface FeatureFlag {
  id: number;
  key: string;
  name: string;
  description: string | null;
  enabled: boolean;
}

interface FeatureFlagContextType {
  flags: Record<string, boolean>;
  isLoading: boolean;
  refresh: () => Promise<void>;
}

const FeatureFlagContext = createContext<FeatureFlagContextType>({
  flags: {},
  isLoading: true,
  refresh: async () => {},
});

export const useFeatureFlags = () => useContext(FeatureFlagContext);

export const useFeatureFlag = (key: string): boolean => {
  const { flags } = useFeatureFlags();
  return flags[key] ?? false;
};

interface FeatureFlagProviderProps {
  children: ReactNode;
}

export const FeatureFlagProvider: React.FC<FeatureFlagProviderProps> = ({ children }) => {
  const [flags, setFlags] = useState<Record<string, boolean>>({});
  const [isLoading, setIsLoading] = useState(true);

  const fetchFlags = async () => {
    try {
      setIsLoading(true);
      const response = await fetchApi<FeatureFlag[]>('/system/feature-flags');

      if (response.error || !response.data) {
        console.error('Failed to fetch feature flags:', response.error);
        setFlags({});
        return;
      }

      // Convert array to key-value map
      const flagMap: Record<string, boolean> = {};
      response.data.forEach((flag) => {
        flagMap[flag.key] = flag.enabled;
      });

      setFlags(flagMap);
    } catch (error) {
      console.error('Failed to fetch feature flags:', error);
      // Set empty flags on error
      setFlags({});
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchFlags();
  }, []);

  const value = {
    flags,
    isLoading,
    refresh: fetchFlags,
  };

  return (
    <FeatureFlagContext.Provider value={value}>
      {children}
    </FeatureFlagContext.Provider>
  );
};
