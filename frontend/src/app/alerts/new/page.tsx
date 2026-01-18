'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'

interface AlertFormData {
  company_name: string
  keyword: string
  alert_type: string
  conditions: {
    frequency?: string
    threshold?: string
  }
}

export default function CreateAlertPage() {
  const router = useRouter()
  const [formData, setFormData] = useState<AlertFormData>({
    company_name: '',
    keyword: '',
    alert_type: 'news',
    conditions: {
      frequency: 'daily',
      threshold: 'any'
    }
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validation
    if (!formData.company_name && !formData.keyword) {
      setError('Please provide either a company name or keyword to monitor')
      return
    }

    try {
      setIsSubmitting(true)

      const token = localStorage.getItem('mi_navigator_token')
      if (!token) {
        router.push('/auth/login')
        return
      }

      const payload: any = {
        alert_type: formData.alert_type,
        conditions: formData.conditions
      }

      if (formData.company_name) {
        payload.company_name = formData.company_name
      }

      if (formData.keyword) {
        payload.keyword = formData.keyword
      }

      const response = await fetch(`${API_BASE_URL}/alerts/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to create alert')
      }

      const createdAlert = await response.json()

      // Redirect to dashboard or alerts list
      router.push('/dashboard')
    } catch (err: any) {
      console.error('Failed to create alert:', err)
      setError(err.message || 'Failed to create alert')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/dashboard" className="text-blue-600 hover:text-blue-700">
            ← Back to Dashboard
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Create Alert</h1>
          <p className="mt-2 text-gray-600">
            Set up monitoring alerts for companies, keywords, or market events.
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Company Name */}
          <div className="rounded-lg border bg-white p-6 shadow-sm">
            <label htmlFor="company_name" className="block text-sm font-medium text-gray-700">
              Company Name
            </label>
            <input
              type="text"
              id="company_name"
              value={formData.company_name}
              onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
              placeholder="e.g., FADO Sp. z o.o."
              className="mt-2 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <p className="mt-1 text-sm text-gray-500">
              Leave empty to monitor by keyword instead
            </p>
          </div>

          {/* Keyword */}
          <div className="rounded-lg border bg-white p-6 shadow-sm">
            <label htmlFor="keyword" className="block text-sm font-medium text-gray-700">
              Keyword
            </label>
            <input
              type="text"
              id="keyword"
              value={formData.keyword}
              onChange={(e) => setFormData({ ...formData, keyword: e.target.value })}
              placeholder="e.g., plastics industry, regulatory changes"
              className="mt-2 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <p className="mt-1 text-sm text-gray-500">
              Optional: Add keywords to refine monitoring
            </p>
          </div>

          {/* Alert Type */}
          <div className="rounded-lg border bg-white p-6 shadow-sm">
            <label className="block text-sm font-medium text-gray-700">
              Alert Type
            </label>
            <div className="mt-3 space-y-3">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="alert_type"
                  value="news"
                  checked={formData.alert_type === 'news'}
                  onChange={(e) => setFormData({ ...formData, alert_type: e.target.value })}
                  className="h-4 w-4 text-blue-600"
                />
                <span className="ml-3">
                  <span className="block font-medium text-gray-900">📰 News Alerts</span>
                  <span className="block text-sm text-gray-500">
                    Get notified about news articles and press releases
                  </span>
                </span>
              </label>

              <label className="flex items-center">
                <input
                  type="radio"
                  name="alert_type"
                  value="financial"
                  checked={formData.alert_type === 'financial'}
                  onChange={(e) => setFormData({ ...formData, alert_type: e.target.value })}
                  className="h-4 w-4 text-blue-600"
                />
                <span className="ml-3">
                  <span className="block font-medium text-gray-900">💰 Financial Changes</span>
                  <span className="block text-sm text-gray-500">
                    Monitor financial reports, revenue changes, and key metrics
                  </span>
                </span>
              </label>

              <label className="flex items-center">
                <input
                  type="radio"
                  name="alert_type"
                  value="competitor"
                  checked={formData.alert_type === 'competitor'}
                  onChange={(e) => setFormData({ ...formData, alert_type: e.target.value })}
                  className="h-4 w-4 text-blue-600"
                />
                <span className="ml-3">
                  <span className="block font-medium text-gray-900">🎯 Competitor Activity</span>
                  <span className="block text-sm text-gray-500">
                    Track competitor moves, product launches, and strategic changes
                  </span>
                </span>
              </label>
            </div>
          </div>

          {/* Alert Conditions */}
          <div className="rounded-lg border bg-white p-6 shadow-sm">
            <h3 className="text-sm font-medium text-gray-700">Alert Conditions</h3>

            <div className="mt-4">
              <label htmlFor="frequency" className="block text-sm font-medium text-gray-700">
                Notification Frequency
              </label>
              <select
                id="frequency"
                value={formData.conditions.frequency}
                onChange={(e) => setFormData({
                  ...formData,
                  conditions: { ...formData.conditions, frequency: e.target.value }
                })}
                className="mt-2 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="realtime">Real-time (immediate)</option>
                <option value="daily">Daily digest</option>
                <option value="weekly">Weekly summary</option>
              </select>
            </div>

            <div className="mt-4">
              <label htmlFor="threshold" className="block text-sm font-medium text-gray-700">
                Alert Threshold
              </label>
              <select
                id="threshold"
                value={formData.conditions.threshold}
                onChange={(e) => setFormData({
                  ...formData,
                  conditions: { ...formData.conditions, threshold: e.target.value }
                })}
                className="mt-2 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="any">Any change</option>
                <option value="significant">Significant changes only</option>
                <option value="critical">Critical events only</option>
              </select>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => router.push('/dashboard')}
              className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:bg-gray-300"
            >
              {isSubmitting ? 'Creating...' : 'Create Alert'}
            </button>
          </div>
        </form>
      </main>
    </div>
  )
}
