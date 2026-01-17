'use client';

import { useState, useEffect } from 'react';
import fetchApi from '@/services/api';
import { useFeatureFlags } from '@/contexts/FeatureFlagContext';

interface FeatureFlag {
  id: number;
  key: string;
  name: string;
  description: string | null;
  enabled: boolean;
}

export default function FeatureFlagsPage() {
  const [flags, setFlags] = useState<FeatureFlag[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [updatingKey, setUpdatingKey] = useState<string | null>(null);
  const { refresh } = useFeatureFlags();

  const loadFlags = async () => {
    try {
      setIsLoading(true);
      setError('');
      const response = await fetchApi<FeatureFlag[]>('/system/feature-flags');

      if (response.error || !response.data) {
        setError(response.error || 'Failed to load feature flags');
        setFlags([]);
        return;
      }

      setFlags(response.data);
    } catch (err: any) {
      console.error('Failed to load feature flags:', err);
      setError(err.message || 'Failed to load feature flags');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadFlags();
  }, []);

  const toggleFlag = async (key: string, currentValue: boolean) => {
    try {
      setUpdatingKey(key);
      setError('');

      await fetchApi(`/system/feature-flags/${key}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !currentValue }),
      });

      // Reload flags
      await loadFlags();

      // Refresh global context
      await refresh();
    } catch (err: any) {
      console.error(`Failed to toggle flag ${key}:`, err);
      setError(err.message || `Failed to toggle ${key}`);
    } finally {
      setUpdatingKey(null);
    }
  };

  if (isLoading) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-6">Feature Flags</h1>
        <p className="text-gray-600">Loading feature flags...</p>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Feature Flags</h1>
        <p className="text-gray-600">
          Control which features are visible and enabled in the application
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <div className="bg-white rounded-lg shadow">
        <div className="p-6 space-y-6">
          {flags.map((flag) => (
            <div
              key={flag.key}
              className="flex items-start justify-between p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">{flag.name}</h3>
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded-full ${
                      flag.enabled
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {flag.enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>

                <p className="text-sm text-gray-600 mb-2">Key: <code className="bg-gray-100 px-2 py-1 rounded">{flag.key}</code></p>

                {flag.description && (
                  <p className="text-sm text-gray-500">{flag.description}</p>
                )}
              </div>

              <button
                onClick={() => toggleFlag(flag.key, flag.enabled)}
                disabled={updatingKey === flag.key}
                className={`ml-4 px-4 py-2 rounded-lg font-medium transition-colors ${
                  flag.enabled
                    ? 'bg-red-600 text-white hover:bg-red-700'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {updatingKey === flag.key ? (
                  'Updating...'
                ) : flag.enabled ? (
                  'Disable'
                ) : (
                  'Enable'
                )}
              </button>
            </div>
          ))}

          {flags.length === 0 && !isLoading && (
            <p className="text-center text-gray-500 py-8">No feature flags found</p>
          )}
        </div>
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="font-semibold text-blue-900 mb-2">How it works:</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Feature flags control visibility of features across the application</li>
          <li>• Changes take effect immediately after toggling</li>
          <li>• Refresh the page to see feature visibility changes</li>
          <li>• Only admin users can manage feature flags</li>
        </ul>
      </div>
    </div>
  );
}
