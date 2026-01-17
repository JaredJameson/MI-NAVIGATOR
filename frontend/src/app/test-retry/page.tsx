'use client';

import { useState, useEffect, useRef } from 'react';
import { getStoredToken } from '@/services/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Test page for Feature #369: Retry failed operation
 *
 * Tests the ability to:
 * 1. Trigger operation failure
 * 2. Click retry button
 * 3. Verify operation retries
 * 4. Verify success on retry
 */
export default function TestRetryPage() {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('idle');
  const [attempt, setAttempt] = useState<number>(0);
  const [maxAttempts, setMaxAttempts] = useState<number>(3);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [isRetrying, setIsRetrying] = useState<boolean>(false);

  const pollingInterval = useRef<NodeJS.Timeout | null>(null);

  // Start a new retryable task that will fail on first attempt
  const startTask = async () => {
    const token = getStoredToken();
    if (!token) {
      setError('Please login first');
      return;
    }

    try {
      setError(null);
      setResult(null);
      setStatus('starting');
      setAttempt(0);

      const response = await fetch(
        `${API_BASE_URL}/reports/retry-task`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            should_fail_first: true,
            max_attempts: 3
          })
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start task');
      }

      const data = await response.json();
      setTaskId(data.task_id);
      setMaxAttempts(data.max_attempts);
      setAttempt(data.attempt);
      setStatus('running');

      // Start polling for status
      startPolling(data.task_id);
    } catch (err: any) {
      setError(err.message || 'Failed to start task');
      setStatus('error');
    }
  };

  // Retry the failed task
  const retryTask = async () => {
    if (!taskId) return;

    const token = getStoredToken();
    if (!token) {
      setError('Please login first');
      return;
    }

    try {
      setIsRetrying(true);
      setError(null);

      const response = await fetch(
        `${API_BASE_URL}/reports/retry-task/${taskId}/retry`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to retry task');
      }

      const data = await response.json();
      setAttempt(data.attempt);
      setStatus('running');

      // Restart polling
      startPolling(taskId);
    } catch (err: any) {
      setError(err.message || 'Failed to retry task');
    } finally {
      setIsRetrying(false);
    }
  };

  // Start polling for task status
  const startPolling = (taskIdToPoll: string) => {
    // Clear any existing polling interval
    if (pollingInterval.current) {
      clearInterval(pollingInterval.current);
    }

    // Poll every 500ms
    pollingInterval.current = setInterval(async () => {
      await checkStatus(taskIdToPoll);
    }, 500);
  };

  // Stop polling
  const stopPolling = () => {
    if (pollingInterval.current) {
      clearInterval(pollingInterval.current);
      pollingInterval.current = null;
    }
  };

  // Check task status
  const checkStatus = async (taskIdToCheck: string) => {
    const token = getStoredToken();
    if (!token) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/retry-task/${taskIdToCheck}/status`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to get task status');
      }

      const data = await response.json();
      setStatus(data.status);
      setAttempt(data.attempt);
      setMaxAttempts(data.max_attempts);

      if (data.status === 'failed') {
        setError(data.error);
        setResult(null);
        stopPolling();
      } else if (data.status === 'success') {
        setResult(data.result);
        setError(null);
        stopPolling();
      }
    } catch (err: any) {
      console.error('Polling error:', err);
    }
  };

  // Reset to initial state
  const resetState = () => {
    stopPolling();
    setTaskId(null);
    setStatus('idle');
    setAttempt(0);
    setMaxAttempts(3);
    setError(null);
    setResult(null);
    setIsRetrying(false);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, []);

  // Get status badge color
  const getStatusColor = (currentStatus: string) => {
    switch (currentStatus) {
      case 'idle':
        return 'bg-gray-100 text-gray-700';
      case 'starting':
      case 'running':
        return 'bg-blue-100 text-blue-700';
      case 'failed':
        return 'bg-red-100 text-red-700';
      case 'success':
        return 'bg-green-100 text-green-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-4xl px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Test: Retry Failed Operation
          </h1>
          <p className="mt-2 text-gray-600">
            Feature #369: Test retrying failed operations
          </p>
        </div>

        {/* Main Card */}
        <div className="rounded-xl bg-white p-6 shadow-sm">
          {/* Status Section */}
          <div className="mb-6 flex items-center justify-between border-b pb-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Task Status</h2>
              <div className="mt-2 flex items-center gap-4">
                <span className={`rounded-full px-3 py-1 text-sm font-medium ${getStatusColor(status)}`}>
                  {status.toUpperCase()}
                </span>
                {attempt > 0 && (
                  <span className="text-sm text-gray-600">
                    Attempt: {attempt}/{maxAttempts}
                  </span>
                )}
              </div>
            </div>
            {taskId && (
              <div className="text-xs text-gray-500">
                Task ID: {taskId.substring(0, 8)}...
              </div>
            )}
          </div>

          {/* Controls */}
          <div className="mb-6 flex gap-3">
            <button
              onClick={startTask}
              disabled={status === 'running'}
              className="rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
            >
              {status === 'idle' ? 'Start Task (Will Fail)' : 'Start New Task'}
            </button>

            {status === 'failed' && (
              <button
                onClick={retryTask}
                disabled={isRetrying || attempt >= maxAttempts}
                className="rounded-lg bg-orange-600 px-6 py-3 font-medium text-white transition-colors hover:bg-orange-700 disabled:cursor-not-allowed disabled:bg-gray-300"
              >
                {isRetrying ? 'Retrying...' : 'Retry Task'}
              </button>
            )}

            {(status === 'failed' || status === 'success') && (
              <button
                onClick={resetState}
                className="rounded-lg border border-gray-300 bg-white px-6 py-3 font-medium text-gray-700 transition-colors hover:bg-gray-50"
              >
                Reset
              </button>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 rounded-lg bg-red-50 p-4">
              <div className="flex items-start gap-3">
                <svg className="h-5 w-5 flex-shrink-0 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 className="font-medium text-red-800">Operation Failed</h3>
                  <p className="mt-1 text-sm text-red-700">{error}</p>
                  {status === 'failed' && attempt < maxAttempts && (
                    <p className="mt-2 text-sm text-red-600">
                      💡 Click "Retry Task" to attempt again ({maxAttempts - attempt} attempts remaining)
                    </p>
                  )}
                  {attempt >= maxAttempts && (
                    <p className="mt-2 text-sm text-red-600">
                      ❌ Maximum retry attempts reached
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Result Display */}
          {result && status === 'success' && (
            <div className="mb-6 rounded-lg bg-green-50 p-4">
              <div className="flex items-start gap-3">
                <svg className="h-5 w-5 flex-shrink-0 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <div className="flex-1">
                  <h3 className="font-medium text-green-800">Operation Successful</h3>
                  <p className="mt-1 text-sm text-green-700">{result.data}</p>
                  <div className="mt-3 rounded bg-white p-3 text-sm text-gray-700">
                    <p><strong>Completed at:</strong> {new Date(result.timestamp).toLocaleString()}</p>
                    <p><strong>Successful attempt:</strong> {result.attempt}</p>
                    {result.attempt > 1 && (
                      <p className="mt-2 text-green-600">
                        ✅ Task succeeded after retry!
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Loading State */}
          {status === 'running' && (
            <div className="mb-6 rounded-lg border border-blue-200 bg-blue-50 p-4">
              <div className="flex items-center gap-3">
                <svg className="h-5 w-5 animate-spin text-blue-600" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span className="text-sm font-medium text-blue-700">
                  Processing task... (Attempt {attempt}/{maxAttempts})
                </span>
              </div>
            </div>
          )}

          {/* Test Instructions */}
          <div className="mt-8 rounded-lg bg-gray-50 p-4">
            <h3 className="mb-3 font-semibold text-gray-900">Test Steps:</h3>
            <ol className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start gap-2">
                <span className="font-semibold text-blue-600">Step 1:</span>
                <span>Click "Start Task" to trigger an operation that will fail</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-semibold text-blue-600">Step 2:</span>
                <span>Wait for the task to fail (should show error message)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-semibold text-blue-600">Step 3:</span>
                <span>Click "Retry Task" button to retry the operation</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-semibold text-blue-600">Step 4:</span>
                <span>Verify that the task succeeds on retry (green success message)</span>
              </li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
