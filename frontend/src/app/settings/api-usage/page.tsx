'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useUserLocale } from '@/hooks/useUserTimezone'
import { formatNumber } from '@/utils/number'

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

export default function ApiUsagePage() {
  const locale = useUserLocale()
  const [usage, setUsage] = useState<ApiUsageData>({
    total_requests: 8432,
    requests_limit: 10000,
    requests_remaining: 1568,
    top_endpoints: [
      { endpoint: '/api/v1/companies/profile', requests: 3245, percentage: 38.5 },
      { endpoint: '/api/v1/reports/generate', requests: 2156, percentage: 25.6 },
      { endpoint: '/api/v1/chat/conversations', requests: 1876, percentage: 22.2 },
      { endpoint: '/api/v1/search/companies', requests: 1155, percentage: 13.7 }
    ],
    daily_usage: [
      { date: '2026-01-11', requests: 856 },
      { date: '2026-01-12', requests: 923 },
      { date: '2026-01-13', requests: 1045 },
      { date: '2026-01-14', requests: 987 },
      { date: '2026-01-15', requests: 1234 },
      { date: '2026-01-16', requests: 1567 },
      { date: '2026-01-17', requests: 1820 }
    ],
    quota_warning: true,
    quota_warning_message: 'You have used 84% of your monthly API quota. Consider upgrading your plan.'
  })
  const [loading, setLoading] = useState(false)

  const usagePercentage = Math.round((usage.total_requests / usage.requests_limit) * 100)

  const maxDailyRequests = Math.max(...usage.daily_usage.map(d => d.requests))

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
            <div className="flex items-end justify-between gap-4 h-64">
              {usage.daily_usage.map((day, index) => {
                const heightPercentage = (day.requests / maxDailyRequests) * 100
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
          </div>

          {/* Top Endpoints */}
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Top Endpoints</h2>
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
                        <div className="text-xs text-gray-500">{endpoint.percentage}% of total</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-gray-900">
                        {formatNumber(endpoint.requests, locale)}
                      </div>
                      <div className="text-xs text-gray-500">requests</div>
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
