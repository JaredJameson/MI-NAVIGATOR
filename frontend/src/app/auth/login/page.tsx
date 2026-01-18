'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { authApi, fetchCsrfToken } from '@/services/api'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // 2FA state
  const [requires2FA, setRequires2FA] = useState(false)
  const [tempToken, setTempToken] = useState('')
  const [twoFactorCode, setTwoFactorCode] = useState('')

  // Field validation errors
  const [fieldErrors, setFieldErrors] = useState<{
    email?: string
    password?: string
    twoFactorCode?: string
  }>({})

  // Field validation success states
  const [fieldSuccess, setFieldSuccess] = useState<{
    email?: boolean
    password?: boolean
    twoFactorCode?: boolean
  }>({})

  // Validate individual fields
  const validateField = (name: string, value: string) => {
    const errors: typeof fieldErrors = { ...fieldErrors }
    const success: typeof fieldSuccess = { ...fieldSuccess }

    switch (name) {
      case 'email':
        if (!value.trim()) {
          errors.email = 'Email is required'
          delete success.email
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          errors.email = 'Please enter a valid email address'
          delete success.email
        } else {
          delete errors.email
          success.email = true
        }
        break
      case 'password':
        if (!value) {
          errors.password = 'Password is required'
          delete success.password
        } else if (value.length < 6) {
          errors.password = 'Password must be at least 6 characters'
          delete success.password
        } else {
          delete errors.password
          success.password = true
        }
        break
      case 'twoFactorCode':
        if (!value) {
          errors.twoFactorCode = 'Authentication code is required'
          delete success.twoFactorCode
        } else if (value.length !== 6) {
          errors.twoFactorCode = 'Code must be 6 digits'
          delete success.twoFactorCode
        } else {
          delete errors.twoFactorCode
          success.twoFactorCode = true
        }
        break
    }

    setFieldErrors(errors)
    setFieldSuccess(success)
    return !errors[name as keyof typeof errors]
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validate all fields
    const emailValid = validateField('email', email)
    const passwordValid = validateField('password', password)

    if (!emailValid || !passwordValid) {
      return
    }

    setLoading(true)

    try {
      const result = await authApi.login(email, password)

      if (result.error) {
        setError(result.error)
      } else if (result.data?.requires_2fa) {
        // 2FA is enabled, show 2FA input
        setRequires2FA(true)
        setTempToken(result.data.temp_token)
      } else {
        // Successfully logged in, redirect to dashboard
        router.push('/dashboard')
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleTwoFactorSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validate 2FA code
    const codeValid = validateField('twoFactorCode', twoFactorCode)

    if (!codeValid) {
      return
    }

    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login/2fa/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          temp_token: tempToken,
          code: twoFactorCode
        })
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.detail || 'Invalid 2FA code')
      } else {
        // Store tokens
        localStorage.setItem('mi_navigator_token', data.access_token)
        localStorage.setItem('mi_navigator_refresh_token', data.refresh_token)

        // Fetch CSRF token after successful login
        await fetchCsrfToken()

        // Successfully logged in, redirect to dashboard
        router.push('/dashboard')
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-8 shadow-lg">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">MI-Navigator</h1>
          <p className="mt-2 text-gray-600">Market Intelligence Platform</p>
        </div>

        {!requires2FA ? (
          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            {error && (
              <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
                <div className="flex items-center">
                  <svg className="mr-2 h-5 w-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                  {error}
                </div>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email
                </label>
                <div className="relative mt-1">
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value)
                      if (fieldErrors.email || fieldSuccess.email) {
                        validateField('email', e.target.value)
                      }
                    }}
                    onBlur={(e) => validateField('email', e.target.value)}
                    className={`block w-full rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-1 ${
                      fieldErrors.email
                        ? 'border-2 border-red-500 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500'
                        : fieldSuccess.email
                        ? 'border-2 border-green-500 focus:border-green-500 focus:ring-green-500'
                        : 'border border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                    }`}
                    placeholder="you@example.com"
                    aria-invalid={fieldErrors.email ? 'true' : 'false'}
                    aria-describedby={fieldErrors.email ? 'email-error' : undefined}
                  />
                  {fieldErrors.email && (
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                      <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                  {fieldSuccess.email && !fieldErrors.email && (
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                      <svg className="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>
                {fieldErrors.email && (
                  <p className="mt-1 text-sm text-red-600" id="email-error">
                    {fieldErrors.email}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <div className="relative mt-1">
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value)
                      if (fieldErrors.password || fieldSuccess.password) {
                        validateField('password', e.target.value)
                      }
                    }}
                    onBlur={(e) => validateField('password', e.target.value)}
                    className={`block w-full rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-1 ${
                      fieldErrors.password
                        ? 'border-2 border-red-500 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500'
                        : fieldSuccess.password
                        ? 'border-2 border-green-500 focus:border-green-500 focus:ring-green-500'
                        : 'border border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                    }`}
                    placeholder="Enter your password"
                    aria-invalid={fieldErrors.password ? 'true' : 'false'}
                    aria-describedby={fieldErrors.password ? 'password-error' : undefined}
                  />
                  {fieldErrors.password && (
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                      <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                  {fieldSuccess.password && !fieldErrors.password && (
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                      <svg className="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>
                {fieldErrors.password && (
                  <p className="mt-1 text-sm text-red-600" id="password-error">
                    {fieldErrors.password}
                  </p>
                )}
              </div>
            </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember"
                type="checkbox"
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="remember" className="ml-2 block text-sm text-gray-700">
                Remember me
              </label>
            </div>

            <Link href="/auth/forgot-password" className="text-sm text-blue-600 hover:underline">
              Forgot password?
            </Link>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-blue-600 px-4 py-2.5 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="mr-2 h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Signing in...
              </span>
            ) : (
              'Sign in'
            )}
          </button>

          <p className="text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <Link href="/auth/register" className="font-medium text-blue-600 hover:underline">
              Sign up
            </Link>
          </p>
        </form>
        ) : (
          <form onSubmit={handleTwoFactorSubmit} className="mt-8 space-y-6">
            <div className="text-center mb-6">
              <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Two-Factor Authentication</h2>
              <p className="mt-2 text-sm text-gray-600">
                Enter the 6-digit code from your authenticator app
              </p>
            </div>

            {error && (
              <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
                <div className="flex items-center">
                  <svg className="mr-2 h-5 w-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                  {error}
                </div>
              </div>
            )}

            <div>
              <label htmlFor="2faCode" className="block text-sm font-medium text-gray-700 mb-2">
                Authentication Code
              </label>
              <div className="relative">
                <input
                  id="2faCode"
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]{6}"
                  maxLength={6}
                  value={twoFactorCode}
                  onChange={(e) => {
                    const value = e.target.value.replace(/\D/g, '')
                    setTwoFactorCode(value)
                    if (fieldErrors.twoFactorCode) {
                      validateField('twoFactorCode', value)
                    }
                  }}
                  onBlur={(e) => validateField('twoFactorCode', e.target.value)}
                  className={`block w-full text-center text-2xl tracking-widest rounded-md px-3 py-3 shadow-sm focus:outline-none focus:ring-1 ${
                    fieldErrors.twoFactorCode
                      ? 'border-2 border-red-500 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500'
                      : 'border border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                  }`}
                  placeholder="000000"
                  autoFocus
                  aria-invalid={fieldErrors.twoFactorCode ? 'true' : 'false'}
                  aria-describedby={fieldErrors.twoFactorCode ? '2fa-error' : '2fa-help'}
                />
                {fieldErrors.twoFactorCode && (
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                    <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </div>
              {fieldErrors.twoFactorCode && (
                <p className="mt-1 text-sm text-red-600" id="2fa-error">
                  {fieldErrors.twoFactorCode}
                </p>
              )}
              {!fieldErrors.twoFactorCode && (
                <p className="mt-2 text-xs text-gray-500 text-center" id="2fa-help">
                  Code expires in 30 seconds
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading || twoFactorCode.length !== 6}
              className="w-full rounded-md bg-blue-600 px-4 py-2.5 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="mr-2 h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Verifying...
                </span>
              ) : (
                'Verify Code'
              )}
            </button>

            <button
              type="button"
              onClick={() => {
                setRequires2FA(false)
                setTwoFactorCode('')
                setError('')
              }}
              className="w-full text-center text-sm text-blue-600 hover:underline"
            >
              ← Back to login
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
