'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'

interface AlertDetails {
  id: string
  severity: string
  severity_label: string
  severity_color: string
  severity_indicator: string
  title: string
  description: string
  source: string
  company: string | null
  created_at: string
  read: boolean
}

export default function AlertDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const alertId = params?.id as string

  const [alert, setAlert] = useState<AlertDetails | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAlert = async () => {
      try {
        setIsLoading(true)
        setError(null)

        const token = localStorage.getItem('mi_navigator_token')
        if (!token) {
          setError('Not authenticated')
          setIsLoading(false)
          return
        }

        const response = await fetch(`${API_BASE_URL}/alerts/${alertId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (response.status === 404) {
          setError('Alert not found')
          setIsLoading(false)
          return
        }

        if (!response.ok) {
          setError('Failed to load alert')
          setIsLoading(false)
          return
        }

        const data = await response.json()
        setAlert(data)
      } catch (err) {
        console.error('Failed to fetch alert:', err)
        setError('Failed to load alert')
      } finally {
        setIsLoading(false)
      }
    }

    if (alertId) {
      fetchAlert()
    }
  }, [alertId])

  // Get severity styling
  const getSeverityColorClasses = (color: string) => {
    switch (color) {
      case 'red':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'yellow':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'green':
        return 'bg-green-100 text-green-800 border-green-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleString('pl-PL', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateString
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="border-b bg-white">
          <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
            <Link href="/dashboard" className="text-blue-600 hover:text-blue-700">
              ← Back to Dashboard
            </Link>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="text-center text-gray-500">Loading alert...</div>
        </main>
      </div>
    )
  }

  if (error || !alert) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="border-b bg-white">
          <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
            <Link href="/dashboard" className="text-blue-600 hover:text-blue-700">
              ← Back to Dashboard
            </Link>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="rounded-lg border border-red-200 bg-red-50 p-4">
            <h2 className="text-lg font-semibold text-red-800">Error</h2>
            <p className="text-sm text-red-600">{error || 'Alert not found'}</p>
          </div>
        </main>
      </div>
    )
  }

  const severityClasses = getSeverityColorClasses(alert.severity_color)

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/dashboard" className="text-blue-600 hover:text-blue-700">
            ← Back to Dashboard
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="rounded-lg border bg-white p-6 shadow-sm">
          {/* Header */}
          <div className="mb-6 flex items-start justify-between">
            <div className="flex items-start gap-3">
              <span className="text-3xl">{alert.severity_indicator}</span>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{alert.title}</h1>
                <div className="mt-2 flex items-center gap-2">
                  <span
                    className={`inline-flex items-center rounded-full border px-3 py-1 text-sm font-medium ${severityClasses}`}
                  >
                    {alert.severity_label} Severity
                  </span>
                  {alert.company && (
                    <span className="inline-flex items-center rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-sm text-gray-700">
                      🏢 {alert.company}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Description */}
          <div className="mb-6">
            <h2 className="mb-2 text-sm font-semibold uppercase text-gray-500">Description</h2>
            <p className="text-gray-700">{alert.description}</p>
          </div>

          {/* Metadata */}
          <div className="grid gap-4 border-t pt-6 sm:grid-cols-2">
            <div>
              <h3 className="mb-1 text-sm font-semibold uppercase text-gray-500">Source</h3>
              <p className="text-gray-700">{alert.source}</p>
            </div>
            <div>
              <h3 className="mb-1 text-sm font-semibold uppercase text-gray-500">Created</h3>
              <p className="text-gray-700">{formatDate(alert.created_at)}</p>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-8 flex gap-3 border-t pt-6">
            <button
              onClick={() => router.push('/dashboard')}
              className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Back to Dashboard
            </button>
            {alert.company && (
              <Link
                href={`/companies?search=${encodeURIComponent(alert.company)}`}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
              >
                View Company Details
              </Link>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
