/**
 * Sync Queue Service
 * Manages pending operations that should be synced when connection is restored
 */

export interface PendingOperation {
  id: string;
  type: 'create' | 'update' | 'delete';
  endpoint: string;
  data: any;
  timestamp: number;
  retries: number;
}

const STORAGE_KEY = 'mi_sync_queue';
const MAX_RETRIES = 3;

class SyncQueueService {
  private queue: PendingOperation[] = [];
  private isSyncing = false;

  constructor() {
    this.loadQueue();
  }

  /**
   * Load queue from localStorage
   */
  private loadQueue(): void {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        this.queue = JSON.parse(stored);
        console.log(`[SyncQueue] Loaded ${this.queue.length} pending operations`);
      }
    } catch (error) {
      console.error('[SyncQueue] Failed to load queue:', error);
      this.queue = [];
    }
  }

  /**
   * Save queue to localStorage
   */
  private saveQueue(): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.queue));
    } catch (error) {
      console.error('[SyncQueue] Failed to save queue:', error);
    }
  }

  /**
   * Add operation to queue
   */
  public addOperation(
    type: 'create' | 'update' | 'delete',
    endpoint: string,
    data: any
  ): string {
    const operation: PendingOperation = {
      id: `op_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      endpoint,
      data,
      timestamp: Date.now(),
      retries: 0,
    };

    this.queue.push(operation);
    this.saveQueue();

    console.log(`[SyncQueue] Added operation:`, operation);
    return operation.id;
  }

  /**
   * Get all pending operations
   */
  public getPendingOperations(): PendingOperation[] {
    return [...this.queue];
  }

  /**
   * Get count of pending operations
   */
  public getPendingCount(): number {
    return this.queue.length;
  }

  /**
   * Sync all pending operations
   * Returns number of successfully synced operations
   */
  public async syncAll(): Promise<{ success: number; failed: number }> {
    if (this.isSyncing) {
      console.log('[SyncQueue] Sync already in progress, skipping');
      return { success: 0, failed: 0 };
    }

    if (this.queue.length === 0) {
      console.log('[SyncQueue] No pending operations to sync');
      return { success: 0, failed: 0 };
    }

    this.isSyncing = true;
    console.log(`[SyncQueue] Starting sync of ${this.queue.length} operations`);

    let successCount = 0;
    let failedCount = 0;

    // Process operations one by one
    const operationsToProcess = [...this.queue];
    this.queue = [];

    for (const operation of operationsToProcess) {
      try {
        const success = await this.syncOperation(operation);
        if (success) {
          successCount++;
          console.log(`[SyncQueue] Synced operation ${operation.id}`);
        } else {
          // Re-add to queue if max retries not reached
          if (operation.retries < MAX_RETRIES) {
            operation.retries++;
            this.queue.push(operation);
            console.log(`[SyncQueue] Retry ${operation.retries}/${MAX_RETRIES} for operation ${operation.id}`);
          } else {
            failedCount++;
            console.error(`[SyncQueue] Operation ${operation.id} failed after ${MAX_RETRIES} retries`);
          }
        }
      } catch (error) {
        console.error(`[SyncQueue] Error syncing operation ${operation.id}:`, error);
        // Re-add to queue if max retries not reached
        if (operation.retries < MAX_RETRIES) {
          operation.retries++;
          this.queue.push(operation);
        } else {
          failedCount++;
        }
      }
    }

    this.saveQueue();
    this.isSyncing = false;

    console.log(`[SyncQueue] Sync complete: ${successCount} success, ${failedCount} failed, ${this.queue.length} remaining`);

    return { success: successCount, failed: failedCount };
  }

  /**
   * Sync a single operation
   */
  private async syncOperation(operation: PendingOperation): Promise<boolean> {
    try {
      const method = this.getHttpMethod(operation.type);
      const response = await fetch(operation.endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: operation.type !== 'delete' ? JSON.stringify(operation.data) : undefined,
      });

      return response.ok;
    } catch (error) {
      console.error(`[SyncQueue] Failed to sync operation:`, error);
      return false;
    }
  }

  /**
   * Get HTTP method for operation type
   */
  private getHttpMethod(type: 'create' | 'update' | 'delete'): string {
    switch (type) {
      case 'create':
        return 'POST';
      case 'update':
        return 'PUT';
      case 'delete':
        return 'DELETE';
    }
  }

  /**
   * Clear all pending operations
   */
  public clearQueue(): void {
    this.queue = [];
    this.saveQueue();
    console.log('[SyncQueue] Queue cleared');
  }

  /**
   * Remove specific operation
   */
  public removeOperation(id: string): boolean {
    const initialLength = this.queue.length;
    this.queue = this.queue.filter(op => op.id !== id);

    if (this.queue.length < initialLength) {
      this.saveQueue();
      console.log(`[SyncQueue] Removed operation ${id}`);
      return true;
    }

    return false;
  }
}

// Export singleton instance
export const syncQueue = new SyncQueueService();
