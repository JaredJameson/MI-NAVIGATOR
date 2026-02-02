'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { authApi } from '@/services/api'

export default function RegisterPage() {
  const t = useTranslations('auth')
  const tCommon = useTranslations('common')
  const router = useRouter()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [fieldSuccess, setFieldSuccess] = useState<Record<string, boolean>>({})
  const [generalError, setGeneralError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const [focusField, setFocusField] = useState<string | null>(null)

  // Refs for form fields
  const emailRef = useRef<HTMLInputElement>(null)
  const passwordRef = useRef<HTMLInputElement>(null)
  const confirmPasswordRef = useRef<HTMLInputElement>(null)

  // Auto-focus first invalid field when errors change
  useEffect(() => {
    if (focusField) {
      const refs: Record<string, React.RefObject<HTMLInputElement>> = {
        email: emailRef,
        password: passwordRef,
        confirmPassword: confirmPasswordRef,
      }
      refs[focusField]?.current?.focus()
      setFocusField(null)
    }
  }, [focusField])

  const validateField = (name: string, value: string): boolean => {
    const newErrors = { ...errors }
    const newSuccess = { ...fieldSuccess }

    switch (name) {
      case 'email':
        if (!value) {
          newErrors.email = tCommon('errors.required')
          delete newSuccess.email
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          newErrors.email = tCommon('errors.invalidEmail')
          delete newSuccess.email
        } else {
          delete newErrors.email
          newSuccess.email = true
        }
        break
      case 'password':
        if (!value) {
          newErrors.password = tCommon('errors.required')
          delete newSuccess.password
        } else if (value.length < 8) {
          newErrors.password = t('register.errors.passwordMinLength')
          delete newSuccess.password
        } else if (!/[A-Z]/.test(value)) {
          newErrors.password = t('register.errors.passwordUppercase')
          delete newSuccess.password
        } else if (!/[0-9]/.test(value)) {
          newErrors.password = t('register.errors.passwordDigit')
          delete newSuccess.password
        } else {
          delete newErrors.password
          newSuccess.password = true
        }
        break
      case 'confirmPassword':
        if (!value) {
          newErrors.confirmPassword = t('register.errors.confirmPasswordRequired')
          delete newSuccess.confirmPassword
        } else if (formData.password !== value) {
          newErrors.confirmPassword = t('register.errors.passwordsNotMatch')
          delete newSuccess.confirmPassword
        } else {
          delete newErrors.confirmPassword
          newSuccess.confirmPassword = true
        }
        break
    }

    setErrors(newErrors)
    setFieldSuccess(newSuccess)
    return !newErrors[name]
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    // Email validation
    if (!formData.email) {
      newErrors.email = tCommon('errors.required')
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = tCommon('errors.invalidEmail')
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = tCommon('errors.required')
    } else if (formData.password.length < 8) {
      newErrors.password = t('register.errors.passwordMinLength')
    } else if (!/[A-Z]/.test(formData.password)) {
      newErrors.password = t('register.errors.passwordUppercase')
    } else if (!/[0-9]/.test(formData.password)) {
      newErrors.password = t('register.errors.passwordDigit')
    }

    // Confirm password
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = t('register.errors.confirmPasswordRequired')
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = t('register.errors.passwordsNotMatch')
    }

    setErrors(newErrors)

    // Focus first invalid field
    if (Object.keys(newErrors).length > 0) {
      const firstError = Object.keys(newErrors)[0]
      setFocusField(firstError)
    }

    return Object.keys(newErrors).length === 0
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    // Validate field on change if it was previously validated
    if (errors[name] || fieldSuccess[name]) {
      validateField(name, value)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setGeneralError('')
    setSuccess(false)

    if (!validateForm()) {
      return
    }

    setLoading(true)

    try {
      const result = await authApi.register(
        formData.email,
        formData.password,
        formData.confirmPassword,
        formData.name || undefined
      )

      if (result.error) {
        setGeneralError(result.error)
      } else {
        setSuccess(true)
        // Redirect to email verification page
        setTimeout(() => {
          router.push(`/auth/verify-email?email=${encodeURIComponent(formData.email)}`)
        }, 2000)
      }
    } catch (err) {
      setGeneralError(tCommon('errors.generic'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-8 shadow-lg">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">{t('register.title')}</h1>
          <p className="mt-2 text-gray-600">{t('register.subtitle')}</p>
        </div>

        {success && (
          <div className="rounded-md bg-green-50 p-4 text-sm text-green-700">
            <div className="flex items-center">
              <svg className="mr-2 h-5 w-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
              </svg>
              {t('register.successMessage')}
            </div>
          </div>
        )}

        {generalError && (
          <div
            role="alert"
            aria-live="assertive"
            className="rounded-md bg-red-50 p-4 text-sm text-red-700"
          >
            <div className="flex items-center">
              <svg className="mr-2 h-5 w-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
              {generalError}
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <div className="space-y-4">
            {/* Name field */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                {t('register.nameLabel')}
              </label>
              <input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                placeholder={t('register.namePlaceholder')}
              />
            </div>

            {/* Email field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                {t('login.email')} <span className="text-red-500">*</span>
              </label>
              <div className="relative mt-1">
                <input
                  ref={emailRef}
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  onBlur={(e) => validateField('email', e.target.value)}
                  className={`block w-full rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-1 ${
                    errors.email
                      ? 'border-2 border-red-500 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500'
                      : fieldSuccess.email
                      ? 'border-2 border-green-500 focus:border-green-500 focus:ring-green-500'
                      : 'border border-gray-300 focus:border-emerald-500 focus:ring-emerald-500'
                  }`}
                  placeholder={t('register.emailPlaceholder')}
                  aria-invalid={errors.email ? 'true' : 'false'}
                  aria-describedby={errors.email ? 'email-error' : undefined}
                />
                {errors.email && (
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                    <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
                {fieldSuccess.email && !errors.email && (
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                    <svg className="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </div>
              {errors.email && (
                <p className="mt-1 text-sm text-red-600" id="email-error" role="alert" aria-live="assertive">
                  {errors.email}
                </p>
              )}
            </div>

            {/* Password field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                {t('login.password')} <span className="text-red-500">*</span>
              </label>
              <div className="relative mt-1">
                <input
                  ref={passwordRef}
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  onBlur={(e) => validateField('password', e.target.value)}
                  className={`block w-full rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-1 ${
                    errors.password
                      ? 'border-2 border-red-500 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500'
                      : fieldSuccess.password
                      ? 'border-2 border-green-500 focus:border-green-500 focus:ring-green-500'
                      : 'border border-gray-300 focus:border-emerald-500 focus:ring-emerald-500'
                  }`}
                  placeholder={t('register.passwordPlaceholder')}
                  aria-invalid={errors.password ? 'true' : 'false'}
                  aria-describedby={errors.password ? 'password-error' : 'password-help'}
                />
                {errors.password && (
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                    <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
                {fieldSuccess.password && !errors.password && (
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                    <svg className="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600" id="password-error" role="alert" aria-live="assertive">
                  {errors.password}
                </p>
              )}
              {!errors.password && (
                <p className="mt-1 text-xs text-gray-500" id="password-help">
                  {t('register.passwordHelpText')}
                </p>
              )}
            </div>

            {/* Confirm Password field */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                {t('register.confirmPasswordLabel')} <span className="text-red-500">*</span>
              </label>
              <div className="relative mt-1">
                <input
                  ref={confirmPasswordRef}
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  onBlur={(e) => validateField('confirmPassword', e.target.value)}
                  className={`block w-full rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-1 ${
                    errors.confirmPassword
                      ? 'border-2 border-red-500 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500'
                      : fieldSuccess.confirmPassword
                      ? 'border-2 border-green-500 focus:border-green-500 focus:ring-green-500'
                      : 'border border-gray-300 focus:border-emerald-500 focus:ring-emerald-500'
                  }`}
                  placeholder={t('register.confirmPasswordPlaceholder')}
                  aria-invalid={errors.confirmPassword ? 'true' : 'false'}
                  aria-describedby={errors.confirmPassword ? 'confirm-password-error' : undefined}
                />
                {errors.confirmPassword && (
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                    <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
                {fieldSuccess.confirmPassword && !errors.confirmPassword && (
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                    <svg className="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </div>
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600" id="confirm-password-error" role="alert" aria-live="assertive">
                  {errors.confirmPassword}
                </p>
              )}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || success}
            className="w-full rounded-md bg-emerald-600 px-4 py-2.5 text-white font-medium hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="mr-2 h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {t('register.creatingAccount')}
              </span>
            ) : (
              t('register.title')
            )}
          </button>

          <p className="text-center text-sm text-gray-600">
            {t('register.haveAccount')}{' '}
            <Link href="/auth/login" className="font-medium text-emerald-600 hover:underline">
              {t('register.signIn')}
            </Link>
          </p>
        </form>
      </div>
    </div>
  )
}
