'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useUserLocale } from '@/hooks/useUserTimezone'
import { formatNumber } from '@/utils/number'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface EndpointUsage {
  endpoint: string
  requests: number
  percentage: number
}

interface DailyUsage {
  date: string
  requests: number
}

interface ApiUsageData {
  total_requests: number
  requests_limit: number
  requests_remaining: number
  top_endpoints: EndpointUsage[]
  daily_usage: DailyUsage[]
  quota_warning: boolean
  quota_warning_message?: string
}

interface AnalyticsStatsResponse {
  total_events: number
  event_counts: Record<string, number>
  days: number
  start_date: string
  end_date: string
}

export default function ApiUsagePage() {
  const locale = useUserLocale()
  const [usage, setUsage] = useState<ApiUsageData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch analytics data from backend
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true)
        setError(null)

        const token = localStorage.getItem('mi_navigator_token')
        if (!token) {
          setError('Not authenticated. Please log in.')
          setLoading(false)
          return
        }

        // Fetch analytics stats from backend
        const response = await fetch(`${API_BASE_URL}/analytics/stats?days=30`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const stats: AnalyticsStatsResponse = await response.json()

        // Transform backend data to frontend format
        const totalEvents = stats.total_events
        const limit = 10000 // Default limit (can be made dynamic)
        const remaining = Math.max(0, limit - totalEvents)

        // Calculate top event types as "endpoints"
        const topEndpoints: EndpointUsage[] = Object.entries(stats.event_counts)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 4)
          .map(([eventType, count]) => ({
            endpoint: eventType,
            requests: count,
            percentage: totalEvents > 0 ? (count / totalEvents) * 100 : 0
          }))

        // For now, use empty daily usage (would need additional backend endpoint)
        const dailyUsage: DailyUsage[] = []

        // Calculate quota warning
        const usagePercent = totalEvents > 0 ? (totalEvents / limit) * 100 : 0
        const quotaWarning = usagePercent >= 75
        const quotaWarningMessage = quotaWarning
          ? `You have used ${Math.round(usagePercent)}% of your monthly quota. Consider upgrading your plan.`
          : undefined

        setUsage({
          total_requests: totalEvents,
          requests_limit: limit,
          requests_remaining: remaining,
          top_endpoints: topEndpoints,
          daily_usage: dailyUsage,
          quota_warning: quotaWarning,
          quota_warning_message: quotaWarningMessage
        })
      } catch (err) {
        console.error('Failed to fetch analytics:', err)
        setError(err instanceof Error ? err.message : 'Failed to load analytics data')
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics data...</p>
        </div>
      </div>
    )
  }

  if (error || !usage) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-red-600 text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Failed to Load Analytics</h2>
          <p className="text-gray-600 mb-4">{error || 'Unknown error occurred'}</p>
          <Link
            href="/settings"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Settings
          </Link>
        </div>
      </div>
    )
  }

  const usagePercentage = Math.round((usage.total_requests / usage.requests_limit) * 100)

  const maxDailyRequests = usage.daily_usage.length > 0
    ? Math.max(...usage.daily_usage.map(d => d.requests))
    : 0

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/settings" className="text-sm text-gray-600 hover:text-gray-900">
            ← Back to Settings
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">API Usage Monitoring</h1>
          <p className="mt-1 text-sm text-gray-600">
            Track your API usage and monitor quotas
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {/* Quota Warning */}
          {usage.quota_warning && (
            <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-4">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">Quota Warning</h3>
                  <p className="mt-1 text-sm text-yellow-700">{usage.quota_warning_message}</p>
                  <div className="mt-3">
                    <Link
                      href="/settings/billing/upgrade"
                      className="inline-flex rounded-lg bg-yellow-600 px-4 py-2 text-sm text-white hover:bg-yellow-700"
                    >
                      Upgrade Plan
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Usage Overview */}
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Current Month Usage</h2>
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="text-3xl font-bold text-gray-900">
                  {formatNumber(usage.total_requests, locale)}
                </div>
                <div className="text-sm text-gray-600">
                  of {formatNumber(usage.requests_limit, locale)} requests
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-semibold text-green-600">
                  {formatNumber(usage.requests_remaining, locale)}
                </div>
                <div className="text-sm text-gray-600">remaining</div>
              </div>
            </div>
            <div className="h-3 rounded-full bg-gray-200">
              <div
                className={`h-full rounded-full ${
                  usagePercentage >= 90 ? 'bg-red-500' :
                  usagePercentage >= 75 ? 'bg-yellow-500' :
                  'bg-blue-500'
                }`}
                style={{ width: `${usagePercentage}%` }}
              />
            </div>
            <div className="mt-2 text-sm text-gray-600 text-right">
              {usagePercentage}% used
            </div>
          </div>

          {/* Daily Usage Chart */}
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <h2 className="mb-6 text-lg font-semibold text-gray-900">Daily Requests (Last 7 Days)</h2>
            {usage.daily_usage.length > 0 ? (
              <div className="flex items-end justify-between gap-4 h-64">
                {usage.daily_usage.map((day, index) => {
                  const heightPercentage = maxDailyRequests > 0 ? (day.requests / maxDailyRequests) * 100 : 0
                  return (
                    <div key={day.date} className="flex flex-col items-center flex-1">
                      <div className="w-full flex flex-col items-center justify-end h-56">
                        <div className="text-xs font-medium text-gray-900 mb-2">
                          {formatNumber(day.requests, locale)}
                        </div>
                        <div
                          className="w-full bg-blue-500 rounded-t transition-all hover:bg-blue-600"
                          style={{ height: `${heightPercentage}%` }}
                          title={`${day.requests} requests`}
                        />
                      </div>
                      <div className="mt-2 text-xs text-gray-600 text-center">
                        {formatDate(day.date)}
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-500">
                <p>Daily usage tracking coming soon</p>
              </div>
            )}
          </div>

          {/* Top Endpoints */}
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Top Event Types</h2>
            {usage.top_endpoints.length > 0 ? (
              <div className="space-y-4">
                {usage.top_endpoints.map((endpoint, index) => (
                  <div key={endpoint.endpoint}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-600">
                          {index + 1}
                        </div>
                        <div>
                          <div className="font-mono text-sm text-gray-900">{endpoint.endpoint}</div>
                          <div className="text-xs text-gray-500">{endpoint.percentage.toFixed(1)}% of total</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold text-gray-900">
                          {formatNumber(endpoint.requests, locale)}
                        </div>
                        <div className="text-xs text-gray-500">events</div>
                      </div>
                    </div>
                    <div className="h-2 rounded-full bg-gray-200">
                      <div
                        className="h-full rounded-full bg-blue-500"
                        style={{ width: `${endpoint.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-32 text-gray-500">
                <p>No events tracked yet</p>
              </div>
            )}
          </div>

          {/* Additional Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="rounded-lg bg-white p-6 shadow-sm">
              <div className="text-sm text-gray-600">Average Daily Requests</div>
              <div className="mt-2 text-2xl font-bold text-gray-900">
                {formatNumber(Math.round(usage.total_requests / 30), locale)}
              </div>
            </div>
            <div className="rounded-lg bg-white p-6 shadow-sm">
              <div className="text-sm text-gray-600">Peak Daily Requests</div>
              <div className="mt-2 text-2xl font-bold text-gray-900">
                {formatNumber(maxDailyRequests, locale)}
              </div>
            </div>
            <div className="rounded-lg bg-white p-6 shadow-sm">
              <div className="text-sm text-gray-600">Days Until Reset</div>
              <div className="mt-2 text-2xl font-bold text-gray-900">
                {Math.ceil((new Date('2026-01-31').getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
