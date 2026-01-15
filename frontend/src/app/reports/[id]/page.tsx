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

interface Annotation {
  id: string
  report_id: string
  section_id: string
  selected_text: string
  start_offset: number
  end_offset: number
  comment: string
  created_at: string
  user_id: string
}

interface ReportVersion {
  version: number
  created_at: string
  author: string
  changes: string
  is_current: boolean
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

  // Annotation state
  const [annotations, setAnnotations] = useState<Annotation[]>([])
  const [selectedText, setSelectedText] = useState('')
  const [selectionInfo, setSelectionInfo] = useState<{
    sectionId: string
    startOffset: number
    endOffset: number
    rect: DOMRect | null
  } | null>(null)
  const [annotationComment, setAnnotationComment] = useState('')
  const [showAnnotationModal, setShowAnnotationModal] = useState(false)
  const [isSavingAnnotation, setIsSavingAnnotation] = useState(false)

  // Version history state
  const [versions, setVersions] = useState<ReportVersion[]>([])
  const [showVersionHistory, setShowVersionHistory] = useState(false)
  const [currentVersion, setCurrentVersion] = useState<number | null>(null)
  const [isLoadingVersion, setIsLoadingVersion] = useState(false)

  // Restore version state
  const [showRestoreConfirm, setShowRestoreConfirm] = useState(false)
  const [versionToRestore, setVersionToRestore] = useState<number | null>(null)
  const [isRestoring, setIsRestoring] = useState(false)
  const [restoreMessage, setRestoreMessage] = useState('')

  useEffect(() => {
    fetchReport()
    fetchAnnotations()
    fetchVersions()
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
        setShowAnnotationModal(false)
        setShowRestoreConfirm(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Text selection handler
  useEffect(() => {
    const handleSelectionChange = () => {
      const selection = window.getSelection()
      if (!selection || selection.isCollapsed || !selection.toString().trim()) {
        return
      }

      const text = selection.toString().trim()
      if (text.length < 3) return // Minimum 3 characters

      // Find which section the selection is in
      const anchorNode = selection.anchorNode
      if (!anchorNode) return

      let element: HTMLElement | null = anchorNode.nodeType === Node.TEXT_NODE
        ? anchorNode.parentElement
        : anchorNode as HTMLElement

      while (element && !element.id?.startsWith('section-')) {
        element = element.parentElement
      }

      if (element && element.id) {
        const sectionId = element.id.replace('section-', '')
        const range = selection.getRangeAt(0)
        const rect = range.getBoundingClientRect()

        setSelectedText(text)
        setSelectionInfo({
          sectionId,
          startOffset: range.startOffset,
          endOffset: range.endOffset,
          rect
        })
      }
    }

    document.addEventListener('selectionchange', handleSelectionChange)
    return () => document.removeEventListener('selectionchange', handleSelectionChange)
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
      setError('Nie udalo sie zaladowac raportu')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchAnnotations = async () => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/annotations`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setAnnotations(data.annotations || [])
      }
    } catch (err) {
      console.error('Failed to fetch annotations:', err)
    }
  }

  const fetchVersions = async () => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/versions`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setVersions(data.versions || [])
        // Set current version
        const current = data.versions?.find((v: ReportVersion) => v.is_current)
        if (current) {
          setCurrentVersion(current.version)
        }
      }
    } catch (err) {
      console.error('Failed to fetch versions:', err)
    }
  }

  const loadVersion = async (version: number) => {
    const token = getStoredToken()
    if (!token) return

    setIsLoadingVersion(true)

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/versions/${version}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setReport(data)
        setCurrentVersion(version)
        setShowVersionHistory(false)
      }
    } catch (err) {
      console.error('Failed to load version:', err)
    } finally {
      setIsLoadingVersion(false)
    }
  }

