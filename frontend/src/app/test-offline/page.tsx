'use client';

import { useState } from 'react';
import { useOnlineStatus } from '@/hooks/useOnlineStatus';

export default function TestOfflinePage() {
  const isOnline = useOnlineStatus();
  const [actionMessage, setActionMessage] = useState<string>('');

  const handleAction = async () => {
    if (!isOnline) {
      setActionMessage('❌ Cannot perform action - You are offline');
      return;
    }

    setActionMessage('⏳ Performing action...');

    try {
      // Simulate API call
      const response = await fetch('/api/v1/users/me');
      if (response.ok) {
        setActionMessage('✅ Action completed successfully');
      } else {
        setActionMessage(`❌ Action failed - Status: ${response.status}`);
      }
    } catch (error) {
      setActionMessage('❌ Action failed - Network error');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">
          Feature #370: Offline Indicator Test
        </h1>

        <div className="bg-white shadow-md rounded-lg p-6 space-y-6">
          {/* Current Status */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Current Connection Status</h2>
            <div className="flex items-center gap-3">
              <div
                className={`w-4 h-4 rounded-full ${
                  isOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                }`}
              />
              <span className="font-medium">
                {isOnline ? '🟢 Online' : '🔴 Offline'}
              </span>
            </div>
          </div>

          {/* Test Instructions */}
          <div className="border-t pt-6">
            <h2 className="text-xl font-semibold mb-4">Test Instructions</h2>
            <ol className="list-decimal list-inside space-y-2 text-gray-700">
              <li>
                <strong>Step 1: Go offline</strong> - Open Chrome DevTools (F12)
                → Network tab → Set throttling to "Offline"
              </li>
              <li>
                <strong>Step 2: Verify offline indicator appears</strong> - Red
                banner should appear at the top
              </li>
              <li>
                <strong>Step 3: Attempt action</strong> - Click button below
              </li>
              <li>
                <strong>Step 4: Verify appropriate message</strong> - Should show
                "Cannot perform action - You are offline"
              </li>
              <li>
                <strong>Step 5: Go online</strong> - Set throttling back to "No
                throttling"
              </li>
              <li>
                <strong>Step 6: Verify indicator disappears</strong> - Red banner
                should disappear, green "Connected" banner should briefly appear
              </li>
            </ol>
          </div>

          {/* Action Button */}
          <div className="border-t pt-6">
            <h2 className="text-xl font-semibold mb-4">Action Test</h2>
            <button
              onClick={handleAction}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
              disabled={!isOnline}
            >
              Perform API Action
            </button>
            {actionMessage && (
              <div className="mt-4 p-4 bg-gray-100 rounded-lg">
                <p className="text-sm font-mono">{actionMessage}</p>
              </div>
            )}
          </div>

          {/* Alternative Testing Method */}
          <div className="border-t pt-6">
            <h2 className="text-xl font-semibold mb-4">
              Alternative Testing (Console)
            </h2>
            <p className="text-gray-700 mb-3">
              You can also test by running this in the browser console:
            </p>
            <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm">
              <p>// Simulate going offline</p>
              <p>
                window.dispatchEvent(new Event('offline'));
              </p>
              <br />
              <p>// Simulate going back online</p>
              <p>
                window.dispatchEvent(new Event('online'));
              </p>
            </div>
          </div>

          {/* Status History */}
          <div className="border-t pt-6">
            <h2 className="text-xl font-semibold mb-4">Technical Details</h2>
            <div className="space-y-2 text-sm text-gray-600">
              <p>
                <strong>API Used:</strong> navigator.onLine + online/offline events
              </p>
              <p>
                <strong>Hook:</strong> useOnlineStatus()
              </p>
              <p>
                <strong>Component:</strong> OfflineIndicator (global in Providers)
              </p>
              <p>
                <strong>Indicator Position:</strong> Fixed top, z-index 50
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
