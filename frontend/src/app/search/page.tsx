'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
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
  const [pkdCode, setPkdCode] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<PKDSearchResult | null>(null)

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
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">Dashboard</Link>
            <Link href="/analysis" className="text-gray-600 hover:text-gray-900">Analiza rynku</Link>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
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
              <div className="flex items-center gap-3">
                <span className="rounded-lg bg-white/20 px-3 py-1 font-mono text-lg">
                  {result.pkd_code}
                </span>
                <span className="rounded-full bg-white/20 px-3 py-1 text-sm">
                  {result.pkd_category}
                </span>
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
    </div>
  )
}
