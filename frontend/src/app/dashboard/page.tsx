'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { authApi, searchApi, SearchSuggestion, getStoredToken } from '@/services/api'
import { DashboardSkeleton } from '@/components/Skeleton'
import { formatRelativeTime } from '@/utils/date'
import { Sidebar } from '@/components/Sidebar'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// Widget type definition
interface Widget {
  id: string
  title: string
  type: 'active-research' | 'recent-activity' | 'usage-stats' | 'projects' | 'alerts'
  visible: boolean
}

// Default widget order
const DEFAULT_WIDGETS: Widget[] = [
  { id: 'active-research', title: 'Active Research', type: 'active-research', visible: true },
  { id: 'recent-activity', title: 'Recent Activity', type: 'recent-activity', visible: true },
  { id: 'usage-stats', title: 'Usage Stats', type: 'usage-stats', visible: true },
  { id: 'projects', title: 'My Projects', type: 'projects', visible: true },
  { id: 'alerts', title: 'Alerts & Monitoring', type: 'alerts', visible: true },
]

const LAYOUT_STORAGE_KEY = 'mi-navigator-dashboard-layout'
const SEARCH_HISTORY_KEY = 'mi-navigator-search-history'
const MAX_SEARCH_HISTORY = 5

// Search history item type
interface SearchHistoryItem {
  id: string
  name: string
  type: string
  url: string
  timestamp: number
}

