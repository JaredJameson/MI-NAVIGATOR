'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface Project {
  id: string
  name: string
  description: string | null
  type: string
  created_at: string
  updated_at: string
  status: string
  report_ids: string[]
}

const PROJECT_TYPE_LABELS: Record<string, { label: string; color: string; icon: string }> = {
  due_diligence: { label: 'Due Diligence', color: 'bg-purple-100 text-purple-800', icon: '🔍' },
  market_analysis: { label: 'Analiza rynku', color: 'bg-green-100 text-green-800', icon: '📊' },
  competitive: { label: 'Konkurencja', color: 'bg-orange-100 text-orange-800', icon: '⚔️' },
  research: { label: 'Badania', color: 'bg-blue-100 text-blue-800', icon: '🔬' }
}

export default function ProjectsPage() {
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    // Ensure we're in browser environment
    if (typeof window === 'undefined') {
      setIsLoading(false)
      return
    }

    const token = getStoredToken()
    if (!token) {
      // Don't redirect - AuthGuard will handle this
      setIsLoading(false)
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE_URL}/projects/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        if (response.status === 401) {
          // Don't show error - AuthGuard will handle this
          setIsLoading(false)
          return
        }
        throw new Error('Failed to fetch projects')
      }

      const data = await response.json()
      setProjects(data.items || [])
    } catch (err) {
      setError('Nie udało się załadować projektów')
    } finally {
      setIsLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pl-PL', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  }

  const getTypeInfo = (type: string) => {
    return PROJECT_TYPE_LABELS[type] || { label: type, color: 'bg-gray-100 text-gray-800', icon: '📁' }
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
            <h1 className="text-xl font-semibold text-gray-900">Projekty</h1>
          </div>
          <nav className="flex items-center gap-2 sm:gap-4">
            <Link href="/dashboard" className="hidden sm:inline text-gray-600 hover:text-gray-900">Dashboard</Link>
            <Link href="/reports" className="hidden sm:inline text-gray-600 hover:text-gray-900">Raporty</Link>
            <Link
              href="/projects/new"
              className="rounded-lg bg-purple-600 px-3 sm:px-4 py-2 text-sm sm:text-base text-white hover:bg-purple-700 transition-colors whitespace-nowrap"
            >
              + Nowy projekt
            </Link>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
        {/* Error Display */}
        {error && (
          <div className="mb-6 rounded-lg bg-red-50 px-4 py-3 text-red-700">
            {error}
          </div>
        )}

        {/* Loading State */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-purple-600 border-t-transparent"></div>
            <span className="ml-3 text-gray-600">Ładowanie projektów...</span>
          </div>
        ) : projects.length === 0 ? (
          /* Empty State */
          <div className="rounded-xl bg-white p-12 text-center shadow-sm">
            <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-gray-100 p-4">
              <svg className="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900">Brak projektów</h3>
            <p className="mt-2 text-gray-600">Nie masz jeszcze żadnych projektów.</p>
          </div>
        ) : (
          /* Projects List */
          <div className="space-y-4">
            {projects.map((project) => {
              const typeInfo = getTypeInfo(project.type)
              return (
                <Link
                  key={project.id}
                  href={`/projects/${project.id}`}
                  className="block rounded-xl bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-2xl">{typeInfo.icon}</span>
                        <span className={`rounded-full px-3 py-1 text-xs font-medium ${typeInfo.color}`}>
                          {typeInfo.label}
                        </span>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 truncate" title={project.name}>{project.name}</h3>
                      {project.description && (
                        <p className="mt-2 text-sm text-gray-600 line-clamp-2">{project.description}</p>
                      )}
                      <div className="mt-3 flex items-center gap-4 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          {project.report_ids?.length || 0} raportów
                        </span>
                        <span>Aktualizacja: {formatDate(project.updated_at)}</span>
                      </div>
                    </div>
                    <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
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
