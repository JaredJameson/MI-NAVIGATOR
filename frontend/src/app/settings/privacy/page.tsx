'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export default function PrivacySettingsPage() {
  const router = useRouter()
  const [isExporting, setIsExporting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Account deletion state
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deletePassword, setDeletePassword] = useState('')
  const [deleteConfirmation, setDeleteConfirmation] = useState('')
  const [isDeleting, setIsDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')

  const getCsrfToken = async (): Promise<string> => {
    const response = await fetch(`${API_BASE_URL}/auth/csrf-token`)
    const data = await response.json()
    return data.csrf_token
  }

  const handleExportData = async () => {
    const token = getStoredToken()
    if (!token) {
      setError('Not authenticated')
      return
    }

    setIsExporting(true)
    setError('')
    setSuccess('')

    try {
      const csrfToken = await getCsrfToken()

      const response = await fetch(`${API_BASE_URL}/users/me/export-data`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-CSRF-Token': csrfToken,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to export data')
      }

      // Get filename from Content-Disposition header
      const contentDisposition = response.headers.get('Content-Disposition')
      let filename = 'user_data_export.json'
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }

      // Download the file
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      setSuccess('Data exported successfully!')
    } catch (err) {
      console.error('Failed to export data:', err)
      setError('Failed to export data. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  const handleDeleteAccount = async () => {
    const token = getStoredToken()
    if (!token) {
      setDeleteError('Not authenticated')
      return
    }

    // Validate inputs
    if (!deletePassword) {
      setDeleteError('Please enter your password')
      return
    }

    if (deleteConfirmation !== 'DELETE') {
      setDeleteError('Please type DELETE to confirm')
      return
    }

    setIsDeleting(true)
    setDeleteError('')

    try {
      const csrfToken = await getCsrfToken()

      const response = await fetch(`${API_BASE_URL}/users/me`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-CSRF-Token': csrfToken,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          password: deletePassword,
          confirmation_text: deleteConfirmation,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to delete account')
      }

      // Account deleted successfully - clear token and redirect to login
      localStorage.removeItem('mi_navigator_token')
      router.push('/auth/login?deleted=true')
    } catch (err: any) {
      console.error('Failed to delete account:', err)
      setDeleteError(err.message || 'Failed to delete account. Please try again.')
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link
                href="/settings"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Privacy Settings</h1>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Success/Error Messages */}
        {error && (
          <div className="mb-6 rounded-lg bg-red-50 border border-red-200 p-4">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-red-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="ml-3 text-sm text-red-800">{error}</p>
            </div>
          </div>
        )}

        {success && (
          <div className="mb-6 rounded-lg bg-green-50 border border-green-200 p-4">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <p className="ml-3 text-sm text-green-800">{success}</p>
            </div>
          </div>
        )}

        {/* Data Export Section */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                </svg>
              </div>
            </div>
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                Export Your Data
              </h2>
              <p className="text-sm text-gray-600 mb-4">
                Download a copy of all your personal data stored in MI-Navigator. This includes your profile information, preferences, activity logs, and more. This export is provided in compliance with GDPR regulations.
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <h3 className="text-sm font-medium text-blue-900 mb-2">What's included in the export:</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>User profile (email, name, role, industry)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Preferences (language, format, depth)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Security settings (2FA status, account status)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Activity log (all actions performed in the system)</span>
                  </li>
                </ul>
              </div>
              <button
                onClick={handleExportData}
                disabled={isExporting}
                className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors"
              >
                {isExporting ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Exporting...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                    </svg>
                    Download My Data
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Data Retention Info */}
        <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                Data Retention
              </h2>
              <p className="text-sm text-gray-600">
                We retain your personal data as long as your account is active. If you wish to delete your account and all associated data, use the "Delete Account" option below. Account deletion is permanent and cannot be undone.
              </p>
            </div>
          </div>
        </div>

        {/* Account Deletion Section */}
        <div className="mt-6 bg-white rounded-xl shadow-sm border border-red-200 p-6">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
            </div>
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-red-900 mb-2">
                Delete Account
              </h2>
              <p className="text-sm text-gray-600 mb-4">
                Permanently delete your account and all associated data. This action cannot be undone. All your reports, projects, and settings will be permanently removed.
              </p>
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <h3 className="text-sm font-medium text-red-900 mb-2">⚠️ Warning: This will delete:</h3>
                <ul className="text-sm text-red-800 space-y-1">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Your user account and profile</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>All audit logs and activity history</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>All saved report templates</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>All preferences and settings</span>
                  </li>
                </ul>
              </div>
              <button
                onClick={() => setShowDeleteModal(true)}
                className="inline-flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete My Account
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Delete Account Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 p-6">
            <div className="flex items-start space-x-4 mb-6">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-gray-900">Confirm Account Deletion</h3>
                <p className="text-sm text-gray-600 mt-1">
                  This action is permanent and cannot be undone.
                </p>
              </div>
            </div>

            {deleteError && (
              <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-3">
                <p className="text-sm text-red-800">{deleteError}</p>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Enter your password to confirm
                </label>
                <input
                  type="password"
                  value={deletePassword}
                  onChange={(e) => setDeletePassword(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  placeholder="Your password"
                  disabled={isDeleting}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Type <span className="font-bold text-red-600">DELETE</span> to confirm
                </label>
                <input
                  type="text"
                  value={deleteConfirmation}
                  onChange={(e) => setDeleteConfirmation(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  placeholder="DELETE"
                  disabled={isDeleting}
                />
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowDeleteModal(false)
                  setDeletePassword('')
                  setDeleteConfirmation('')
                  setDeleteError('')
                }}
                disabled={isDeleting}
                className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 disabled:bg-gray-100 text-gray-800 rounded-lg font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteAccount}
                disabled={isDeleting || !deletePassword || deleteConfirmation !== 'DELETE'}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors"
              >
                {isDeleting ? (
                  <>
                    <svg className="animate-spin inline-block -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Deleting...
                  </>
                ) : (
                  'Delete My Account'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
