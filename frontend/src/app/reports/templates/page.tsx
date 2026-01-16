'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

function getStoredToken() {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('token')
}

interface Template {
  id: string
  name: string
  type: string
  created_at: string
  created_by: string
  use_count: number
  last_used: string | null
  original_report_title: string
}

export default function TemplatesPage() {
  const router = useRouter()
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/reports/templates`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setTemplates(data.templates || [])
      } else {
        throw new Error('Failed to load templates')
      }
    } catch (err) {
      console.error('Error loading templates:', err)
      setError('Nie udało się załadować szablonów')
    } finally {
      setLoading(false)
    }
  }

  const deleteTemplate = async (templateId: string) => {
    if (!confirm('Czy na pewno chcesz usunąć ten szablon?')) return

    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/reports/templates/${templateId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        setTemplates(templates.filter(t => t.id !== templateId))
        alert('Szablon został usunięty')
      } else {
        throw new Error('Failed to delete template')
      }
    } catch (err) {
      console.error('Error deleting template:', err)
      alert('Nie udało się usunąć szablonu')
    }
  }

  const useTemplate = async (templateId: string, templateName: string) => {
    const reportTitle = prompt(`Wprowadź tytuł nowego raportu bazującego na szablonie "${templateName}":`)
    if (!reportTitle || reportTitle.trim() === '') return

    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/reports/templates/${templateId}/use?report_title=${encodeURIComponent(reportTitle.trim())}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        router.push(`/reports/${data.report_id}`)
      } else {
        throw new Error('Failed to create report from template')
      }
    } catch (err) {
      console.error('Error using template:', err)
      alert('Nie udało się utworzyć raportu z szablonu')
    }
  }

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'company_profile': 'Profil firmy',
      'market_analysis': 'Analiza rynku',
      'competitive': 'Analiza konkurencji',
      'financial': 'Analiza finansowa',
    }
    return labels[type] || type
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pl-PL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
          <p className="mt-2 text-slate-600">Ładowanie szablonów...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link href="/dashboard" className="text-blue-600 hover:text-blue-700">
                MI-Navigator
              </Link>
              <span className="text-slate-400">/</span>
              <Link href="/reports" className="text-slate-600 hover:text-slate-900">
                Raporty
              </Link>
              <span className="text-slate-400">/</span>
              <span className="font-medium text-slate-900">Szablony</span>
            </div>
            <nav className="flex items-center gap-4">
              <Link href="/reports" className="text-sm text-slate-600 hover:text-slate-900">
                Lista raportów
              </Link>
              <Link href="/dashboard" className="text-sm text-slate-600 hover:text-slate-900">
                Dashboard
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-slate-900">Szablony raportów</h1>
          <p className="mt-2 text-slate-600">
            Zarządzaj szablonami raportów. Twórz nowe raporty bazując na istniejących szablonach.
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-lg bg-red-50 border border-red-200 p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {templates.length === 0 ? (
          <div className="rounded-lg bg-white border border-slate-200 p-12 text-center">
            <div className="mx-auto max-w-md">
              <div className="mb-4 text-6xl">📋</div>
              <h3 className="mb-2 text-lg font-semibold text-slate-900">Brak szablonów</h3>
              <p className="mb-6 text-slate-600">
                Nie masz jeszcze żadnych szablonów raportów. Utwórz szablon z istniejącego raportu używając przycisku "Zapisz jako szablon".
              </p>
              <Link
                href="/reports"
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
              >
                Przejdź do raportów
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {templates.map((template) => (
              <div
                key={template.id}
                className="rounded-lg bg-white border border-slate-200 p-6 hover:shadow-lg transition-shadow"
              >
                <div className="mb-4">
                  <div className="flex items-start justify-between">
                    <h3 className="text-lg font-semibold text-slate-900 line-clamp-2">
                      {template.name}
                    </h3>
                    <span className="ml-2 inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
                      {getTypeLabel(template.type)}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-slate-600">
                    Bazuje na: {template.original_report_title}
                  </p>
                </div>

                <div className="mb-4 space-y-2 text-sm text-slate-600">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">Utworzony:</span>
                    <span>{formatDate(template.created_at)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">Użyty:</span>
                    <span>{template.use_count} {template.use_count === 1 ? 'raz' : 'razy'}</span>
                  </div>
                  {template.last_used && (
                    <div className="flex items-center gap-2">
                      <span className="font-medium">Ostatnio:</span>
                      <span>{formatDate(template.last_used)}</span>
                    </div>
                  )}
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => useTemplate(template.id, template.name)}
                    className="flex-1 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                  >
                    Użyj szablonu
                  </button>
                  <button
                    onClick={() => deleteTemplate(template.id)}
                    className="rounded-lg border border-red-300 px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                    title="Usuń szablon"
                  >
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
