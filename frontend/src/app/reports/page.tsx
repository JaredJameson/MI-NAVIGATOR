'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// Helper function to get CSRF token
const getCsrfToken = async (): Promise<string | null> => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/csrf-token`)
    if (response.ok) {
      const data = await response.json()
      return data.csrf_token
    }
  } catch (err) {
    console.error('Failed to get CSRF token:', err)
  }
  return null
}

interface Tag {
  id: string
  name: string
  color: string
  description: string | null
  created_at: string
  user_id: string
}

interface ReportSummary {
  id: string
  title: string
  type: string
  company: string | null
  created_at: string
  status: string
  summary: string
  tags?: Tag[]
  is_favorite?: boolean
}

interface ReportsResponse {
  items: ReportSummary[]
  total: number
  page: number
  limit: number
  pages: number
}

interface AllIdsResponse {
  ids: string[]
  total: number
}

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
  const [filterTag, setFilterTag] = useState('')
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false)
  const [filterStatus, setFilterStatus] = useState('')
  const [showArchived, setShowArchived] = useState(false)

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalReports, setTotalReports] = useState(0)
  const pageSize = 5 // Reports per page

  // Bulk selection state
  const [selectedReports, setSelectedReports] = useState<Set<string>>(new Set())
  const [isSelectionMode, setIsSelectionMode] = useState(false)
  const [showBulkExportMenu, setShowBulkExportMenu] = useState(false)
  const [isBulkExporting, setIsBulkExporting] = useState(false)
  const [allReportIds, setAllReportIds] = useState<string[]>([])
  const [showSelectAllModal, setShowSelectAllModal] = useState(false)

  // Project assignment state
  const [showProjectModal, setShowProjectModal] = useState(false)
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoadingProjects, setIsLoadingProjects] = useState(false)
  const [isAssigning, setIsAssigning] = useState(false)
  const [assignmentSuccess, setAssignmentSuccess] = useState('')

  // Bulk delete state
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [deleteSuccess, setDeleteSuccess] = useState('')

  // Tag management state
  const [allTags, setAllTags] = useState<Tag[]>([])
  const [reportTags, setReportTags] = useState<Record<string, Tag[]>>({})
  const [showTagModal, setShowTagModal] = useState(false)
  const [selectedReportForTags, setSelectedReportForTags] = useState<string | null>(null)
  const [isLoadingTags, setIsLoadingTags] = useState(false)

  useEffect(() => {
    fetchReports()
    fetchAllTags()
  }, [filterType, filterTag, filterStatus, currentPage, showFavoritesOnly, showArchived])

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
      params.append('page', currentPage.toString())
      params.append('limit', pageSize.toString())
      if (filterType) params.append('type', filterType)
      if (searchQuery) params.append('search', searchQuery)
      if (filterTag) params.append('tag_id', filterTag)
      if (filterStatus) params.append('status', filterStatus)
      if (showFavoritesOnly) params.append('favorites_only', 'true')
      if (showArchived) params.append('archived', 'true')

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
      setReports(data.items)
      setTotalPages(data.pages)
      setTotalReports(data.total)
    } catch (err) {
      setError('Nie udało się załadować raportów')
    } finally {
      setIsLoading(false)
    }
  }

  // Fetch all report IDs for "select all across pages"
  const fetchAllReportIds = async () => {
    const token = getStoredToken()
    if (!token) return

    try {
      const params = new URLSearchParams()
      if (filterType) params.append('type', filterType)
      if (searchQuery) params.append('search', searchQuery)
      if (filterTag) params.append('tag_id', filterTag)
      if (showFavoritesOnly) params.append('favorites_only', 'true')

      const response = await fetch(
        `${API_BASE_URL}/reports/ids?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        const data: AllIdsResponse = await response.json()
        setAllReportIds(data.ids)
      }
    } catch (err) {
      console.error('Failed to fetch all report IDs:', err)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setCurrentPage(1)
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

  // Selection functions
  const toggleReportSelection = (reportId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setSelectedReports(prev => {
      const newSet = new Set(prev)
      if (newSet.has(reportId)) {
        newSet.delete(reportId)
      } else {
        newSet.add(reportId)
      }
      return newSet
    })
  }

  // Check if all items on current page are selected
  const allOnPageSelected = reports.length > 0 && reports.every(r => selectedReports.has(r.id))

  // Check if all items across all pages are selected
  const allAcrossPagesSelected = allReportIds.length > 0 && selectedReports.size === allReportIds.length

  const selectAllOnPage = () => {
    if (allOnPageSelected) {
      // Deselect all on current page
      const newSet = new Set(selectedReports)
      reports.forEach(r => newSet.delete(r.id))
      setSelectedReports(newSet)
    } else {
      // Select all on current page
      const newSet = new Set(selectedReports)
      reports.forEach(r => newSet.add(r.id))
      setSelectedReports(newSet)

      // Show option to select all across pages if there are more pages
      if (totalPages > 1 && !allAcrossPagesSelected) {
        fetchAllReportIds()
        setShowSelectAllModal(true)
      }
    }
  }

  const selectAllAcrossPages = async () => {
    if (allReportIds.length === 0) {
      await fetchAllReportIds()
    }
    setSelectedReports(new Set(allReportIds))
    setShowSelectAllModal(false)
  }

  const clearSelection = () => {
    setSelectedReports(new Set())
    setShowSelectAllModal(false)
  }

  const exitSelectionMode = () => {
    setIsSelectionMode(false)
    setSelectedReports(new Set())
    setShowBulkExportMenu(false)
    setShowProjectModal(false)
    setShowSelectAllModal(false)
    setAllReportIds([])
  }

  // Fetch projects for assignment modal
  const fetchProjects = async () => {
    const token = getStoredToken()
    if (!token) return

    setIsLoadingProjects(true)
    try {
      const response = await fetch(`${API_BASE_URL}/projects/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setProjects(data.items || [])
      }
    } catch (err) {
      console.error('Failed to fetch projects:', err)
    } finally {
      setIsLoadingProjects(false)
    }
  }

  // Open project assignment modal
  const openProjectAssignment = () => {
    setShowProjectModal(true)
    fetchProjects()
  }

  // Assign selected reports to a project
  const handleAssignToProject = async (projectId: string) => {
    const token = getStoredToken()
    if (!token || selectedReports.size === 0) return

    setIsAssigning(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE_URL}/projects/bulk-assign`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          report_ids: Array.from(selectedReports),
          project_id: projectId
        }),
      })

      if (!response.ok) {
        throw new Error('Assignment failed')
      }

      const data = await response.json()
      setAssignmentSuccess(data.message || `Przypisano ${selectedReports.size} raportów do projektu`)

      // Clear selection after successful assignment
      setTimeout(() => {
        exitSelectionMode()
        setAssignmentSuccess('')
      }, 2000)
    } catch (err) {
      setError('Nie udało się przypisać raportów do projektu')
    } finally {
      setIsAssigning(false)
    }
  }

  // Bulk delete function
  const handleBulkDelete = async () => {
    const token = getStoredToken()
    if (!token || selectedReports.size === 0) return

    setIsDeleting(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE_URL}/reports/bulk-delete/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          report_ids: Array.from(selectedReports)
        }),
      })

      if (!response.ok) {
        throw new Error('Delete failed')
      }

      const data = await response.json()
      setDeleteSuccess(data.message || `Usunięto ${selectedReports.size} raportów`)

      // Close confirm modal and refresh reports
      setShowDeleteConfirm(false)

      // Remove deleted reports from local state
      setReports(prev => prev.filter(r => !selectedReports.has(r.id)))

      // Clear selection after successful delete
      setTimeout(() => {
        exitSelectionMode()
        setDeleteSuccess('')
      }, 2000)
    } catch (err) {
      setError('Nie udało się usunąć raportów')
      setShowDeleteConfirm(false)
    } finally {
      setIsDeleting(false)
    }
  }

  // Bulk export function
  const handleBulkExport = async (format: 'xlsx' | 'pdf' | 'docx') => {
    const token = getStoredToken()
    if (!token || selectedReports.size === 0) return

    setIsBulkExporting(true)
    setShowBulkExportMenu(false)

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/bulk-export`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            report_ids: Array.from(selectedReports),
            format
          }),
        }
      )

      if (!response.ok) {
        throw new Error('Bulk export failed')
      }

      // Check if response is a file download
      const contentType = response.headers.get('content-type')

      if (contentType?.includes('application/zip') || contentType?.includes('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) {
        const blob = await response.blob()
        const contentDisposition = response.headers.get('content-disposition')
        let filename = `reports_export_${Date.now()}.${format === 'xlsx' ? 'xlsx' : 'zip'}`

        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="?([^";\n]+)"?/)
          if (filenameMatch) {
            filename = filenameMatch[1]
          }
        }

        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)

        // Success - exit selection mode
        exitSelectionMode()
      } else {
        const data = await response.json()
        if (data.message) {
          setError(data.message)
        }
      }
    } catch (err) {
      console.error('Bulk export failed:', err)
      setError('Nie udało się wyeksportować raportów')
    } finally {
      setIsBulkExporting(false)
    }
  }

  // Fetch all available tags
  const fetchAllTags = async () => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/tags/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const tags = await response.json()
        setAllTags(tags)
      }
    } catch (err) {
      console.error('Failed to fetch tags:', err)
    }
  }

  // Fetch tags for a specific report
  const fetchReportTags = async (reportId: string) => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/tags/reports/${reportId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const tags = await response.json()
        setReportTags(prev => ({ ...prev, [reportId]: tags }))
      }
    } catch (err) {
      console.error('Failed to fetch report tags:', err)
    }
  }

  // Load tags for all visible reports
  useEffect(() => {
    reports.forEach(report => {
      if (!reportTags[report.id]) {
        fetchReportTags(report.id)
      }
    })
  }, [reports])

  // Open tag assignment modal
  const openTagModal = (reportId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setSelectedReportForTags(reportId)
    setShowTagModal(true)
  }

  // Toggle tag assignment for a report
  const toggleTagForReport = async (reportId: string, tagId: string) => {
    const token = getStoredToken()
    if (!token) return

    setIsLoadingTags(true)
    const currentTags = reportTags[reportId] || []
    const hasTag = currentTags.some(t => t.id === tagId)

    try {
      if (hasTag) {
        // Remove tag
        const response = await fetch(`${API_BASE_URL}/tags/reports/${reportId}/tags/${tagId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        })
        if (response.ok) {
          setReportTags(prev => ({
            ...prev,
            [reportId]: currentTags.filter(t => t.id !== tagId)
          }))
        }
      } else {
        // Add tag
        const response = await fetch(`${API_BASE_URL}/tags/reports/${reportId}/add?tag_id=${tagId}`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        })
        if (response.ok) {
          const newTag = allTags.find(t => t.id === tagId)
          if (newTag) {
            setReportTags(prev => ({
              ...prev,
              [reportId]: [...currentTags, newTag]
            }))
          }
        }
      }
    } catch (err) {
      console.error('Failed to toggle tag:', err)
      setError('Nie udało się zaktualizować tagów')
    } finally {
      setIsLoadingTags(false)
    }
  }

  // Toggle favorite status for a report
  const toggleFavorite = async (reportId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    const token = getStoredToken()
    if (!token) return

    const report = reports.find(r => r.id === reportId)
    if (!report) return

    const isFavorite = report.is_favorite
    const csrfToken = await getCsrfToken()

    try {
      const method = isFavorite ? 'DELETE' : 'POST'
      const headers: HeadersInit = {
        'Authorization': `Bearer ${token}`,
      }

      if (csrfToken) {
        headers['X-CSRF-Token'] = csrfToken
      }

      const response = await fetch(`${API_BASE_URL}/reports/${reportId}/favorite`, {
        method,
        headers,
      })

      if (response.ok) {
        // Update the report in local state
        setReports(prev => prev.map(r =>
          r.id === reportId ? { ...r, is_favorite: !isFavorite } : r
        ))
      }
    } catch (err) {
      console.error('Failed to toggle favorite:', err)
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
            <h1 className="text-xl font-semibold text-gray-900">Raporty</h1>
          </div>
          <nav className="flex items-center gap-4">
            {/* Context-sensitive help button */}
            <Link
              href="/help?context=reports"
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-gray-600 hover:bg-gray-100"
              title="Pomoc dot. raportow"
            >
              <span className="text-lg">❓</span>
              <span className="hidden sm:inline">Pomoc</span>
            </Link>

            {/* Selection mode toggle */}
            <button
              onClick={() => isSelectionMode ? exitSelectionMode() : setIsSelectionMode(true)}
              className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm ${
                isSelectionMode
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              {isSelectionMode ? 'Anuluj zaznaczanie' : 'Wybierz'}
            </button>

            {/* Bulk action buttons - only visible when reports are selected */}
            {selectedReports.size > 0 && (
              <>
                {/* Delete button */}
                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700"
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  Usuń ({selectedReports.size})
                </button>

                {/* Assign to project button */}
                <button
                  onClick={openProjectAssignment}
                  className="flex items-center gap-2 rounded-lg bg-purple-600 px-4 py-2 text-sm text-white hover:bg-purple-700"
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                  Przypisz do projektu ({selectedReports.size})
                </button>

                {/* Bulk export button */}
                <div className="relative">
                  <button
                    onClick={() => setShowBulkExportMenu(!showBulkExportMenu)}
                    disabled={isBulkExporting}
                    className="flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700 disabled:opacity-50"
                  >
                  {isBulkExporting ? (
                    <>
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                      Eksportowanie...
                    </>
                  ) : (
                    <>
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      Eksportuj ({selectedReports.size})
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </>
                  )}
                </button>

                {/* Bulk export dropdown menu */}
                {showBulkExportMenu && (
                  <div className="absolute right-0 mt-2 w-56 rounded-lg bg-white shadow-lg ring-1 ring-black ring-opacity-5 z-50">
                    <div className="py-1">
                      <button
                        onClick={() => handleBulkExport('xlsx')}
                        className="flex w-full items-center gap-3 px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50"
                      >
                        <div className="flex h-8 w-8 items-center justify-center rounded bg-green-100">
                          <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                        <div>
                          <div className="font-medium">Excel (.xlsx)</div>
                          <div className="text-xs text-gray-500">Wszystkie w jednym pliku</div>
                        </div>
                      </button>
                      <button
                        onClick={() => handleBulkExport('pdf')}
                        className="flex w-full items-center gap-3 px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50"
                      >
                        <div className="flex h-8 w-8 items-center justify-center rounded bg-red-100">
                          <svg className="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <div>
                          <div className="font-medium">PDF (archiwum ZIP)</div>
                          <div className="text-xs text-gray-500">Osobne pliki w ZIP</div>
                        </div>
                      </button>
                    </div>
                  </div>
                )}
                </div>
              </>
            )}

            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">Dashboard</Link>
            <Link href="/search" className="text-gray-600 hover:text-gray-900">PKD Search</Link>
          </nav>
        </div>
      </header>

      {/* Selection mode banner */}
      {isSelectionMode && (
        <div className="bg-blue-50 border-b border-blue-200 px-4 py-3">
          <div className="mx-auto max-w-6xl flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Select all checkbox */}
              <button
                onClick={selectAllOnPage}
                className="flex items-center gap-2 cursor-pointer"
                type="button"
              >
                <div
                  className={`h-5 w-5 rounded border-2 flex items-center justify-center transition-colors ${
                    allOnPageSelected
                      ? 'bg-blue-600 border-blue-600'
                      : allAcrossPagesSelected
                        ? 'bg-blue-600 border-blue-600'
                        : selectedReports.size > 0
                          ? 'bg-blue-200 border-blue-400'
                          : 'bg-white border-gray-300 hover:border-blue-400'
                  }`}
                >
                  {(allOnPageSelected || allAcrossPagesSelected) && (
                    <svg className="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                  {!allOnPageSelected && !allAcrossPagesSelected && selectedReports.size > 0 && (
                    <div className="h-2 w-2 bg-blue-600 rounded-sm"></div>
                  )}
                </div>
                <span className="text-sm text-blue-700">
                  {allAcrossPagesSelected ? 'Zaznaczono wszystkie' : allOnPageSelected ? 'Zaznaczono stronę' : 'Zaznacz wszystkie'}
                </span>
              </button>
              <span className="text-sm text-blue-600 font-medium">
                {selectedReports.size} z {totalReports} wybranych
              </span>
              {/* Select all across pages notification */}
              {showSelectAllModal && totalPages > 1 && !allAcrossPagesSelected && (
                <div className="flex items-center gap-2 ml-2 px-3 py-1 bg-yellow-100 rounded-lg border border-yellow-300">
                  <span className="text-sm text-yellow-800">
                    Zaznaczono wszystkie {reports.length} na tej stronie.
                  </span>
                  <button
                    onClick={selectAllAcrossPages}
                    className="text-sm font-medium text-blue-700 hover:text-blue-900 underline"
                  >
                    Zaznacz wszystkie {totalReports} raportów
                  </button>
                </div>
              )}
            </div>
            <div className="flex items-center gap-3">
              {selectedReports.size > 0 && (
                <button
                  onClick={clearSelection}
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  Wyczyść zaznaczenie
                </button>
              )}
              <button
                onClick={exitSelectionMode}
                className="text-sm text-blue-700 hover:text-blue-900"
              >
                Anuluj
              </button>
            </div>
          </div>
        </div>
      )}

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
            <button
              type="button"
              onClick={() => {
                setShowFavoritesOnly(!showFavoritesOnly)
                setCurrentPage(1)
              }}
              className={`flex items-center gap-2 rounded-lg px-4 py-2 font-medium transition-colors ${
                showFavoritesOnly
                  ? 'bg-yellow-100 text-yellow-800 border-2 border-yellow-500'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
              title="Pokaż tylko ulubione"
            >
              <svg
                className={`h-5 w-5 ${showFavoritesOnly ? 'fill-yellow-500' : 'fill-none stroke-current'}`}
                viewBox="0 0 24 24"
                strokeWidth={1.5}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
              </svg>
              <span className="hidden sm:inline">Ulubione</span>
            </button>
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
            <select
              value={filterTag}
              onChange={(e) => {
                setFilterTag(e.target.value)
                setCurrentPage(1)
              }}
              className="rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Wszystkie tagi</option>
              {allTags.map((tag) => (
                <option key={tag.id} value={tag.id}>
                  {tag.name}
                </option>
              ))}
            </select>
            <button
              type="submit"
              className="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700"
            >
              Szukaj
            </button>
          </form>
        </div>

        {/* Quick Status Filters */}
        <div className="mb-6 flex gap-3">
          <button
            onClick={() => {
              setFilterStatus('')
              setShowArchived(false)
              setCurrentPage(1)
            }}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              filterStatus === '' && !showArchived
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            📊 Wszystkie
          </button>
          <button
            onClick={() => {
              setFilterStatus('draft')
              setShowArchived(false)
              setCurrentPage(1)
            }}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              filterStatus === 'draft' && !showArchived
                ? 'bg-yellow-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            📝 Szkice
          </button>
          <button
            onClick={() => {
              setFilterStatus('in_progress')
              setShowArchived(false)
              setCurrentPage(1)
            }}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              filterStatus === 'in_progress' && !showArchived
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            ⏳ W trakcie
          </button>
          <button
            onClick={() => {
              setFilterStatus('completed')
              setShowArchived(false)
              setCurrentPage(1)
            }}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              filterStatus === 'completed' && !showArchived
                ? 'bg-green-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            ✅ Zakończone
          </button>
          <button
            onClick={() => {
              setShowArchived(!showArchived)
              setCurrentPage(1)
            }}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              showArchived
                ? 'bg-gray-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            📦 Archiwum
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 rounded-lg bg-red-50 px-4 py-3">
            <div className="flex items-center justify-between">
              <span className="text-red-700">{error}</span>
              <Link
                href={`/feedback?type=bug&error=${encodeURIComponent(error)}&page=${encodeURIComponent('/reports')}`}
                className="text-sm text-red-600 hover:text-red-800 underline"
              >
                Zgłoś problem
              </Link>
            </div>
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
              const isSelected = selectedReports.has(report.id)
              return (
                <div
                  key={report.id}
                  className={`relative rounded-xl bg-white p-6 shadow-sm transition-all ${
                    isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:shadow-md'
                  } ${isSelectionMode ? 'cursor-pointer' : ''}`}
                  onClick={(e) => isSelectionMode ? toggleReportSelection(report.id, e) : undefined}
                >
                  {/* Checkbox - visible in selection mode */}
                  {isSelectionMode && (
                    <div className="absolute left-4 top-1/2 -translate-y-1/2">
                      <div
                        className={`h-6 w-6 rounded border-2 flex items-center justify-center ${
                          isSelected
                            ? 'bg-blue-600 border-blue-600'
                            : 'bg-white border-gray-300 hover:border-blue-400'
                        }`}
                      >
                        {isSelected && (
                          <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                      </div>
                    </div>
                  )}

                  <Link
                    href={`/reports/${report.id}`}
                    className={`block ${isSelectionMode ? 'pl-10 pointer-events-none' : ''}`}
                    onClick={(e) => isSelectionMode && e.preventDefault()}
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

                        {/* Tags Display */}
                        <div className="mt-3 flex items-center gap-2 flex-wrap">
                          {reportTags[report.id]?.map(tag => (
                            <span
                              key={tag.id}
                              className="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium text-white"
                              style={{ backgroundColor: tag.color }}
                            >
                              <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M17.707 9.293a1 1 0 010 1.414l-7 7a1 1 0 01-1.414 0l-7-7A.997.997 0 012 10V5a3 3 0 013-3h5c.256 0 .512.098.707.293l7 7zM5 6a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                              </svg>
                              {tag.name}
                            </span>
                          ))}
                          {!isSelectionMode && (
                            <button
                              onClick={(e) => openTagModal(report.id, e)}
                              className="inline-flex items-center gap-1 rounded-full border-2 border-dashed border-gray-300 px-2.5 py-0.5 text-xs font-medium text-gray-600 hover:border-gray-400 hover:text-gray-900 transition-colors"
                            >
                              <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                              </svg>
                              Dodaj tag
                            </button>
                          )}
                        </div>
                      </div>
                      <div className="flex flex-col items-end ml-4 gap-2">
                        <div className="flex items-center gap-2">
                          {/* Favorite star button */}
                          {!isSelectionMode && (
                            <button
                              onClick={(e) => toggleFavorite(report.id, e)}
                              className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
                              title={report.is_favorite ? 'Usuń z ulubionych' : 'Dodaj do ulubionych'}
                            >
                              <svg
                                className={`h-5 w-5 ${report.is_favorite ? 'fill-yellow-400 stroke-yellow-500' : 'fill-none stroke-gray-400'}`}
                                viewBox="0 0 24 24"
                                strokeWidth={1.5}
                              >
                                <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                              </svg>
                            </button>
                          )}
                          <span className={`inline-block rounded-full px-2 py-1 text-xs font-medium ${
                            report.status === 'completed' ? 'bg-green-100 text-green-800' :
                            report.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {report.status === 'completed' ? 'Zakończony' :
                             report.status === 'in_progress' ? 'W trakcie' :
                             'Szkic'}
                          </span>
                        </div>
                        <p className="text-xs text-gray-400">{formatDate(report.created_at)}</p>
                      </div>
                    </div>
                  </Link>
                </div>
              )
            })}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-8 flex items-center justify-center gap-2">
                {/* Previous button */}
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="flex items-center gap-1 rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Poprzednia
                </button>

                {/* Page numbers */}
                <div className="flex items-center gap-1">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                    <button
                      key={page}
                      onClick={() => setCurrentPage(page)}
                      className={`h-10 w-10 rounded-lg text-sm font-medium transition-colors ${
                        page === currentPage
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      {page}
                    </button>
                  ))}
                </div>

                {/* Next button */}
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="flex items-center gap-1 rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Następna
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            )}

            {/* Page info */}
            {totalReports > 0 && (
              <div className="mt-4 text-center text-sm text-gray-500">
                Pokazano {((currentPage - 1) * pageSize) + 1}-{Math.min(currentPage * pageSize, totalReports)} z {totalReports} raportów
              </div>
            )}
          </div>
        )}
      </main>

      {/* Success message toast */}
      {assignmentSuccess && (
        <div className="fixed bottom-4 right-4 rounded-lg bg-green-500 px-6 py-3 text-white shadow-lg z-50">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            {assignmentSuccess}
          </div>
        </div>
      )}

      {/* Delete success toast */}
      {deleteSuccess && (
        <div className="fixed bottom-4 right-4 rounded-lg bg-green-500 px-6 py-3 text-white shadow-lg z-50">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            {deleteSuccess}
          </div>
        </div>
      )}

      {/* Delete confirmation modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="w-full max-w-md rounded-xl bg-white shadow-xl">
            <div className="p-6">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </div>
              <h2 className="mb-2 text-center text-lg font-semibold text-gray-900">
                Potwierdź usunięcie
              </h2>
              <p className="mb-6 text-center text-gray-600">
                Czy na pewno chcesz usunąć <span className="font-semibold text-red-600">{selectedReports.size}</span> {selectedReports.size === 1 ? 'raport' : selectedReports.size < 5 ? 'raporty' : 'raportów'}?
                <br />
                <span className="text-sm text-gray-500">Ta operacja jest nieodwracalna.</span>
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  disabled={isDeleting}
                  className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  Anuluj
                </button>
                <button
                  onClick={handleBulkDelete}
                  disabled={isDeleting}
                  className="flex-1 rounded-lg bg-red-600 px-4 py-2 text-white hover:bg-red-700 disabled:opacity-50"
                >
                  {isDeleting ? (
                    <span className="flex items-center justify-center gap-2">
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                      Usuwanie...
                    </span>
                  ) : (
                    `Usuń ${selectedReports.size} ${selectedReports.size === 1 ? 'raport' : selectedReports.size < 5 ? 'raporty' : 'raportów'}`
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Project assignment modal */}
      {showProjectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="w-full max-w-md rounded-xl bg-white shadow-xl">
            <div className="border-b px-6 py-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Przypisz do projektu</h2>
                <button
                  onClick={() => setShowProjectModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                Wybierz projekt, do którego chcesz przypisać {selectedReports.size} raportów
              </p>
            </div>

            <div className="max-h-96 overflow-y-auto p-4">
              {isLoadingProjects ? (
                <div className="flex items-center justify-center py-8">
                  <div className="h-6 w-6 animate-spin rounded-full border-2 border-purple-600 border-t-transparent"></div>
                  <span className="ml-2 text-gray-600">Ładowanie projektów...</span>
                </div>
              ) : projects.length === 0 ? (
                <div className="py-8 text-center text-gray-500">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                  <p className="mt-2">Brak dostępnych projektów</p>
                  <Link
                    href="/projects"
                    className="mt-4 inline-block text-purple-600 hover:text-purple-700"
                  >
                    Utwórz pierwszy projekt →
                  </Link>
                </div>
              ) : (
                <div className="space-y-2">
                  {projects.map((project) => (
                    <button
                      key={project.id}
                      onClick={() => handleAssignToProject(project.id)}
                      disabled={isAssigning}
                      className="w-full rounded-lg border border-gray-200 p-4 text-left hover:border-purple-300 hover:bg-purple-50 disabled:opacity-50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-medium text-gray-900">{project.name}</h3>
                          {project.description && (
                            <p className="mt-1 text-sm text-gray-500 line-clamp-2">{project.description}</p>
                          )}
                          <div className="mt-2 flex items-center gap-2">
                            <span className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                              {project.type === 'due_diligence' ? 'Due Diligence' :
                               project.type === 'market_analysis' ? 'Analiza rynku' :
                               project.type === 'competitive' ? 'Konkurencja' : 'Badania'}
                            </span>
                            <span className="text-xs text-gray-400">
                              {project.report_ids?.length || 0} raportów
                            </span>
                          </div>
                        </div>
                        <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="border-t px-6 py-4">
              <button
                onClick={() => setShowProjectModal(false)}
                className="w-full rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
              >
                Anuluj
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tag Assignment Modal */}
      {showTagModal && selectedReportForTags && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
          <div className="w-full max-w-md rounded-xl bg-white shadow-xl">
            <div className="border-b px-6 py-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Zarządzaj tagami</h2>
                <button
                  onClick={() => setShowTagModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div className="px-6 py-4 max-h-96 overflow-y-auto">
              {allTags.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-500 mb-4">Nie masz jeszcze żadnych tagów</p>
                  <Link
                    href="/settings/tags"
                    className="inline-block rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
                  >
                    Utwórz pierwszy tag
                  </Link>
                </div>
              ) : (
                <div className="space-y-2">
                  {allTags.map(tag => {
                    const isAssigned = reportTags[selectedReportForTags]?.some(t => t.id === tag.id)
                    return (
                      <button
                        key={tag.id}
                        onClick={() => toggleTagForReport(selectedReportForTags, tag.id)}
                        disabled={isLoadingTags}
                        className={`w-full flex items-center gap-3 rounded-lg border-2 p-3 text-left transition-all ${
                          isAssigned
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                        } ${isLoadingTags ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        <div
                          className="h-6 w-6 rounded border-2 flex items-center justify-center flex-shrink-0"
                          style={{
                            backgroundColor: isAssigned ? tag.color : 'transparent',
                            borderColor: tag.color
                          }}
                        >
                          {isAssigned && (
                            <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </div>
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">{tag.name}</div>
                          {tag.description && (
                            <div className="text-sm text-gray-500 line-clamp-1">{tag.description}</div>
                          )}
                        </div>
                      </button>
                    )
                  })}
                </div>
              )}
            </div>

            <div className="border-t px-6 py-4">
              <button
                onClick={() => setShowTagModal(false)}
                className="w-full rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
              >
                Zamknij
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
