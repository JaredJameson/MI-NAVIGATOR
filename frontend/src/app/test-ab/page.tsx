'use client'

/**
 * A/B Testing Demo Page
 * Demonstrates A/B test variant assignment and tracking
 */

import { useABTest } from '@/hooks/useABTest'
import { useState } from 'react'

export default function ABTestPage() {
  const { variant, isLoading, error, track, variantData } = useABTest('hero_design_test')
  const [events, setEvents] = useState<string[]>([])

  const handleTrackClick = async () => {
    await track('button_click')
    setEvents(prev => [...prev, `Clicked button (Variant ${variant})`])
  }

  const handleTrackConversion = async () => {
    await track('conversion')
    setEvents(prev => [...prev, `Conversion event (Variant ${variant})`])
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Assigning A/B test variant...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h2 className="text-red-800 font-semibold mb-2">A/B Test Error</h2>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">A/B Testing Demo</h1>
          <p className="text-gray-600">Testing variant assignment and event tracking</p>
        </div>

        {/* Variant Assignment */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Assigned Variant</h2>
          <div className="flex items-center space-x-4">
            <div className={`text-6xl font-bold ${variant === 'A' ? 'text-blue-600' : 'text-green-600'}`}>
              {variant}
            </div>
            <div className="flex-1">
              <p className="text-gray-600 mb-2">
                You have been assigned to <strong>Variant {variant}</strong> for the experiment <code className="bg-gray-100 px-2 py-1 rounded">{variantData?.experiment}</code>
              </p>
              <p className="text-sm text-gray-500">
                Session ID: <code className="bg-gray-100 px-2 py-1 rounded text-xs">{variantData?.session_id}</code>
              </p>
              {variantData?.user_id && (
                <p className="text-sm text-gray-500 mt-1">
                  User ID: <code className="bg-gray-100 px-2 py-1 rounded text-xs">{variantData.user_id}</code>
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Different Content Based on Variant */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Variant-Specific Content</h2>

          {variant === 'A' ? (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-2xl font-bold text-blue-900 mb-3">Version A: Classic Design</h3>
              <p className="text-blue-800 mb-4">
                This is the control variant with a traditional blue color scheme.
                This represents the current experience.
              </p>
              <button
                onClick={handleTrackClick}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium"
              >
                Classic Button
              </button>
            </div>
          ) : (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-2xl font-bold text-green-900 mb-3">Version B: Modern Design</h3>
              <p className="text-green-800 mb-4">
                This is the test variant with a fresh green color scheme.
                This represents the new experience we're testing.
              </p>
              <button
                onClick={handleTrackClick}
                className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-medium"
              >
                Modern Button
              </button>
            </div>
          )}
        </div>

        {/* Event Tracking */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Event Tracking</h2>
          <div className="flex space-x-4 mb-4">
            <button
              onClick={handleTrackConversion}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
            >
              Track Conversion
            </button>
            <button
              onClick={() => {
                setEvents([])
              }}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
            >
              Clear Events
            </button>
          </div>

          <div className="bg-gray-50 rounded-lg p-4 min-h-[100px]">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Tracked Events:</h3>
            {events.length === 0 ? (
              <p className="text-gray-500 text-sm">No events tracked yet. Click buttons above to track events.</p>
            ) : (
              <ul className="space-y-1">
                {events.map((event, index) => (
                  <li key={index} className="text-sm text-gray-600">
                    {index + 1}. {event}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-blue-900 mb-3">Testing Instructions</h2>
          <ol className="list-decimal list-inside space-y-2 text-blue-800">
            <li>Refresh this page multiple times - you should always see the same variant</li>
            <li>Clear your cookies and refresh - you may get assigned to a different variant</li>
            <li>Open this page in an incognito window - you'll get a new variant assignment</li>
            <li>Check the browser console to see variant assignment and tracking logs</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
