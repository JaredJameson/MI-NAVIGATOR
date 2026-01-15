'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface FeedbackType {
  id: string
  label: string
  icon: string
}

interface FeedbackItem {
  id: string
  type: string
  type_label: string
  message: string
  page_context: string | null
  created_at: string
  status: string
}

// Icons for feedback types
const TYPE_ICONS: Record<string, string> = {
  'bug': '🐛',
  'feature': '💡',
  'improvement': '📈',
  'question': '❓',
  'other': '💬',
}

export default function FeedbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [feedbackTypes, setFeedbackTypes] = useState<FeedbackType[]>([])
  const [myFeedback, setMyFeedback] = useState<FeedbackItem[]>([])
  const [selectedType, setSelectedType] = useState('')
  const [message, setMessage] = useState('')
  const [errorContext, setErrorContext] = useState('')
  const [errorPage, setErrorPage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showHistory, setShowHistory] = useState(false)

  useEffect(() => {
    fetchFeedbackTypes()
    fetchMyFeedback()

    // Check for error reporting context from URL params
    const errorType = searchParams.get('type')
    const errorMsg = searchParams.get('error')
    const errorPageParam = searchParams.get('page')

    if (errorType === 'bug' || errorMsg) {
      setSelectedType('bug')
      if (errorMsg) {
        setErrorContext(decodeURIComponent(errorMsg))
      }
      if (errorPageParam) {
        setErrorPage(decodeURIComponent(errorPageParam))
      }
    }
  }, [])

  const fetchFeedbackTypes = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/feedback/types`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setFeedbackTypes(data.types || [])
      }
    } catch (err) {
      console.error('Failed to fetch feedback types:', err)
    }
  }

  const fetchMyFeedback = async () => {
    const token = getStoredToken()
    if (!token) return

    setIsLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/feedback`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setMyFeedback(data.items || [])
      }
    } catch (err) {
      console.error('Failed to fetch feedback:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (!selectedType) {
      setError('Wybierz typ opinii')
      return
    }

    if (!message || message.trim().length < 10) {
      setError('Wiadomość musi zawierać co najmniej 10 znaków')
      return
    }

    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await fetch(`${API_BASE_URL}/feedback`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: selectedType,
          message: errorContext
            ? `[Błąd: ${errorContext}]\n\n${message.trim()}`
            : message.trim(),
          page_context: errorPage || window.location.pathname
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Nie udało się przesłać opinii')
      }

      const data = await response.json()
      setSuccess(data.message)
      setSelectedType('')
      setMessage('')
      setErrorContext('')
      setErrorPage('')

      // Clear URL params after successful submission
      router.push('/feedback')

      // Refresh feedback list
      fetchMyFeedback()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Wystąpił błąd')
    } finally {
      setIsSubmitting(false)
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('pl-PL', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-3xl">💬</span>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Prześlij opinię</h1>
                <p className="mt-1 text-sm text-gray-500">
                  Pomóż nam ulepszyć MI-Navigator
                </p>
              </div>
            </div>
            <Link
              href="/dashboard"
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
            >
              ← Powrót do dashboardu
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Feedback Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">Nowa opinia</h2>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Feedback Type Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Typ opinii *
                  </label>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {feedbackTypes.map((type) => (
                      <button
                        key={type.id}
                        type="button"
                        onClick={() => setSelectedType(type.id)}
                        className={`p-3 rounded-lg border-2 text-left transition-colors ${
                          selectedType === type.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <span className="text-2xl block mb-1">
                          {TYPE_ICONS[type.id] || '📝'}
                        </span>
                        <span className="text-sm font-medium text-gray-900">
                          {type.label}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Error Context - auto-populated when reporting an error */}
                {errorContext && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-start gap-3">
                      <span className="text-xl">⚠️</span>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-red-800 mb-1">
                          Kontekst błędu (automatycznie dodany)
                        </p>
                        <p className="text-sm text-red-700 font-mono bg-red-100 p-2 rounded">
                          {errorContext}
                        </p>
                        {errorPage && (
                          <p className="text-xs text-red-600 mt-2">
                            Strona: {errorPage}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Message */}
                <div>
                  <label
                    htmlFor="message"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    {errorContext ? 'Dodatkowy opis problemu *' : 'Twoja wiadomość *'}
                  </label>
                  <textarea
                    id="message"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    rows={5}
                    placeholder={errorContext
                      ? "Opisz co robiłeś gdy wystąpił błąd..."
                      : "Opisz swoją opinię, sugestię lub problem..."
                    }
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Minimum 10 znaków ({message.length}/10)
                  </p>
                </div>

                {/* Error/Success Messages */}
                {error && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                    {error}
                  </div>
                )}

                {success && (
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
                    {success}
                  </div>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  {isSubmitting ? (
                    <span className="flex items-center justify-center gap-2">
                      <span className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
                      Wysyłanie...
                    </span>
                  ) : (
                    'Wyślij opinię'
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Sidebar - My Feedback */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">Moje opinie</h3>
                <span className="text-sm text-gray-500">
                  {myFeedback.length} wysłanych
                </span>
              </div>

              {isLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                </div>
              ) : myFeedback.length === 0 ? (
                <div className="text-center py-8">
                  <span className="text-4xl">📭</span>
                  <p className="mt-2 text-sm text-gray-500">
                    Nie wysłałeś jeszcze żadnej opinii
                  </p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {myFeedback.map((item) => (
                    <div
                      key={item.id}
                      className="p-3 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-start gap-2">
                        <span className="text-lg">
                          {TYPE_ICONS[item.type] || '📝'}
                        </span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900">
                            {item.type_label}
                          </p>
                          <p className="text-xs text-gray-500 truncate">
                            {item.message}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {formatDate(item.created_at)}
                          </p>
                        </div>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          item.status === 'new'
                            ? 'bg-blue-100 text-blue-700'
                            : 'bg-gray-100 text-gray-600'
                        }`}>
                          {item.status === 'new' ? 'Nowa' : item.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
