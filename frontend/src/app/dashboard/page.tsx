'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { authApi } from '@/services/api'

// Widget type definition
interface Widget {
  id: string
  title: string
  type: 'active-research' | 'recent-activity' | 'usage-stats' | 'projects' | 'alerts'
}

// Default widget order
const DEFAULT_WIDGETS: Widget[] = [
  { id: 'active-research', title: 'Active Research', type: 'active-research' },
  { id: 'recent-activity', title: 'Recent Activity', type: 'recent-activity' },
  { id: 'usage-stats', title: 'Usage Stats', type: 'usage-stats' },
  { id: 'projects', title: 'My Projects', type: 'projects' },
  { id: 'alerts', title: 'Alerts & Monitoring', type: 'alerts' },
]

const LAYOUT_STORAGE_KEY = 'mi-navigator-dashboard-layout'

export default function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const [isCustomizeMode, setIsCustomizeMode] = useState(false)
  const [widgets, setWidgets] = useState<Widget[]>(DEFAULT_WIDGETS)
  const [isSaving, setIsSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState('')
  const router = useRouter()

  // Load saved layout on mount
  useEffect(() => {
    const savedLayout = localStorage.getItem(LAYOUT_STORAGE_KEY)
    if (savedLayout) {
      try {
        const parsed = JSON.parse(savedLayout)
        // Validate the parsed data has all required widgets
        if (Array.isArray(parsed) && parsed.length === DEFAULT_WIDGETS.length) {
          const hasAllWidgets = DEFAULT_WIDGETS.every(dw =>
            parsed.some((pw: Widget) => pw.id === dw.id)
          )
          if (hasAllWidgets) {
            setWidgets(parsed)
          }
        }
      } catch (e) {
        console.error('Failed to load dashboard layout:', e)
      }
    }
  }, [])

  const handleLogout = async () => {
    setIsLoggingOut(true)
    try {
      await authApi.logout()
      router.push('/auth/login')
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      setIsLoggingOut(false)
    }
  }

  const moveWidget = (index: number, direction: 'up' | 'down') => {
    const newWidgets = [...widgets]
    const targetIndex = direction === 'up' ? index - 1 : index + 1

    if (targetIndex < 0 || targetIndex >= widgets.length) return

    // Swap widgets
    [newWidgets[index], newWidgets[targetIndex]] = [newWidgets[targetIndex], newWidgets[index]]
    setWidgets(newWidgets)
  }

  const saveLayout = () => {
    setIsSaving(true)
    try {
      localStorage.setItem(LAYOUT_STORAGE_KEY, JSON.stringify(widgets))
      setSaveMessage('Układ zapisany pomyślnie!')
      setTimeout(() => setSaveMessage(''), 3000)
    } catch (e) {
      console.error('Failed to save layout:', e)
      setSaveMessage('Błąd zapisu układu')
    } finally {
      setIsSaving(false)
      setIsCustomizeMode(false)
    }
  }

  const resetLayout = () => {
    setWidgets(DEFAULT_WIDGETS)
    localStorage.removeItem(LAYOUT_STORAGE_KEY)
    setSaveMessage('Układ przywrócony do domyślnego')
    setTimeout(() => setSaveMessage(''), 3000)
  }

  const cancelCustomize = () => {
    // Reload saved layout or default
    const savedLayout = localStorage.getItem(LAYOUT_STORAGE_KEY)
    if (savedLayout) {
      try {
        setWidgets(JSON.parse(savedLayout))
      } catch (e) {
        setWidgets(DEFAULT_WIDGETS)
      }
    } else {
      setWidgets(DEFAULT_WIDGETS)
    }
    setIsCustomizeMode(false)
  }

  // Widget rendering components
  const renderWidget = (widget: Widget, index: number) => {
    const isFirst = index === 0
    const isLast = index === widgets.length - 1

    const wrapperClasses = isCustomizeMode
      ? 'relative border-2 border-dashed border-blue-300 rounded-xl'
      : ''

    const CustomizeOverlay = () => (
      <div className="absolute -top-3 -right-3 flex gap-1 z-10">
        <button
          onClick={() => moveWidget(index, 'up')}
          disabled={isFirst}
          className="rounded-full bg-blue-600 p-1.5 text-white shadow-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          title="Przesuń w górę"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
          </svg>
        </button>
        <button
          onClick={() => moveWidget(index, 'down')}
          disabled={isLast}
          className="rounded-full bg-blue-600 p-1.5 text-white shadow-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          title="Przesuń w dół"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
    )

    switch (widget.type) {
      case 'active-research':
        return (
          <div key={widget.id} className={wrapperClasses}>
            {isCustomizeMode && <CustomizeOverlay />}
            <ActiveResearchWidget />
          </div>
        )
      case 'recent-activity':
        return (
          <div key={widget.id} className={wrapperClasses}>
            {isCustomizeMode && <CustomizeOverlay />}
            <RecentActivityWidget />
          </div>
        )
      case 'usage-stats':
        return (
          <div key={widget.id} className={wrapperClasses}>
            {isCustomizeMode && <CustomizeOverlay />}
            <UsageStatsWidget />
          </div>
        )
      case 'projects':
        return (
          <div key={widget.id} className={`col-span-full ${wrapperClasses}`}>
            {isCustomizeMode && <CustomizeOverlay />}
            <ProjectsWidget />
          </div>
        )
      case 'alerts':
        return (
          <div key={widget.id} className={`col-span-full ${wrapperClasses}`}>
            {isCustomizeMode && <CustomizeOverlay />}
            <AlertsWidget />
          </div>
        )
      default:
        return null
    }
  }

  // Get grid widgets (first 3) and full-width widgets (rest)
  const gridWidgets = widgets.filter(w => ['active-research', 'recent-activity', 'usage-stats'].includes(w.type))
  const fullWidgets = widgets.filter(w => ['projects', 'alerts'].includes(w.type))

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">MI-Navigator</h1>
            <nav className="flex items-center space-x-4">
              <Link href="/reports" className="text-gray-600 hover:text-gray-900">
                Reports
              </Link>
              <Link href="/projects" className="text-gray-600 hover:text-gray-900">
                Projects
              </Link>
              <Link href="/settings" className="text-gray-600 hover:text-gray-900">
                Settings
              </Link>
              <button
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="rounded-md bg-red-600 px-3 py-1.5 text-sm text-white hover:bg-red-700 disabled:opacity-50"
              >
                {isLoggingOut ? 'Logging out...' : 'Logout'}
              </button>
            </nav>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Customize Mode Banner */}
        {isCustomizeMode && (
          <div className="mb-4 rounded-lg bg-blue-50 border border-blue-200 p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
                <span className="font-medium text-blue-800">Tryb dostosowywania</span>
                <span className="text-sm text-blue-600">- Użyj strzałek aby zmienić kolejność widgetów</span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={resetLayout}
                  className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Resetuj
                </button>
                <button
                  onClick={cancelCustomize}
                  className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Anuluj
                </button>
                <button
                  onClick={saveLayout}
                  disabled={isSaving}
                  className="rounded-md bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {isSaving ? 'Zapisywanie...' : 'Zapisz układ'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Save Message Toast */}
        {saveMessage && (
          <div className="mb-4 rounded-lg bg-green-50 border border-green-200 p-3 text-green-800 text-sm">
            {saveMessage}
          </div>
        )}

        {/* Customize Button (when not in customize mode) */}
        {!isCustomizeMode && (
          <div className="mb-4 flex justify-end">
            <button
              onClick={() => setIsCustomizeMode(true)}
              className="flex items-center gap-2 rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
              </svg>
              Dostosuj układ
            </button>
          </div>
        )}

        {/* Quick Search */}
        <div className="mb-8 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white">
          <h2 className="mb-4 text-xl font-semibold">Rozpocznij badanie</h2>
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Szukaj firmy, osoby, wklej URL do analizy..."
              className="w-full rounded-lg bg-white px-4 py-3 pl-12 text-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-white"
            />
            <svg
              className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="text-sm text-blue-200">Ostatnie:</span>
            <button className="rounded bg-white/20 px-2 py-1 text-sm hover:bg-white/30">
              FADO Sp. z o.o.
            </button>
            <button className="rounded bg-white/20 px-2 py-1 text-sm hover:bg-white/30">
              Splast S.A.
            </button>
          </div>
        </div>

        {/* Widgets Grid - Rendered based on saved order */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {gridWidgets.map((widget, idx) => {
            const globalIndex = widgets.findIndex(w => w.id === widget.id)
            return renderWidget(widget, globalIndex)
          })}
        </div>

        {/* Full-width Widgets */}
        <div className="mt-8 space-y-8">
          {fullWidgets.map((widget) => {
            const globalIndex = widgets.findIndex(w => w.id === widget.id)
            return renderWidget(widget, globalIndex)
          })}
        </div>
      </main>
    </div>
  )
}

// Individual Widget Components
function ActiveResearchWidget() {
  return (
    <div className="rounded-xl bg-white p-6 shadow-sm h-full">
      <h3 className="mb-4 font-semibold text-gray-900">Active Research</h3>
      <div className="rounded-lg bg-gray-50 p-4">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />
          <span className="text-sm font-medium">Analiza FADO</span>
        </div>
        <div className="mt-2">
          <div className="text-sm text-gray-500">Progress: 67%</div>
          <div className="mt-1 h-2 rounded-full bg-gray-200">
            <div className="h-full w-2/3 rounded-full bg-blue-500" />
          </div>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <Link
          href="/chat"
          className="inline-block rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
        >
          Start New Research
        </Link>
        <Link
          href="/analysis"
          className="inline-block rounded-md border border-blue-600 px-4 py-2 text-sm text-blue-600 hover:bg-blue-50"
        >
          Market Analysis
        </Link>
        <Link
          href="/search"
          className="inline-block rounded-md border border-indigo-600 px-4 py-2 text-sm text-indigo-600 hover:bg-indigo-50"
        >
          PKD Search
        </Link>
      </div>
    </div>
  )
}

function RecentActivityWidget() {
  return (
    <div className="rounded-xl bg-white p-6 shadow-sm h-full">
      <h3 className="mb-4 font-semibold text-gray-900">Recent Activity</h3>
      <ul className="space-y-3">
        <li className="text-sm">
          <span className="text-gray-500">14:32</span> - Raport FADO zakończony
        </li>
        <li className="text-sm">
          <span className="text-gray-500">12:15</span> - Nowy alert: Konkurent X
        </li>
        <li className="text-sm">
          <span className="text-gray-500">11:45</span> - Upload: raport_q3.pdf
        </li>
      </ul>
      <Link href="/activity" className="mt-4 inline-block text-sm text-blue-600 hover:underline">
        Zobacz wszystkie →
      </Link>
    </div>
  )
}

function UsageStatsWidget() {
  return (
    <div className="rounded-xl bg-white p-6 shadow-sm h-full">
      <h3 className="mb-4 font-semibold text-gray-900">Usage Stats</h3>
      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Analyses this month</span>
            <span className="font-medium">42/100</span>
          </div>
          <div className="mt-1 h-2 rounded-full bg-gray-200">
            <div className="h-full w-[42%] rounded-full bg-blue-500" />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Storage</span>
            <span className="font-medium">2.4 GB / 10 GB</span>
          </div>
          <div className="mt-1 h-2 rounded-full bg-gray-200">
            <div className="h-full w-[24%] rounded-full bg-green-500" />
          </div>
        </div>
        <div className="text-sm text-gray-600">
          API calls: <span className="font-medium">8,432</span>
        </div>
      </div>
    </div>
  )
}

function ProjectsWidget() {
  return (
    <section>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">My Projects</h2>
        <Link
          href="/projects/new"
          className="rounded-md bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700"
        >
          + New
        </Link>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {['Due Diligence - ACME Corp', 'Market Entry - Germany', 'Competitive Watch'].map(
          (project) => (
            <div
              key={project}
              className="cursor-pointer rounded-xl bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="flex items-start gap-3">
                <span className="text-2xl">📁</span>
                <div>
                  <h3 className="font-medium text-gray-900">{project}</h3>
                  <div className="mt-2 flex gap-4 text-sm text-gray-500">
                    <span>📄 5 reports</span>
                    <span>🔔 3 alerts</span>
                  </div>
                  <div className="mt-2 text-xs text-gray-400">Updated: 2 days ago</div>
                </div>
              </div>
            </div>
          )
        )}
      </div>
    </section>
  )
}

function AlertsWidget() {
  return (
    <section>
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Alerts & Monitoring</h2>
      <div className="space-y-2">
        <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-3">
          <span>🔴</span>
          <div>
            <p className="text-sm font-medium text-red-800">Konkurent X: nowy produkt</p>
            <p className="text-xs text-red-600">Wykryto ogłoszenie nowego produktu</p>
          </div>
        </div>
        <div className="flex items-start gap-2 rounded-lg border border-yellow-200 bg-yellow-50 p-3">
          <span>🟡</span>
          <div>
            <p className="text-sm font-medium text-yellow-800">FADO: zmiana w zarządzie</p>
            <p className="text-xs text-yellow-600">Nowy członek zarządu</p>
          </div>
        </div>
        <div className="flex items-start gap-2 rounded-lg border border-green-200 bg-green-50 p-3">
          <span>🟢</span>
          <div>
            <p className="text-sm font-medium text-green-800">Rynek +5% vs prognoza</p>
            <p className="text-xs text-green-600">Pozytywny trend rynkowy</p>
          </div>
        </div>
      </div>
    </section>
  )
}
