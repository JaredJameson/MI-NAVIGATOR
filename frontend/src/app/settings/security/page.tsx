'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken, getStoredRefreshToken } from '@/services/api'
import { useTranslations } from 'next-intl'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface TwoFactorStatus {
  enabled: boolean
  message: string
}

interface TwoFactorSetup {
  secret: string
  qr_code: string
  manual_entry_key: string
}

export default function SecuritySettingsPage() {
  const router = useRouter()
  const t = useTranslations('settings.security')
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // 2FA Setup State
  const [showSetupModal, setShowSetupModal] = useState(false)
  const [setupData, setSetupData] = useState<TwoFactorSetup | null>(null)
  const [verificationCode, setVerificationCode] = useState('')
  const [isSettingUp, setIsSettingUp] = useState(false)
  const [isVerifying, setIsVerifying] = useState(false)

  // Password Change State
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isChangingPassword, setIsChangingPassword] = useState(false)

  useEffect(() => {
    fetchTwoFactorStatus()
  }, [])

  const fetchTwoFactorStatus = async () => {
    if (typeof window === 'undefined') {
      setIsLoading(false)
      return
    }

    const token = getStoredToken()
    if (!token) {
      setIsLoading(false)
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/2fa/status`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error(t('errors.failedToFetch2FAStatus'))
      }

      const data: TwoFactorStatus = await response.json()
      setTwoFactorEnabled(data.enabled)
    } catch (err) {
      console.error('Failed to fetch 2FA status:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const getCsrfToken = async (): Promise<string> => {
    const response = await fetch(`${API_BASE_URL}/auth/csrf-token`)
    const data = await response.json()
    return data.csrf_token
  }

  const handleSetup2FA = async () => {
    const token = getStoredToken()
    if (!token) return

    setIsSettingUp(true)
    setError('')

    try {
      const csrfToken = await getCsrfToken()
      const response = await fetch(`${API_BASE_URL}/auth/2fa/setup`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-CSRF-Token': csrfToken,
        },
      })

      if (!response.ok) {
        throw new Error(t('errors.failedToSetup2FA'))
      }

      const data: TwoFactorSetup = await response.json()
      setSetupData(data)
      setShowSetupModal(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : t('errors.failedToSetup2FA'))
    } finally {
      setIsSettingUp(false)
    }
  }

  const handleVerify2FA = async () => {
    const token = getStoredToken()
    if (!token || !verificationCode) return

    setIsVerifying(true)
    setError('')

    try {
      const csrfToken = await getCsrfToken()
      const response = await fetch(`${API_BASE_URL}/auth/2fa/verify`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken,
        },
        body: JSON.stringify({ code: verificationCode }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || t('errors.invalidVerificationCode'))
      }

      const data: TwoFactorStatus = await response.json()
      setTwoFactorEnabled(true)
      setShowSetupModal(false)
      setSuccess(data.message)
      setSetupData(null)
      setVerificationCode('')
      setTimeout(() => setSuccess(''), 5000)
    } catch (err) {
      setError(err instanceof Error ? err.message : t('errors.verificationFailed'))
    } finally {
      setIsVerifying(false)
    }
  }

  const handleDisable2FA = async () => {
    if (!confirm(t('twoFactor.confirmDisable'))) {
      return
    }

    const token = getStoredToken()
    if (!token) return

    setError('')

    try {
      const csrfToken = await getCsrfToken()
      const response = await fetch(`${API_BASE_URL}/auth/2fa/disable`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-CSRF-Token': csrfToken,
        },
      })

      if (!response.ok) {
        throw new Error(t('errors.failedToDisable2FA'))
      }

      const data: TwoFactorStatus = await response.json()
      setTwoFactorEnabled(false)
      setSuccess(data.message)
      setTimeout(() => setSuccess(''), 5000)
    } catch (err) {
      setError(err instanceof Error ? err.message : t('errors.failedToDisable2FA'))
    }
  }

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // Validation
    if (!currentPassword || !newPassword || !confirmPassword) {
      setError(t('errors.allFieldsRequired'))
      return
    }

    if (newPassword.length < 6) {
      setError(t('errors.passwordTooShort'))
      return
    }

    if (newPassword !== confirmPassword) {
      setError(t('errors.passwordsMismatch'))
      return
    }

    const token = getStoredToken()
    if (!token) {
      setError(t('errors.notAuthenticated'))
      return
    }

    // Get refresh token from localStorage
    const refreshToken = getStoredRefreshToken()
    if (!refreshToken) {
      setError(t('errors.sessionNotFound'))
      return
    }

    setIsChangingPassword(true)

    try {
      const csrfToken = await getCsrfToken()
      const response = await fetch(`${API_BASE_URL}/users/me/password`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken,
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
          refresh_token: refreshToken
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: t('errors.failedToChangePassword') }))
        throw new Error(errorData.detail || t('errors.failedToChangePassword'))
      }

      const data = await response.json()
      setSuccess(`${data.message} (${data.sessions_invalidated} other session(s) logged out)`)

      // Clear form
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')

      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(''), 5000)
    } catch (err) {
      setError(err instanceof Error ? err.message : t('errors.failedToChangePassword'))
    } finally {
      setIsChangingPassword(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4">
            <Link href="/settings" className="text-gray-600 hover:text-gray-900">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">{t('title')}</h1>
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

        {/* Two-Factor Authentication Section */}
        <section className="mb-8 rounded-xl bg-white p-6 shadow-sm">
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900">{t('twoFactor.title')}</h2>
            <p className="text-sm text-gray-500 mt-1">
              {t('twoFactor.description')}
            </p>
          </div>

          <div className="flex items-center justify-between py-4 border-t border-b">
            <div>
              <h3 className="font-medium text-gray-900">{t('twoFactor.statusTitle')}</h3>
              <p className="text-sm text-gray-500">
                {twoFactorEnabled ? t('twoFactor.statusEnabled') : t('twoFactor.statusDisabled')}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                twoFactorEnabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {twoFactorEnabled ? t('twoFactor.enabled') : t('twoFactor.disabled')}
              </span>
              {twoFactorEnabled ? (
                <button
                  onClick={handleDisable2FA}
                  className="text-red-600 hover:text-red-700 text-sm font-medium px-4 py-2 rounded-lg hover:bg-red-50"
                >
                  {t('twoFactor.disableButton')}
                </button>
              ) : (
                <button
                  onClick={handleSetup2FA}
                  disabled={isSettingUp}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-50"
                >
                  {isSettingUp ? t('twoFactor.settingUp') : t('twoFactor.enableButton')}
                </button>
              )}
            </div>
          </div>

          {twoFactorEnabled && (
            <div className="mt-4 p-4 bg-green-50 rounded-lg">
              <div className="flex items-start gap-2">
                <svg className="h-5 w-5 text-green-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-green-900">{t('twoFactor.protectedMessage')}</p>
                  <p className="text-sm text-green-700 mt-1">
                    {t('twoFactor.protectedDescription')}
                  </p>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Change Password Section */}
        <section className="mb-8 rounded-xl bg-white p-6 shadow-sm">
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900">{t('password.title')}</h2>
            <p className="text-sm text-gray-500 mt-1">
              {t('password.description')}
            </p>
          </div>

          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label htmlFor="current-password" className="block text-sm font-medium text-gray-700 mb-1">
                {t('password.currentPassword')}
              </label>
              <input
                id="current-password"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                disabled={isChangingPassword}
              />
            </div>

            <div>
              <label htmlFor="new-password" className="block text-sm font-medium text-gray-700 mb-1">
                {t('password.newPassword')}
              </label>
              <input
                id="new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                disabled={isChangingPassword}
              />
              <p className="text-xs text-gray-500 mt-1">
                {t('password.passwordRequirement')}
              </p>
            </div>

            <div>
              <label htmlFor="confirm-password" className="block text-sm font-medium text-gray-700 mb-1">
                {t('password.confirmPassword')}
              </label>
              <input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                disabled={isChangingPassword}
              />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={isChangingPassword}
                className="bg-emerald-600 hover:bg-emerald-700 text-white font-medium px-6 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isChangingPassword ? t('password.changingButton') : t('password.changeButton')}
              </button>
            </div>

            <div className="mt-4 p-4 bg-amber-50 rounded-lg border border-amber-200">
              <div className="flex items-start gap-2">
                <svg className="h-5 w-5 text-amber-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-amber-900">{t('password.securityNoticeTitle')}</p>
                  <p className="text-sm text-amber-700 mt-1">
                    {t('password.securityNoticeDescription')}
                  </p>
                </div>
              </div>
            </div>
          </form>
        </section>

        {/* Back to Settings */}
        <div className="flex justify-end">
          <Link
            href="/settings"
            className="rounded-lg border border-gray-300 px-6 py-2 text-gray-700 hover:bg-gray-50"
          >
            {t('backToSettings')}
          </Link>
        </div>
      </main>

      {/* 2FA Setup Modal */}
      {showSetupModal && setupData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
          <div className="bg-white rounded-xl max-w-lg w-full p-6 shadow-xl">
            <h2 className="text-xl font-bold text-gray-900 mb-4">{t('twoFactorSetup.modalTitle')}</h2>

            <div className="space-y-6">
              {/* Step 1: Scan QR Code */}
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-2">{t('twoFactorSetup.step1Title')}</h3>
                <p className="text-sm text-gray-600 mb-4">
                  {t('twoFactorSetup.step1Description')}
                </p>
                <div className="flex justify-center p-4 bg-gray-50 rounded-lg">
                  <img src={setupData.qr_code} alt="2FA QR Code" className="max-w-full h-auto" />
                </div>
              </div>

              {/* Manual Entry Key */}
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-2">{t('twoFactorSetup.manualEntryTitle')}</h3>
                <div className="bg-gray-50 rounded-lg p-3">
                  <code className="text-sm text-gray-800 font-mono break-all">{setupData.manual_entry_key}</code>
                </div>
              </div>

              {/* Step 2: Enter Verification Code */}
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-2">{t('twoFactorSetup.step2Title')}</h3>
                <p className="text-sm text-gray-600 mb-3">
                  {t('twoFactorSetup.step2Description')}
                </p>
                <input
                  type="text"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder={t('twoFactorSetup.verificationPlaceholder')}
                  maxLength={6}
                  className="block w-full text-center text-2xl font-mono tracking-widest rounded-lg border border-gray-300 px-4 py-3 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                />
              </div>

              {/* Error in modal */}
              {error && (
                <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-red-800 text-sm">
                  {error}
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => {
                    setShowSetupModal(false)
                    setSetupData(null)
                    setVerificationCode('')
                    setError('')
                  }}
                  className="flex-1 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg border border-gray-300"
                >
                  {t('twoFactorSetup.cancel')}
                </button>
                <button
                  onClick={handleVerify2FA}
                  disabled={isVerifying || verificationCode.length !== 6}
                  className="flex-1 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isVerifying ? t('twoFactorSetup.verifying') : t('twoFactorSetup.verifyButton')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
