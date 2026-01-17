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

interface Workspace {
  id: string
  name: string
  description: string | null
  owner_id: string
  is_active: boolean
  created_at: string
  updated_at: string
  member_count: number
  current_user_role: string
}

interface Member {
  id: string
  workspace_id: string
  user_id: string
  user_email: string
  user_name: string | null
  role: string
  invitation_accepted: boolean
  created_at: string
}

export default function WorkspaceSettingsPage() {
  const router = useRouter()
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [selectedWorkspace, setSelectedWorkspace] = useState<Workspace | null>(null)
  const [members, setMembers] = useState<Member[]>([])
  const [loading, setLoading] = useState(true)
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState('member')
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  useEffect(() => {
    loadWorkspaces()
  }, [])

  const loadWorkspaces = async () => {
    try {
      const token = getStoredToken()
      if (!token) {
        router.push('/auth/login')
        return
      }

      const response = await fetch(`${API_BASE_URL}/workspaces/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to load workspaces')
      }

      const data = await response.json()
      setWorkspaces(data)

      // Auto-select first workspace
      if (data.length > 0) {
        selectWorkspace(data[0])
      }
    } catch (error) {
      console.error('Error loading workspaces:', error)
      showMessage('error', 'Failed to load workspaces')
    } finally {
      setLoading(false)
    }
  }

  const selectWorkspace = async (workspace: Workspace) => {
    setSelectedWorkspace(workspace)
    await loadMembers(workspace.id)
  }

  const loadMembers = async (workspaceId: string) => {
    try {
      const token = getStoredToken()
      if (!token) return

      const response = await fetch(`${API_BASE_URL}/workspaces/${workspaceId}/members`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to load members')
      }

      const data = await response.json()
      setMembers(data)
    } catch (error) {
      console.error('Error loading members:', error)
      showMessage('error', 'Failed to load members')
    }
  }

  const inviteMember = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedWorkspace) return
    if (!inviteEmail || !inviteEmail.includes('@')) {
      showMessage('error', 'Please enter a valid email address')
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

      const response = await fetch(`${API_BASE_URL}/workspaces/${selectedWorkspace.id}/members`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken
        },
        body: JSON.stringify({
          email: inviteEmail,
          role: inviteRole
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to invite member')
      }

      showMessage('success', 'Member invited successfully')
      setInviteEmail('')
      setInviteRole('MEMBER')
      await loadMembers(selectedWorkspace.id)
    } catch (error: any) {
      console.error('Error inviting member:', error)
      showMessage('error', error.message || 'Failed to invite member')
    }
  }

  const removeMember = async (memberId: string, memberEmail: string) => {
    if (!selectedWorkspace) return

    if (!confirm(`Are you sure you want to remove ${memberEmail} from this workspace?`)) {
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

      const response = await fetch(`${API_BASE_URL}/workspaces/${selectedWorkspace.id}/members/${memberId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-CSRF-Token': csrfToken
        }
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to remove member')
      }

      showMessage('success', `Removed ${memberEmail} from workspace`)
      await loadMembers(selectedWorkspace.id)
    } catch (error: any) {
      console.error('Error removing member:', error)
      showMessage('error', error.message || 'Failed to remove member')
    }
  }

  const transferOwnership = async (newOwnerUserId: string, newOwnerEmail: string) => {
    if (!selectedWorkspace) return

    if (!confirm(`Are you sure you want to transfer ownership of this workspace to ${newOwnerEmail}? You will become an Admin.`)) {
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

      const response = await fetch(`${API_BASE_URL}/workspaces/${selectedWorkspace.id}/transfer-ownership`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken
        },
        body: JSON.stringify({
          new_owner_user_id: newOwnerUserId
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to transfer ownership')
      }

      showMessage('success', `Ownership transferred to ${newOwnerEmail}`)
      await loadWorkspaces()
      if (selectedWorkspace) {
        await loadMembers(selectedWorkspace.id)
      }
    } catch (error: any) {
      console.error('Error transferring ownership:', error)
      showMessage('error', error.message || 'Failed to transfer ownership')
    }
  }

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text })
    setTimeout(() => setMessage(null), 5000)
  }

  const createWorkspace = async () => {
    const workspaceName = prompt('Enter workspace name:')
    if (!workspaceName || workspaceName.trim() === '') {
      return
    }

    const description = prompt('Enter workspace description (optional):')

    try {
      const token = getStoredToken()
      if (!token) {
        router.push('/auth/login')
        return
      }

      // Get CSRF token
      const csrfToken = await getCsrfToken()
      if (!csrfToken) {
        throw new Error('Failed to get CSRF token')
      }

      const response = await fetch(`${API_BASE_URL}/workspaces/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken
        },
        body: JSON.stringify({
          name: workspaceName.trim(),
          description: description?.trim() || null
        })
      })

      if (!response.ok) {
        throw new Error('Failed to create workspace')
      }

      showMessage('success', 'Workspace created successfully')
      await loadWorkspaces()
    } catch (error) {
      console.error('Error creating workspace:', error)
      showMessage('error', 'Failed to create workspace')
    }
  }

  const canManageMembers = selectedWorkspace && ['owner', 'admin'].includes(selectedWorkspace.current_user_role.toLowerCase())

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div>
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900 text-sm mb-2 inline-block">
              ← Back to Dashboard
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">Workspace Settings</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Success/Error Messages */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg ${message.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'}`}>
            {message.text}
          </div>
        )}

        {workspaces.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600 mb-4">You are not a member of any workspace yet.</p>
            <button
              onClick={createWorkspace}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Create Workspace
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-6">
            {/* Workspace List Sidebar */}
            <div className="col-span-1">
              <div className="bg-white rounded-lg shadow">
                <div className="p-4 border-b border-gray-200">
                  <h2 className="font-semibold text-gray-900">My Workspaces</h2>
                </div>
                <div className="divide-y divide-gray-200">
                  {workspaces.map(workspace => (
                    <button
                      key={workspace.id}
                      onClick={() => selectWorkspace(workspace)}
                      className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${
                        selectedWorkspace?.id === workspace.id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
                      }`}
                    >
                      <div className="font-medium text-gray-900">{workspace.name}</div>
                      <div className="text-sm text-gray-500 mt-1">
                        {workspace.member_count} {workspace.member_count === 1 ? 'member' : 'members'}
                      </div>
                      <div className="text-xs text-gray-400 mt-1">
                        Role: {workspace.current_user_role}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Workspace Details */}
            <div className="col-span-2">
              {selectedWorkspace ? (
                <div className="space-y-6">
                  {/* Workspace Info */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">{selectedWorkspace.name}</h2>
                    {selectedWorkspace.description && (
                      <p className="text-gray-600 mb-4">{selectedWorkspace.description}</p>
                    )}
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>Created: {new Date(selectedWorkspace.created_at).toLocaleDateString()}</span>
                      <span>•</span>
                      <span>{selectedWorkspace.member_count} members</span>
                    </div>
                  </div>

                  {/* Members Section */}
                  <div className="bg-white rounded-lg shadow">
                    <div className="p-6 border-b border-gray-200">
                      <h3 className="text-lg font-semibold text-gray-900">Members</h3>
                    </div>

                    {/* Invite Form */}
                    {canManageMembers && (
                      <div className="p-6 border-b border-gray-200 bg-gray-50">
                        <form onSubmit={inviteMember} className="flex gap-4">
                          <input
                            type="email"
                            value={inviteEmail}
                            onChange={(e) => setInviteEmail(e.target.value)}
                            placeholder="Email address"
                            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                          <select
                            value={inviteRole}
                            onChange={(e) => setInviteRole(e.target.value)}
                            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          >
                            <option value="viewer">Viewer</option>
                            <option value="member">Member</option>
                            <option value="admin">Admin</option>
                          </select>
                          <button
                            type="submit"
                            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 whitespace-nowrap"
                          >
                            Invite Member
                          </button>
                        </form>
                      </div>
                    )}

                    {/* Members List */}
                    <div className="divide-y divide-gray-200">
                      {members.map(member => (
                        <div key={member.id} className="p-6 flex items-center justify-between">
                          <div>
                            <div className="font-medium text-gray-900">
                              {member.user_name || member.user_email}
                            </div>
                            <div className="text-sm text-gray-500">{member.user_email}</div>
                            <div className="flex items-center gap-2 mt-1">
                              <span className={`text-xs px-2 py-1 rounded ${
                                member.role.toLowerCase() === 'owner' ? 'bg-purple-100 text-purple-800' :
                                member.role.toLowerCase() === 'admin' ? 'bg-blue-100 text-blue-800' :
                                member.role.toLowerCase() === 'member' ? 'bg-green-100 text-green-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {member.role.toUpperCase()}
                              </span>
                              {!member.invitation_accepted && (
                                <span className="text-xs px-2 py-1 rounded bg-yellow-100 text-yellow-800">
                                  Invitation Pending
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="flex gap-2">
                            {/* Transfer Ownership - only owner can transfer */}
                            {selectedWorkspace && selectedWorkspace.current_user_role.toLowerCase() === 'owner' && member.role.toLowerCase() !== 'owner' && member.invitation_accepted && (
                              <button
                                onClick={() => transferOwnership(member.user_id, member.user_email)}
                                className="text-purple-600 hover:text-purple-800 text-sm font-medium"
                              >
                                Transfer Ownership
                              </button>
                            )}
                            {/* Remove - owner/admin can remove non-owners */}
                            {canManageMembers && member.role.toLowerCase() !== 'owner' && (
                              <button
                                onClick={() => removeMember(member.id, member.user_email)}
                                className="text-red-600 hover:text-red-800 text-sm font-medium"
                              >
                                Remove
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
                  Select a workspace to view details
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
