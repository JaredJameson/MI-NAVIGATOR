'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface PKDDescription {
  code: string
  name: string
  category: string
}

interface CompanyResult {
  id: string
  name: string
  nip: string
  address: { city: string; street: string; postal_code: string }
  pkd_codes: string[]
  pkd_descriptions: PKDDescription[]
  status: string
}

interface PKDSearchResult {
  pkd_code: string
  pkd_description: string
  pkd_category: string
  companies: CompanyResult[]
  total_count: number
}

interface SavedSearch {
  id: string
  name: string
  search_type: string
  query: string
  filters?: Record<string, unknown>
  created_at: string
  result_count?: number
}

// Common PKD codes for quick selection
const POPULAR_PKD_CODES = [
  { code: '22.21.Z', name: 'Produkcja tworzyw sztucznych', icon: '🏭' },
  { code: '62.01.Z', name: 'Oprogramowanie', icon: '💻' },
  { code: '49.41.Z', name: 'Transport drogowy', icon: '🚚' },
  { code: '41.20.Z', name: 'Budownictwo', icon: '🏗️' },
  { code: '69.20.Z', name: 'Księgowość', icon: '📊' },
  { code: '46.71.Z', name: 'Handel paliwami', icon: '⛽' },
]

export default function SearchPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [pkdCode, setPkdCode] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<PKDSearchResult | null>(null)

  // Saved searches state
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([])
  const [showSavedSearches, setShowSavedSearches] = useState(false)
  const [showSaveModal, setShowSaveModal] = useState(false)
  const [saveSearchName, setSaveSearchName] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [saveError, setSaveError] = useState('')
  const [saveSuccess, setSaveSuccess] = useState('')

  // Load saved searches on mount
  useEffect(() => {
    loadSavedSearches()
  }, [])

  // Handle URL parameter for loading saved search
  useEffect(() => {
    const pkdParam = searchParams.get('pkd')
    if (pkdParam) {
      setPkdCode(pkdParam)
      handleSearch(pkdParam)
    }
  }, [searchParams])

  const loadSavedSearches = async () => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/search/saved`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setSavedSearches(data.searches)
      }
    } catch (err) {
      console.error('Failed to load saved searches:', err)
    }
  }

  const handleSearch = async (codeToSearch?: string) => {
    const searchCode = codeToSearch || pkdCode

    if (!searchCode.trim()) {
      setError('Wprowadź kod PKD')
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
      const response = await fetch(
        `${API_BASE_URL}/companies/search/pkd?code=${encodeURIComponent(searchCode)}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error('Failed to search')
      }

      const data = await response.json()
      setResult(data)

      if (codeToSearch) {
        setPkdCode(codeToSearch)
      }
    } catch (err) {
      setError('Nie udało się wyszukać firm. Spróbuj ponownie.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const handleSaveSearch = async () => {
    if (!saveSearchName.trim()) {
      setSaveError('Wprowadź nazwę wyszukiwania')
      return
    }

    if (!result) {
      setSaveError('Najpierw wykonaj wyszukiwanie')
      return
    }

    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsSaving(true)
    setSaveError('')

    try {
      const response = await fetch(`${API_BASE_URL}/search/saved`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: saveSearchName,
          search_type: 'pkd',
          query: result.pkd_code,
          filters: {
            pkd_description: result.pkd_description,
            pkd_category: result.pkd_category,
          },
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to save search')
      }

      const newSearch = await response.json()
      setSavedSearches([newSearch, ...savedSearches])
      setShowSaveModal(false)
      setSaveSearchName('')
      setSaveSuccess('Wyszukiwanie zapisane!')
      setTimeout(() => setSaveSuccess(''), 3000)
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Nie udało się zapisać wyszukiwania')
    } finally {
      setIsSaving(false)
    }
  }

  const handleLoadSearch = async (search: SavedSearch) => {
    if (search.search_type === 'pkd') {
      setPkdCode(search.query)
      await handleSearch(search.query)
      setShowSavedSearches(false)
    }
  }

  const handleDeleteSearch = async (searchId: string) => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/search/saved/${searchId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        setSavedSearches(savedSearches.filter(s => s.id !== searchId))
      }
    } catch (err) {
      console.error('Failed to delete saved search:', err)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pl-PL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
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
            <h1 className="text-xl font-semibold text-gray-900">Wyszukiwanie PKD</h1>
          </div>
          <nav className="flex items-center gap-4">
            <button
              onClick={() => setShowSavedSearches(!showSavedSearches)}
              className="flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
              Zapisane ({savedSearches.length})
            </button>
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">Dashboard</Link>
            <Link href="/analysis" className="text-gray-600 hover:text-gray-900">Analiza rynku</Link>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
        {/* Success message */}
        {saveSuccess && (
          <div className="mb-6 rounded-lg bg-green-50 px-4 py-3 text-green-700 flex items-center gap-2">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            {saveSuccess}
          </div>
        )}

        {/* Saved Searches Panel */}
        {showSavedSearches && (
          <div className="mb-8 rounded-xl bg-white p-6 shadow-sm border-2 border-blue-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                </svg>
                Zapisane wyszukiwania
              </h2>
              <button
                onClick={() => setShowSavedSearches(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {savedSearches.length === 0 ? (
              <p className="text-gray-500 text-center py-4">
                Brak zapisanych wyszukiwań. Wykonaj wyszukiwanie i kliknij &quot;Zapisz&quot; aby dodać.
              </p>
            ) : (
              <div className="space-y-3">
                {savedSearches.map((search) => (
                  <div
                    key={search.id}
                    className="flex items-center justify-between rounded-lg border border-gray-200 p-4 hover:bg-gray-50"
                  >
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{search.name}</h3>
                      <p className="text-sm text-gray-600">
                        Kod PKD: <span className="font-mono">{search.query}</span>
                        {search.filters?.pkd_description && (
                          <span className="ml-2 text-gray-400">- {String(search.filters.pkd_description).slice(0, 50)}...</span>
                        )}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        Zapisano: {formatDate(search.created_at)}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleLoadSearch(search)}
                        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                      >
                        Załaduj
                      </button>
                      <button
                        onClick={() => handleDeleteSearch(search.id)}
                        className="rounded-lg border border-gray-200 p-2 text-gray-400 hover:bg-red-50 hover:text-red-600 hover:border-red-200"
                        title="Usuń"
                      >
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Search Form */}
        <div className="mb-8 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Wyszukaj firmy według kodu PKD</h2>
          <p className="mb-6 text-sm text-gray-600">
            PKD (Polska Klasyfikacja Działalności) to kod określający rodzaj działalności gospodarczej firmy.
          </p>

          <div className="flex gap-4">
            <div className="flex-1">
              <input
                type="text"
                value={pkdCode}
                onChange={(e) => setPkdCode(e.target.value.toUpperCase())}
                onKeyDown={handleKeyDown}
                placeholder="Wpisz kod PKD (np. 22.21.Z)"
                className="w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <button
              onClick={() => handleSearch()}
              disabled={isLoading}
              className="rounded-lg bg-blue-600 px-8 py-3 font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <svg className="h-5 w-5 animate-spin" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Szukam...
                </span>
              ) : (
                'Szukaj'
              )}
            </button>
          </div>

          {/* Popular PKD codes */}
          <div className="mt-6">
            <p className="mb-3 text-sm font-medium text-gray-700">Popularne kody PKD:</p>
            <div className="flex flex-wrap gap-2">
              {POPULAR_PKD_CODES.map((pkd) => (
                <button
                  key={pkd.code}
                  onClick={() => handleSearch(pkd.code)}
                  className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-700 transition-colors hover:border-blue-300 hover:bg-blue-50"
                >
                  <span>{pkd.icon}</span>
                  <span className="font-mono">{pkd.code}</span>
                  <span className="text-gray-500">-</span>
                  <span>{pkd.name}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 rounded-lg bg-red-50 px-4 py-3 text-red-700">
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* PKD Info Header */}
            <div className="rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="rounded-lg bg-white/20 px-3 py-1 font-mono text-lg">
                    {result.pkd_code}
                  </span>
                  <span className="rounded-full bg-white/20 px-3 py-1 text-sm">
                    {result.pkd_category}
                  </span>
                </div>
                <button
                  onClick={() => setShowSaveModal(true)}
                  className="flex items-center gap-2 rounded-lg bg-white/20 px-4 py-2 text-white hover:bg-white/30 transition-colors"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                  </svg>
                  Zapisz wyszukiwanie
                </button>
              </div>
              <h3 className="mt-3 text-xl font-semibold">{result.pkd_description}</h3>
              <p className="mt-2 text-indigo-100">
                Znaleziono {result.total_count} {result.total_count === 1 ? 'firmę' :
                  result.total_count < 5 ? 'firmy' : 'firm'} z tym kodem PKD
              </p>
            </div>

            {/* Companies List */}
            {result.companies.length > 0 ? (
              <div className="rounded-xl bg-white p-6 shadow-sm">
                <h4 className="mb-4 text-lg font-semibold text-gray-900">Firmy z kodem {result.pkd_code}</h4>
                <div className="space-y-4">
                  {result.companies.map((company) => (
                    <div
                      key={company.id}
                      className="rounded-lg border border-gray-200 p-4 transition-shadow hover:shadow-md"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h5 className="text-lg font-semibold text-gray-900">{company.name}</h5>
                          <p className="mt-1 text-sm text-gray-600">
                            NIP: <span className="font-mono">{company.nip}</span>
                          </p>
                          <p className="text-sm text-gray-600">
                            {company.address.street}, {company.address.postal_code} {company.address.city}
                          </p>
                        </div>
                        <span className={`rounded-full px-3 py-1 text-xs font-medium ${
                          company.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {company.status === 'active' ? 'Aktywna' : company.status}
                        </span>
                      </div>

                      {/* PKD codes for this company */}
                      <div className="mt-4">
                        <p className="mb-2 text-xs font-medium text-gray-500 uppercase">Kody PKD</p>
                        <div className="flex flex-wrap gap-2">
                          {company.pkd_descriptions.map((pkd) => (
                            <span
                              key={pkd.code}
                              className={`rounded px-2 py-1 text-xs ${
                                pkd.code === result.pkd_code
                                  ? 'bg-blue-100 text-blue-800 font-medium'
                                  : 'bg-gray-100 text-gray-700'
                              }`}
                              title={pkd.name}
                            >
                              {pkd.code}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="rounded-xl bg-white p-8 text-center shadow-sm">
                <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-gray-100 p-4">
                  <svg className="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <h4 className="text-lg font-medium text-gray-900">Brak firm</h4>
                <p className="mt-2 text-gray-600">
                  Nie znaleziono firm z kodem PKD {result.pkd_code}
                </p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Save Search Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Zapisz wyszukiwanie</h3>
              <button
                onClick={() => {
                  setShowSaveModal(false)
                  setSaveSearchName('')
                  setSaveError('')
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {result && (
              <div className="mb-4 rounded-lg bg-gray-50 p-3">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Kod PKD:</span> {result.pkd_code}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Opis:</span> {result.pkd_description}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Wyniki:</span> {result.total_count} firm
                </p>
              </div>
            )}

            <div className="mb-4">
              <label htmlFor="searchName" className="block text-sm font-medium text-gray-700 mb-1">
                Nazwa wyszukiwania
              </label>
              <input
                id="searchName"
                type="text"
                value={saveSearchName}
                onChange={(e) => setSaveSearchName(e.target.value)}
                placeholder="np. Firmy plastikowe"
                className="w-full rounded-lg border border-gray-300 px-4 py-2 text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleSaveSearch()
                  }
                  if (e.key === 'Escape') {
                    setShowSaveModal(false)
                    setSaveSearchName('')
                    setSaveError('')
                  }
                }}
                autoFocus
              />
            </div>

            {saveError && (
              <div className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
                {saveError}
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowSaveModal(false)
                  setSaveSearchName('')
                  setSaveError('')
                }}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50"
              >
                Anuluj
              </button>
              <button
                onClick={handleSaveSearch}
                disabled={isSaving}
                className="flex-1 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:bg-gray-300"
              >
                {isSaving ? 'Zapisuję...' : 'Zapisz'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
