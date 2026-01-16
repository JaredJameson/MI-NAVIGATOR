'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface Tag {
  id: string
  name: string
  color: string
  description: string | null
  created_at: string
  user_id: string
}

const PRESET_COLORS = [
  { value: '#EF4444', label: 'Red' },
  { value: '#F59E0B', label: 'Amber' },
  { value: '#10B981', label: 'Green' },
  { value: '#3B82F6', label: 'Blue' },
  { value: '#8B5CF6', label: 'Purple' },
  { value: '#EC4899', label: 'Pink' },
  { value: '#6B7280', label: 'Gray' },
]

export default function TagManagementPage() {
  const router = useRouter()
  const [tags, setTags] = useState<Tag[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Create/Edit form state
  const [showForm, setShowForm] = useState(false)
  const [editingTag, setEditingTag] = useState<Tag | null>(null)
  const [formName, setFormName] = useState('')
  const [formColor, setFormColor] = useState(PRESET_COLORS[0].value)
  const [formDescription, setFormDescription] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  // Delete confirmation
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [tagToDelete, setTagToDelete] = useState<Tag | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    fetchTags()
  }, [])

  const fetchTags = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE_URL}/tags/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to fetch tags')
      }

      const data: Tag[] = await response.json()
      setTags(data)
    } catch (err) {
      setError('Nie udało się załadować tagów')
    } finally {
      setIsLoading(false)
    }
  }

  const openCreateForm = () => {
    setEditingTag(null)
    setFormName('')
    setFormColor(PRESET_COLORS[0].value)
    setFormDescription('')
    setShowForm(true)
  }

  const openEditForm = (tag: Tag) => {
    setEditingTag(tag)
    setFormName(tag.name)
    setFormColor(tag.color)
    setFormDescription(tag.description || '')
    setShowForm(true)
  }

  const closeForm = () => {
    setShowForm(false)
    setEditingTag(null)
    setFormName('')
    setFormColor(PRESET_COLORS[0].value)
    setFormDescription('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formName.trim()) {
      setError('Nazwa tagu jest wymagana')
      return
    }

    const token = getStoredToken()
    if (!token) return

    setIsSaving(true)
    setError('')

    try {
      const url = editingTag
        ? `${API_BASE_URL}/tags/${editingTag.id}`
        : `${API_BASE_URL}/tags/`

      const method = editingTag ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formName.trim(),
          color: formColor,
          description: formDescription.trim() || null,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to save tag')
      }

      const savedTag: Tag = await response.json()

      if (editingTag) {
        // Update existing tag in list
        setTags(tags.map(t => t.id === savedTag.id ? savedTag : t))
        setSuccess(`Tag "${savedTag.name}" został zaktualizowany`)
      } else {
        // Add new tag to list
        setTags([...tags, savedTag])
        setSuccess(`Tag "${savedTag.name}" został utworzony`)
      }

      closeForm()

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Nie udało się zapisać tagu')
    } finally {
      setIsSaving(false)
    }
  }

  const confirmDelete = (tag: Tag) => {
    setTagToDelete(tag)
    setShowDeleteConfirm(true)
  }

  const handleDelete = async () => {
    if (!tagToDelete) return

    const token = getStoredToken()
    if (!token) return

    setIsDeleting(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE_URL}/tags/${tagToDelete.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to delete tag')
      }

      // Remove tag from list
      setTags(tags.filter(t => t.id !== tagToDelete.id))
      setSuccess(`Tag "${tagToDelete.name}" został usunięty`)

      setShowDeleteConfirm(false)
      setTagToDelete(null)

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Nie udało się usunąć tagu')
      setShowDeleteConfirm(false)
    } finally {
      setIsDeleting(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pl-PL', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-white px-4 py-3">
        <div className="mx-auto flex max-w-4xl items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/settings" className="text-gray-600 hover:text-gray-900">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </Link>
            <h1 className="text-xl font-semibold text-gray-900">Zarządzanie tagami</h1>
          </div>
          <button
            onClick={openCreateForm}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          >
            + Nowy tag
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-8">
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

        {/* Info Card */}
        <div className="mb-6 rounded-lg bg-blue-50 border border-blue-200 px-4 py-3">
          <div className="flex items-start gap-3">
            <svg className="h-5 w-5 text-blue-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Czym są tagi?</p>
              <p>Tagi pozwalają organizować raporty według własnych kategorii. Możesz przypisać wiele tagów do jednego raportu.</p>
            </div>
          </div>
        </div>

        {/* Tags List */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
            <span className="ml-3 text-gray-600">Ładowanie tagów...</span>
          </div>
        ) : tags.length === 0 ? (
          <div className="rounded-xl bg-white p-12 text-center shadow-sm">
            <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-gray-100 p-4">
              <svg className="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900">Brak tagów</h3>
            <p className="mt-2 text-gray-600">Utwórz pierwszy tag aby rozpocząć organizację raportów.</p>
            <button
              onClick={openCreateForm}
              className="mt-4 inline-block rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              + Utwórz pierwszy tag
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {tags.map((tag) => (
              <div
                key={tag.id}
                className="rounded-xl bg-white p-4 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3 flex-1">
                    {/* Color indicator */}
                    <div
                      className="h-10 w-10 rounded-lg flex items-center justify-center"
                      style={{ backgroundColor: tag.color }}
                    >
                      <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                      </svg>
                    </div>

                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{tag.name}</h3>
                      {tag.description && (
                        <p className="text-sm text-gray-600 mt-1">{tag.description}</p>
                      )}
                      <p className="text-xs text-gray-400 mt-1">Utworzony: {formatDate(tag.created_at)}</p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => openEditForm(tag)}
                      className="rounded-lg p-2 text-gray-600 hover:bg-gray-100"
                      title="Edytuj tag"
                    >
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      onClick={() => confirmDelete(tag)}
                      className="rounded-lg p-2 text-red-600 hover:bg-red-50"
                      title="Usuń tag"
                    >
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Create/Edit Form Modal */}
      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="w-full max-w-md rounded-xl bg-white shadow-xl">
            <form onSubmit={handleSubmit}>
              <div className="border-b px-6 py-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">
                    {editingTag ? 'Edytuj tag' : 'Utwórz nowy tag'}
                  </h2>
                  <button
                    type="button"
                    onClick={closeForm}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              <div className="p-6 space-y-4">
                {/* Name */}
                <div>
                  <label htmlFor="tag-name" className="block text-sm font-medium text-gray-700 mb-1">
                    Nazwa tagu *
                  </label>
                  <input
                    type="text"
                    id="tag-name"
                    value={formName}
                    onChange={(e) => setFormName(e.target.value)}
                    placeholder="np. Priorytet wysoki"
                    className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    required
                  />
                </div>

                {/* Color */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Kolor *
                  </label>
                  <div className="grid grid-cols-7 gap-2">
                    {PRESET_COLORS.map((color) => (
                      <button
                        key={color.value}
                        type="button"
                        onClick={() => setFormColor(color.value)}
                        className={`h-10 rounded-lg transition-all ${
                          formColor === color.value
                            ? 'ring-2 ring-offset-2 ring-blue-500 scale-110'
                            : 'hover:scale-105'
                        }`}
                        style={{ backgroundColor: color.value }}
                        title={color.label}
                      />
                    ))}
                  </div>
                </div>

                {/* Description */}
                <div>
                  <label htmlFor="tag-description" className="block text-sm font-medium text-gray-700 mb-1">
                    Opis (opcjonalny)
                  </label>
                  <textarea
                    id="tag-description"
                    value={formDescription}
                    onChange={(e) => setFormDescription(e.target.value)}
                    placeholder="Krótki opis przeznaczenia tagu..."
                    rows={3}
                    className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="border-t px-6 py-4 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={closeForm}
                  disabled={isSaving}
                  className="rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  Anuluj
                </button>
                <button
                  type="submit"
                  disabled={isSaving}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {isSaving ? (
                    <span className="flex items-center gap-2">
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                      Zapisywanie...
                    </span>
                  ) : editingTag ? 'Zapisz zmiany' : 'Utwórz tag'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && tagToDelete && (
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
                Czy na pewno chcesz usunąć tag <span className="font-semibold">"{tagToDelete.name}"</span>?
                <br />
                <span className="text-sm text-gray-500">Tag zostanie usunięty ze wszystkich raportów.</span>
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setShowDeleteConfirm(false)
                    setTagToDelete(null)
                  }}
                  disabled={isDeleting}
                  className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  Anuluj
                </button>
                <button
                  onClick={handleDelete}
                  disabled={isDeleting}
                  className="flex-1 rounded-lg bg-red-600 px-4 py-2 text-white hover:bg-red-700 disabled:opacity-50"
                >
                  {isDeleting ? (
                    <span className="flex items-center justify-center gap-2">
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                      Usuwanie...
                    </span>
                  ) : 'Usuń tag'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
