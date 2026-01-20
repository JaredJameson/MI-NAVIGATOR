'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { toast } from 'sonner'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/proxy'

interface APIKey {
  id: string
  key_prefix: string
  name: string | null
  description: string | null
  is_active: boolean
  created_at: string
  last_used_at: string | null
  expires_at: string | null
}

interface NewAPIKeyResponse {
  id: string
  key: string  // Full key - shown only once!
  key_prefix: string
  name: string | null
  description: string | null
  created_at: string
  expires_at: string | null
}

export default function APIKeysPage() {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [newKeyDescription, setNewKeyDescription] = useState('')
  const [createdKey, setCreatedKey] = useState<NewAPIKeyResponse | null>(null)
  const [copiedKey, setCopiedKey] = useState(false)

  // Fetch API keys
  const fetchAPIKeys = async () => {
    try {
      setLoading(true)
      setError(null)

      const token = localStorage.getItem('mi_navigator_token')
      if (!token) {
        setError('Not authenticated. Please log in.')
        setLoading(false)
        return
      }

      const response = await fetch(`${API_BASE_URL}/api-keys/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: APIKey[] = await response.json()
      setApiKeys(data)
    } catch (err) {
      console.error('Error fetching API keys:', err)
      setError('Failed to load API keys')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAPIKeys()
  }, [])

  // Create new API key
  const handleCreateAPIKey = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const token = localStorage.getItem('mi_navigator_token')
      const csrfToken = localStorage.getItem('csrf_token')

      if (!token) {
        toast.error('Not authenticated')
        return
      }

      const response = await fetch(`${API_BASE_URL}/api-keys/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken || ''
        },
        body: JSON.stringify({
          name: newKeyName || null,
          description: newKeyDescription || null
        })
      })

      if (!response.ok) {
        throw new Error('Failed to create API key')
      }

      const data: NewAPIKeyResponse = await response.json()
      setCreatedKey(data)
      setShowCreateForm(false)
      setNewKeyName('')
      setNewKeyDescription('')

      // Refresh the list
      await fetchAPIKeys()

      toast.success('API key created successfully', {
        description: 'Make sure to copy your key now. You won\'t be able to see it again!'
      })
    } catch (err) {
      console.error('Error creating API key:', err)
      toast.error('Failed to create API key')
    }
  }

  // Delete API key
  const handleDeleteAPIKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return
    }

    try {
      const token = localStorage.getItem('mi_navigator_token')
      const csrfToken = localStorage.getItem('csrf_token')

      if (!token) {
        toast.error('Not authenticated')
        return
      }

      const response = await fetch(`${API_BASE_URL}/api-keys/${keyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-CSRF-Token': csrfToken || ''
        }
      })

      if (!response.ok) {
        throw new Error('Failed to delete API key')
      }

      await fetchAPIKeys()
      toast.success('API key deleted successfully')
    } catch (err) {
      console.error('Error deleting API key:', err)
      toast.error('Failed to delete API key')
    }
  }

  // Copy key to clipboard
  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedKey(true)
      toast.success('API key copied to clipboard')
      setTimeout(() => setCopiedKey(false), 2000)
    } catch (err) {
      toast.error('Failed to copy to clipboard')
    }
  }

  // Close created key modal
  const handleCloseCreatedKey = () => {
    setCreatedKey(null)
    setCopiedKey(false)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <Link href="/settings" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
              ← Back to Settings
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">API Keys</h1>
            <p className="text-gray-600 mt-2">Manage API keys for programmatic access</p>
          </div>
          <div className="text-center py-12">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">Loading API keys...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <Link href="/settings" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
              ← Back to Settings
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">API Keys</h1>
          </div>
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <h3 className="text-lg font-semibold text-red-900 mb-2">Error</h3>
            <p className="text-red-700">{error}</p>
            <button
              onClick={fetchAPIKeys}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link href="/settings" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
            ← Back to Settings
          </Link>
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">API Keys</h1>
              <p className="text-gray-600 mt-2">
                Generate and manage API keys for programmatic access to MI-Navigator
              </p>
            </div>
            <button
              onClick={() => setShowCreateForm(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              + Generate New Key
            </button>
          </div>
        </div>

        {/* Create Form Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold mb-4">Generate New API Key</h2>
              <form onSubmit={handleCreateAPIKey}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Key Name (optional)
                  </label>
                  <input
                    type="text"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    placeholder="e.g., Production Server"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description (optional)
                  </label>
                  <textarea
                    value={newKeyDescription}
                    onChange={(e) => setNewKeyDescription(e.target.value)}
                    placeholder="Brief description of what this key will be used for..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setShowCreateForm(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Generate Key
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Created Key Modal - Shows the key ONCE */}
        {createdKey && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-8 max-w-2xl w-full">
              <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">API Key Created!</h2>
                <p className="text-red-600 font-semibold">⚠️ Copy your API key now. You won't be able to see it again!</p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">Your API Key</label>
                  <button
                    onClick={() => copyToClipboard(createdKey.key)}
                    className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                  >
                    {copiedKey ? '✓ Copied!' : '📋 Copy'}
                  </button>
                </div>
                <code className="block bg-white border border-gray-300 rounded px-3 py-2 font-mono text-sm break-all">
                  {createdKey.key}
                </code>
              </div>

              {createdKey.name && (
                <div className="mb-4">
                  <span className="text-sm font-medium text-gray-700">Name: </span>
                  <span className="text-sm text-gray-900">{createdKey.name}</span>
                </div>
              )}

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <p className="text-sm text-yellow-800">
                  <strong>Important:</strong> Store this key securely. It provides full access to your account via the API.
                </p>
              </div>

              <button
                onClick={handleCloseCreatedKey}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                I've Saved My Key
              </button>
            </div>
          </div>
        )}

        {/* API Keys List */}
        {apiKeys.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="mb-4">
              <svg className="w-16 h-16 text-gray-400 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No API Keys</h3>
            <p className="text-gray-600 mb-6">
              You haven't generated any API keys yet. Create one to get started with programmatic access.
            </p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Generate Your First Key
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Key
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name / Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Used
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {apiKeys.map((key) => (
                  <tr key={key.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <code className="text-sm font-mono text-gray-900 bg-gray-100 px-2 py-1 rounded">
                        {key.key_prefix}•••
                      </code>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">
                        {key.name || <span className="text-gray-400">Unnamed key</span>}
                      </div>
                      {key.description && (
                        <div className="text-sm text-gray-500 mt-1">{key.description}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(key.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {key.last_used_at ? new Date(key.last_used_at).toLocaleDateString() : 'Never'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        key.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {key.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleDeleteAPIKey(key.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Documentation */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">Using Your API Key</h3>
          <p className="text-blue-800 mb-4">
            Include your API key in the Authorization header of your HTTP requests:
          </p>
          <code className="block bg-white border border-blue-300 rounded px-4 py-3 text-sm font-mono text-blue-900">
            Authorization: Bearer YOUR_API_KEY
          </code>
          <p className="text-blue-800 mt-4 text-sm">
            For full API documentation, visit <Link href="/docs/api" className="underline font-semibold">API Documentation</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
