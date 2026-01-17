'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

interface MaintenanceStatus {
  maintenance: boolean
  message: string | null
  eta: string | null
}

export default function MaintenancePage() {
  const router = useRouter()
  const [status, setStatus] = useState<MaintenanceStatus>({
    maintenance: true,
    message: 'System is currently under maintenance. Please check back later.',
    eta: null
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check maintenance status on mount
    checkMaintenanceStatus()

    // Poll every 30 seconds to see if maintenance is over
    const interval = setInterval(checkMaintenanceStatus, 30000)

    return () => clearInterval(interval)
  }, [])

  const checkMaintenanceStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/system/maintenance')
      const data = await response.json()

      setStatus(data)
      setLoading(false)

      // If maintenance is disabled, redirect to dashboard
      if (!data.maintenance) {
        router.push('/dashboard')
      }
    } catch (error) {
      console.error('Failed to check maintenance status:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-orange-50 to-red-100">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-orange-50 to-red-100 px-4">
      <div className="w-full max-w-md text-center">
        {/* Maintenance Icon */}
        <div className="mb-8">
          <div className="mx-auto flex h-32 w-32 items-center justify-center rounded-full bg-orange-100">
            <svg
              className="h-16 w-16 text-orange-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
          </div>
        </div>

        {/* Status Code */}
        <h1 className="mb-4 text-7xl font-bold text-gray-800">503</h1>

        {/* Maintenance Message */}
        <h2 className="mb-2 text-2xl font-semibold text-gray-700">
          Under Maintenance
        </h2>
        <p className="mb-4 text-gray-600">
          {status.message || 'System is currently under maintenance. Please check back later.'}
        </p>

        {/* Estimated Downtime */}
        {status.eta && (
          <div className="mb-8 rounded-lg bg-white p-4 shadow-sm">
            <p className="text-sm font-medium text-gray-700">
              Estimated Time:
            </p>
            <p className="text-lg font-semibold text-orange-600">
              {status.eta}
            </p>
          </div>
        )}

        {/* Info Box */}
        <div className="mb-8 rounded-lg bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-600">
            We're currently performing scheduled maintenance to improve our services.
            The system will be back online shortly.
          </p>
        </div>

        {/* Refresh Button */}
        <button
          onClick={checkMaintenanceStatus}
          className="rounded-lg bg-orange-600 px-6 py-3 font-medium text-white transition-colors hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
        >
          Check Status
        </button>

        {/* Auto-refresh Notice */}
        <p className="mt-4 text-xs text-gray-500">
          This page automatically checks every 30 seconds
        </p>
      </div>
    </div>
  )
}
