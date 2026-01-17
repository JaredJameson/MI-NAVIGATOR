'use client'

import { useState } from 'react'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface ProgressState {
  task_id: string
  status: 'processing' | 'completed' | 'failed'
  total: number
  processed: number
  percentage: number
  result?: string
  error?: string
}

export default function TestBatchProgressPage() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState<ProgressState | null>(null)
  const [completionMessage, setCompletionMessage] = useState('')

  // Simulate starting a batch operation
  const startBatchOperation = async () => {
    const token = getStoredToken()
    if (!token) {
      alert('Please login first')
      return
    }

    setIsProcessing(true)
    setProgress(null)
    setCompletionMessage('')

    try {
      // Start bulk export with 10 mock report IDs
      const mockReportIds = Array.from({ length: 10 }, (_, i) => `report_${i + 1}`)

      const response = await fetch(`${API_BASE_URL}/reports/bulk-export-async`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          report_ids: mockReportIds,
          format: 'xlsx'
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to start batch operation')
      }

      const data = await response.json()
      const taskId = data.task_id

      // Poll for progress every 500ms
      const pollInterval = setInterval(async () => {
        try {
          const progressResponse = await fetch(
            `${API_BASE_URL}/reports/bulk-export-progress/${taskId}`,
            {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            }
          )

          if (progressResponse.ok) {
            const progressData = await progressResponse.json()
            setProgress(progressData)

            // Stop polling when completed or failed
            if (progressData.status === 'completed' || progressData.status === 'failed') {
              clearInterval(pollInterval)
              setIsProcessing(false)

              if (progressData.status === 'completed') {
                setCompletionMessage(progressData.result || 'Batch operation completed!')
              } else {
                setCompletionMessage(`Failed: ${progressData.error}`)
              }
            }
          }
        } catch (error) {
          console.error('Error polling progress:', error)
          clearInterval(pollInterval)
          setIsProcessing(false)
        }
      }, 500)

    } catch (error) {
      console.error('Error starting batch operation:', error)
      setIsProcessing(false)
      alert('Failed to start batch operation')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-2xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Test: Batch Operation Progress Tracking
          </h1>
          <p className="mt-2 text-gray-600">
            Feature #367 - Progress tracking for batch operations
          </p>
        </div>

        {/* Start Button */}
        <div className="mb-8">
          <button
            onClick={startBatchOperation}
            disabled={isProcessing}
            className="rounded-lg bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isProcessing ? 'Processing...' : 'Start Batch Export (10 items)'}
          </button>
        </div>

        {/* Progress Display */}
        {progress && (
          <div className="rounded-lg bg-white p-6 shadow-md">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Export Progress
            </h2>

            {/* Progress Bar */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Progress
                </span>
                <span className="text-sm font-bold text-blue-600">
                  {progress.percentage}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                <div
                  className="bg-blue-600 h-full rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${progress.percentage}%` }}
                />
              </div>
            </div>

            {/* Item Count */}
            <div className="mb-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Items processed:</span>
                <span className="font-semibold text-gray-900">
                  {progress.processed} / {progress.total}
                </span>
              </div>
            </div>

            {/* Status */}
            <div className="mb-4">
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Status:</span>
                <span
                  className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${
                    progress.status === 'completed'
                      ? 'bg-green-100 text-green-800'
                      : progress.status === 'failed'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-blue-100 text-blue-800'
                  }`}
                >
                  {progress.status === 'processing' && (
                    <div className="h-2 w-2 animate-spin rounded-full border border-blue-600 border-t-transparent" />
                  )}
                  {progress.status === 'completed' && '✓'}
                  {progress.status === 'failed' && '✕'}
                  <span className="capitalize">{progress.status}</span>
                </span>
              </div>
            </div>

            {/* Task ID (for debugging) */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                Task ID: {progress.task_id}
              </p>
            </div>
          </div>
        )}

        {/* Completion Notification */}
        {completionMessage && (
          <div
            className={`mt-6 rounded-lg p-4 ${
              completionMessage.includes('Failed')
                ? 'bg-red-50 text-red-800'
                : 'bg-green-50 text-green-800'
            }`}
          >
            <div className="flex items-center gap-2">
              <span className="text-xl">
                {completionMessage.includes('Failed') ? '❌' : '✅'}
              </span>
              <span className="font-medium">{completionMessage}</span>
            </div>
          </div>
        )}

        {/* Test Steps Documentation */}
        <div className="mt-12 rounded-lg bg-blue-50 p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">
            Test Steps (Feature #367):
          </h3>
          <ol className="list-decimal list-inside space-y-2 text-sm text-blue-800">
            <li>✅ Step 1: Start batch operation (click button above)</li>
            <li>✅ Step 2: Verify progress bar appears</li>
            <li>✅ Step 3: Verify percentage updates (0% → 100%)</li>
            <li>✅ Step 4: Verify item count shown (0/10 → 10/10)</li>
            <li>✅ Step 5: Verify completion notification (green success message)</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
