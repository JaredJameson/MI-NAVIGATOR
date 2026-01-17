'use client';

import { useState, useEffect, useRef } from 'react';
import { getStoredToken } from '@/services/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Test page for Feature #368: Cancel long-running operation
 *
 * Tests the ability to:
 * 1. Start a long-running task
 * 2. Cancel the task mid-execution
 * 3. View partial results
 * 4. Restore clean state
 */
export default function TestCancelPage() {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('idle');
  const [progress, setProgress] = useState<number>(0);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [totalSteps, setTotalSteps] = useState<number>(10);
  const [result, setResult] = useState<any>(null);
  const [isCancelling, setIsCancelling] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const pollingInterval = useRef<NodeJS.Timeout | null>(null);

  // Start a new cancellable task
  const startTask = async () => {
    const token = getStoredToken();
    if (!token) {
      setError('Please login first');
      return;
    }

    try {
      setError(null);
      setResult(null);
      setProgress(0);
      setCurrentStep(0);
      setStatus('starting');

      const response = await fetch(
        `${API_BASE_URL}/reports/cancellable-task?total_steps=10&step_duration=2`,
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
        throw new Error(errorData.detail || 'Failed to start task');
      }

      const data = await response.json();
      setTaskId(data.task_id);
      setTotalSteps(data.total_steps);
      setStatus('running');

      // Start polling for progress
      startPolling(data.task_id);
    } catch (err: any) {
      setError(err.message || 'Failed to start task');
      setStatus('error');
    }
  };

  // Cancel the running task
  const cancelTask = async () => {
    if (!taskId) return;

    const token = getStoredToken();
    if (!token) {
      setError('Please login first');
      return;
    }

    try {
      setIsCancelling(true);
      setError(null);

      const response = await fetch(
        `${API_BASE_URL}/reports/cancellable-task/${taskId}/cancel`,
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
        throw new Error(errorData.detail || 'Failed to cancel task');
      }

      // Don't stop polling yet - wait for status to change to 'cancelled'
      // The backend will update the status after current step completes
    } catch (err: any) {
      setError(err.message || 'Failed to cancel task');
    } finally {
      setIsCancelling(false);
    }
  };

  // Poll for task status
  const startPolling = (task_id: string) => {
    if (pollingInterval.current) {
      clearInterval(pollingInterval.current);
    }

    pollingInterval.current = setInterval(async () => {
      const token = getStoredToken();
      if (!token) {
        console.error('No token available for polling');
        return;
      }

      try {
        const response = await fetch(
          `${API_BASE_URL}/reports/cancellable-task/${task_id}/status`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          console.error('Failed to poll status:', response.status);
          return;
        }

        const data = await response.json();

        setStatus(data.status);
        setProgress(data.progress);
        setCurrentStep(data.current_step);
        setTotalSteps(data.total_steps);

        if (data.result) {
          setResult(data.result);
        }

        // Stop polling if task finished
        if (data.status === 'completed' || data.status === 'cancelled' || data.status === 'error') {
          if (pollingInterval.current) {
            clearInterval(pollingInterval.current);
            pollingInterval.current = null;
          }
        }
      } catch (err: any) {
        console.error('Error polling task status:', err);
        // Don't stop polling on error - backend might be reloading
      }
    }, 500);  // Poll every 500ms
  };

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
      }
    };
  }, []);

  // Reset to clean state
  const resetState = () => {
    if (pollingInterval.current) {
      clearInterval(pollingInterval.current);
      pollingInterval.current = null;
    }

    setTaskId(null);
    setStatus('idle');
    setProgress(0);
    setCurrentStep(0);
    setTotalSteps(10);
    setResult(null);
    setIsCancelling(false);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow p-6">
          <h1 className="text-2xl font-bold mb-2">Test: Cancel Long-Running Operation</h1>
          <p className="text-gray-600 mb-6">Feature #368 - Test cancelling tasks in progress</p>

          {/* Control Buttons */}
          <div className="flex gap-3 mb-6">
            <button
              onClick={startTask}
              disabled={status === 'running' || status === 'starting'}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {status === 'starting' ? 'Starting...' : 'Start Long Operation'}
            </button>

            <button
              onClick={cancelTask}
              disabled={status !== 'running' || isCancelling}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isCancelling ? 'Cancelling...' : 'Cancel Operation'}
            </button>

            <button
              onClick={resetState}
              disabled={status === 'running'}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Reset State
            </button>
          </div>

          {/* Status Display */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Status:</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                status === 'idle' ? 'bg-gray-100 text-gray-700' :
                status === 'running' || status === 'starting' ? 'bg-blue-100 text-blue-700' :
                status === 'completed' ? 'bg-green-100 text-green-700' :
                status === 'cancelled' ? 'bg-yellow-100 text-yellow-700' :
                'bg-red-100 text-red-700'
              }`}>
                {status === 'running' && isCancelling ? 'cancelling...' : status}
              </span>
            </div>

            {taskId && (
              <div className="text-xs text-gray-500 mb-3">
                Task ID: {taskId}
              </div>
            )}

            {/* Progress Bar */}
            {status === 'running' && (
              <div className="mb-3">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Progress: {progress}%</span>
                  <span>Step {currentStep} of {totalSteps}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                  <div
                    className="h-full bg-blue-600 transition-all duration-300 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                <strong>Error:</strong> {error}
              </div>
            )}
          </div>

          {/* Result Display */}
          {result && (
            <div className="border-t pt-4">
              <h2 className="text-lg font-semibold mb-3">Result:</h2>

              <div className={`p-4 rounded-lg ${
                status === 'completed' ? 'bg-green-50 border border-green-200' :
                status === 'cancelled' ? 'bg-yellow-50 border border-yellow-200' :
                'bg-red-50 border border-red-200'
              }`}>
                <p className="font-medium mb-2">{result.message}</p>
                <p className="text-sm text-gray-600 mb-3">
                  Completed {result.completed_steps} of {result.total_steps} steps
                </p>

                {/* Partial Data */}
                {result.partial_data && result.partial_data.length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-gray-700 mb-2">Partial Results:</p>
                    <div className="bg-white p-3 rounded border max-h-40 overflow-y-auto">
                      <ul className="text-sm space-y-1">
                        {result.partial_data.map((item: string, idx: number) => (
                          <li key={idx} className="text-gray-600">✓ {item}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Final Data */}
                {result.final_data && result.final_data.length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-gray-700 mb-2">Complete Results:</p>
                    <div className="bg-white p-3 rounded border max-h-40 overflow-y-auto">
                      <ul className="text-sm space-y-1">
                        {result.final_data.map((item: string, idx: number) => (
                          <li key={idx} className="text-gray-600">✓ {item}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Test Instructions */}
          <div className="mt-6 border-t pt-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Test Steps:</h3>
            <ol className="text-sm text-gray-600 space-y-1 list-decimal list-inside">
              <li>Click "Start Long Operation" to begin a 10-step task</li>
              <li>Wait for a few steps to complete (watch progress bar)</li>
              <li>Click "Cancel Operation" to stop the task</li>
              <li>Verify that the task stops after current step completes</li>
              <li>Check partial results are displayed</li>
              <li>Click "Reset State" to restore clean state</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
