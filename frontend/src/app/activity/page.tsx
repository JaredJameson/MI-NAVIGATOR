'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { getStoredToken } from '@/services/api'
import { formatDateInTimezone } from '@/utils/date'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface ActivityItem {
  id: string
  type: string
  title: string
  description: string
  metadata: Record<string, unknown>
  timestamp: string
}

interface ActivityResponse {
  items: ActivityItem[]
  total: number
  page: number
  limit: number
  pages: number
}

interface ActivityTypeInfo {
  type: string
  label: string
  icon: string
  color: string
  count: number
}

// Activity type icon mapping
const ACTIVITY_ICONS: Record<string, string> = {
  'document-add': '📄',
  'eye': '👁️',
  'download': '⬇️',
  'trash': '🗑️',
  'search': '🔍',
  'folder-add': '📁',
  'folder': '📂',
  'chat': '💬',
  'login': '🔓',
  'logout': '🔒',
  'cog': '⚙️',
  'bell': '🔔',
}

// Activity type color mapping
const ACTIVITY_COLORS: Record<string, string> = {
  'green': 'bg-green-100 text-green-800 border-green-200',
  'blue': 'bg-blue-100 text-blue-800 border-blue-200',
  'purple': 'bg-purple-100 text-purple-800 border-purple-200',
  'red': 'bg-red-100 text-red-800 border-red-200',
  'gray': 'bg-gray-100 text-gray-800 border-gray-200',
  'yellow': 'bg-yellow-100 text-yellow-800 border-yellow-200',
  'orange': 'bg-orange-100 text-orange-800 border-orange-200',
}

