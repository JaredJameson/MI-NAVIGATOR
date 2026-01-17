'use client';

import { useState, useEffect } from 'react';
import { useOnlineStatus } from '@/hooks/useOnlineStatus';
import { useSyncOnReconnect } from '@/hooks/useSyncOnReconnect';
import { syncQueue } from '@/services/syncQueue';

export default function TestSyncPage() {
  const isOnline = useOnlineStatus();
  const { syncStatus, performSync, pendingCount } = useSyncOnReconnect();
  const [operations, setOperations] = useState<any[]>([]);
  const [formData, setFormData] = useState({ title: '', description: '' });
  const [lastAction, setLastAction] = useState<string>('');

  // Update operations list periodically
  useEffect(() => {
    updateOperationsList();
    const interval = setInterval(updateOperationsList, 1000);
    return () => clearInterval(interval);
  }, []);

  const updateOperationsList = () => {
    setOperations(syncQueue.getPendingOperations());
  };

  const addOfflineOperation = () => {
    if (!formData.title.trim()) {
      setLastAction('❌ Title is required');
      return;
    }

    const id = syncQueue.addOperation('create', '/api/v1/test-data', {
      title: formData.title,
      description: formData.description,
      createdAt: new Date().toISOString(),
    });

    setLastAction(`✅ Added operation ${id} to queue (${isOnline ? 'will sync immediately' : 'will sync when online'})`);
    setFormData({ title: '', description: '' });
    updateOperationsList();

    // If online, trigger sync immediately
    if (isOnline) {
      setTimeout(() => performSync(), 500);
    }
  };

  const manualSync = async () => {
    setLastAction('⏳ Syncing...');
    await performSync();
    setLastAction(`✅ Sync complete: ${syncStatus.successCount} success, ${syncStatus.failedCount} failed`);
    updateOperationsList();
  };

  const clearQueue = () => {
    syncQueue.clearQueue();
    setLastAction('🗑️ Queue cleared');
    updateOperationsList();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">
          Feature #371: Data Sync on Reconnection Test
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Status & Controls */}
          <div className="space-y-6">
            {/* Connection Status */}
            <div className="bg-white shadow-md rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Connection Status</h2>
              <div className="flex items-center gap-3 mb-4">
                <div
                  className={`w-4 h-4 rounded-full ${
                    isOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                  }`}
                />
                <span className="font-medium text-lg">
                  {isOnline ? '🟢 Online' : '🔴 Offline'}
                </span>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Pending operations:</span>
                  <span className="font-semibold">{pendingCount}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Syncing:</span>
                  <span className="font-semibold">
                    {syncStatus.isSyncing ? '✅ Yes' : '❌ No'}
                  </span>
                </div>
                {syncStatus.lastSyncTime && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Last sync:</span>
                    <span className="font-semibold text-xs">
                      {new Date(syncStatus.lastSyncTime).toLocaleTimeString()}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Add Operation Form */}
            <div className="bg-white shadow-md rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Add Operation</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) =>
                      setFormData({ ...formData, title: e.target.value })
                    }
                    placeholder="Enter title..."
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                    placeholder="Enter description..."
                    rows={3}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <button
                  onClick={addOfflineOperation}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Add to Queue
                </button>

                {lastAction && (
                  <div className="mt-3 p-3 bg-gray-100 rounded-lg text-sm">
                    {lastAction}
                  </div>
                )}
              </div>
            </div>

            {/* Manual Controls */}
            <div className="bg-white shadow-md rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Manual Controls</h2>
              <div className="space-y-3">
                <button
                  onClick={manualSync}
                  disabled={!isOnline || syncStatus.isSyncing || pendingCount === 0}
                  className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {syncStatus.isSyncing ? 'Syncing...' : 'Manual Sync'}
                </button>

                <button
                  onClick={clearQueue}
                  disabled={pendingCount === 0}
                  className="w-full bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  Clear Queue
                </button>
              </div>
            </div>
          </div>

          {/* Right Column: Test Instructions & Queue */}
          <div className="space-y-6">
            {/* Test Instructions */}
            <div className="bg-white shadow-md rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Test Instructions</h2>
              <ol className="list-decimal list-inside space-y-3 text-sm text-gray-700">
                <li>
                  <strong>Step 1: Make changes offline</strong>
                  <ul className="ml-6 mt-1 space-y-1 list-disc">
                    <li>Open DevTools (F12) → Network tab</li>
                    <li>Set throttling to "Offline"</li>
                    <li>Add 2-3 operations using the form</li>
                    <li>Verify they appear in the queue below</li>
                  </ul>
                </li>
                <li>
                  <strong>Step 2: Go online</strong>
                  <ul className="ml-6 mt-1 space-y-1 list-disc">
                    <li>Set throttling back to "No throttling"</li>
                    <li>Wait a moment for reconnection</li>
                  </ul>
                </li>
                <li>
                  <strong>Step 3: Verify sync occurs</strong>
                  <ul className="ml-6 mt-1 space-y-1 list-disc">
                    <li>Green banner should appear briefly</li>
                    <li>Automatic sync should trigger</li>
                    <li>Check console for sync logs</li>
                  </ul>
                </li>
                <li>
                  <strong>Step 4: Verify changes persisted</strong>
                  <ul className="ml-6 mt-1 space-y-1 list-disc">
                    <li>Queue should be empty (or reduced)</li>
                    <li>Check "Last sync" timestamp</li>
                    <li>Verify success/failed counts</li>
                  </ul>
                </li>
              </ol>
            </div>

            {/* Pending Operations Queue */}
            <div className="bg-white shadow-md rounded-lg p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Pending Operations</h2>
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
                  {operations.length}
                </span>
              </div>

              {operations.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p className="mb-2">No pending operations</p>
                  <p className="text-sm">Add operations using the form above</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {operations.map((op) => (
                    <div
                      key={op.id}
                      className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-semibold text-sm">{op.data.title}</span>
                        <span className="text-xs bg-gray-200 px-2 py-1 rounded">
                          {op.type.toUpperCase()}
                        </span>
                      </div>
                      {op.data.description && (
                        <p className="text-sm text-gray-600 mb-2">
                          {op.data.description}
                        </p>
                      )}
                      <div className="flex justify-between items-center text-xs text-gray-500">
                        <span>
                          {new Date(op.timestamp).toLocaleTimeString()}
                        </span>
                        {op.retries > 0 && (
                          <span className="text-orange-600 font-semibold">
                            Retries: {op.retries}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Console Alternative */}
        <div className="mt-6 bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Console Testing</h2>
          <p className="text-gray-700 mb-3 text-sm">
            Alternatively, test offline/online simulation via console:
          </p>
          <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm space-y-2">
            <p>// Simulate going offline</p>
            <p className="text-yellow-300">window.dispatchEvent(new Event('offline'));</p>
            <p className="mt-4">// Simulate going online</p>
            <p className="text-yellow-300">window.dispatchEvent(new Event('online'));</p>
          </div>
        </div>
      </div>
    </div>
  );
}
