/**
 * Hook to automatically sync pending operations when connection is restored
 */

'use client';

import { useEffect, useRef, useState } from 'react';
import { useOnlineStatus } from './useOnlineStatus';
import { syncQueue } from '@/services/syncQueue';

export interface SyncStatus {
  isSyncing: boolean;
  lastSyncTime: number | null;
  successCount: number;
  failedCount: number;
}

export function useSyncOnReconnect() {
  const isOnline = useOnlineStatus();
  const previousOnlineStatus = useRef(isOnline);
  const [syncStatus, setSyncStatus] = useState<SyncStatus>({
    isSyncing: false,
    lastSyncTime: null,
    successCount: 0,
    failedCount: 0,
  });

  useEffect(() => {
    const wasOffline = !previousOnlineStatus.current;
    const isNowOnline = isOnline;

    // Trigger sync when transitioning from offline to online
    if (wasOffline && isNowOnline) {
      console.log('[useSyncOnReconnect] Connection restored, triggering sync');
      performSync();
    }

    previousOnlineStatus.current = isOnline;
  }, [isOnline]);

  const performSync = async () => {
    setSyncStatus(prev => ({ ...prev, isSyncing: true }));

    try {
      const result = await syncQueue.syncAll();

      setSyncStatus({
        isSyncing: false,
        lastSyncTime: Date.now(),
        successCount: result.success,
        failedCount: result.failed,
      });

      console.log('[useSyncOnReconnect] Sync completed:', result);
    } catch (error) {
      console.error('[useSyncOnReconnect] Sync error:', error);
      setSyncStatus(prev => ({ ...prev, isSyncing: false }));
    }
  };

  return {
    syncStatus,
    performSync,
    pendingCount: syncQueue.getPendingCount(),
  };
}