export default function ActivityPage() {
  const router = useRouter()
  const [activities, setActivities] = useState<ActivityItem[]>([])
  const [activityTypes, setActivityTypes] = useState<ActivityTypeInfo[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [filterType, setFilterType] = useState('')
  const [userTimezone, setUserTimezone] = useState('Europe/Warsaw')

  // Export state
  const [showExportModal, setShowExportModal] = useState(false)
  // Set sensible date defaults: 30 days ago to today
  const [exportDateFrom, setExportDateFrom] = useState(() => {
    const date = new Date()
    date.setDate(date.getDate() - 30)
    return date.toISOString().split('T')[0]
  })
  const [exportDateTo, setExportDateTo] = useState(() => {
    return new Date().toISOString().split('T')[0]
  })
  const [isExporting, setIsExporting] = useState(false)

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalActivities, setTotalActivities] = useState(0)
  const pageSize = 10

  useEffect(() => {
    fetchActivityTypes()
    fetchUserTimezone()
  }, [])

  useEffect(() => {
    fetchActivities()
  }, [filterType, currentPage])

  const fetchUserTimezone = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const user = await response.json()
        if (user.timezone) {
          setUserTimezone(user.timezone)
        }
      }
    } catch (err) {
      console.error('Failed to fetch user timezone:', err)
    }
  }

  const fetchActivityTypes = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/activity/types`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setActivityTypes(data.types || [])
      }
    } catch (err) {
      console.error('Failed to fetch activity types:', err)
    }
  }

  const fetchActivities = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const params = new URLSearchParams()
      params.append('page', currentPage.toString())
      params.append('limit', pageSize.toString())
      if (filterType) {
        params.append('type', filterType)
      }

      const response = await fetch(`${API_BASE_URL}/activity/?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        if (response.status === 401) {
          router.push('/auth/login')
          return
        }
        throw new Error('Failed to fetch activities')
      }

      const data: ActivityResponse = await response.json()
      setActivities(data.items)
      setTotalPages(data.pages)
      setTotalActivities(data.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load activities')
    } finally {
      setIsLoading(false)
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
      // Use timezone-aware formatting for older dates
      return formatDateInTimezone(timestamp, userTimezone, 'pl-PL')
    }
  }

  const getActivityTypeInfo = (type: string) => {
    return activityTypes.find(t => t.type === type)
  }

  const handleFilterChange = (type: string) => {
    setFilterType(type)
    setCurrentPage(1)
  }

  const handleExport = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsExporting(true)

    try {
      const params = new URLSearchParams()
      if (exportDateFrom) {
        params.append('date_from', new Date(exportDateFrom).toISOString())
      }
      if (exportDateTo) {
        params.append('date_to', new Date(exportDateTo).toISOString())
      }
      if (filterType) {
        params.append('type', filterType)
      }

      const response = await fetch(`${API_BASE_URL}/activity/export/csv?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to export activities')
      }

      // Get the filename from Content-Disposition header or use default
      const contentDisposition = response.headers.get('Content-Disposition')
      let filename = 'activity-export.csv'
      if (contentDisposition) {
        const match = contentDisposition.match(/filename=(.+)/)
        if (match) {
          filename = match[1]
        }
      }

      // Download the file
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      setShowExportModal(false)
      setExportDateFrom('')
      setExportDateTo('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export activities')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Historia aktywnosci</h1>
              <p className="mt-1 text-sm text-gray-500">
                Przegladaj swoja ostatnia aktywnosc w systemie
              </p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowExportModal(true)}
                className="px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
              >
                <span>⬇️</span>
                Eksportuj
              </button>
              <button
                onClick={() => router.push('/dashboard')}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
              >
                ← Powrot do dashboardu
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Export Modal */}
      {showExportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Eksportuj aktywnosci</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Data od
                </label>
                <input
                  type="date"
                  value={exportDateFrom}
                  onChange={(e) => setExportDateFrom(e.target.value)}
                  max={new Date().toISOString().split('T')[0]}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Data do
                </label>
                <input
                  type="date"
                  value={exportDateTo}
                  onChange={(e) => setExportDateTo(e.target.value)}
                  max={new Date().toISOString().split('T')[0]}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              {filterType && (
                <p className="text-sm text-gray-500">
                  Eksport bedzie zawierac tylko aktywnosci typu: {activityTypes.find(t => t.type === filterType)?.label}
                </p>
              )}
              <p className="text-sm text-gray-500">
                Pozostaw puste, aby eksportowac wszystkie aktywnosci.
              </p>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowExportModal(false)
                  setExportDateFrom('')
                  setExportDateTo('')
                }}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
              >
                Anuluj
              </button>
              <button
                onClick={handleExport}
                disabled={isExporting}
                className="px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isExporting ? (
                  <>
                    <span className="animate-spin">⏳</span>
                    Eksportowanie...
                  </>
                ) : (
                  <>
                    <span>⬇️</span>
                    Eksportuj CSV
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <div className="w-full lg:w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h3 className="font-semibold text-gray-900 mb-4">Filtruj po typie</h3>
              <div className="space-y-2">
                <button
                  onClick={() => handleFilterChange('')}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                    filterType === ''
                      ? 'bg-blue-100 text-blue-800 font-medium'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  Wszystkie ({totalActivities})
                </button>
                {activityTypes.map((type) => (
                  <button
                    key={type.type}
                    onClick={() => handleFilterChange(type.type)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center justify-between ${
                      filterType === type.type
                        ? 'bg-blue-100 text-blue-800 font-medium'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <span>{ACTIVITY_ICONS[type.icon] || '📌'}</span>
                      <span>{type.label}</span>
                    </span>
                    <span className="text-xs bg-gray-200 px-2 py-0.5 rounded-full">
                      {type.count}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Activity List */}
          <div className="flex-1">
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                {error}
              </div>
            )}

            {isLoading ? (
              <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-gray-500">Ladowanie aktywnosci...</p>
              </div>
            ) : activities.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                <p className="text-gray-500">Brak aktywnosci do wyswietlenia</p>
              </div>
            ) : (
              <>
                <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                  <ul className="divide-y divide-gray-200">
                    {activities.map((activity) => {
                      const typeInfo = getActivityTypeInfo(activity.type)
                      const colorClass = typeInfo
                        ? ACTIVITY_COLORS[typeInfo.color] || ACTIVITY_COLORS['gray']
                        : ACTIVITY_COLORS['gray']
                      const icon = typeInfo
                        ? ACTIVITY_ICONS[typeInfo.icon] || '📌'
                        : '📌'

                      return (
                        <li key={activity.id} className="p-4 hover:bg-gray-50 transition-colors">
                          <div className="flex items-start gap-4">
                            <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${colorClass}`}>
                              <span className="text-lg">{icon}</span>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between">
                                <p className="text-sm font-medium text-gray-900">
                                  {activity.title}
                                </p>
                                <span className="text-xs text-gray-500">
                                  {formatTimestamp(activity.timestamp)}
                                </span>
                              </div>
                              <p className="mt-1 text-sm text-gray-600 line-clamp-2" title={activity.description}>
                                {activity.description}
                              </p>
                              {typeInfo && (
                                <span className={`inline-block mt-2 px-2 py-0.5 text-xs rounded-full ${colorClass}`}>
                                  {typeInfo.label}
                                </span>
                              )}
                            </div>
                          </div>
                        </li>
                      )
                    })}
                  </ul>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="mt-4 flex items-center justify-between bg-white rounded-lg shadow-sm px-4 py-3">
                    <div className="text-sm text-gray-500">
                      Strona {currentPage} z {totalPages} ({totalActivities} aktywnosci)
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                        className="px-3 py-1 text-sm border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                      >
                        Poprzednia
                      </button>
                      {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                        <button
                          key={page}
                          onClick={() => setCurrentPage(page)}
                          className={`px-3 py-1 text-sm border rounded-lg ${
                            currentPage === page
                              ? 'bg-blue-600 text-white border-blue-600'
                              : 'hover:bg-gray-50'
                          }`}
                        >
                          {page}
                        </button>
                      ))}
                      <button
                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                        className="px-3 py-1 text-sm border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                      >
                        Nastepna
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
