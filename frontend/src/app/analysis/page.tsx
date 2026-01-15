'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface MarketDataPoint {
  region: string
  market_size: number
  growth_rate: number
  key_players: number
  year: number
}

interface MarketAnalysisResult {
  id: string
  industry: string
  geography: string
  status: string
  data: MarketDataPoint[]
  insights: string[]
  trends: { name: string; impact: string; timeline: string }[]
}

const INDUSTRIES = [
  { value: 'manufacturing', label: 'Produkcja / Manufacturing' },
  { value: 'technology', label: 'Technologia / IT' },
  { value: 'logistics', label: 'Logistyka / Transport' },
  { value: 'retail', label: 'Handel detaliczny' },
  { value: 'services', label: 'Usługi' },
]

const GEOGRAPHIES = [
  { value: 'poland', label: 'Polska', flag: '🇵🇱' },
  { value: 'europe', label: 'Europa (EU)', flag: '🇪🇺' },
  { value: 'cee', label: 'Europa Środkowo-Wschodnia', flag: '🌍' },
  { value: 'global', label: 'Globalnie', flag: '🌐' },
]

export default function MarketAnalysisPage() {
  const router = useRouter()
  const [industry, setIndustry] = useState('manufacturing')
  const [geography, setGeography] = useState('poland')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<MarketAnalysisResult | null>(null)

  const handleAnalyze = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE_URL}/analysis/market`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          industry,
          geography,
          depth: 'standard',
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to analyze market')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError('Nie udało się przeprowadzić analizy. Spróbuj ponownie.')
    } finally {
      setIsLoading(false)
    }
  }

  const getImpactBadgeColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'bg-red-100 text-red-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
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
            <h1 className="text-xl font-semibold text-gray-900">Analiza Rynku</h1>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">Dashboard</Link>
            <Link href="/chat" className="text-gray-600 hover:text-gray-900">Chat</Link>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
        {/* Analysis Form */}
        <div className="mb-8 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-6 text-lg font-semibold text-gray-900">Parametry analizy</h2>

          <div className="grid gap-6 md:grid-cols-2">
            {/* Industry Selection */}
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">
                Branża
              </label>
              <select
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                {INDUSTRIES.map((ind) => (
                  <option key={ind.value} value={ind.value}>
                    {ind.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Geography Selection */}
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">
                Obszar geograficzny
              </label>
              <div className="grid grid-cols-2 gap-3">
                {GEOGRAPHIES.map((geo) => (
                  <button
                    key={geo.value}
                    onClick={() => setGeography(geo.value)}
                    className={`flex items-center gap-2 rounded-lg border px-4 py-3 text-left transition-all ${
                      geography === geo.value
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <span className="text-xl">{geo.flag}</span>
                    <span className="font-medium">{geo.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={isLoading}
            className="mt-6 w-full rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="h-5 w-5 animate-spin" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Analizowanie...
              </span>
            ) : (
              'Rozpocznij analizę'
            )}
          </button>
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
            {/* Summary Header */}
            <div className="rounded-xl bg-gradient-to-r from-blue-600 to-blue-700 p-6 text-white">
              <div className="flex items-center gap-2 text-blue-100">
                <span className="text-2xl">
                  {GEOGRAPHIES.find(g => g.value === result.geography)?.flag}
                </span>
                <span className="text-lg">
                  {GEOGRAPHIES.find(g => g.value === result.geography)?.label}
                </span>
              </div>
              <h3 className="mt-2 text-2xl font-bold capitalize">
                Analiza rynku: {INDUSTRIES.find(i => i.value === result.industry)?.label}
              </h3>
              <p className="mt-1 text-blue-100">
                Dane za rok {result.data[0]?.year || 2024}
              </p>
            </div>

            {/* Market Data Table */}
            <div className="rounded-xl bg-white p-6 shadow-sm">
              <h4 className="mb-4 text-lg font-semibold text-gray-900">Dane rynkowe</h4>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b text-left text-sm font-medium text-gray-500">
                      <th className="pb-3 pr-4">Region</th>
                      <th className="pb-3 pr-4">Wielkość rynku (mld EUR)</th>
                      <th className="pb-3 pr-4">Wzrost YoY</th>
                      <th className="pb-3">Liczba graczy</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {result.data.map((point, index) => (
                      <tr key={index} className="text-sm">
                        <td className="py-3 pr-4 font-medium text-gray-900">{point.region}</td>
                        <td className="py-3 pr-4 text-gray-700">{point.market_size.toFixed(1)}</td>
                        <td className="py-3 pr-4">
                          <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                            point.growth_rate > 5 ? 'bg-green-100 text-green-800' :
                            point.growth_rate > 3 ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            +{point.growth_rate.toFixed(1)}%
                          </span>
                        </td>
                        <td className="py-3 text-gray-700">{point.key_players.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Insights */}
            <div className="rounded-xl bg-white p-6 shadow-sm">
              <h4 className="mb-4 text-lg font-semibold text-gray-900">Kluczowe wnioski</h4>
              <ul className="space-y-3">
                {result.insights.map((insight, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="mt-1 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs text-blue-600">
                      {index + 1}
                    </span>
                    <span className="text-gray-700">{insight}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Trends */}
            <div className="rounded-xl bg-white p-6 shadow-sm">
              <h4 className="mb-4 text-lg font-semibold text-gray-900">Trendy rynkowe</h4>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {result.trends.map((trend, index) => (
                  <div key={index} className="rounded-lg border border-gray-200 p-4">
                    <div className="mb-2 flex items-center justify-between">
                      <h5 className="font-medium text-gray-900">{trend.name}</h5>
                      <span className={`rounded-full px-2 py-1 text-xs font-medium ${getImpactBadgeColor(trend.impact)}`}>
                        {trend.impact === 'high' ? 'Wysoki' : trend.impact === 'medium' ? 'Średni' : 'Niski'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500">Horyzont: {trend.timeline}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
