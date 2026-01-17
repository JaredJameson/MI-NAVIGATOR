'use client'

import { useState, useEffect } from 'react'
import { DashboardSkeleton, ReportListSkeleton, CardSkeleton, ListSkeleton } from '@/components/Skeleton'

export default function TestSkeletonPage() {
  const [showDashboard, setShowDashboard] = useState(true)
  const [showReports, setShowReports] = useState(false)
  const [showCards, setShowCards] = useState(false)
  const [showList, setShowList] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Auto-stop loading after 5 seconds for demo
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 5000)

    return () => clearTimeout(timer)
  }, [])

  const resetDemo = () => {
    setIsLoading(true)
    setTimeout(() => setIsLoading(false), 5000)
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Skeleton Screen Demo
          </h1>
          <p className="text-gray-600 mb-6">
            This page demonstrates loading skeleton screens. Toggle between different skeleton types below.
          </p>

          {/* Controls */}
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => {
                setShowDashboard(true)
                setShowReports(false)
                setShowCards(false)
                setShowList(false)
              }}
              className={`px-4 py-2 rounded-md ${
                showDashboard
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              } transition-colors`}
            >
              Dashboard Skeleton
            </button>
            <button
              onClick={() => {
                setShowDashboard(false)
                setShowReports(true)
                setShowCards(false)
                setShowList(false)
              }}
              className={`px-4 py-2 rounded-md ${
                showReports
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              } transition-colors`}
            >
              Report List Skeleton
            </button>
            <button
              onClick={() => {
                setShowDashboard(false)
                setShowReports(false)
                setShowCards(true)
                setShowList(false)
              }}
              className={`px-4 py-2 rounded-md ${
                showCards
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              } transition-colors`}
            >
              Card Skeleton
            </button>
            <button
              onClick={() => {
                setShowDashboard(false)
                setShowReports(false)
                setShowCards(false)
                setShowList(true)
              }}
              className={`px-4 py-2 rounded-md ${
                showList
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              } transition-colors`}
            >
              List Skeleton
            </button>
            <button
              onClick={resetDemo}
              className="px-4 py-2 rounded-md bg-green-600 text-white hover:bg-green-700 transition-colors ml-auto"
            >
              Reset Demo (5s)
            </button>
          </div>

          {/* Loading Status */}
          <div className="flex items-center gap-3 mb-6">
            <div
              className={`w-3 h-3 rounded-full ${
                isLoading ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'
              }`}
            />
            <span className="text-sm font-medium">
              {isLoading ? 'Loading (skeleton visible)...' : 'Loaded (skeleton hidden)'}
            </span>
          </div>
        </div>

        {/* Skeleton Display Area */}
        <div className="bg-gray-100 rounded-lg p-6">
          {isLoading ? (
            <>
              {showDashboard && <DashboardSkeleton />}
              {showReports && <ReportListSkeleton items={3} />}
              {showCards && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <CardSkeleton />
                  <CardSkeleton />
                  <CardSkeleton />
                </div>
              )}
              {showList && <ListSkeleton items={5} />}
            </>
          ) : (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <div className="text-6xl mb-4">✅</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Content Loaded!</h2>
              <p className="text-gray-600">
                The skeleton screen has successfully transitioned to real content.
              </p>
              <p className="text-sm text-gray-500 mt-4">
                Click "Reset Demo" to see the loading skeleton again.
              </p>
            </div>
          )}
        </div>

        {/* Info Panel */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-2">ℹ️ About Skeleton Screens</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Skeleton screens improve perceived performance during data loading</li>
            <li>• They match the layout of the actual content that will appear</li>
            <li>• Pulse animation indicates ongoing loading process</li>
            <li>• Smooth transition from skeleton to real content enhances UX</li>
            <li>• Used on Dashboard, Reports, and other data-heavy pages</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
