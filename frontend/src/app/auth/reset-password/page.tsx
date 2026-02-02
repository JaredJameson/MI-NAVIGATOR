'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { useTranslations } from 'next-intl'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

function ResetPasswordForm() {
  const t = useTranslations('auth')
  const tCommon = useTranslations('common')
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get('token')

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (!token) {
      setError(t('resetPassword.errors.invalidToken'))
    }
  }, [token, t])

  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 8) return t('resetPassword.errors.passwordMinLength')
    if (!/[A-Z]/.test(pwd)) return t('resetPassword.errors.passwordUppercase')
    if (!/[0-9]/.test(pwd)) return t('resetPassword.errors.passwordDigit')
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validate password
    const pwdError = validatePassword(password)
    if (pwdError) {
      setError(pwdError)
      return
    }

    if (password !== confirmPassword) {
      setError(t('resetPassword.errors.passwordsNotMatch'))
      return
    }

    if (!token) {
      setError(t('resetPassword.errors.invalidTokenShort'))
      return
    }

    setIsLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          password,
          confirm_password: confirmPassword,
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || t('resetPassword.errors.resetFailed'))
      }

      setSuccess(true)
      setTimeout(() => {
        router.push('/auth/login')
      }, 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : tCommon('errors.generic'))
    } finally {
      setIsLoading(false)
    }
  }

  if (success) {
    return (
      <div className="rounded-2xl bg-white/10 p-8 backdrop-blur-lg">
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-500/20">
            <svg className="h-8 w-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="mb-2 text-2xl font-bold text-white">{t('resetPassword.successTitle')}</h2>
          <p className="mb-4 text-gray-300">
            {t('resetPassword.successMessage')}
          </p>
          <Link
            href="/auth/login"
            className="inline-block text-emerald-400 hover:text-emerald-300"
          >
            {t('resetPassword.goToLogin')}
          </Link>
        </div>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-2xl bg-white/10 p-8 backdrop-blur-lg">
      {error && (
        <div className="mb-4 flex items-center gap-2 rounded-lg bg-red-500/20 px-4 py-3 text-red-200">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
        </div>
      )}

      <div className="space-y-6">
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-300">
            {t('resetPassword.newPasswordLabel')}
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder={t('resetPassword.newPasswordPlaceholder')}
            required
            className="mt-2 w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-gray-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
          />
          <p className="mt-1 text-xs text-gray-400">
            {t('resetPassword.passwordHelpText')}
          </p>
        </div>

        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300">
            {t('resetPassword.confirmPasswordLabel')}
          </label>
          <input
            id="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder={t('resetPassword.confirmPasswordPlaceholder')}
            required
            className="mt-2 w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-gray-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
          />
        </div>

        <button
          type="submit"
          disabled={isLoading || !token}
          className="w-full rounded-lg bg-emerald-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? t('resetPassword.resettingButton') : t('resetPassword.submitButton')}
        </button>
      </div>

      <p className="mt-6 text-center text-sm text-gray-400">
        <Link href="/auth/login" className="font-medium text-emerald-400 hover:text-emerald-300">
          {t('forgotPassword.backToLogin')}
        </Link>
      </p>
    </form>
  )
}

export default function ResetPasswordPage() {
  const t = useTranslations('auth')

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-emerald-900 to-slate-900 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-white">{t('resetPassword.title')}</h1>
          <p className="mt-2 text-gray-400">{t('resetPassword.subtitle')}</p>
        </div>

        <Suspense fallback={
          <div className="rounded-2xl bg-white/10 p-8 backdrop-blur-lg text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto"></div>
          </div>
        }>
          <ResetPasswordForm />
        </Suspense>
      </div>
    </div>
  )
}
