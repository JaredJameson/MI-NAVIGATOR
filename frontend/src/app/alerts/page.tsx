'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'

interface AlertConfig {
  id: string
  company_name?: string
  company_id?: string
  keyword?: string
  alert_type: string
  conditions?: {
    frequency?: string
    threshold?: string
  }
  is_active: boolean
  created_at: string
}

interface Alert {
  id: string
  severity: string
  title: string
  description: string
  source: string
  company?: string
  created_at: string
  read: boolean
}

export default function AlertsPage() {
  const router = useRouter()
  const [alertConfigs, setAlertConfigs] = useState<AlertConfig[]>([])
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('mi_navigator_token')
      if (!token) {
        router.push('/auth/login')
        return
      }

      // Fetch alert configurations
      const configsResponse = await fetch(`${API_BASE_URL}/alerts/configs`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!configsResponse.ok) {
        throw new Error('Failed to fetch alert configurations')
      }

      const configsData = await configsResponse.json()
      setAlertConfigs(configsData.items || [])

      // Fetch recent alerts
      const alertsResponse = await fetch(`${API_BASE_URL}/alerts?limit=10`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!alertsResponse.ok) {
        throw new Error('Failed to fetch alerts')
      }

      const alertsData = await alertsResponse.json()
      setRecentAlerts(alertsData.items || [])

    } catch (err: any) {
      console.error('Failed to fetch data:', err)
      setError(err.message || 'Failed to load alerts')
    } finally {
      setLoading(false)
    }
  }

  const toggleConfig = async (configId: string) => {
    try {
      const token = localStorage.getItem('mi_navigator_token')
      if (!token) {
        router.push('/auth/login')
        return
      }

      const response = await fetch(`${API_BASE_URL}/alerts/configs/${configId}/toggle`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to toggle alert configuration')
      }

      // Refresh data
      await fetchData()
    } catch (err: any) {
      console.error('Failed to toggle config:', err)
      alert(err.message || 'Failed to toggle alert configuration')
    }
  }

  const deleteConfig = async (configId: string) => {
    if (!confirm('Are you sure you want to delete this alert configuration?')) {
      return
    }

    try {
      const token = localStorage.getItem('mi_navigator_token')
      if (!token) {
        router.push('/auth/login')
        return
      }

      const response = await fetch(`${API_BASE_URL}/alerts/configs/${configId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to delete alert configuration')
      }

      // Refresh data
      await fetchData()
    } catch (err: any) {
      console.error('Failed to delete config:', err)
      alert(err.message || 'Failed to delete alert configuration')
    }
  }

  const getAlertTypeLabel = (type: string) => {
    switch (type) {
      case 'news': return '📰 News'
      case 'financial': return '💰 Financial'
      case 'competitor': return '🎯 Competitor'
      default: return type
    }
  }

  const getSeverityIndicator = (severity: string) => {
    switch (severity) {
      case 'high': return '🔴'
      case 'medium': return '🟡'
      case 'low': return '🟢'
      default: return '⚪'
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)

    if (diffHours < 1) return 'Just now'
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays} days ago`

    return date.toLocaleDateString('pl-PL', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="border-b bg-white">
          <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
            <Link href="/dashboard" className="text-blue-600 hover:text-blue-700">
              ← Back to Dashboard
            </Link>
          </div>
        </header>
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-600">Loading alerts...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <Link href="/dashboard" className="text-blue-600 hover:text-blue-700">
              ← Back to Dashboard
            </Link>
            <Link
              href="/alerts/new"
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              + Create New Alert
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Alerts & Monitoring</h1>
          <p className="mt-2 text-gray-600">
            Monitor companies, keywords, and market events with automated alerts.
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        <div className="grid gap-8 lg:grid-cols-2">
          {/* Alert Configurations */}
          <div>
            <h2 className="mb-4 text-xl font-semibold text-gray-900">
              Active Monitoring ({alertConfigs.length})
            </h2>

            {alertConfigs.length === 0 ? (
              <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
                <p className="text-gray-600">No alert configurations yet.</p>
                <Link
                  href="/alerts/new"
                  className="mt-4 inline-block rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                >
                  Create Your First Alert
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {alertConfigs.map((config) => (
                  <div
                    key={config.id}
                    className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{getAlertTypeLabel(config.alert_type)}</span>
                          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                            config.is_active
                              ? 'bg-green-100 text-green-700'
                              : 'bg-gray-100 text-gray-700'
                          }`}>
                            {config.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>

                        <div className="mt-2 space-y-1">
                          {config.company_name && (
                            <p className="text-sm text-gray-900">
                              <span className="font-medium">Company:</span> {config.company_name}
                            </p>
                          )}
                          {config.keyword && (
                            <p className="text-sm text-gray-900">
                              <span className="font-medium">Keyword:</span> {config.keyword}
                            </p>
                          )}
                          {config.conditions && (
                            <p className="text-xs text-gray-500">
                              Frequency: {config.conditions.frequency || 'daily'} •
                              Threshold: {config.conditions.threshold || 'any'}
                            </p>
                          )}
                        </div>

                        <p className="mt-2 text-xs text-gray-500">
                          Created {formatDate(config.created_at)}
                        </p>
                      </div>

                      <div className="ml-4 flex gap-2">
                        <button
                          onClick={() => toggleConfig(config.id)}
                          className={`${config.is_active ? 'text-orange-600 hover:text-orange-700' : 'text-green-600 hover:text-green-700'}`}
                          title={config.is_active ? 'Disable alert' : 'Enable alert'}
                        >
                          {config.is_active ? '⏸️' : '▶️'}
                        </button>
                        <Link
                          href={`/alerts/edit/${config.id}`}
                          className="text-blue-600 hover:text-blue-700"
                          title="Edit alert"
                        >
                          ✏️
                        </Link>
                        <button
                          onClick={() => deleteConfig(config.id)}
                          className="text-red-600 hover:text-red-700"
                          title="Delete alert"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Alerts */}
          <div>
            <h2 className="mb-4 text-xl font-semibold text-gray-900">
              Recent Alerts ({recentAlerts.length})
            </h2>

            {recentAlerts.length === 0 ? (
              <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
                <p className="text-gray-600">No alerts yet.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {recentAlerts.map((alert) => (
                  <Link
                    key={alert.id}
                    href={`/alerts/${alert.id}`}
                    className="block rounded-lg border border-gray-200 bg-white p-4 shadow-sm hover:border-blue-300 hover:shadow-md"
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">{getSeverityIndicator(alert.severity)}</span>
                      <div className="flex-1">
                        <h3 className={`font-medium truncate ${
                          alert.read ? 'text-gray-600' : 'text-gray-900'
                        }`} title={alert.title}>
                          {alert.title}
                        </h3>
                        <p className="mt-1 text-sm text-gray-600">{alert.description}</p>
                        <div className="mt-2 flex items-center gap-3 text-xs text-gray-500">
                          <span>{alert.source}</span>
                          <span>•</span>
                          <span>{formatDate(alert.created_at)}</span>
                        </div>
                      </div>
                      {!alert.read && (
                        <span className="h-2 w-2 rounded-full bg-blue-600" title="Unread"></span>
                      )}
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
