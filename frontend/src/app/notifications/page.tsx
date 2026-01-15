'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface NotificationItem {
  id: string
  type: string
  title: string
  message: string
  link: string | null
  read: boolean
  created_at: string
}

interface NotificationsResponse {
  items: NotificationItem[]
  total: number
  unread_count: number
}

// Notification type icons
const NOTIFICATION_ICONS: Record<string, string> = {
  'report_ready': '📄',
  'alert': '🔔',
  'project_update': '📁',
  'comment': '💬',
  'system': 'ℹ️',
}

// Notification type colors
const NOTIFICATION_COLORS: Record<string, string> = {
  'report_ready': 'bg-green-100 text-green-800',
  'alert': 'bg-orange-100 text-orange-800',
  'project_update': 'bg-blue-100 text-blue-800',
  'comment': 'bg-purple-100 text-purple-800',
  'system': 'bg-gray-100 text-gray-800',
}

export default function NotificationsPage() {
  const router = useRouter()
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [unreadCount, setUnreadCount] = useState(0)
  const [showUnreadOnly, setShowUnreadOnly] = useState(false)

  useEffect(() => {
    fetchNotifications()
  }, [showUnreadOnly])

  const fetchNotifications = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const params = new URLSearchParams()
      if (showUnreadOnly) {
        params.append('unread_only', 'true')
      }

      const response = await fetch(`${API_BASE_URL}/notifications/?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        if (response.status === 401) {
          router.push('/auth/login')
          return
        }
        throw new Error('Failed to fetch notifications')
      }

      const data: NotificationsResponse = await response.json()
      setNotifications(data.items)
      setUnreadCount(data.unread_count)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load notifications')
    } finally {
      setIsLoading(false)
    }
  }

  const markAsRead = async (notificationId: string) => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/notifications/mark-read`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ notification_ids: [notificationId] }),
      })

      if (response.ok) {
        const data = await response.json()
        setUnreadCount(data.unread_count)
        // Update local state
        setNotifications(prev =>
          prev.map(n =>
            n.id === notificationId ? { ...n, read: true } : n
          )
        )
      }
    } catch (err) {
      console.error('Failed to mark notification as read:', err)
    }
  }

  const markAllAsRead = async () => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/notifications/mark-all-read`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setUnreadCount(data.unread_count)
        // Update local state
        setNotifications(prev =>
          prev.map(n => ({ ...n, read: true }))
        )
      }
    } catch (err) {
      console.error('Failed to mark all notifications as read:', err)
    }
  }

  const handleNotificationClick = async (notification: NotificationItem) => {
    if (!notification.read) {
      await markAsRead(notification.id)
    }
    if (notification.link) {
      router.push(notification.link)
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffMins < 60) {
      return `${diffMins} min temu`
    } else if (diffHours < 24) {
      return `${diffHours} godz. temu`
    } else if (diffDays < 7) {
      return `${diffDays} dni temu`
    } else {
      return date.toLocaleDateString('pl-PL', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      })
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-gray-900">Powiadomienia</h1>
              {unreadCount > 0 && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  {unreadCount} nieprzeczytanych
                </span>
              )}
            </div>
            <div className="flex items-center gap-4">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="px-4 py-2 text-sm text-blue-600 hover:text-blue-800 font-medium"
                >
                  Oznacz wszystkie jako przeczytane
                </button>
              )}
              <Link
                href="/dashboard"
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
              >
                ← Powrot do dashboardu
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filter */}
        <div className="mb-6 flex items-center gap-4">
          <button
            onClick={() => setShowUnreadOnly(false)}
            className={`px-4 py-2 text-sm rounded-lg ${
              !showUnreadOnly
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Wszystkie
          </button>
          <button
            onClick={() => setShowUnreadOnly(true)}
            className={`px-4 py-2 text-sm rounded-lg ${
              showUnreadOnly
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Tylko nieprzeczytane
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="bg-white rounded-lg shadow-sm p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-500">Ladowanie powiadomien...</p>
          </div>
        ) : notifications.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-8 text-center">
            <span className="text-4xl">🔔</span>
            <p className="mt-4 text-gray-500">
              {showUnreadOnly ? 'Brak nieprzeczytanych powiadomien' : 'Brak powiadomien'}
            </p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <ul className="divide-y divide-gray-200">
              {notifications.map((notification) => {
                const icon = NOTIFICATION_ICONS[notification.type] || '🔔'
                const colorClass = NOTIFICATION_COLORS[notification.type] || 'bg-gray-100 text-gray-800'

                return (
                  <li
                    key={notification.id}
                    onClick={() => handleNotificationClick(notification)}
                    className={`p-4 cursor-pointer transition-colors ${
                      notification.read
                        ? 'bg-white hover:bg-gray-50'
                        : 'bg-blue-50 hover:bg-blue-100'
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${colorClass}`}>
                        <span className="text-lg">{icon}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className={`text-sm font-medium ${notification.read ? 'text-gray-900' : 'text-gray-900'}`}>
                            {notification.title}
                            {!notification.read && (
                              <span className="ml-2 inline-flex w-2 h-2 bg-blue-600 rounded-full"></span>
                            )}
                          </p>
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(notification.created_at)}
                          </span>
                        </div>
                        <p className={`mt-1 text-sm ${notification.read ? 'text-gray-600' : 'text-gray-700'}`}>
                          {notification.message}
                        </p>
                      </div>
                    </div>
                  </li>
                )
              })}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
