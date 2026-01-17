'use client';

import { useSyncOnReconnect } from '@/hooks/useSyncOnReconnect';
import { useEffect } from 'react';

/**
 * SyncManager - Handles automatic data synchronization on reconnection
 * This component uses the useSyncOnReconnect hook to monitor online/offline
 * status and automatically sync pending operations when connection is restored.
 */
export function SyncManager() {
  const { syncStatus, pendingCount } = useSyncOnReconnect();

  useEffect(() => {
    if (syncStatus.lastSyncTime) {
      console.log('[SyncManager] Sync completed:', {
        success: syncStatus.successCount,
        failed: syncStatus.failedCount,
        remaining: pendingCount,
      });
    }
  }, [syncStatus, pendingCount]);

  // This component doesn't render anything - it just manages sync in the background
  return null;
}