  const restoreVersion = async () => {
    if (!versionToRestore) return

    const token = getStoredToken()
    if (!token) return

    setIsRestoring(true)
    setRestoreMessage('')

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/versions/restore`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ version: versionToRestore }),
        }
      )

      if (response.ok) {
        const data = await response.json()
        setRestoreMessage(`Przywrócono wersję ${versionToRestore}. Utworzono nową wersję ${data.new_version}.`)
        setShowRestoreConfirm(false)
        // Refresh versions and report
        await fetchVersions()
        await loadVersion(data.new_version)
      } else {
        setRestoreMessage('Nie udało się przywrócić wersji')
      }
    } catch (err) {
      console.error('Failed to restore version:', err)
      setRestoreMessage('Błąd podczas przywracania wersji')
    } finally {
      setIsRestoring(false)
    }
  }

  const handleRestoreClick = (version: number, e: React.MouseEvent) => {
    e.stopPropagation()
    setVersionToRestore(version)
    setShowRestoreConfirm(true)
  }

  const saveAnnotation = async () => {
    if (!selectedText || !selectionInfo || !annotationComment.trim()) return

    const token = getStoredToken()
    if (!token) return

    setIsSavingAnnotation(true)

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/annotations`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            section_id: selectionInfo.sectionId,
            selected_text: selectedText,
            start_offset: selectionInfo.startOffset,
            end_offset: selectionInfo.endOffset,
            comment: annotationComment,
          }),
        }
      )

      if (response.ok) {
        const newAnnotation = await response.json()
        setAnnotations(prev => [...prev, newAnnotation])
        setShowAnnotationModal(false)
        setAnnotationComment('')
        setSelectedText('')
        setSelectionInfo(null)
        // Clear selection
        window.getSelection()?.removeAllRanges()
      }
    } catch (err) {
      console.error('Failed to save annotation:', err)
    } finally {
      setIsSavingAnnotation(false)
    }
  }

  const deleteAnnotation = async (annotationId: string) => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/annotations/${annotationId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        setAnnotations(prev => prev.filter(a => a.id !== annotationId))
      }
    } catch (err) {
      console.error('Failed to delete annotation:', err)
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

  // Get annotations for a specific section
  const getSectionAnnotations = (sectionId: string) => {
    return annotations.filter(a => a.section_id === sectionId)
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
          <p className="mt-3 text-gray-600">Ladowanie raportu...</p>
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
            Wroc do listy raportow
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
              onClick={() => setShowVersionHistory(!showVersionHistory)}
              className="rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-50"
              title="Historia wersji"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
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

      {/* Version History Panel */}
      {showVersionHistory && (
        <div className="fixed inset-0 z-50 flex items-start justify-end bg-black/30">
          <div className="h-full w-full max-w-md bg-white shadow-xl overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-4 py-3 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Historia wersji</h2>
              <button
                onClick={() => setShowVersionHistory(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-4 space-y-3">
              {versions.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Brak historii wersji</p>
              ) : (
                versions.map((version) => (
                  <div
                    key={version.version}
                    className={`rounded-lg border p-4 cursor-pointer transition-colors ${
                      currentVersion === version.version
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                    }`}
                    onClick={() => loadVersion(version.version)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">
                        Wersja {version.version}
                        {version.is_current && (
                          <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full">
                            Aktualna
                          </span>
                        )}
                      </span>
                      <div className="flex items-center gap-2">
                        {!version.is_current && (
                          <button
                            onClick={(e) => handleRestoreClick(version.version, e)}
                            className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded hover:bg-amber-200 transition-colors"
                            title="Przywróć tę wersję"
                          >
                            Przywróć
                          </button>
                        )}
                        {isLoadingVersion && currentVersion === version.version && (
                          <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"></div>
                        )}
                      </div>
                    </div>
                    <div className="text-sm text-gray-600 mb-1">{version.changes}</div>
                    <div className="text-xs text-gray-500">
                      {version.author} &bull; {new Date(version.created_at).toLocaleDateString('pl-PL', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Restore Confirmation Modal */}
      {showRestoreConfirm && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Przywróć wersję</h3>
            <p className="text-gray-600 mb-4">
              Czy na pewno chcesz przywrócić raport do wersji {versionToRestore}?
            </p>
            <p className="text-sm text-gray-500 mb-6">
              Zostanie utworzona nowa wersja z zawartością wybranej wersji historycznej.
              Obecna wersja nie zostanie utracona.
            </p>
            {restoreMessage && (
              <div className={`mb-4 p-3 rounded-lg text-sm ${
                restoreMessage.includes('Błąd') || restoreMessage.includes('Nie udało')
                  ? 'bg-red-50 text-red-700'
                  : 'bg-green-50 text-green-700'
              }`}>
                {restoreMessage}
              </div>
            )}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowRestoreConfirm(false)
                  setVersionToRestore(null)
                  setRestoreMessage('')
                }}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                disabled={isRestoring}
              >
                Anuluj
              </button>
              <button
                onClick={restoreVersion}
                disabled={isRestoring}
                className="rounded-lg bg-amber-600 px-4 py-2 text-sm text-white hover:bg-amber-700 disabled:opacity-50"
              >
                {isRestoring ? 'Przywracanie...' : 'Przywróć'}
              </button>
            </div>
          </div>
        </div>
      )}

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
                title="Nastepny wynik"
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

      {/* Annotation Tooltip - shows when text is selected */}
      {selectedText && selectionInfo && selectionInfo.rect && !showAnnotationModal && (
        <div
          className="fixed z-50 bg-gray-900 text-white rounded-lg shadow-lg px-3 py-2 text-sm"
          style={{
            top: selectionInfo.rect.bottom + window.scrollY + 8,
            left: selectionInfo.rect.left + selectionInfo.rect.width / 2,
            transform: 'translateX(-50%)'
          }}
        >
          <button
            onClick={() => setShowAnnotationModal(true)}
            className="flex items-center gap-2 hover:text-blue-300"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
            Dodaj adnotacje
          </button>
        </div>
      )}

      {/* Annotation Modal */}
      {showAnnotationModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Dodaj adnotacje</h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Zaznaczony tekst:
              </label>
              <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-3 text-sm text-gray-700">
                &quot;{selectedText.substring(0, 100)}{selectedText.length > 100 ? '...' : ''}&quot;
              </div>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Komentarz:
              </label>
              <textarea
                value={annotationComment}
                onChange={(e) => setAnnotationComment(e.target.value)}
                placeholder="Wpisz swoj komentarz..."
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                rows={3}
                autoFocus
              />
            </div>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowAnnotationModal(false)
                  setAnnotationComment('')
                }}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
              >
                Anuluj
              </button>
              <button
                onClick={saveAnnotation}
                disabled={!annotationComment.trim() || isSavingAnnotation}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {isSavingAnnotation ? 'Zapisywanie...' : 'Zapisz'}
              </button>
            </div>
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
              <span className="text-blue-100">&#x2022; {report.company}</span>
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
          <h2 className="mb-4 font-semibold text-gray-900">Spis tresci</h2>
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

        {/* Annotations Summary */}
        {annotations.length > 0 && (
          <div className="mb-8 rounded-xl bg-yellow-50 border border-yellow-200 p-6">
            <h2 className="mb-4 font-semibold text-gray-900 flex items-center gap-2">
              <svg className="h-5 w-5 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
              Adnotacje ({annotations.length})
            </h2>
            <div className="space-y-3">
              {annotations.map((annotation) => (
                <div key={annotation.id} className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="text-sm text-gray-500 mb-1">
                        Zaznaczony tekst:
                      </div>
                      <div className="text-sm text-gray-700 italic mb-2">
                        &quot;{annotation.selected_text.substring(0, 80)}{annotation.selected_text.length > 80 ? '...' : ''}&quot;
                      </div>
                      <div className="text-gray-800">{annotation.comment}</div>
                    </div>
                    <button
                      onClick={() => deleteAnnotation(annotation.id)}
                      className="ml-2 text-gray-400 hover:text-red-500"
                      title="Usun adnotacje"
                    >
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

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
              {/* Section Annotations */}
              {getSectionAnnotations(section.id).length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="text-sm font-medium text-yellow-700 mb-2">
                    Adnotacje w tej sekcji:
                  </div>
                  {getSectionAnnotations(section.id).map((annotation) => (
                    <div key={annotation.id} className="bg-yellow-50 rounded-lg p-3 mb-2 text-sm">
                      <div className="text-gray-500 italic mb-1">
                        &quot;{annotation.selected_text.substring(0, 50)}...&quot;
                      </div>
                      <div className="text-gray-700">{annotation.comment}</div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          ))}
        </div>

        {/* Sources */}
        <div className="mt-8 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-4 font-semibold text-gray-900">Zrodla</h2>
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
                  <span className="text-sm text-gray-500">Pewnosc:</span>
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

        {/* Annotation Instructions */}
        <div className="mt-8 rounded-xl bg-blue-50 border border-blue-200 p-4 text-sm text-blue-700">
          <div className="font-medium mb-1">Jak dodac adnotacje?</div>
          <p>Zaznacz dowolny tekst w raporcie, a pojawi sie opcja dodania komentarza. Twoje adnotacje zostana zapisane i beda widoczne przy kolejnych wizytach.</p>
        </div>
      </main>
    </div>
  )
}
