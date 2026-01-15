'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

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

export default function ReportsPage() {
  const router = useRouter()
  const [reports, setReports] = useState<ReportSummary[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState('')

  useEffect(() => {
    fetchReports()
  }, [filterType])

  const fetchReports = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const params = new URLSearchParams()
      if (filterType) params.append('type', filterType)
      if (searchQuery) params.append('search', searchQuery)

      const response = await fetch(
        `${API_BASE_URL}/reports?${params.toString()}`,
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
      setReports(data.items)
    } catch (err) {
      setError('Nie udało się załadować raportów')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    fetchReports()
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pl-PL', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getTypeInfo = (type: string) => {
    return REPORT_TYPE_LABELS[type] || { label: type, color: 'bg-gray-100 text-gray-800', icon: '📄' }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-white px-4 py-3">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </Link>
            <h1 className="text-xl font-semibold text-gray-900">Raporty</h1>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">Dashboard</Link>
            <Link href="/search" className="text-gray-600 hover:text-gray-900">PKD Search</Link>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
        {/* Search and Filters */}
        <div className="mb-6 rounded-xl bg-white p-6 shadow-sm">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Szukaj w raportach..."
                className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Wszystkie typy</option>
              <option value="company_profile">Profil firmy</option>
              <option value="market_analysis">Analiza rynku</option>
              <option value="due_diligence">Due Diligence</option>
              <option value="competitive">Konkurencja</option>
            </select>
            <button
              type="submit"
              className="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700"
            >
              Szukaj
            </button>
          </form>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 rounded-lg bg-red-50 px-4 py-3 text-red-700">
            {error}
          </div>
        )}

        {/* Loading State */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
            <span className="ml-3 text-gray-600">Ładowanie raportów...</span>
          </div>
        ) : reports.length === 0 ? (
          /* Empty State */
          <div className="rounded-xl bg-white p-12 text-center shadow-sm">
            <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-gray-100 p-4">
              <svg className="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900">Brak raportów</h3>
            <p className="mt-2 text-gray-600">Nie znaleziono raportów spełniających kryteria wyszukiwania.</p>
            <Link
              href="/chat"
              className="mt-4 inline-block rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              Rozpocznij nową analizę
            </Link>
          </div>
        ) : (
          /* Reports List */
          <div className="space-y-4">
            {reports.map((report) => {
              const typeInfo = getTypeInfo(report.type)
              return (
                <Link
                  key={report.id}
                  href={`/reports/${report.id}`}
                  className="block rounded-xl bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
                >
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
                    <div className="text-right ml-4">
                      <span className={`inline-block rounded-full px-2 py-1 text-xs font-medium ${
                        report.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {report.status === 'completed' ? 'Zakończony' : 'W toku'}
                      </span>
                      <p className="mt-2 text-xs text-gray-400">{formatDate(report.created_at)}</p>
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        )}
      </main>
    </div>
  )
}
