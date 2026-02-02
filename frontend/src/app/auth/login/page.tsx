'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { authApi, fetchCsrfToken } from '@/services/api'

export default function LoginPage() {
  const t = useTranslations('auth')
  const router = useRouter()
  const searchParams = useSearchParams()
  // BUGFIX Session 375 (Feature #122): Get redirect URL from query params
  const redirectUrl = searchParams.get('redirect') || '/dashboard'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [focusField, setFocusField] = useState<string | null>(null)

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

  // Refs for form fields
  const emailRef = useRef<HTMLInputElement>(null)
  const passwordRef = useRef<HTMLInputElement>(null)
  const twoFactorCodeRef = useRef<HTMLInputElement>(null)

  // Auto-focus first invalid field when errors change
  useEffect(() => {
    if (focusField) {
      const refs: Record<string, React.RefObject<HTMLInputElement>> = {
        email: emailRef,
        password: passwordRef,
        twoFactorCode: twoFactorCodeRef,
      }
      refs[focusField]?.current?.focus()
      setFocusField(null)
    }
  }, [focusField])

  // Validate individual fields
  const validateField = (name: string, value: string) => {
    const errors: typeof fieldErrors = { ...fieldErrors }
    const success: typeof fieldSuccess = { ...fieldSuccess }

    switch (name) {
      case 'email':
        if (!value.trim()) {
          errors.email = t('login.errors.emailRequired')
          delete success.email
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          errors.email = t('login.errors.invalidEmail')
          delete success.email
        } else {
          delete errors.email
          success.email = true
        }
        break
      case 'password':
        if (!value) {
          errors.password = t('login.errors.passwordRequired')
          delete success.password
        } else if (value.length < 6) {
          errors.password = t('login.errors.passwordMinLength')
          delete success.password
        } else {
          delete errors.password
          success.password = true
        }
        break
      case 'twoFactorCode':
        if (!value) {
          errors.twoFactorCode = t('twoFactor.errors.codeRequired')
          delete success.twoFactorCode
        } else if (value.length !== 6) {
          errors.twoFactorCode = t('twoFactor.errors.codeLength')
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
      // Focus first invalid field
      if (!emailValid) {
        setFocusField('email')
      } else if (!passwordValid) {
        setFocusField('password')
      }
      return
    }

    setLoading(true)

    try {
      const result = await authApi.login(email, password, rememberMe)

      if (result.error) {
        setError(result.error)
      } else if (result.data?.requires_2fa) {
        // 2FA is enabled, show 2FA input
        setRequires2FA(true)
        setTempToken(result.data.temp_token)
      } else {
        // Successfully logged in, redirect to originally requested page or dashboard
        router.push(redirectUrl)
      }
    } catch (err) {
      setError(t('login.errors.unexpectedError'))
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
      setFocusField('twoFactorCode')
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
        setError(data.detail || t('twoFactor.errors.invalidCode'))
      } else {
        // Store tokens
        localStorage.setItem('mi_navigator_token', data.access_token)
        localStorage.setItem('mi_navigator_refresh_token', data.refresh_token)

        // Fetch CSRF token after successful login
        await fetchCsrfToken()

        // Successfully logged in, redirect to originally requested page or dashboard
        router.push(redirectUrl)
      }
    } catch (err) {
      setError(t('login.errors.unexpectedError'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-8 shadow-lg">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">MI-Navigator</h1>
          <p className="mt-2 text-gray-600">{t('login.subtitle')}</p>
        </div>

        {!requires2FA ? (
          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            {error && (
              <div
                role="alert"
                aria-live="assertive"
                className="rounded-md bg-red-50 p-4 text-sm text-red-700"
              >
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
                  {t('login.email')}
                </label>
                <div className="relative mt-1">
                  <input
                    ref={emailRef}
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
                        : 'border border-gray-300 focus:border-emerald-500 focus:ring-emerald-500'
                    }`}
                    placeholder={t('login.emailPlaceholder')}
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
                  <p className="mt-1 text-sm text-red-600" id="email-error" role="alert" aria-live="assertive">
                    {fieldErrors.email}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  {t('login.password')}
                </label>
                <div className="relative mt-1">
                  <input
                    ref={passwordRef}
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
                        : 'border border-gray-300 focus:border-emerald-500 focus:ring-emerald-500'
                    }`}
                    placeholder={t('login.passwordPlaceholder')}
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
                  <p className="mt-1 text-sm text-red-600" id="password-error" role="alert" aria-live="assertive">
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
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500"
              />
              <label htmlFor="remember" className="ml-2 block text-sm text-gray-700">
                {t('login.rememberMe')}
              </label>
            </div>

            <Link href="/auth/forgot-password" className="text-sm text-emerald-600 hover:underline">
              {t('login.forgotPassword')}
            </Link>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-emerald-600 px-4 py-2.5 text-white font-medium hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="mr-2 h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {t('login.signingIn')}
              </span>
            ) : (
              t('login.signIn')
            )}
          </button>

          <p className="text-center text-sm text-gray-600">
            {t('login.noAccount')}{' '}
            <Link href="/auth/register" className="font-medium text-emerald-600 hover:underline">
              {t('login.signUp')}
            </Link>
          </p>
        </form>
        ) : (
          <form onSubmit={handleTwoFactorSubmit} className="mt-8 space-y-6">
            <div className="text-center mb-6">
              <div className="mx-auto w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-900">{t('twoFactor.title')}</h2>
              <p className="mt-2 text-sm text-gray-600">
                {t('twoFactor.description')}
              </p>
            </div>

            {error && (
              <div
                role="alert"
                aria-live="assertive"
                className="rounded-md bg-red-50 p-4 text-sm text-red-700"
              >
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
                {t('twoFactor.codeLabel')}
              </label>
              <div className="relative">
                <input
                  ref={twoFactorCodeRef}
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
                      : 'border border-gray-300 focus:border-emerald-500 focus:ring-emerald-500'
                  }`}
                  placeholder={t('twoFactor.codePlaceholder')}
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
                <p className="mt-1 text-sm text-red-600" id="2fa-error" role="alert" aria-live="assertive">
                  {fieldErrors.twoFactorCode}
                </p>
              )}
              {!fieldErrors.twoFactorCode && (
                <p className="mt-2 text-xs text-gray-500 text-center" id="2fa-help">
                  {t('twoFactor.codeExpires')}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading || twoFactorCode.length !== 6}
              className="w-full rounded-md bg-emerald-600 px-4 py-2.5 text-white font-medium hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="mr-2 h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {t('twoFactor.verifying')}
                </span>
              ) : (
                t('twoFactor.verify')
              )}
            </button>

            <button
              type="button"
              onClick={() => {
                setRequires2FA(false)
                setTwoFactorCode('')
                setError('')
              }}
              className="w-full text-center text-sm text-emerald-600 hover:underline"
            >
              {t('twoFactor.backToLogin')}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
