'use client'

import Link from 'next/link'
import { useEffect } from 'react'
import { logError } from '@/services/errorTracking'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log error to backend error tracking system
    console.error('Application error:', error)
    logError(error, {
      type: 'react_error_boundary',
      digest: error.digest,
      component: 'ErrorBoundary',
    })
  }, [error])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-red-50 to-orange-100 px-4">
      <div className="w-full max-w-md text-center">
        {/* Error Icon */}
        <div className="mb-8">
          <div className="mx-auto flex h-32 w-32 items-center justify-center rounded-full bg-red-100">
            <svg
              className="h-16 w-16 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
        </div>

        {/* Error Code */}
        <h1 className="mb-4 text-7xl font-bold text-gray-800">500</h1>

        {/* Error Message */}
        <h2 className="mb-2 text-2xl font-semibold text-gray-700">
          Something Went Wrong
        </h2>
        <p className="mb-8 text-gray-600">
          We're sorry, but something unexpected happened. Our team has been notified and is working on it.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col gap-3">
          <button
            onClick={reset}
            className="rounded-lg bg-red-600 px-6 py-3 font-medium text-white transition-colors hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          >
            Try Again
          </button>
          <Link
            href="/dashboard"
            className="rounded-lg border border-gray-300 bg-white px-6 py-3 font-medium text-gray-700 transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          >
            Go to Dashboard
          </Link>
          <button
            onClick={() => window.history.back()}
            className="rounded-lg px-6 py-3 font-medium text-gray-600 transition-colors hover:text-gray-800 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          >
            ← Go Back
          </button>
        </div>

        {/* Contact Support */}
        <div className="mt-8 border-t border-gray-200 pt-6">
          <p className="mb-3 text-sm text-gray-500">Need help?</p>
          <div className="flex flex-col gap-2 text-sm">
            <a
              href="mailto:support@mi-navigator.com"
              className="text-red-600 hover:underline focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              Contact Support
            </a>
            <Link
              href="/help"
              className="text-red-600 hover:underline focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              Help Center
            </Link>
            <Link
              href="/reports"
              className="text-gray-600 hover:underline focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              View Reports
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
