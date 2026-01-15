'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface ReportSection {
  id: string
  title: string
  content: string
}

interface ReportSource {
  name: string
  confidence: number
  url: string
}

interface ReportDetail {
  id: string
  title: string
  type: string
  company: string | null
  created_at: string
  updated_at: string
  status: string
  summary: string
  sections: ReportSection[]
  sources: ReportSource[]
}

interface SearchMatch {
  sectionId: string
  sectionTitle: string
  startIndex: number
  endIndex: number
  context: string
}

export default function ReportViewerPage() {
  const router = useRouter()
  const params = useParams()
  const reportId = params.id as string

  const [report, setReport] = useState<ReportDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  // Search state
  const [searchQuery, setSearchQuery] = useState('')
  const [searchMatches, setSearchMatches] = useState<SearchMatch[]>([])
  const [currentMatchIndex, setCurrentMatchIndex] = useState(0)
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const searchInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetchReport()
  }, [reportId])

  // Keyboard shortcut for search (Ctrl+F)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault()
        setIsSearchOpen(true)
        setTimeout(() => searchInputRef.current?.focus(), 100)
      }
      if (e.key === 'Escape') {
        setIsSearchOpen(false)
        setSearchQuery('')
        setSearchMatches([])
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const fetchReport = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error('Failed to fetch report')
      }

      const data = await response.json()
      setReport(data)
    } catch (err) {
      setError('Nie udało się załadować raportu')
    } finally {
      setIsLoading(false)
    }
  }

  // Search functionality
  const performSearch = useCallback((query: string) => {
    if (!report || !query.trim()) {
      setSearchMatches([])
      setCurrentMatchIndex(0)
      return
    }

    const matches: SearchMatch[] = []
    const queryLower = query.toLowerCase()

    report.sections.forEach((section) => {
      const contentLower = section.content.toLowerCase()
      let startIndex = 0

      while (true) {
        const index = contentLower.indexOf(queryLower, startIndex)
        if (index === -1) break

        // Get context around the match (50 chars before and after)
        const contextStart = Math.max(0, index - 50)
        const contextEnd = Math.min(section.content.length, index + query.length + 50)
        let context = section.content.substring(contextStart, contextEnd)

        if (contextStart > 0) context = '...' + context
        if (contextEnd < section.content.length) context = context + '...'

        matches.push({
          sectionId: section.id,
          sectionTitle: section.title,
          startIndex: index,
          endIndex: index + query.length,
          context
        })

        startIndex = index + 1
      }
    })

    setSearchMatches(matches)
    setCurrentMatchIndex(0)

    // Scroll to first match
    if (matches.length > 0) {
      scrollToMatch(0, matches)
    }
  }, [report])

  const scrollToMatch = (index: number, matches: SearchMatch[] = searchMatches) => {
    if (matches.length === 0) return

    const match = matches[index]
    const sectionElement = document.getElementById(`section-${match.sectionId}`)
    if (sectionElement) {
      sectionElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value
    setSearchQuery(query)
    performSearch(query)
  }

  const goToNextMatch = () => {
    if (searchMatches.length === 0) return
    const nextIndex = (currentMatchIndex + 1) % searchMatches.length
    setCurrentMatchIndex(nextIndex)
    scrollToMatch(nextIndex)
  }

  const goToPrevMatch = () => {
    if (searchMatches.length === 0) return
    const prevIndex = currentMatchIndex === 0 ? searchMatches.length - 1 : currentMatchIndex - 1
    setCurrentMatchIndex(prevIndex)
    scrollToMatch(prevIndex)
  }

  // Highlight matching text in content (per paragraph)
  const highlightText = (content: string, sectionId: string) => {
    if (!searchQuery.trim()) return content

    const parts: (string | JSX.Element)[] = []
    const queryLower = searchQuery.toLowerCase()
    const contentLower = content.toLowerCase()
    let lastIndex = 0
    let matchIndex = 0

    // Find matches within this specific paragraph
    while (true) {
      const index = contentLower.indexOf(queryLower, lastIndex)
      if (index === -1) break

      // Add text before match
      if (index > lastIndex) {
        parts.push(content.substring(lastIndex, index))
      }

      // Find if this is the current global match
      const sectionMatches = searchMatches.filter(m => m.sectionId === sectionId)
      const globalMatchIndex = searchMatches.findIndex(
        m => m.sectionId === sectionId &&
        content.toLowerCase().indexOf(searchQuery.toLowerCase()) === index
      )

      // Determine if this is highlighted as current
      const isCurrentMatch = sectionMatches.some((m, idx) => {
        const matchInSection = searchMatches.indexOf(m)
        return matchInSection === currentMatchIndex &&
               content.substring(index, index + searchQuery.length).toLowerCase() === queryLower
      })

      // Add highlighted match
      parts.push(
        <mark
          key={`${sectionId}-${index}-${matchIndex}`}
          className={`${isCurrentMatch ? 'bg-orange-400' : 'bg-yellow-200'} px-0.5 rounded`}
        >
          {content.substring(index, index + searchQuery.length)}
        </mark>
      )

      lastIndex = index + searchQuery.length
      matchIndex++
    }

    // Add remaining text
    if (lastIndex < content.length) {
      parts.push(content.substring(lastIndex))
    }

    return parts.length > 0 ? parts : content
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pl-PL', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
          <p className="mt-3 text-gray-600">Ładowanie raportu...</p>
        </div>
      </div>
    )
  }

  if (error || !report) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-red-600">{error || 'Nie znaleziono raportu'}</p>
          <Link href="/reports" className="mt-4 inline-block text-blue-600 hover:underline">
            Wróć do listy raportów
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-white px-4 py-3">
        <div className="mx-auto flex max-w-4xl items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/reports" className="text-gray-600 hover:text-gray-900">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </Link>
            <h1 className="text-lg font-semibold text-gray-900 truncate max-w-md">{report.title}</h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setIsSearchOpen(!isSearchOpen)
                if (!isSearchOpen) {
                  setTimeout(() => searchInputRef.current?.focus(), 100)
                }
              }}
              className="rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-50"
              title="Szukaj w raporcie (Ctrl+F)"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
            <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">
              Eksportuj
            </button>
          </div>
        </div>
      </header>

      {/* Search Bar */}
      {isSearchOpen && (
        <div className="sticky top-[57px] z-40 border-b bg-white px-4 py-3 shadow-sm">
          <div className="mx-auto flex max-w-4xl items-center gap-3">
            <div className="relative flex-1">
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={handleSearchChange}
                placeholder="Szukaj w raporcie..."
                className="w-full rounded-lg border border-gray-300 px-4 py-2 pr-20 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                autoFocus
              />
              {searchMatches.length > 0 && (
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-gray-500">
                  {currentMatchIndex + 1} / {searchMatches.length}
                </span>
              )}
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={goToPrevMatch}
                disabled={searchMatches.length === 0}
                className="rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-50 disabled:opacity-50"
                title="Poprzedni wynik"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                </svg>
              </button>
              <button
                onClick={goToNextMatch}
                disabled={searchMatches.length === 0}
                className="rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-50 disabled:opacity-50"
                title="Następny wynik"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            <button
              onClick={() => {
                setIsSearchOpen(false)
                setSearchQuery('')
                setSearchMatches([])
              }}
              className="rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-50"
              title="Zamknij (Esc)"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      <main className="mx-auto max-w-4xl px-4 py-8">
        {/* Report Header */}
        <div className="mb-8 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 p-8 text-white">
          <div className="mb-4 flex items-center gap-3">
            <span className="rounded-full bg-white/20 px-3 py-1 text-sm">
              {report.type === 'company_profile' ? 'Profil firmy' :
               report.type === 'market_analysis' ? 'Analiza rynku' :
               report.type === 'due_diligence' ? 'Due Diligence' : report.type}
            </span>
            {report.company && (
              <span className="text-blue-100">• {report.company}</span>
            )}
          </div>
          <h1 className="text-2xl font-bold">{report.title}</h1>
          <p className="mt-3 text-blue-100">{report.summary}</p>
          <div className="mt-4 flex gap-4 text-sm text-blue-200">
            <span>Utworzono: {formatDate(report.created_at)}</span>
            <span>Aktualizacja: {formatDate(report.updated_at)}</span>
          </div>
        </div>

        {/* Table of Contents */}
        <div className="mb-8 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-4 font-semibold text-gray-900">Spis treści</h2>
          <nav className="space-y-2">
            {report.sections.map((section, index) => (
              <a
                key={section.id}
                href={`#section-${section.id}`}
                className="block text-gray-600 hover:text-blue-600"
              >
                {index + 1}. {section.title}
              </a>
            ))}
          </nav>
        </div>

        {/* Report Sections */}
        <div className="space-y-8">
          {report.sections.map((section, index) => (
            <section
              key={section.id}
              id={`section-${section.id}`}
              className="rounded-xl bg-white p-6 shadow-sm"
            >
              <h2 className="mb-4 text-xl font-semibold text-gray-900">
                {index + 1}. {section.title}
              </h2>
              <div className="prose prose-gray max-w-none">
                {section.content.split('\n').map((paragraph, pIdx) => (
                  <p key={pIdx} className="mb-4 text-gray-700 whitespace-pre-wrap">
                    {highlightText(paragraph, section.id)}
                  </p>
                ))}
              </div>
            </section>
          ))}
        </div>

        {/* Sources */}
        <div className="mt-8 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-4 font-semibold text-gray-900">Źródła</h2>
          <div className="space-y-3">
            {report.sources.map((source, idx) => (
              <div key={idx} className="flex items-center justify-between rounded-lg border border-gray-200 p-3">
                <div className="flex items-center gap-3">
                  <span className="text-gray-600">{source.name}</span>
                  <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline">
                    {source.url}
                  </a>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-500">Pewność:</span>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    source.confidence >= 0.9 ? 'bg-green-100 text-green-800' :
                    source.confidence >= 0.75 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-orange-100 text-orange-800'
                  }`}>
                    {Math.round(source.confidence * 100)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
