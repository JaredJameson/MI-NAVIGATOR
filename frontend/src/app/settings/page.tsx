'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken, authApi } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface UserProfile {
  id: string
  email: string
  name: string | null
  industry: string | null
  industry_segment: string | null
  user_role: string | null
  preferred_language: string
  preferred_depth: string
  preferred_format: string
  onboarding_completed: boolean
}

interface CustomFieldDefinition {
  id: string
  name: string
  field_type: string
  description: string | null
  is_required: boolean
  is_active: boolean
  options: string[] | null
  display_order: number
  created_at: string
  updated_at: string
}

const INDUSTRIES = [
  { value: 'manufacturing', label: 'Manufacturing' },
  { value: 'services', label: 'Services' },
  { value: 'technology', label: 'Technology' },
  { value: 'retail', label: 'Retail' },
  { value: 'finance', label: 'Finance' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'logistics', label: 'Logistics' },
  { value: 'other', label: 'Other' },
]

const USER_ROLES = [
  { value: 'ceo', label: 'CEO / Executive' },
  { value: 'sales', label: 'Sales' },
  { value: 'analyst', label: 'Analyst' },
  { value: 'bd', label: 'Business Development' },
  { value: 'operations', label: 'Operations' },
  { value: 'other', label: 'Other' },
]

const LANGUAGES = [
  { value: 'pl', label: 'Polski' },
  { value: 'en', label: 'English' },
]

const DEPTHS = [
  { value: 'quick', label: 'Quick (Basic overview)' },
  { value: 'standard', label: 'Standard (Detailed analysis)' },
  { value: 'deep', label: 'Deep (Comprehensive research)' },
]

const FORMATS = [
  { value: 'pdf', label: 'PDF' },
  { value: 'docx', label: 'Word (DOCX)' },
  { value: 'pptx', label: 'PowerPoint (PPTX)' },
]

const FIELD_TYPES = [
  { value: 'text', label: 'Text' },
  { value: 'number', label: 'Number' },
  { value: 'date', label: 'Date' },
  { value: 'email', label: 'Email' },
  { value: 'url', label: 'URL' },
  { value: 'select', label: 'Select (dropdown)' },
  { value: 'multiselect', label: 'Multi-select' },
]

