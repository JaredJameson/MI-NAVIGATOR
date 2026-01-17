'use client';

import { useState, useEffect } from 'react';

/**
 * Hook to detect online/offline status
 * Uses browser's navigator.onLine API and online/offline events
 */
export function useOnlineStatus(): boolean {
  const [isOnline, setIsOnline] = useState<boolean>(
    typeof window !== 'undefined' ? navigator.onLine : true
  );

  useEffect(() => {
    // Handler for online event
    const handleOnline = () => {
      console.log('[useOnlineStatus] Connection restored - Online');
      setIsOnline(true);
    };

    // Handler for offline event
    const handleOffline = () => {
      console.log('[useOnlineStatus] Connection lost - Offline');
      setIsOnline(false);
    };

    // Add event listeners
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Cleanup
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}
