'use client'

interface Activity {
  id: string
  type: string
  description: string
  user: string
  timestamp: string
}

interface ActivityFeedProps {
  activities: Activity[]
  isLoading?: boolean
}

const ACTIVITY_ICONS: Record<string, string> = {
  project_created: '🎉',
  project_updated: '✏️',
  report_added: '📄',
  report_removed: '🗑️',
  default: '📋'
}

export function ActivityFeed({ activities, isLoading }: ActivityFeedProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Teraz'
    if (diffMins < 60) return `${diffMins} min temu`
    if (diffHours < 24) return `${diffHours} godz. temu`
    if (diffDays < 7) return `${diffDays} dni temu`

    return date.toLocaleDateString('pl-PL', {
      day: 'numeric',
      month: 'short',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    })
  }

  const getActivityIcon = (type: string) => {
    return ACTIVITY_ICONS[type] || ACTIVITY_ICONS.default
  }

  if (isLoading) {
    return (
      <div className="rounded-xl bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">
          Historia aktywności
        </h2>
        <div className="flex items-center justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-purple-600 border-t-transparent"></div>
        </div>
      </div>
    )
  }

  if (activities.length === 0) {
    return (
      <div className="rounded-xl bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">
          Historia aktywności
        </h2>
        <div className="py-8 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p className="mt-2 text-gray-500">Brak aktywności</p>
          <p className="text-sm text-gray-400">
            Aktywności projektu będą wyświetlane tutaj
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-xl bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">
        Historia aktywności
      </h2>
      <div className="space-y-4">
        {activities.map((activity) => (
          <div key={activity.id} className="flex gap-4 border-l-2 border-gray-200 pl-4 pb-4 last:pb-0">
            <div className="flex-shrink-0 text-2xl">
              {getActivityIcon(activity.type)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-900">
                {activity.description}
              </p>
              <div className="mt-1 flex items-center gap-2 text-xs text-gray-500">
                <span>{activity.user}</span>
                <span>•</span>
                <span>{formatDate(activity.timestamp)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
