'use client';

import { useState } from 'react';
import { logError } from '@/services/errorTracking';

/**
 * Test page for error tracking - DO NOT use in production.
 * This page is for testing error boundary and error logging functionality.
 */
export default function TestErrorPage() {
  const [shouldThrow, setShouldThrow] = useState(false);

  if (shouldThrow) {
    // This will trigger the ErrorBoundary
    throw new Error('Test error triggered from TestErrorPage');
  }

  const handleManualError = async () => {
    try {
      // Simulate an error and log it manually
      const error = new Error('Manual test error');
      await logError(error, {
        test: true,
        triggeredBy: 'manual_button_click',
      });
      alert('Error logged successfully! Check the backend logs.');
    } catch (e) {
      console.error('Failed to log error:', e);
    }
  };

  const handleRenderError = () => {
    // This will cause a React render error
    setShouldThrow(true);
  };

  const handleAsyncError = () => {
    // This will trigger an unhandled promise rejection
    Promise.reject(new Error('Unhandled promise rejection test'));
  };

  const handleJavaScriptError = () => {
    // This will trigger a JavaScript runtime error
    // @ts-ignore
    const obj = null;
    // @ts-ignore
    obj.property.nested; // TypeError: Cannot read property 'nested' of null
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white shadow rounded-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Error Tracking Test Page
          </h1>
          <p className="text-gray-600 mb-8">
            Test different types of errors to verify error tracking is working correctly.
          </p>

          <div className="space-y-4">
            <div className="border-l-4 border-yellow-400 bg-yellow-50 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-yellow-700">
                    <strong>Warning:</strong> This page is for testing purposes only.
                    Clicking these buttons will intentionally trigger errors.
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-4">Test Scenarios</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={handleManualError}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors text-left"
                >
                  <div className="font-semibold">1. Manual Error Log</div>
                  <div className="text-sm text-blue-100 mt-1">
                    Log an error manually without throwing
                  </div>
                </button>

                <button
                  onClick={handleRenderError}
                  className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors text-left"
                >
                  <div className="font-semibold">2. React Render Error</div>
                  <div className="text-sm text-red-100 mt-1">
                    Trigger ErrorBoundary with render error
                  </div>
                </button>

                <button
                  onClick={handleAsyncError}
                  className="bg-orange-600 text-white px-6 py-3 rounded-lg hover:bg-orange-700 transition-colors text-left"
                >
                  <div className="font-semibold">3. Unhandled Rejection</div>
                  <div className="text-sm text-orange-100 mt-1">
                    Trigger unhandled promise rejection
                  </div>
                </button>

                <button
                  onClick={handleJavaScriptError}
                  className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors text-left"
                >
                  <div className="font-semibold">4. JavaScript Error</div>
                  <div className="text-sm text-purple-100 mt-1">
                    Trigger TypeError (null reference)
                  </div>
                </button>
              </div>
            </div>

            <div className="bg-gray-100 p-4 rounded-lg mt-8">
              <h3 className="font-semibold text-gray-900 mb-2">How to verify:</h3>
              <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
                <li>Click one of the test buttons above</li>
                <li>Check the browser console for error messages</li>
                <li>Check the backend logs for the error being logged</li>
                <li>Verify the error appears in the database (error_logs table)</li>
                <li>Verify the error includes stack trace and user context</li>
              </ol>
            </div>

            <div className="mt-6">
              <a
                href="/dashboard"
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                ← Back to Dashboard
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