export default function SettingsPage() {
  const router = useRouter()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Form fields
  const [name, setName] = useState('')
  const [industry, setIndustry] = useState('')
  const [userRole, setUserRole] = useState('')
  const [language, setLanguage] = useState('pl')
  const [depth, setDepth] = useState('standard')
  const [format, setFormat] = useState('pdf')

  // Notification preferences
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [inAppNotifications, setInAppNotifications] = useState(true)

  // Custom Fields state
  const [customFields, setCustomFields] = useState<CustomFieldDefinition[]>([])
  const [isLoadingFields, setIsLoadingFields] = useState(false)
  const [showAddFieldForm, setShowAddFieldForm] = useState(false)
  const [newFieldName, setNewFieldName] = useState('')
  const [newFieldType, setNewFieldType] = useState('text')
  const [newFieldDescription, setNewFieldDescription] = useState('')
  const [newFieldRequired, setNewFieldRequired] = useState(false)
  const [newFieldOptions, setNewFieldOptions] = useState('')
  const [fieldError, setFieldError] = useState('')

  useEffect(() => {
    fetchProfile()
    fetchNotificationPreferences()
    fetchCustomFields()
  }, [])

  const fetchProfile = async () => {
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

    try {
      const response = await fetch(`${API_BASE_URL}/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        if (response.status === 401) {
          // Don't redirect - AuthGuard will handle this
          // Don't show error either - just silently fail and let AuthGuard redirect if needed
          setIsLoading(false)
          return
        }
        throw new Error('Failed to fetch profile')
      }

      const data = await response.json()
      setProfile(data)
      setName(data.name || '')
      setIndustry(data.industry || '')
      setUserRole(data.user_role || '')
      setLanguage(data.preferred_language || 'pl')
      setDepth(data.preferred_depth || 'standard')
      setFormat(data.preferred_format || 'pdf')
    } catch (err) {
      setError('Failed to load profile')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchNotificationPreferences = async () => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/users/me/notifications`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setEmailNotifications(data.email_notifications ?? true)
        setInAppNotifications(data.in_app_notifications ?? true)
      }
    } catch (err) {
      console.error('Failed to fetch notification preferences:', err)
    }
  }

  const fetchCustomFields = async () => {
    const token = getStoredToken()
    if (!token) return

    setIsLoadingFields(true)
    try {
      const response = await fetch(`${API_BASE_URL}/custom-fields/definitions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setCustomFields(data)
      }
    } catch (err) {
      console.error('Failed to fetch custom fields:', err)
    } finally {
      setIsLoadingFields(false)
    }
  }

  const handleAddCustomField = async () => {
    const token = getStoredToken()
    if (!token) return

    setFieldError('')

    // Validation
    if (!newFieldName.trim()) {
      setFieldError('Field name is required')
      return
    }

    if ((newFieldType === 'select' || newFieldType === 'multiselect') && !newFieldOptions.trim()) {
      setFieldError('Options are required for select and multiselect fields')
      return
    }

    try {
      const options = (newFieldType === 'select' || newFieldType === 'multiselect')
        ? newFieldOptions.split(',').map(o => o.trim()).filter(o => o.length > 0)
        : null

      const response = await fetch(`${API_BASE_URL}/custom-fields/definitions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newFieldName.trim(),
          field_type: newFieldType,
          description: newFieldDescription.trim() || null,
          is_required: newFieldRequired,
          options,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to create custom field')
      }

      // Reset form
      setNewFieldName('')
      setNewFieldType('text')
      setNewFieldDescription('')
      setNewFieldRequired(false)
      setNewFieldOptions('')
      setShowAddFieldForm(false)

      // Refresh list
      fetchCustomFields()
      setSuccess('Custom field created successfully!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setFieldError(err instanceof Error ? err.message : 'Failed to create custom field')
    }
  }

  const handleDeleteCustomField = async (fieldId: string) => {
    const token = getStoredToken()
    if (!token) return

    if (!confirm('Are you sure you want to delete this custom field? All associated data will be lost.')) {
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/custom-fields/definitions/${fieldId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to delete custom field')
      }

      fetchCustomFields()
      setSuccess('Custom field deleted successfully!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete custom field')
    }
  }

  const handleSaveProfile = async () => {
    const token = getStoredToken()
    if (!token) return

    setIsSaving(true)
    setError('')
    setSuccess('')

    try {
      // Update profile
      const profileResponse = await fetch(`${API_BASE_URL}/users/me`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          industry,
          user_role: userRole,
        }),
      })

      if (!profileResponse.ok) {
        throw new Error('Failed to update profile')
      }

      // Update preferences
      const prefsResponse = await fetch(`${API_BASE_URL}/users/me/preferences`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          preferred_language: language,
          preferred_depth: depth,
          preferred_format: format,
        }),
      })

      if (!prefsResponse.ok) {
        throw new Error('Failed to update preferences')
      }

      // Update notification preferences
      const notifResponse = await fetch(`${API_BASE_URL}/users/me/notifications`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email_notifications: emailNotifications,
          in_app_notifications: inAppNotifications,
        }),
      })

      if (!notifResponse.ok) {
        throw new Error('Failed to update notification preferences')
      }

      setSuccess('Settings saved successfully!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save settings')
    } finally {
      setIsSaving(false)
    }
  }

  const handleLogout = async () => {
    setIsLoggingOut(true)
    try {
      await authApi.logout()
      router.push('/auth/login')
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      setIsLoggingOut(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
            </div>
            <nav className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                Dashboard
              </Link>
              <Link href="/chat" className="text-gray-600 hover:text-gray-900">
                Chat
              </Link>
              <button
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="rounded-md bg-red-600 px-3 py-1.5 text-sm text-white hover:bg-red-700 disabled:opacity-50"
              >
                {isLoggingOut ? 'Logging out...' : 'Logout'}
              </button>
            </nav>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Success/Error Messages */}
        {success && (
          <div className="mb-6 rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-green-800 flex items-center gap-2">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            {success}
          </div>
        )}

        {error && (
          <div className="mb-6 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-red-800 flex items-center gap-2">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </div>
        )}

        {/* Profile Section */}
        <section className="mb-8 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-6 text-lg font-semibold text-gray-900">Profile Information</h2>

          <div className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                type="email"
                id="email"
                value={profile?.email || ''}
                disabled
                className="mt-1 block w-full rounded-lg border border-gray-300 bg-gray-100 px-4 py-2 text-gray-500"
              />
              <p className="mt-1 text-xs text-gray-500">Email cannot be changed</p>
            </div>

            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Display Name
              </label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                className="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div className="grid gap-6 sm:grid-cols-2">
              <div>
                <label htmlFor="industry" className="block text-sm font-medium text-gray-700">
                  Industry
                </label>
                <select
                  id="industry"
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                  className="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">Select industry...</option>
                  {INDUSTRIES.map((ind) => (
                    <option key={ind.value} value={ind.value}>
                      {ind.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="userRole" className="block text-sm font-medium text-gray-700">
                  Role
                </label>
                <select
                  id="userRole"
                  value={userRole}
                  onChange={(e) => setUserRole(e.target.value)}
                  className="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">Select role...</option>
                  {USER_ROLES.map((role) => (
                    <option key={role.value} value={role.value}>
                      {role.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </section>

        {/* Preferences Section */}
        <section className="mb-8 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-6 text-lg font-semibold text-gray-900">Preferences</h2>

          <div className="space-y-6">
            <div>
              <label htmlFor="language" className="block text-sm font-medium text-gray-700">
                Language
              </label>
              <select
                id="language"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                {LANGUAGES.map((lang) => (
                  <option key={lang.value} value={lang.value}>
                    {lang.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="depth" className="block text-sm font-medium text-gray-700">
                Default Analysis Depth
              </label>
              <select
                id="depth"
                value={depth}
                onChange={(e) => setDepth(e.target.value)}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                {DEPTHS.map((d) => (
                  <option key={d.value} value={d.value}>
                    {d.label}
                  </option>
                ))}
              </select>
              <p className="mt-1 text-xs text-gray-500">
                Controls the detail level of generated reports and analyses
              </p>
            </div>

            <div>
              <label htmlFor="format" className="block text-sm font-medium text-gray-700">
                Default Export Format
              </label>
              <select
                id="format"
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                {FORMATS.map((f) => (
                  <option key={f.value} value={f.value}>
                    {f.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </section>

        {/* Notifications Section */}
        <section className="mb-8 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-6 text-lg font-semibold text-gray-900">Notifications</h2>

          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <label htmlFor="emailNotifications" className="block text-sm font-medium text-gray-900">
                  Email Notifications
                </label>
                <p className="text-sm text-gray-500">
                  Receive email notifications about reports, alerts, and updates
                </p>
              </div>
              <button
                type="button"
                role="switch"
                aria-checked={emailNotifications}
                onClick={() => setEmailNotifications(!emailNotifications)}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                  emailNotifications ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    emailNotifications ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label htmlFor="inAppNotifications" className="block text-sm font-medium text-gray-900">
                  In-App Notifications
                </label>
                <p className="text-sm text-gray-500">
                  Show notifications within the application
                </p>
              </div>
              <button
                type="button"
                role="switch"
                aria-checked={inAppNotifications}
                onClick={() => setInAppNotifications(!inAppNotifications)}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                  inAppNotifications ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    inAppNotifications ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
          </div>
        </section>

        {/* Tags Section */}
        <section className="mb-8 rounded-xl bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Tags</h2>
              <p className="text-sm text-gray-500 mt-1">Organize your reports with custom tags</p>
            </div>
            <Link
              href="/settings/tags"
              className="text-sm bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              Manage Tags
            </Link>
          </div>
        </section>

        {/* Custom Fields Section */}
        <section className="mb-8 rounded-xl bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Custom Fields</h2>
            <button
              onClick={() => setShowAddFieldForm(!showAddFieldForm)}
              className="text-sm bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
            >
              {showAddFieldForm ? 'Cancel' : '+ Add Field'}
            </button>
          </div>

          {/* Add Field Form */}
          {showAddFieldForm && (
            <div className="mb-6 p-4 border border-gray-200 rounded-lg bg-gray-50">
              <h3 className="text-sm font-medium text-gray-900 mb-4">New Custom Field</h3>

              {fieldError && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-800 rounded-lg text-sm">
                  {fieldError}
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <label htmlFor="newFieldName" className="block text-sm font-medium text-gray-700">
                    Field Name *
                  </label>
                  <input
                    type="text"
                    id="newFieldName"
                    value={newFieldName}
                    onChange={(e) => setNewFieldName(e.target.value)}
                    placeholder="e.g., Industry Specialization"
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label htmlFor="newFieldType" className="block text-sm font-medium text-gray-700">
                    Field Type *
                  </label>
                  <select
                    id="newFieldType"
                    value={newFieldType}
                    onChange={(e) => setNewFieldType(e.target.value)}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    {FIELD_TYPES.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="newFieldDescription" className="block text-sm font-medium text-gray-700">
                    Description
                  </label>
                  <textarea
                    id="newFieldDescription"
                    value={newFieldDescription}
                    onChange={(e) => setNewFieldDescription(e.target.value)}
                    placeholder="Optional description"
                    rows={2}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>

                {(newFieldType === 'select' || newFieldType === 'multiselect') && (
                  <div>
                    <label htmlFor="newFieldOptions" className="block text-sm font-medium text-gray-700">
                      Options * (comma-separated)
                    </label>
                    <input
                      type="text"
                      id="newFieldOptions"
                      value={newFieldOptions}
                      onChange={(e) => setNewFieldOptions(e.target.value)}
                      placeholder="e.g., Option 1, Option 2, Option 3"
                      className="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                )}

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="newFieldRequired"
                    checked={newFieldRequired}
                    onChange={(e) => setNewFieldRequired(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="newFieldRequired" className="ml-2 block text-sm text-gray-700">
                    Required field
                  </label>
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    onClick={() => {
                      setShowAddFieldForm(false)
                      setFieldError('')
                      setNewFieldName('')
                      setNewFieldType('text')
                      setNewFieldDescription('')
                      setNewFieldRequired(false)
                      setNewFieldOptions('')
                    }}
                    className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAddCustomField}
                    className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
                  >
                    Create Field
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Custom Fields List */}
          {isLoadingFields ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : customFields.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No custom fields defined yet.</p>
              <p className="text-sm mt-1">Click "Add Field" to create your first custom field.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {customFields.map((field) => (
                <div key={field.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium text-gray-900">{field.name}</h3>
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        {FIELD_TYPES.find(t => t.value === field.field_type)?.label || field.field_type}
                      </span>
                      {field.is_required && (
                        <span className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded">Required</span>
                      )}
                    </div>
                    {field.description && (
                      <p className="text-sm text-gray-500 mt-1">{field.description}</p>
                    )}
                    {field.options && field.options.length > 0 && (
                      <p className="text-xs text-gray-400 mt-1">
                        Options: {field.options.join(', ')}
                      </p>
                    )}
                  </div>
                  <button
                    onClick={() => handleDeleteCustomField(field.id)}
                    className="ml-4 text-red-600 hover:text-red-700 text-sm font-medium"
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Save Button */}
        <div className="flex justify-end gap-4">
          <Link
            href="/dashboard"
            className="rounded-lg border border-gray-300 px-6 py-2 text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </Link>
          <button
            onClick={handleSaveProfile}
            disabled={isSaving}
            className="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>

        {/* Account Section */}
        <section className="mt-8 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-6 text-lg font-semibold text-gray-900">Account</h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between py-4 border-b">
              <div>
                <h3 className="font-medium text-gray-900">Security Settings</h3>
                <p className="text-sm text-gray-500">Two-factor authentication and security options</p>
              </div>
              <Link
                href="/settings/security"
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                Manage Security →
              </Link>
            </div>

            <div className="flex items-center justify-between py-4 border-b">
              <div>
                <h3 className="font-medium text-gray-900">Audit Trail</h3>
                <p className="text-sm text-gray-500">View log of all sensitive operations</p>
              </div>
              <Link
                href="/settings/audit"
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                View Audit Log →
              </Link>
            </div>

            <div className="flex items-center justify-between py-4 border-b">
              <div>
                <h3 className="font-medium text-gray-900">Change Password</h3>
                <p className="text-sm text-gray-500">Update your password</p>
              </div>
              <Link
                href="/auth/forgot-password"
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                Reset Password
              </Link>
            </div>

            <div className="flex items-center justify-between py-4">
              <div>
                <h3 className="font-medium text-red-600">Delete Account</h3>
                <p className="text-sm text-gray-500">Permanently delete your account and all data</p>
              </div>
              <button
                className="text-red-600 hover:text-red-700 text-sm font-medium"
                disabled
              >
                Delete (Coming soon)
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
