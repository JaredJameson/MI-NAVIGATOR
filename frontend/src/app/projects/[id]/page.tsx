'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken, getCsrfToken, fetchCsrfToken } from '@/services/api'
import { ActivityFeed } from '@/components/projects/ActivityFeed'
import { Breadcrumb } from '@/components/ui/Breadcrumb'

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

interface ReportSummary {
  id: string
  title: string
  type: string
  company: string | null
  status: string
  updated_at: string
}

interface Activity {
  id: string
  type: string
  description: string
  user: string
  timestamp: string
}

const PROJECT_TYPE_LABELS: Record<string, string> = {
  due_diligence: 'Due Diligence',
  market_analysis: 'Analiza rynku',
  competitive: 'Konkurencja',
  research: 'Badania'
}

const REPORT_TYPE_LABELS: Record<string, { label: string; icon: string }> = {
  company_profile: { label: 'Profil firmy', icon: '🏢' },
  market_analysis: { label: 'Analiza rynku', icon: '📊' },
  due_diligence: { label: 'Due Diligence', icon: '🔍' },
  competitive: { label: 'Konkurencja', icon: '⚔️' },
}

export default function ProjectDetailPage() {
  const router = useRouter()
  const params = useParams()
  const projectId = params.id as string

  const [project, setProject] = useState<Project | null>(null)
  const [reports, setReports] = useState<ReportSummary[]>([])
  const [activities, setActivities] = useState<Activity[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingActivities, setIsLoadingActivities] = useState(true)
  const [error, setError] = useState('')
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    fetchProjectDetails()
    fetchProjectActivity()
  }, [projectId])

  const fetchProjectDetails = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      // Fetch project details
      const projectResponse = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!projectResponse.ok) {
        throw new Error('Failed to fetch project')
      }

      const projectData = await projectResponse.json()
      setProject(projectData)

      // Fetch project reports
      const reportsResponse = await fetch(`${API_BASE_URL}/projects/${projectId}/reports`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (reportsResponse.ok) {
        const reportsData = await reportsResponse.json()
        setReports(reportsData.reports || [])
      }
    } catch (err) {
      setError('Nie udało się załadować projektu')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchProjectActivity = async () => {
    const token = getStoredToken()
    if (!token) {
      return
    }

    setIsLoadingActivities(true)

    try {
      const response = await fetch(`${API_BASE_URL}/projects/${projectId}/activity`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setActivities(data.activities || [])
      }
    } catch (err) {
      console.error('Failed to fetch activities:', err)
    } finally {
      setIsLoadingActivities(false)
    }
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

  const getReportTypeInfo = (type: string) => {
    return REPORT_TYPE_LABELS[type] || { label: type, icon: '📄' }
  }

  const handleDeleteProject = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsDeleting(true)
    setError('')

    try {
      // Get CSRF token
      let csrfToken = getCsrfToken()
      if (!csrfToken) {
        csrfToken = await fetchCsrfToken()
      }

      const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-CSRF-Token': csrfToken || '',
        },
      })

      if (!response.ok) {
        throw new Error('Failed to delete project')
      }

      // Redirect to projects list after successful deletion
      router.push('/projects')
    } catch (err) {
      setError('Nie udało się usunąć projektu')
      setIsDeleting(false)
      setShowDeleteDialog(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-purple-600 border-t-transparent"></div>
        <span className="ml-3 text-gray-600">Ładowanie projektu...</span>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">{error || 'Projekt nie został znaleziony'}</p>
          <Link href="/projects" className="mt-4 inline-block text-purple-600 hover:text-purple-700">
            ← Wróć do projektów
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-white px-4 py-3">
        <div className="mx-auto flex max-w-6xl flex-col gap-2">
          <Breadcrumb
            items={[
              { label: 'Dashboard', href: '/dashboard' },
              { label: 'Projects', href: '/projects' },
              { label: project.name }
            ]}
          />
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">{project.name}</h1>
              <span className="text-sm text-gray-500">
                {PROJECT_TYPE_LABELS[project.type] || project.type}
              </span>
            </div>
            <nav className="flex items-center gap-4">
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">Dashboard</Link>
              <Link href="/reports" className="text-gray-600 hover:text-gray-900">Raporty</Link>
              <Link
                href={`/projects/${projectId}/edit`}
                className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 transition-colors"
              >
                Edit Project
              </Link>
              <button
                onClick={() => setShowDeleteDialog(true)}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 transition-colors"
              >
                Delete
              </button>
            </nav>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
        {/* Project Info */}
        <div className="mb-6 rounded-xl bg-white p-6 shadow-sm">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Opis</h3>
              <p className="mt-1 text-gray-900">{project.description || 'Brak opisu'}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Utworzony</h3>
              <p className="mt-1 text-gray-900">{formatDate(project.created_at)}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Ostatnia aktualizacja</h3>
              <p className="mt-1 text-gray-900">{formatDate(project.updated_at)}</p>
            </div>
          </div>
        </div>

        {/* Reports in Project */}
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Raporty w projekcie ({reports.length})
            </h2>
            <Link
              href="/reports"
              className="text-sm text-purple-600 hover:text-purple-700"
            >
              + Dodaj raporty
            </Link>
          </div>

          {reports.length === 0 ? (
            <div className="py-12 text-center">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="mt-2 text-gray-500">Brak raportów w projekcie</p>
              <p className="text-sm text-gray-400">
                Przejdź do listy raportów, aby przypisać raporty do tego projektu
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {reports.map((report) => {
                const typeInfo = getReportTypeInfo(report.type)
                return (
                  <Link
                    key={report.id}
                    href={`/reports/${report.id}`}
                    className="block rounded-lg border border-gray-200 p-4 hover:border-purple-300 hover:bg-purple-50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-xl">{typeInfo.icon}</span>
                        <div>
                          <h3 className="font-medium text-gray-900">{report.title}</h3>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-gray-500">{typeInfo.label}</span>
                            {report.company && (
                              <span className="text-xs text-gray-400">• {report.company}</span>
                            )}
                          </div>
                        </div>
                      </div>
                      <span className={`rounded-full px-2 py-1 text-xs font-medium ${
                        report.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {report.status === 'completed' ? 'Zakończony' : 'W toku'}
                      </span>
                    </div>
                  </Link>
                )
              })}
            </div>
          )}
        </div>

        {/* Activity Feed */}
        <div className="mt-6">
          <ActivityFeed activities={activities} isLoading={isLoadingActivities} />
        </div>
      </main>

      {/* Delete Confirmation Dialog */}
      {showDeleteDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full max-h-[calc(100vh-2rem)] overflow-y-auto">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Delete Project</h3>
                <p className="text-sm text-gray-500">This action cannot be undone</p>
              </div>
            </div>

            <p className="text-gray-700 mb-6">
              Are you sure you want to delete <strong>{project?.name}</strong>?
              {reports.length > 0 && (
                <span className="block mt-2 text-sm text-orange-600">
                  ⚠️ This project has {reports.length} report(s) assigned. They will remain in your reports list.
                </span>
              )}
            </p>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
                {error}
              </div>
            )}

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowDeleteDialog(false)
                  setError('')
                }}
                disabled={isDeleting}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteProject}
                disabled={isDeleting}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                {isDeleting ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                    Deleting...
                  </>
                ) : (
                  'Delete Project'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
