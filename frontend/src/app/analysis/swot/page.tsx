'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface SWOTItem {
  title: string
  description: string
}

interface SWOTData {
  company_name: string
  strengths: SWOTItem[]
  weaknesses: SWOTItem[]
  opportunities: SWOTItem[]
  threats: SWOTItem[]
}

export default function SWOTAnalysisPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [swotData, setSwotData] = useState<SWOTData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())
  const [companyId, setCompanyId] = useState('')

  useEffect(() => {
    const company = searchParams.get('company') || 'fado'
    setCompanyId(company)
    fetchSWOTAnalysis(company)
  }, [searchParams])

  const fetchSWOTAnalysis = async (company: string) => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE_URL}/analysis/swot/${company}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        if (response.status === 401) {
          router.push('/auth/login')
          return
        }
        throw new Error('Nie udało się załadować analizy SWOT')
      }

      const data = await response.json()
      setSwotData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Wystąpił błąd')
    } finally {
      setIsLoading(false)
    }
  }

  const toggleItem = (quadrant: string, index: number) => {
    const key = `${quadrant}-${index}`
    setExpandedItems(prev => {
      const newSet = new Set(prev)
      if (newSet.has(key)) {
        newSet.delete(key)
      } else {
        newSet.add(key)
      }
      return newSet
    })
  }

  const isExpanded = (quadrant: string, index: number) => {
    return expandedItems.has(`${quadrant}-${index}`)
  }

  const renderQuadrant = (
    title: string,
    items: SWOTItem[],
    quadrant: string,
    bgColor: string,
    borderColor: string,
    icon: string
  ) => (
    <div className={`${bgColor} ${borderColor} border-2 rounded-xl p-4 min-h-[280px]`}>
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">{icon}</span>
        <h3 className="text-lg font-bold text-gray-900">{title}</h3>
        <span className="ml-auto text-sm text-gray-500">({items.length})</span>
      </div>
      <div className="space-y-2">
        {items.map((item, index) => (
          <div
            key={index}
            className="bg-white/80 rounded-lg p-3 cursor-pointer hover:bg-white transition-colors"
            onClick={() => toggleItem(quadrant, index)}
          >
            <div className="flex items-start justify-between gap-2">
              <span className="font-medium text-gray-800 text-sm">{item.title}</span>
              <span className="text-gray-400 text-xs">
                {isExpanded(quadrant, index) ? '▼' : '▶'}
              </span>
            </div>
            {isExpanded(quadrant, index) && (
              <p className="mt-2 text-sm text-gray-600 border-t pt-2">
                {item.description}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-3xl">📊</span>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Analiza SWOT</h1>
                <p className="mt-1 text-sm text-gray-500">
                  {swotData?.company_name || 'Ładowanie...'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Link
                href="/analysis"
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
              >
                ← Powrót do analiz
              </Link>
              <Link
                href="/dashboard"
                className="px-4 py-2 text-sm bg-gray-100 rounded-lg text-gray-600 hover:bg-gray-200"
              >
                Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-500">Ładowanie analizy SWOT...</p>
            </div>
          </div>
        ) : swotData ? (
          <>
            {/* SWOT Diagram Legend */}
            <div className="mb-6 flex flex-wrap gap-4 justify-center">
              <div className="flex items-center gap-2 text-sm">
                <div className="w-4 h-4 bg-green-100 border-2 border-green-300 rounded"></div>
                <span className="text-gray-600">Mocne strony (wewnętrzne, pozytywne)</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <div className="w-4 h-4 bg-red-100 border-2 border-red-300 rounded"></div>
                <span className="text-gray-600">Słabe strony (wewnętrzne, negatywne)</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <div className="w-4 h-4 bg-blue-100 border-2 border-blue-300 rounded"></div>
                <span className="text-gray-600">Szanse (zewnętrzne, pozytywne)</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <div className="w-4 h-4 bg-orange-100 border-2 border-orange-300 rounded"></div>
                <span className="text-gray-600">Zagrożenia (zewnętrzne, negatywne)</span>
              </div>
            </div>

            {/* SWOT Quadrant Diagram */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              {/* Axis Labels */}
              <div className="flex justify-center mb-2">
                <span className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
                  Czynniki wewnętrzne
                </span>
              </div>

              <div className="flex">
                {/* Left axis label */}
                <div className="flex items-center justify-center w-8">
                  <span className="text-sm font-semibold text-gray-500 uppercase tracking-wide transform -rotate-90 whitespace-nowrap">
                    Pozytywne
                  </span>
                </div>

                {/* Main grid */}
                <div className="flex-1 grid grid-cols-2 gap-4">
                  {/* Strengths - Top Left */}
                  {renderQuadrant(
                    'Mocne strony',
                    swotData.strengths,
                    'strengths',
                    'bg-green-50',
                    'border-green-300',
                    '💪'
                  )}

                  {/* Weaknesses - Top Right */}
                  {renderQuadrant(
                    'Słabe strony',
                    swotData.weaknesses,
                    'weaknesses',
                    'bg-red-50',
                    'border-red-300',
                    '⚠️'
                  )}

                  {/* Opportunities - Bottom Left */}
                  {renderQuadrant(
                    'Szanse',
                    swotData.opportunities,
                    'opportunities',
                    'bg-blue-50',
                    'border-blue-300',
                    '🚀'
                  )}

                  {/* Threats - Bottom Right */}
                  {renderQuadrant(
                    'Zagrożenia',
                    swotData.threats,
                    'threats',
                    'bg-orange-50',
                    'border-orange-300',
                    '⛔'
                  )}
                </div>

                {/* Right axis label */}
                <div className="flex items-center justify-center w-8">
                  <span className="text-sm font-semibold text-gray-500 uppercase tracking-wide transform rotate-90 whitespace-nowrap">
                    Negatywne
                  </span>
                </div>
              </div>

              {/* Bottom axis label */}
              <div className="flex justify-center mt-2">
                <span className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
                  Czynniki zewnętrzne
                </span>
              </div>
            </div>

            {/* Summary */}
            <div className="mt-6 bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Podsumowanie analizy</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{swotData.strengths.length}</div>
                  <div className="text-sm text-gray-600">Mocnych stron</div>
                </div>
                <div className="p-4 bg-red-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">{swotData.weaknesses.length}</div>
                  <div className="text-sm text-gray-600">Słabych stron</div>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{swotData.opportunities.length}</div>
                  <div className="text-sm text-gray-600">Szans</div>
                </div>
                <div className="p-4 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">{swotData.threats.length}</div>
                  <div className="text-sm text-gray-600">Zagrożeń</div>
                </div>
              </div>
              <p className="mt-4 text-sm text-gray-500 text-center">
                Kliknij w element, aby rozwinąć szczegóły
              </p>
            </div>
          </>
        ) : null}
      </div>
    </div>
  )
}
