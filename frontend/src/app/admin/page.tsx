'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

interface SystemStats {
  total_users: number
  active_users: number
  total_reports: number
  total_searches: number
  total_analyses: number
}

interface UserProfile {
  id: string
  email: string
  name?: string
  role: string
}

export default function AdminDashboard() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [isAuthorized, setIsAuthorized] = useState(false)
  const [stats, setStats] = useState<SystemStats | null>(null)
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkAuthAndFetchData = async () => {
      try {
        const token = getStoredToken()
        if (!token) {
          router.push('/auth/login')
          return
        }

        // Fetch current user profile to check role
        const profileResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/users/me`,
          {
            headers: { 'Authorization': `Bearer ${token}` }
          }
        )

        if (!profileResponse.ok) {
          if (profileResponse.status === 401) {
            router.push('/auth/login')
            return
          }
          throw new Error('Failed to fetch user profile')
        }

        const profile = await profileResponse.json()
        setCurrentUser(profile)

        // Check if user is admin
        if (profile.role !== 'admin') {
          setError('Access Denied: Admin privileges required')
          setIsAuthorized(false)
          setIsLoading(false)
          return
        }

        setIsAuthorized(true)

        // Fetch admin stats
        const statsResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/admin/stats`,
          {
            headers: { 'Authorization': `Bearer ${token}` }
          }
        )

        if (!statsResponse.ok) {
          if (statsResponse.status === 403) {
            setError('Access Denied: Admin privileges required')
            setIsAuthorized(false)
            return
          }
          throw new Error('Failed to fetch stats')
        }

        const statsData = await statsResponse.json()
        setStats(statsData)
      } catch (err) {
        console.error('Error:', err)
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setIsLoading(false)
      }
    }

    checkAuthAndFetchData()
  }, [router])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Verifying authorization...</p>
        </div>
      </div>
    )
  }

  if (!isAuthorized || error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
              <svg className="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
            <p className="text-gray-600 mb-6">
              {error || 'You do not have permission to access the admin panel. Admin privileges are required.'}
            </p>
            <div className="space-y-2">
              <Link
                href="/dashboard"
                className="block w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
              >
                Go to Dashboard
              </Link>
              {currentUser && (
                <p className="text-sm text-gray-500 mt-4">
                  Logged in as: {currentUser.email} ({currentUser.role})
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Panel</h1>
              <p className="text-sm text-gray-600 mt-1">
                Logged in as: {currentUser?.email} ({currentUser?.role})
              </p>
            </div>
            <Link
              href="/dashboard"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <StatCard
            title="Total Users"
            value={stats?.total_users || 0}
            icon="👥"
            color="blue"
          />
          <StatCard
            title="Active Users"
            value={stats?.active_users || 0}
            icon="✅"
            color="green"
          />
          <StatCard
            title="Reports"
            value={stats?.total_reports || 0}
            icon="📄"
            color="purple"
          />
          <StatCard
            title="Searches"
            value={stats?.total_searches || 0}
            icon="🔍"
            color="yellow"
          />
          <StatCard
            title="Analyses"
            value={stats?.total_analyses || 0}
            icon="📊"
            color="red"
          />
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              href="/admin/users"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
            >
              <div className="flex-shrink-0 w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-2xl mr-4">
                👥
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">User Management</h3>
                <p className="text-sm text-gray-600">Manage users and roles</p>
              </div>
            </Link>

            <Link
              href="/settings"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
            >
              <div className="flex-shrink-0 w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-2xl mr-4">
                ⚙️
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">System Settings</h3>
                <p className="text-sm text-gray-600">Configure system preferences</p>
              </div>
            </Link>

            <Link
              href="/reports"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
            >
              <div className="flex-shrink-0 w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center text-2xl mr-4">
                📊
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">View Reports</h3>
                <p className="text-sm text-gray-600">Access all system reports</p>
              </div>
            </Link>
          </div>
        </div>

        {/* Admin Features */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Admin Features</h2>
          <div className="space-y-3">
            <div className="flex items-start">
              <div className="flex-shrink-0 text-green-500 mt-1">✓</div>
              <div className="ml-3">
                <p className="text-gray-900 font-medium">User Management</p>
                <p className="text-sm text-gray-600">Create, edit, and delete user accounts</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 text-green-500 mt-1">✓</div>
              <div className="ml-3">
                <p className="text-gray-900 font-medium">Role Assignment</p>
                <p className="text-sm text-gray-600">Manage user roles and permissions</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 text-green-500 mt-1">✓</div>
              <div className="ml-3">
                <p className="text-gray-900 font-medium">System Statistics</p>
                <p className="text-sm text-gray-600">View real-time system usage metrics</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

interface StatCardProps {
  title: string
  value: number
  icon: string
  color: 'blue' | 'green' | 'purple' | 'yellow' | 'red'
}

function StatCard({ title, value, icon, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-2xl ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  )
}
