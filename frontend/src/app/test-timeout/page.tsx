'use client'

import { useState } from 'react'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export default function TestTimeoutPage() {
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [delaySeconds, setDelaySeconds] = useState(30)
  const [timeoutSeconds, setTimeoutSeconds] = useState(10)

  const generateComplexReport = async () => {
    setLoading(true)
    setProgress(0)
    setResult(null)
    setError(null)

    try {
      const token = getStoredToken()
      if (!token) {
        throw new Error('Not authenticated')
      }

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) return prev
          return prev + 10
        })
      }, 1000)

      const controller = new AbortController()
      const timeoutId = setTimeout(() => {
        controller.abort()
      }, timeoutSeconds * 1000)

      try {
        const response = await fetch(
          `${API_BASE_URL}/reports/generate-complex?delay_seconds=${delaySeconds}`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            signal: controller.signal,
          }
        )

        clearTimeout(timeoutId)
        clearInterval(progressInterval)

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const data = await response.json()
        setProgress(100)
        setResult(data)
      } catch (err: any) {
        clearTimeout(timeoutId)
        clearInterval(progressInterval)

        if (err.name === 'AbortError') {
          // Timeout occurred
          setError(`Request timed out after ${timeoutSeconds} seconds`)
          setResult({
            status: 'timeout',
            message: 'Report generation timed out. Partial results may be available.',
            sections_completed: Math.floor(progress / 10),
            total_sections: 10,
            partial_results: {
              summary: 'Partial analysis available',
              completed_sections: ['Market Overview', 'Key Players', 'Revenue Analysis'].slice(0, Math.floor(progress / 30))
            }
          })
        } else {
          throw err
        }
      }
    } catch (err: any) {
      console.error('Error generating report:', err)
      setError(err.message || 'Failed to generate report')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h1 className="text-2xl font-bold mb-6">Test Report Generation Timeout</h1>

          <div className="space-y-4 mb-6">
            <div>
              <label className="block text-sm font-medium mb-2">
                Backend Delay (seconds)
              </label>
              <input
                type="number"
                value={delaySeconds}
                onChange={(e) => setDelaySeconds(parseInt(e.target.value) || 30)}
                className="border rounded px-3 py-2 w-full"
                min="1"
                max="120"
              />
              <p className="text-sm text-gray-500 mt-1">
                How long the backend will take to generate the report
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Frontend Timeout (seconds)
              </label>
              <input
                type="number"
                value={timeoutSeconds}
                onChange={(e) => setTimeoutSeconds(parseInt(e.target.value) || 10)}
                className="border rounded px-3 py-2 w-full"
                min="1"
                max="60"
              />
              <p className="text-sm text-gray-500 mt-1">
                When to abort the request if it takes too long
              </p>
            </div>
          </div>

          <button
            onClick={generateComplexReport}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating...' : 'Generate Complex Report'}
          </button>

          {loading && (
            <div className="mt-6">
              <div className="mb-2 flex justify-between text-sm">
                <span>Progress:</span>
                <span>{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className="bg-blue-600 h-4 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Generating report... This may take a while.
              </p>
            </div>
          )}

          {error && (
            <div className="mt-6 bg-red-50 border border-red-200 rounded p-4">
              <h3 className="font-semibold text-red-800 mb-2">Error</h3>
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {result && (
            <div className="mt-6 bg-gray-50 border border-gray-200 rounded p-4">
              <h3 className="font-semibold mb-2">Result</h3>
              <div className="space-y-2">
                <div>
                  <span className="font-medium">Status:</span>{' '}
                  <span className={result.status === 'completed' ? 'text-green-600' : 'text-yellow-600'}>
                    {result.status}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Message:</span> {result.message}
                </div>
                {result.sections_completed !== undefined && (
                  <div>
                    <span className="font-medium">Sections Completed:</span>{' '}
                    {result.sections_completed}/{result.total_sections}
                  </div>
                )}
                {result.partial_results && (
                  <div className="mt-4">
                    <h4 className="font-medium mb-2">Partial Results Available:</h4>
                    <div className="bg-white p-3 rounded border">
                      <p className="text-sm mb-2">{result.partial_results.summary}</p>
                      {result.partial_results.completed_sections && (
                        <ul className="text-sm list-disc list-inside">
                          {result.partial_results.completed_sections.map((section: string, i: number) => (
                            <li key={i}>{section}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>
                )}
                {result.data && (
                  <div className="mt-4">
                    <h4 className="font-medium mb-2">Full Results:</h4>
                    <div className="bg-white p-3 rounded border">
                      <pre className="text-sm overflow-auto">
                        {JSON.stringify(result.data, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
