'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
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

export default function EditAlertPage() {
  const router = useRouter()
  const params = useParams()
  const configId = params?.id as string

  const [formData, setFormData] = useState<AlertFormData>({
    company_name: '',
    keyword: '',
    alert_type: 'news',
    conditions: {
      frequency: 'daily',
      threshold: 'any'
    }
  })
  const [loading, setLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (configId) {
      fetchAlertConfig()
    }
  }, [configId])

  const fetchAlertConfig = async () => {
    try {
      const token = localStorage.getItem('mi_navigator_token')
      if (!token) {
        router.push('/auth/login')
        return
      }

      const response = await fetch(`${API_BASE_URL}/alerts/configs/${configId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch alert configuration')
      }

      const config = await response.json()

      setFormData({
        company_name: config.company_name || '',
        keyword: config.keyword || '',
        alert_type: config.alert_type,
        conditions: config.conditions || {
          frequency: 'daily',
          threshold: 'any'
        }
      })
    } catch (err: any) {
      console.error('Failed to fetch config:', err)
      setError(err.message || 'Failed to load alert configuration')
    } finally {
      setLoading(false)
    }
  }

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

      const response = await fetch(`${API_BASE_URL}/alerts/configs/${configId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to update alert')
      }

      // Redirect to alerts list
      router.push('/alerts')
    } catch (err: any) {
      console.error('Failed to update alert:', err)
      setError(err.message || 'Failed to update alert')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="border-b bg-white">
          <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
            <Link href="/alerts" className="text-blue-600 hover:text-blue-700">
              ← Back to Alerts
            </Link>
          </div>
        </header>
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-600">Loading alert configuration...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/alerts" className="text-blue-600 hover:text-blue-700">
            ← Back to Alerts
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Edit Alert</h1>
          <p className="mt-2 text-gray-600">
            Update monitoring alert settings.
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
              onClick={() => router.push('/alerts')}
              className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:bg-gray-300"
            >
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </main>
    </div>
  )
}