export default function DashboardPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const [isCustomizeMode, setIsCustomizeMode] = useState(false)
  const [widgets, setWidgets] = useState<Widget[]>(DEFAULT_WIDGETS)
  const [isSaving, setIsSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState('')
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false)
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1)
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([])
  const searchInputRef = useRef<HTMLInputElement>(null)
  const suggestionsRef = useRef<HTMLDivElement>(null)
  const router = useRouter()

  // Load saved layout on mount
  useEffect(() => {
    const loadDashboardData = async () => {
      setIsLoading(true)
      try {
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
                // Ensure all widgets have visible property (backward compatibility)
                const widgetsWithVisibility = parsed.map((w: Widget) => ({
                  ...w,
                  visible: w.visible !== undefined ? w.visible : true
                }))
                setWidgets(widgetsWithVisibility)
              }
            }
          } catch (e) {
            console.error('Failed to load dashboard layout:', e)
          }
        }

        // Simulate minimum loading time for smooth skeleton transition
        await new Promise(resolve => setTimeout(resolve, 300))
      } finally {
        setIsLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  // Load search history on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem(SEARCH_HISTORY_KEY)
    if (savedHistory) {
      try {
        const parsed = JSON.parse(savedHistory)
        if (Array.isArray(parsed)) {
          setSearchHistory(parsed)
        }
      } catch (e) {
        console.error('Failed to load search history:', e)
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

  const toggleWidgetVisibility = (widgetId: string) => {
    setWidgets(widgets.map(w =>
      w.id === widgetId ? { ...w, visible: !w.visible } : w
    ))
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

  // Debounce function for search
  const debounceRef = useRef<NodeJS.Timeout | null>(null)

  const fetchSuggestions = useCallback(async (query: string) => {
    if (query.length < 1) {
      setSuggestions([])
      setShowSuggestions(false)
      return
    }

    setIsLoadingSuggestions(true)
    const result = await searchApi.getSuggestions(query)
    setIsLoadingSuggestions(false)

    if (result.data) {
      setSuggestions(result.data.suggestions)
      setShowSuggestions(true)
      setSelectedSuggestionIndex(-1)
    }
  }, [])

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setSearchQuery(value)

    // Debounce API calls
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }
    debounceRef.current = setTimeout(() => {
      fetchSuggestions(value)
    }, 200)
  }

  const addToSearchHistory = (item: SearchSuggestion) => {
    const historyItem: SearchHistoryItem = {
      id: item.id,
      name: item.name,
      type: item.type,
      url: item.url,
      timestamp: Date.now()
    }

    // Remove duplicates and add new item at the beginning
    const newHistory = [
      historyItem,
      ...searchHistory.filter(h => h.url !== item.url)
    ].slice(0, MAX_SEARCH_HISTORY)

    setSearchHistory(newHistory)
    localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(newHistory))
  }

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    setShowSuggestions(false)
    setSearchQuery(suggestion.name)
    addToSearchHistory(suggestion)
    router.push(suggestion.url)
  }

  const handleHistoryClick = (item: SearchHistoryItem) => {
    setShowSuggestions(false)
    setSearchQuery(item.name)
    router.push(item.url)
  }

  const handleDirectSearch = (query: string) => {
    setShowSuggestions(false)

    // Detect input type and navigate to chat with appropriate parameter
    // URL detection: starts with http:// or https:// or www.
    const isUrl = /^(https?:\/\/|www\.)/i.test(query)

    // NIP detection: 10 digits, optionally with dashes
    const nipPattern = /^\d{3}-?\d{3}-?\d{2}-?\d{2}$|^\d{10}$/
    const isNIP = nipPattern.test(query.replace(/\s/g, ''))

    let chatUrl = '/chat'
    let searchType = 'query'

    if (isUrl) {
      // Navigate with URL parameter
      chatUrl = `/chat?url=${encodeURIComponent(query)}`
      searchType = 'url'
    } else if (isNIP) {
      // Navigate with company_id parameter (NIP)
      chatUrl = `/chat?company_id=${encodeURIComponent(query.replace(/\s|-/g, ''))}`
      searchType = 'company'
    } else {
      // Navigate with query parameter (company name or general query)
      chatUrl = `/chat?query=${encodeURIComponent(query)}`
      searchType = 'query'
    }

    // Add to search history before navigating
    const historyItem: SearchHistoryItem = {
      id: `direct-${Date.now()}`,
      name: query,
      type: searchType,
      url: chatUrl,
      timestamp: Date.now()
    }

    const newHistory = [
      historyItem,
      ...searchHistory.filter(h => h.url !== chatUrl)
    ].slice(0, MAX_SEARCH_HISTORY)

    setSearchHistory(newHistory)
    localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(newHistory))

    router.push(chatUrl)
  }

  const handleSearchKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Handle Enter key - navigate to chat with query
    if (e.key === 'Enter') {
      e.preventDefault()

      // If a suggestion is selected, use it
      if (showSuggestions && selectedSuggestionIndex >= 0 && selectedSuggestionIndex < suggestions.length) {
        handleSuggestionClick(suggestions[selectedSuggestionIndex])
        return
      }

      // If no suggestion selected but we have text, navigate to chat with query
      if (searchQuery.trim().length > 0) {
        handleDirectSearch(searchQuery.trim())
        return
      }
    }

    // Handle other navigation keys only when suggestions are visible
    if (!showSuggestions || suggestions.length === 0) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedSuggestionIndex(prev =>
          prev < suggestions.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedSuggestionIndex(prev => prev > 0 ? prev - 1 : -1)
        break
      case 'Escape':
        setShowSuggestions(false)
        setSelectedSuggestionIndex(-1)
        break
    }
  }

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        searchInputRef.current &&
        !searchInputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Get type icon for suggestion
  const getSuggestionIcon = (type: string) => {
    switch (type) {
      case 'company':
        return '🏢'
      case 'report':
        return '📄'
      case 'person':
        return '👤'
      case 'pkd':
        return '🏷️'
      default:
        return '🔍'
    }
  }

  // Widget rendering components
  const renderWidget = (widget: Widget, index: number) => {
    const isFirst = index === 0
    const isLast = index === widgets.length - 1

    const isHidden = !widget.visible
    const wrapperClasses = isCustomizeMode
      ? `relative border-2 border-dashed rounded-xl ${isHidden ? 'border-red-300 bg-red-50 opacity-60' : 'border-blue-300'}`
      : ''

    const CustomizeOverlay = () => (
      <div className="absolute -top-3 -right-3 flex gap-1 z-10">
        <button
          onClick={() => moveWidget(index, 'up')}
          disabled={isFirst}
          className="rounded-full bg-blue-600 p-1.5 text-white shadow-md transition-colors hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          title="Przesuń w górę"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
          </svg>
        </button>
        <button
          onClick={() => moveWidget(index, 'down')}
          disabled={isLast}
          className="rounded-full bg-blue-600 p-1.5 text-white shadow-md transition-colors hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          title="Przesuń w dół"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <button
          onClick={() => toggleWidgetVisibility(widget.id)}
          className={`rounded-full p-1.5 text-white shadow-md transition-colors ${isHidden ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}`}
          title={isHidden ? 'Pokaż widget' : 'Ukryj widget'}
        >
          {isHidden ? (
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          ) : (
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          )}
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

  // Get visible widgets only (unless in customize mode)
  const visibleWidgets = isCustomizeMode ? widgets : widgets.filter(w => w.visible)
  const hiddenWidgets = widgets.filter(w => !w.visible)

  // Get grid widgets (first 3) and full-width widgets (rest)
  const gridWidgets = visibleWidgets.filter(w => ['active-research', 'recent-activity', 'usage-stats'].includes(w.type))
  const fullWidgets = visibleWidgets.filter(w => ['projects', 'alerts'].includes(w.type))

  // Show skeleton while loading
  if (isLoading) {
    return <DashboardSkeleton />
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar className="h-full" />

      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200">
          <div className="px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
              <div className="flex items-center space-x-4">
                <button
                  onClick={handleLogout}
                  disabled={isLoggingOut}
                  className="rounded-md bg-red-600 px-3 py-1.5 text-sm text-white transition-colors hover:bg-red-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                >
                  {isLoggingOut ? 'Logging out...' : 'Logout'}
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Scrollable main content */}
        <main id="main-content" className="flex-1 overflow-y-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Customize Mode Banner */}
        {isCustomizeMode && (
          <div className="mb-4 rounded-lg bg-blue-50 border border-blue-200 p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
                <span className="font-medium text-blue-800">Tryb dostosowywania</span>
                <span className="text-sm text-blue-600">- Użyj strzałek aby zmienić kolejność, czerwonej ikony aby ukryć widget</span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={resetLayout}
                  className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  Resetuj
                </button>
                <button
                  onClick={cancelCustomize}
                  className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  Anuluj
                </button>
                <button
                  onClick={saveLayout}
                  disabled={isSaving}
                  className="rounded-md bg-blue-600 px-3 py-1.5 text-sm text-white transition-colors hover:bg-blue-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  {isSaving ? 'Zapisywanie...' : 'Zapisz układ'}
                </button>
              </div>
            </div>
            {/* Hidden widgets section */}
            {hiddenWidgets.length > 0 && (
              <div className="mt-3 pt-3 border-t border-blue-200">
                <div className="text-sm text-blue-700 mb-2">
                  Ukryte widgety ({hiddenWidgets.length}):
                </div>
                <div className="flex flex-wrap gap-2">
                  {hiddenWidgets.map(w => (
                    <button
                      key={w.id}
                      onClick={() => toggleWidgetVisibility(w.id)}
                      className="flex items-center gap-1 rounded-md bg-white border border-blue-300 px-2 py-1 text-sm text-blue-700 transition-colors hover:bg-blue-100 max-w-[200px] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                      title={w.title}
                    >
                      <svg className="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      <span className="truncate">{w.title}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
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
              className="flex items-center gap-2 rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
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
              ref={searchInputRef}
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              onKeyDown={handleSearchKeyDown}
              onFocus={() => {
                // Show suggestions if we have suggestions, or show history if query is empty and we have history
                if ((searchQuery.length > 0 && suggestions.length > 0) || (searchQuery.length === 0 && searchHistory.length > 0)) {
                  setShowSuggestions(true)
                }
              }}
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
            {/* Loading indicator */}
            {isLoadingSuggestions && (
              <div className="absolute right-4 top-1/2 -translate-y-1/2">
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600"></div>
              </div>
            )}
            {/* Search history dropdown (when query is empty) */}
            {showSuggestions && searchQuery.length === 0 && searchHistory.length > 0 && (
              <div
                ref={suggestionsRef}
                className="absolute left-0 right-0 top-full z-50 mt-2 max-h-80 overflow-y-auto rounded-lg bg-white shadow-xl"
              >
                <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase border-b border-gray-100">
                  Ostatnie wyszukiwania
                </div>
                {searchHistory.map((item, index) => (
                  <button
                    key={`history-${item.url}-${item.timestamp}`}
                    onClick={() => handleHistoryClick(item)}
                    className={`flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-gray-50 ${
                      index === selectedSuggestionIndex ? 'bg-blue-50' : ''
                    } ${index !== searchHistory.length - 1 ? 'border-b border-gray-100' : ''}`}
                  >
                    <span className="text-xl">🕐</span>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-900 truncate">{item.name}</div>
                    </div>
                    <span className="text-xs text-gray-400 uppercase">{item.type}</span>
                  </button>
                ))}
              </div>
            )}
            {/* Suggestions dropdown */}
            {showSuggestions && suggestions.length > 0 && searchQuery.length > 0 && (
              <div
                ref={suggestionsRef}
                className="absolute left-0 right-0 top-full z-50 mt-2 max-h-80 overflow-y-auto rounded-lg bg-white shadow-xl"
              >
                {suggestions.map((suggestion, index) => (
                  <button
                    key={`${suggestion.type}-${suggestion.id}`}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className={`flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-gray-50 ${
                      index === selectedSuggestionIndex ? 'bg-blue-50' : ''
                    } ${index !== suggestions.length - 1 ? 'border-b border-gray-100' : ''}`}
                  >
                    <span className="text-xl">{getSuggestionIcon(suggestion.type)}</span>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-900 truncate">{suggestion.name}</div>
                      {suggestion.subtitle && (
                        <div className="text-sm text-gray-500 truncate">{suggestion.subtitle}</div>
                      )}
                    </div>
                    <span className="text-xs text-gray-400 uppercase">{suggestion.type}</span>
                  </button>
                ))}
              </div>
            )}
            {/* No results message */}
            {showSuggestions && suggestions.length === 0 && searchQuery.length > 0 && !isLoadingSuggestions && (
              <div
                ref={suggestionsRef}
                className="absolute left-0 right-0 top-full z-50 mt-2 rounded-lg bg-white p-4 shadow-xl"
              >
                <div className="text-center text-gray-500">
                  Brak wyników dla &quot;{searchQuery}&quot;
                </div>
              </div>
            )}
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="text-sm text-white">Ostatnie:</span>
            {searchHistory.slice(0, 3).map((item) => (
              <button
                key={`recent-${item.id}`}
                onClick={() => handleHistoryClick(item)}
                className="rounded bg-white/20 px-2 py-1 text-sm transition-colors hover:bg-white/30 max-w-[200px] truncate"
                title={item.name}
              >
                {item.name}
              </button>
            ))}
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
    </div>
  )
}

// Individual Widget Components
function ActiveResearchWidget() {
  const [activeResearch, setActiveResearch] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchActiveResearch = async () => {
      if (typeof window === 'undefined') return

      const token = localStorage.getItem('mi_navigator_token')
      if (!token) {
        setIsLoading(false)
        return
      }

      try {
        const response = await fetch(`${API_BASE_URL}/research/active`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (response.ok) {
          const data = await response.json()
          setActiveResearch(data.items || [])
        }
      } catch (error) {
        console.error('Failed to fetch active research:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchActiveResearch()
  }, [])

  return (
    <div className="rounded-xl bg-white p-6 shadow-sm h-full">
      <h3 className="mb-4 font-semibold text-gray-900">Active Research</h3>
      {isLoading ? (
        <div className="text-center py-4 text-gray-500">Loading...</div>
      ) : activeResearch.length > 0 ? (
        <div className="space-y-3">
          {activeResearch.slice(0, 2).map((research) => (
            <div key={research.id} className="rounded-lg bg-gray-50 p-4">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />
                <span className="text-sm font-medium">{research.name}</span>
              </div>
              <div className="mt-2">
                <div className="text-sm text-gray-500">Progress: {research.progress}%</div>
                <div className="mt-1 h-2 rounded-full bg-gray-200">
                  <div
                    className="h-full rounded-full bg-blue-500"
                    style={{ width: `${research.progress}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-4">
          <p className="text-sm text-gray-500 mb-4">No active research. Start a new analysis!</p>
        </div>
      )}
      <div className="mt-4 flex flex-wrap gap-2">
        <Link
          href="/chat"
          className="inline-block rounded-md bg-blue-600 px-4 py-2 text-sm text-white transition-colors hover:bg-blue-700"
        >
          Start New Research
        </Link>
        <Link
          href="/analysis"
          className="inline-block rounded-md border border-blue-600 px-4 py-2 text-sm text-blue-600 transition-colors hover:bg-blue-50"
        >
          Market Analysis
        </Link>
        <Link
          href="/search"
          className="inline-block rounded-md border border-indigo-600 px-4 py-2 text-sm text-indigo-600 transition-colors hover:bg-indigo-50"
        >
          PKD Search
        </Link>
      </div>
    </div>
  )
}

function RecentActivityWidget() {
  const [activities, setActivities] = useState<{ id: string; title: string; timestamp: string }[]>([])
  const [userTimezone, setUserTimezone] = useState('Europe/Warsaw')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchRecentActivities = async () => {
      try {
        const token = getStoredToken()
        if (!token) return

        // Fetch user profile to get timezone
        const profileResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/users/me`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (profileResponse.ok) {
          const profile = await profileResponse.json()
          if (profile.timezone) {
            setUserTimezone(profile.timezone)
          }
        }

        // Fetch recent activities (limit 3)
        const activitiesResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/activity?limit=3`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (activitiesResponse.ok) {
          const data = await activitiesResponse.json()
          setActivities(data.items || [])
        }
      } catch (error) {
        console.error('Failed to fetch activities:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchRecentActivities()
  }, [])

  const formatTimeOnly = (timestamp: string, timezone: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('pl-PL', {
      hour: '2-digit',
      minute: '2-digit',
      timeZone: timezone
    })
  }

  return (
    <div className="rounded-xl bg-white p-6 shadow-sm h-full">
      <h3 className="mb-4 font-semibold text-gray-900">Recent Activity</h3>
      {isLoading ? (
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded animate-pulse" />
          <div className="h-4 bg-gray-200 rounded animate-pulse" />
          <div className="h-4 bg-gray-200 rounded animate-pulse" />
        </div>
      ) : activities.length > 0 ? (
        <ul className="space-y-3">
          {activities.map((activity) => (
            <li key={activity.id} className="text-sm">
              <span className="text-gray-500">{formatTimeOnly(activity.timestamp, userTimezone)}</span> - <span className="truncate inline-block max-w-[300px] align-bottom" title={activity.title}>{activity.title}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-gray-500">Brak ostatniej aktywności</p>
      )}
      <Link href="/activity" className="mt-4 inline-block text-sm text-blue-600 hover:underline">
        Zobacz wszystkie →
      </Link>
    </div>
  )
}

function UsageStatsWidget() {
  const [usageStats, setUsageStats] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchUsageStats = async () => {
      if (typeof window === 'undefined') return

      const token = localStorage.getItem('mi_navigator_token')
      if (!token) {
        setIsLoading(false)
        return
      }

      try {
        const response = await fetch(`${API_BASE_URL}/users/usage?period=month`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (response.ok) {
          const data = await response.json()
          setUsageStats(data)
        }
      } catch (error) {
        console.error('Failed to fetch usage stats:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchUsageStats()
  }, [])

  if (isLoading) {
    return (
      <div className="rounded-xl bg-white p-6 shadow-sm h-full">
        <h3 className="mb-4 font-semibold text-gray-900">Usage Stats</h3>
        <div className="text-center py-4 text-gray-500">Loading...</div>
      </div>
    )
  }

  if (!usageStats) {
    return (
      <div className="rounded-xl bg-white p-6 shadow-sm h-full">
        <h3 className="mb-4 font-semibold text-gray-900">Usage Stats</h3>
        <div className="text-center py-4 text-gray-500">Unable to load stats</div>
      </div>
    )
  }

  return (
    <div className="rounded-xl bg-white p-6 shadow-sm h-full">
      <h3 className="mb-4 font-semibold text-gray-900">Usage Stats</h3>
      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Analyses this month</span>
            <span className="font-medium">{usageStats.analyses_count}/{usageStats.analyses_limit}</span>
          </div>
          <div className="mt-1 h-2 rounded-full bg-gray-200">
            <div
              className="h-full rounded-full bg-blue-500"
              style={{ width: `${Math.min(usageStats.analyses_percentage, 100)}%` }}
            />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Storage</span>
            <span className="font-medium">{usageStats.storage_used_gb} GB / {usageStats.storage_limit_gb} GB</span>
          </div>
          <div className="mt-1 h-2 rounded-full bg-gray-200">
            <div
              className="h-full rounded-full bg-green-500"
              style={{ width: `${Math.min(usageStats.storage_percentage, 100)}%` }}
            />
          </div>
        </div>
        <div className="text-sm text-gray-600">
          API calls: <span className="font-medium">{usageStats.api_calls_count.toLocaleString()}</span>
        </div>
      </div>
    </div>
  )
}

function ProjectsWidget() {
  const [projects, setProjects] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchProjects = async () => {
      if (typeof window === 'undefined') return

      const token = localStorage.getItem('mi_navigator_token')
      if (!token) {
        setIsLoading(false)
        return
      }

      try {
        const response = await fetch(`${API_BASE_URL}/projects/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (response.ok) {
          const data = await response.json()
          setProjects(data.items || [])
        }
      } catch (error) {
        console.error('Failed to fetch projects:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchProjects()
  }, [])

  const formatDate = (dateString: string) => {
    return formatRelativeTime(dateString, 'pl-PL')
  }

  return (
    <section>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">My Projects</h2>
        <Link
          href="/projects/new"
          className="rounded-md bg-blue-600 px-3 py-1.5 text-sm text-white transition-colors hover:bg-blue-700"
        >
          + New
        </Link>
      </div>
      {isLoading ? (
        <div className="text-center py-8 text-gray-500">Loading projects...</div>
      ) : projects.length === 0 ? (
        <div className="text-center py-8 text-gray-500">No projects yet</div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.slice(0, 3).map((project) => (
            <Link
              key={project.id}
              href={`/projects/${project.id}`}
              className="block rounded-xl bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="flex items-start gap-3">
                <span className="text-2xl">📁</span>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-gray-900 truncate" title={project.name}>{project.name}</h3>
                  <div className="mt-2 flex gap-4 text-sm text-gray-500">
                    <span>📄 {project.report_ids?.length || 0} reports</span>
                    <span>🔔 {project.alert_count || 0} alerts</span>
                  </div>
                  <div className="mt-2 text-xs text-gray-400">
                    Updated: {formatDate(project.updated_at)}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </section>
  )
}

function AlertsWidget() {
  const [alerts, setAlerts] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        setIsLoading(true)
        const token = localStorage.getItem('mi_navigator_token')
        if (!token) {
          setIsLoading(false)
          return
        }

        const response = await fetch(`${API_BASE_URL}/alerts/?limit=3`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          setAlerts(data.items || [])
        }
      } catch (error) {
        console.error('Failed to fetch alerts:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchAlerts()
  }, [])

  // Get severity styling
  const getSeverityStyles = (severity: string) => {
    switch (severity) {
      case 'high':
        return {
          indicator: '🔴',
          bg: 'bg-red-50',
          border: 'border-red-200',
          titleColor: 'text-red-900',
          descColor: 'text-red-800'
        }
      case 'medium':
        return {
          indicator: '🟡',
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          titleColor: 'text-yellow-900',
          descColor: 'text-yellow-800'
        }
      case 'low':
        return {
          indicator: '🟢',
          bg: 'bg-green-50',
          border: 'border-green-200',
          titleColor: 'text-green-900',
          descColor: 'text-green-800'
        }
      default:
        return {
          indicator: '⚪',
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          titleColor: 'text-gray-800',
          descColor: 'text-gray-600'
        }
    }
  }

  return (
    <section>
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Alerts & Monitoring</h2>
      {isLoading ? (
        <div className="py-4 text-center text-sm text-gray-500">Loading alerts...</div>
      ) : alerts.length === 0 ? (
        <div className="py-4 text-center text-sm text-gray-500">No alerts</div>
      ) : (
        <div className="space-y-2">
          {alerts.map((alert) => {
            const styles = getSeverityStyles(alert.severity)
            return (
              <Link
                key={alert.id}
                href={`/alerts/${alert.id}`}
                className={`flex items-start gap-2 rounded-lg border ${styles.border} ${styles.bg} p-3 cursor-pointer hover:opacity-80 transition-opacity`}
              >
                <span>{styles.indicator}</span>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium truncate ${styles.titleColor}`} title={alert.title}>{alert.title}</p>
                  <p className={`text-xs line-clamp-2 ${styles.descColor}`} title={alert.description}>{alert.description}</p>
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </section>
  )
}
