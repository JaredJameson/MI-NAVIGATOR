'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// Helper function to get CSRF token
const getCsrfToken = async (): Promise<string | null> => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/csrf-token`)
    if (response.ok) {
      const data = await response.json()
      return data.csrf_token
    }
  } catch (err) {
    console.error('Failed to get CSRF token:', err)
  }
  return null
}

interface PendingInvitation {
  id: string
  workspace_id: string
  user_id: string
  user_email: string
  user_name: string | null
  role: string
  invitation_accepted: boolean
  created_at: string
}

interface Workspace {
  id: string
  name: string
  description: string | null
}

export default function InvitationsPage() {
  const router = useRouter()
  const [invitations, setInvitations] = useState<PendingInvitation[]>([])
  const [workspaces, setWorkspaces] = useState<Map<string, Workspace>>(new Map())
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  useEffect(() => {
    loadInvitations()
  }, [])

  const loadInvitations = async () => {
    try {
      const token = getStoredToken()
      if (!token) {
        router.push('/auth/login')
        return
      }

      const response = await fetch(`${API_BASE_URL}/workspaces/invitations/pending`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to load invitations')
      }

      const data = await response.json()
      setInvitations(data)

      // Load workspace details for each invitation
      const workspaceMap = new Map<string, Workspace>()
      for (const invitation of data) {
        if (!workspaceMap.has(invitation.workspace_id)) {
          try {
            const wsResponse = await fetch(`${API_BASE_URL}/workspaces/${invitation.workspace_id}`, {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            })
            if (wsResponse.ok) {
              const workspace = await wsResponse.json()
              workspaceMap.set(invitation.workspace_id, workspace)
            }
          } catch (err) {
            console.error('Failed to load workspace details:', err)
          }
        }
      }
      setWorkspaces(workspaceMap)
    } catch (error) {
      console.error('Error loading invitations:', error)
      showMessage('error', 'Failed to load invitations')
    } finally {
      setLoading(false)
    }
  }

  const acceptInvitation = async (invitation: PendingInvitation) => {
    try {
      const token = getStoredToken()
      if (!token) return

      // Get CSRF token
      const csrfToken = await getCsrfToken()
      if (!csrfToken) {
        throw new Error('Failed to get CSRF token')
      }

      const response = await fetch(
        `${API_BASE_URL}/workspaces/${invitation.workspace_id}/members/${invitation.id}/accept`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'X-CSRF-Token': csrfToken
          }
        }
      )

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to accept invitation')
      }

      showMessage('success', 'Invitation accepted! You now have access to the workspace.')

      // Reload invitations to remove the accepted one
      await loadInvitations()
    } catch (error: any) {
      console.error('Error accepting invitation:', error)
      showMessage('error', error.message || 'Failed to accept invitation')
    }
  }

  const declineInvitation = async (invitation: PendingInvitation) => {
    if (!confirm('Are you sure you want to decline this invitation?')) {
      return
    }

    try {
      const token = getStoredToken()
      if (!token) return

      // Get CSRF token
      const csrfToken = await getCsrfToken()
      if (!csrfToken) {
        throw new Error('Failed to get CSRF token')
      }

      const response = await fetch(
        `${API_BASE_URL}/workspaces/${invitation.workspace_id}/members/${invitation.id}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'X-CSRF-Token': csrfToken
          }
        }
      )

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to decline invitation')
      }

      showMessage('success', 'Invitation declined')
      await loadInvitations()
    } catch (error: any) {
      console.error('Error declining invitation:', error)
      showMessage('error', error.message || 'Failed to decline invitation')
    }
  }

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text })
    setTimeout(() => setMessage(null), 5000)
  }

  const getRoleBadgeColor = (role: string) => {
    switch (role.toLowerCase()) {
      case 'owner':
        return 'bg-purple-100 text-purple-800 border-purple-300'
      case 'admin':
        return 'bg-blue-100 text-blue-800 border-blue-300'
      case 'member':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'viewer':
        return 'bg-gray-100 text-gray-800 border-gray-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading invitations...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link
                href="/dashboard"
                className="text-gray-600 hover:text-gray-900 flex items-center"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Back to Dashboard
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Workspace Invitations</h1>
            </div>
            <Link
              href="/settings/workspace"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Manage Workspaces
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Message Banner */}
        {message && (
          <div
            className={`mb-6 p-4 rounded-md ${
              message.type === 'success'
                ? 'bg-green-50 text-green-800 border border-green-200'
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}
          >
            {message.text}
          </div>
        )}

        {/* Invitations List */}
        {invitations.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <svg
              className="w-16 h-16 mx-auto text-gray-400 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76"
              />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Pending Invitations</h3>
            <p className="text-gray-600 mb-6">
              You don't have any pending workspace invitations at the moment.
            </p>
            <Link
              href="/dashboard"
              className="inline-block px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Go to Dashboard
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-gray-600 mb-4">
              You have {invitations.length} pending invitation{invitations.length !== 1 ? 's' : ''}
            </p>

            {invitations.map((invitation) => {
              const workspace = workspaces.get(invitation.workspace_id)
              return (
                <div
                  key={invitation.id}
                  className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {workspace?.name || 'Workspace'}
                      </h3>
                      {workspace?.description && (
                        <p className="text-gray-600 mb-3">{workspace.description}</p>
                      )}
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>Invited as:</span>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium border ${getRoleBadgeColor(
                            invitation.role
                          )}`}
                        >
                          {invitation.role.toUpperCase()}
                        </span>
                      </div>
                      <div className="mt-2 text-xs text-gray-400">
                        Invited on {new Date(invitation.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex flex-col space-y-2 ml-6">
                      <button
                        onClick={() => acceptInvitation(invitation)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm font-medium"
                      >
                        Accept
                      </button>
                      <button
                        onClick={() => declineInvitation(invitation)}
                        className="px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 text-sm font-medium"
                      >
                        Decline
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </main>
    </div>
  )
}
