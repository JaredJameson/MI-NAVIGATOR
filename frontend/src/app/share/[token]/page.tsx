'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface Report {
  id: string
  title: string
  type: string
  company?: string
  created_at: string
  sections: Array<{
    id: string
    title: string
    content: string
  }>
}

interface SharedReportData {
  report: Report
  shared_by: string
  share_token: string
  password_protected?: boolean
}

export default function SharedReportPage() {
  const params = useParams()
  const token = params.token as string

  const [data, setData] = useState<SharedReportData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [passwordRequired, setPasswordRequired] = useState(false)
  const [password, setPassword] = useState('')
  const [isVerifying, setIsVerifying] = useState(false)
  const [passwordError, setPasswordError] = useState('')

  useEffect(() => {
    if (!token) return

    const fetchSharedReport = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/reports/public/share/${token}`)

        if (!response.ok) {
          if (response.status === 404) {
            setError('Share link not found or has expired')
          } else if (response.status === 410) {
            setError('This share link has expired')
          } else if (response.status === 403) {
            // Password required
            setPasswordRequired(true)
            setIsLoading(false)
            return
          } else {
            setError('Failed to load shared report')
          }
          setIsLoading(false)
          return
        }

        const result = await response.json()

        // Check if password protected
        if (result.password_protected) {
          setPasswordRequired(true)
          setIsLoading(false)
          return
        }

        setData(result)
        setIsLoading(false)
      } catch (err) {
        console.error('Error fetching shared report:', err)
        setError('Failed to load shared report')
        setIsLoading(false)
      }
    }

    fetchSharedReport()
  }, [token])

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsVerifying(true)
    setPasswordError('')

    try {
      // Verify password
      const verifyResponse = await fetch(
        `${API_BASE_URL}/reports/public/share/${token}/verify-password`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ password }),
        }
      )

      if (!verifyResponse.ok) {
        if (verifyResponse.status === 401) {
          setPasswordError('Incorrect password')
        } else {
          setPasswordError('Verification failed')
        }
        setIsVerifying(false)
        return
      }

      // Password verified, now fetch the report
      const reportResponse = await fetch(
        `${API_BASE_URL}/reports/public/share/${token}?password_verified=true`
      )

      if (!reportResponse.ok) {
        setPasswordError('Failed to load report')
        setIsVerifying(false)
        return
      }

      const result = await reportResponse.json()
      setData(result)
      setPasswordRequired(false)
    } catch (err) {
      console.error('Password verification error:', err)
      setPasswordError('Verification failed')
    } finally {
      setIsVerifying(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (passwordRequired) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
          <div className="text-center mb-6">
            <div className="bg-blue-100 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
              <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Password Protected</h1>
            <p className="text-gray-600">This report is protected. Please enter the password to continue.</p>
          </div>

          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            {passwordError && (
              <div className="rounded-md bg-red-50 p-3">
                <p className="text-sm text-red-700">{passwordError}</p>
              </div>
            )}

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password..."
                className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                autoFocus
                required
              />
            </div>

            <button
              type="submit"
              disabled={isVerifying || !password}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isVerifying ? (
                <>
                  <div className="inline-block h-4 w-4 mr-2 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                  Verifying...
                </>
              ) : (
                'Access Report'
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <Link
              href="/"
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              ← Back to Homepage
            </Link>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="text-red-500 mb-4">
            <svg className="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Link Not Found</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <Link
            href="/"
            className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Go to Homepage
          </Link>
        </div>
      </div>
    )
  }

  if (!data) return null

  const { report, shared_by } = data

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">MI-Navigator</h1>
              <p className="text-sm text-gray-500 mt-1">Shared Report</p>
            </div>
            <Link
              href="/"
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Sign in to create your own reports →
            </Link>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-5xl mx-auto px-4 py-8">
        {/* Shared by notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3 mb-6 flex items-center gap-2">
          <svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
          <span className="text-sm text-blue-900">
            This report was shared with you by <strong>{shared_by}</strong>
          </span>
        </div>

        {/* Report */}
        <article className="bg-white rounded-xl shadow-lg p-8">
          {/* Report Header */}
          <div className="border-b pb-6 mb-6">
            <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                {report.type.replace('_', ' ').toUpperCase()}
              </span>
              {report.company && (
                <span className="text-gray-400">•</span>
              )}
              {report.company && (
                <span>{report.company}</span>
              )}
            </div>
            <h1 className="text-3xl font-bold text-gray-900">{report.title}</h1>
            <p className="text-sm text-gray-500 mt-2">
              Created: {new Date(report.created_at).toLocaleDateString('pl-PL', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </p>
          </div>

          {/* Report Sections */}
          <div className="space-y-8">
            {report.sections.map((section) => (
              <section key={section.id} className="prose max-w-none">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">{section.title}</h2>
                <div
                  className="text-gray-700 leading-relaxed whitespace-pre-wrap"
                  dangerouslySetInnerHTML={{ __html: section.content.replace(/\n/g, '<br/>') }}
                />
              </section>
            ))}
          </div>
        </article>

        {/* Footer CTA */}
        <div className="mt-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-lg p-8 text-center text-white">
          <h3 className="text-2xl font-bold mb-2">Want to create reports like this?</h3>
          <p className="text-blue-100 mb-4">
            MI-Navigator helps you analyze companies, markets, and competitors with AI-powered intelligence.
          </p>
          <Link
            href="/auth/register"
            className="inline-block bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
          >
            Get Started Free
          </Link>
        </div>
      </main>
    </div>
  )
}
