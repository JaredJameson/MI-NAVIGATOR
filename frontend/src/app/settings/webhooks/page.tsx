'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { toast } from 'sonner'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface Webhook {
  id: string
  user_id: string
  url: string
  event_type: string
  secret: string | null
  is_active: boolean
  max_retries: number
  retry_count: number
  status: string
  last_triggered_at: string | null
  last_delivered_at: string | null
  last_error: string | null
  next_retry_at: string | null
  created_at: string
}

const EVENT_TYPES = [
  { value: 'report.created', label: 'Report Created' },
  { value: 'report.updated', label: 'Report Updated' },
  { value: 'report.deleted', label: 'Report Deleted' },
  { value: 'analysis.completed', label: 'Analysis Completed' },
  { value: 'alert.triggered', label: 'Alert Triggered' },
]

export default function WebhooksPage() {
  const [webhooks, setWebhooks] = useState<Webhook[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newWebhookUrl, setNewWebhookUrl] = useState('')
  const [selectedEventTypes, setSelectedEventTypes] = useState<string[]>([])

  // Fetch webhooks
  const fetchWebhooks = async () => {
    try {
      setLoading(true)
      setError(null)

      const token = localStorage.getItem('mi_navigator_token')
      if (!token) {
        setError('Not authenticated. Please log in.')
        setLoading(false)
        return
      }

      const response = await fetch(`${API_BASE_URL}/webhooks/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: Webhook[] = await response.json()
      setWebhooks(data)
    } catch (err) {
      console.error('Error fetching webhooks:', err)
      setError('Failed to load webhooks')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWebhooks()
  }, [])

  // Create new webhook
  const handleCreateWebhook = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!newWebhookUrl || selectedEventTypes.length === 0) {
      toast.error('Please provide URL and select at least one event type')
      return
    }

    try {
      const token = localStorage.getItem('mi_navigator_token')
      const csrfToken = localStorage.getItem('csrf_token')

      if (!token) {
        toast.error('Not authenticated')
        return
      }

      // Create webhook for each selected event type
      for (const eventType of selectedEventTypes) {
        const response = await fetch(`${API_BASE_URL}/webhooks/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken || ''
          },
          body: JSON.stringify({
            url: newWebhookUrl,
            event_type: eventType,
            max_retries: 5
          })
        })

        if (!response.ok) {
          throw new Error(`Failed to create webhook for ${eventType}`)
        }
      }

      toast.success('Webhook(s) created successfully')
      setShowCreateForm(false)
      setNewWebhookUrl('')
      setSelectedEventTypes([])
      fetchWebhooks()
    } catch (err) {
      console.error('Error creating webhook:', err)
      toast.error('Failed to create webhook')
    }
  }

  // Delete webhook
  const handleDeleteWebhook = async (webhookId: string) => {
    if (!confirm('Are you sure you want to delete this webhook?')) {
      return
    }

    try {
      const token = localStorage.getItem('mi_navigator_token')
      const csrfToken = localStorage.getItem('csrf_token')

      if (!token) {
        toast.error('Not authenticated')
        return
      }

      const response = await fetch(`${API_BASE_URL}/webhooks/${webhookId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-CSRF-Token': csrfToken || ''
        }
      })

      if (!response.ok) {
        throw new Error('Failed to delete webhook')
      }

      toast.success('Webhook deleted successfully')
      fetchWebhooks()
    } catch (err) {
      console.error('Error deleting webhook:', err)
      toast.error('Failed to delete webhook')
    }
  }

  // Test webhook
  const handleTestWebhook = async (webhookId: string) => {
    try {
      const token = localStorage.getItem('mi_navigator_token')
      const csrfToken = localStorage.getItem('csrf_token')

      if (!token) {
        toast.error('Not authenticated')
        return
      }

      const response = await fetch(`${API_BASE_URL}/webhooks/${webhookId}/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken || ''
        },
        body: JSON.stringify({
          payload: {
            test: true,
            event: 'manual_trigger',
            timestamp: new Date().toISOString()
          }
        })
      })

      if (!response.ok) {
        throw new Error('Failed to test webhook')
      }

      const result = await response.json()

      if (result.last_error) {
        toast.error(`Webhook test failed: ${result.last_error}`)
      } else {
        toast.success('Webhook test triggered successfully')
      }

      // Refresh to see updated status
      fetchWebhooks()
    } catch (err) {
      console.error('Error testing webhook:', err)
      toast.error('Failed to test webhook')
    }
  }

  // Toggle webhook event type selection
  const toggleEventType = (eventType: string) => {
    setSelectedEventTypes(prev =>
      prev.includes(eventType)
        ? prev.filter(e => e !== eventType)
        : [...prev, eventType]
    )
  }

  // Format date
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never'
    return new Date(dateString).toLocaleString('pl-PL')
  }

  // Get status badge color
  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'delivered':
        return 'bg-green-100 text-green-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'retrying':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-5xl mx-auto">
          <h1 className="text-3xl font-bold mb-6">Webhook Settings</h1>
          <div className="text-center py-12">Loading webhooks...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-5xl mx-auto">
          <h1 className="text-3xl font-bold mb-6">Webhook Settings</h1>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
            {error}
          </div>
          <Link href="/settings" className="mt-4 inline-block text-blue-600 hover:underline">
            ← Back to Settings
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Link href="/settings" className="text-blue-600 hover:underline mb-2 inline-block">
            ← Back to Settings
          </Link>
          <h1 className="text-3xl font-bold">Webhook Settings</h1>
          <p className="text-gray-600 mt-2">
            Configure webhooks to receive real-time notifications for events in your account.
          </p>
        </div>

        {/* Create Webhook Button */}
        {!showCreateForm && (
          <div className="mb-6">
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              + Add Webhook
            </button>
          </div>
        )}

        {/* Create Webhook Form */}
        {showCreateForm && (
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Add New Webhook</h2>
            <form onSubmit={handleCreateWebhook} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Webhook URL *
                </label>
                <input
                  type="url"
                  value={newWebhookUrl}
                  onChange={(e) => setNewWebhookUrl(e.target.value)}
                  placeholder="https://your-domain.com/webhook"
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
                <p className="text-sm text-gray-500 mt-1">
                  The URL where webhook notifications will be sent
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Events * (choose one or more)
                </label>
                <div className="space-y-2">
                  {EVENT_TYPES.map((event) => (
                    <label key={event.value} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedEventTypes.includes(event.value)}
                        onChange={() => toggleEventType(event.value)}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="text-sm">{event.label}</span>
                      <code className="text-xs bg-gray-100 px-2 py-1 rounded">{event.value}</code>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Create Webhook
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateForm(false)
                    setNewWebhookUrl('')
                    setSelectedEventTypes([])
                  }}
                  className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Webhooks List */}
        {webhooks.length === 0 ? (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
            <div className="text-4xl mb-4">🔔</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No Webhooks</h3>
            <p className="text-gray-500 mb-4">
              You haven't configured any webhooks yet. Add your first webhook to start receiving notifications.
            </p>
            {!showCreateForm && (
              <button
                onClick={() => setShowCreateForm(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Add Your First Webhook
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {webhooks.map((webhook) => (
              <div key={webhook.id} className="bg-white border border-gray-200 rounded-lg p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="font-semibold text-lg break-all">{webhook.url}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadgeClass(webhook.status)}`}>
                        {webhook.status}
                      </span>
                      {webhook.is_active ? (
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Active
                        </span>
                      ) : (
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          Inactive
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p><strong>Event:</strong> <code className="bg-gray-100 px-2 py-1 rounded">{webhook.event_type}</code></p>
                      <p><strong>Created:</strong> {formatDate(webhook.created_at)}</p>
                      <p><strong>Last Triggered:</strong> {formatDate(webhook.last_triggered_at)}</p>
                      <p><strong>Last Delivered:</strong> {formatDate(webhook.last_delivered_at)}</p>
                      {webhook.retry_count > 0 && (
                        <p><strong>Retry Count:</strong> {webhook.retry_count} / {webhook.max_retries}</p>
                      )}
                      {webhook.last_error && (
                        <p className="text-red-600"><strong>Last Error:</strong> {webhook.last_error}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <button
                      onClick={() => handleTestWebhook(webhook.id)}
                      className="bg-blue-100 text-blue-700 px-3 py-1 rounded hover:bg-blue-200 transition-colors text-sm"
                      title="Test webhook"
                    >
                      🧪 Test
                    </button>
                    <button
                      onClick={() => handleDeleteWebhook(webhook.id)}
                      className="bg-red-100 text-red-700 px-3 py-1 rounded hover:bg-red-200 transition-colors text-sm"
                      title="Delete webhook"
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Documentation */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">📚 Webhook Documentation</h3>
          <div className="text-sm text-blue-800 space-y-2">
            <p><strong>Webhook Format:</strong> All webhooks are sent as POST requests with JSON payload.</p>
            <p><strong>Authentication:</strong> Webhooks include an HMAC signature in the <code className="bg-blue-100 px-1">X-Webhook-Signature</code> header.</p>
            <p><strong>Retry Policy:</strong> Failed webhooks are retried up to 5 times with exponential backoff.</p>
            <p><strong>Timeout:</strong> Webhook requests timeout after 10 seconds.</p>
            <p className="mt-3 pt-3 border-t border-blue-200">
              <strong>Example Payload:</strong>
            </p>
            <pre className="bg-blue-100 p-3 rounded mt-2 overflow-x-auto text-xs">
{`{
  "event": "report.created",
  "data": {
    "report_id": "123",
    "title": "Market Analysis",
    "created_at": "2024-01-20T10:00:00Z"
  },
  "timestamp": "2024-01-20T10:00:00Z"
}`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  )
}
