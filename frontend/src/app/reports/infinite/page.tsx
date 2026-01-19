'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'
import { useUserTimezone, useUserLocale } from '@/hooks/useUserTimezone'
import { formatDateInTimezone } from '@/utils/date'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface ReportSummary {
  id: string
  title: string
  type: string
  company: string | null
  created_at: string
  status: string
  summary: string
}

interface ReportsResponse {
  items: ReportSummary[]
  total: number
  page: number
  limit: number
  pages: number
}

const REPORT_TYPE_LABELS: Record<string, { label: string; color: string; icon: string }> = {
  company_profile: { label: 'Profil firmy', color: 'bg-blue-100 text-blue-800', icon: '🏢' },
  market_analysis: { label: 'Analiza rynku', color: 'bg-green-100 text-green-800', icon: '📊' },
  due_diligence: { label: 'Due Diligence', color: 'bg-purple-100 text-purple-800', icon: '🔍' },
  competitive: { label: 'Konkurencja', color: 'bg-orange-100 text-orange-800', icon: '⚔️' },
}

export default function InfiniteScrollReportsPage() {
  const router = useRouter()
  const userTimezone = useUserTimezone()
  const userLocale = useUserLocale()

  const [reports, setReports] = useState<ReportSummary[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  const [totalReports, setTotalReports] = useState(0)

  // Ref for the sentinel element (trigger for loading more)
  const sentinelRef = useRef<HTMLDivElement>(null)

  // Track which pages we've loaded to avoid duplicates
  const loadedPagesRef = useRef<Set<number>>(new Set())

  const pageSize = 20 // Items per page

  // Fetch reports for a specific page
  const fetchReports = useCallback(async (page: number) => {
    // Avoid loading same page twice
    if (loadedPagesRef.current.has(page)) {
      return
    }

    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const params = new URLSearchParams()
      params.append('page', page.toString())
      params.append('limit', pageSize.toString())

      const response = await fetch(
        `${API_BASE_URL}/reports/?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error('Failed to fetch reports')
      }

      const data: ReportsResponse = await response.json()

      // Mark this page as loaded
      loadedPagesRef.current.add(page)

      // Append new reports to existing ones
      setReports(prev => [...prev, ...data.items])
      setTotalReports(data.total)

      // Check if there are more pages
      setHasMore(page < data.pages)

    } catch (err) {
      setError('Nie udało się załadować raportów')
      console.error('Fetch error:', err)
    } finally {
      setIsLoading(false)
    }
  }, [router])

  // Load more reports when sentinel comes into view
  const loadMore = useCallback(() => {
    if (!isLoading && hasMore) {
      setCurrentPage(prev => prev + 1)
    }
  }, [isLoading, hasMore])

  // Initial load
  useEffect(() => {
    fetchReports(1)
  }, []) // Only run once on mount

  // Load more when currentPage changes
  useEffect(() => {
    if (currentPage > 1) {
      fetchReports(currentPage)
    }
  }, [currentPage, fetchReports])

  // Setup Intersection Observer for infinite scroll
  useEffect(() => {
    const sentinel = sentinelRef.current
    if (!sentinel) return

    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0]
        if (entry.isIntersecting) {
          loadMore()
        }
      },
      {
        root: null, // viewport
        rootMargin: '100px', // trigger 100px before reaching bottom
        threshold: 0.1,
      }
    )

    observer.observe(sentinel)

    return () => {
      if (sentinel) {
        observer.unobserve(sentinel)
      }
    }
  }, [loadMore])

  const formatDate = (dateString: string) => {
    return formatDateInTimezone(dateString, userTimezone, userLocale)
  }

  const getTypeInfo = (type: string) => {
    return REPORT_TYPE_LABELS[type] || { label: type, color: 'bg-gray-100 text-gray-800', icon: '📄' }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-white px-4 py-3 shadow-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/reports" className="text-gray-600 hover:text-gray-900" aria-label="Wróć do raportów (paginacja)">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </Link>
            <h1 className="text-xl font-semibold text-gray-900">Raporty (Infinite Scroll)</h1>
            <span className="text-sm text-gray-500">Performance Test Mode</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/reports" className="text-sm text-blue-600 hover:text-blue-800">
              ← Tryb paginacji
            </Link>
            <Link href="/dashboard" className="hidden sm:inline text-gray-600 hover:text-gray-900">Dashboard</Link>
          </nav>
        </div>
      </header>

      <main id="main-content" className="mx-auto max-w-6xl px-4 py-8">
        {/* Stats header */}
        <div className="mb-6 rounded-xl bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Załadowane raporty</h2>
              <p className="text-sm text-gray-600">
                {reports.length} z {totalReports} raportów
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">{reports.length}</div>
              <div className="text-xs text-gray-500">Strona {currentPage}</div>
            </div>
          </div>

          {/* Progress bar */}
          <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${totalReports > 0 ? (reports.length / totalReports) * 100 : 0}%` }}
            ></div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 rounded-lg bg-red-50 px-4 py-3">
            <span className="text-red-700">{error}</span>
          </div>
        )}

        {/* Reports List */}
        <div className="space-y-4">
          {reports.map((report, index) => {
            const typeInfo = getTypeInfo(report.type)
            return (
              <div
                key={`${report.id}-${index}`}
                className="rounded-xl bg-white p-6 shadow-sm transition-all hover:shadow-md"
              >
                <Link href={`/reports/${report.id}`} className="block">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-2xl">{typeInfo.icon}</span>
                        <span className={`rounded-full px-3 py-1 text-xs font-medium ${typeInfo.color}`}>
                          {typeInfo.label}
                        </span>
                        {report.company && (
                          <span className="text-sm text-gray-500">• {report.company}</span>
                        )}
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900">{report.title}</h3>
                      <p className="mt-2 text-sm text-gray-600 line-clamp-2">{report.summary}</p>
                    </div>
                    <div className="flex flex-col items-end ml-4 gap-2">
                      <span className={`inline-block rounded-full px-2 py-1 text-xs font-medium ${
                        report.status === 'completed' ? 'bg-green-100 text-green-800' :
                        report.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {report.status === 'completed' ? 'Zakończony' :
                         report.status === 'in_progress' ? 'W trakcie' :
                         'Szkic'}
                      </span>
                      <p className="text-xs text-gray-400">{formatDate(report.created_at)}</p>
                    </div>
                  </div>
                </Link>
              </div>
            )
          })}
        </div>

        {/* Sentinel element for Intersection Observer */}
        <div ref={sentinelRef} className="py-8">
          {isLoading && (
            <div className="flex items-center justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
              <span className="ml-3 text-gray-600">Ładowanie kolejnych raportów...</span>
            </div>
          )}

          {!hasMore && reports.length > 0 && (
            <div className="text-center text-gray-500">
              <svg className="mx-auto h-12 w-12 text-gray-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="font-medium">Koniec listy</p>
              <p className="text-sm">Załadowano wszystkie {reports.length} raportów</p>
            </div>
          )}

          {!isLoading && reports.length === 0 && (
            <div className="rounded-xl bg-white p-12 text-center shadow-sm">
              <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-gray-100 p-4">
                <svg className="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900">Brak raportów</h3>
              <p className="mt-2 text-gray-600">Nie znaleziono żadnych raportów.</p>
              <Link
                href="/chat"
                className="mt-4 inline-block rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
              >
                Rozpocznij nową analizę
              </Link>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
