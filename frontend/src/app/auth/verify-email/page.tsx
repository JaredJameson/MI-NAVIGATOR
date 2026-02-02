"use client"

import { useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'

export default function VerifyEmailPage() {
  const t = useTranslations('auth')
  const router = useRouter()
  const searchParams = useSearchParams()
  const email = searchParams.get('email') || ''

  const [isResending, setIsResending] = useState(false)
  const [resendMessage, setResendMessage] = useState('')
  const [resendError, setResendError] = useState('')

  const handleResend = async () => {
    if (!email) {
      setResendError(t('verifyEmail.errors.emailMissing'))
      return
    }

    setIsResending(true)
    setResendMessage('')
    setResendError('')

    try {
      const response = await fetch('http://localhost:8100/api/v1/auth/resend-verification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      })

      if (response.ok) {
        setResendMessage(t('verifyEmail.success.resent'))
      } else if (response.status === 429) {
        const data = await response.json()
        setResendError(data.detail || t('verifyEmail.errors.tooManyRequests'))
      } else {
        setResendError(t('verifyEmail.errors.resendFailed'))
      }
    } catch (error) {
      setResendError(t('verifyEmail.errors.networkError'))
    } finally {
      setIsResending(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-purple-50 px-4">
      <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-lg">
        {/* Icon */}
        <div className="flex justify-center">
          <div className="w-20 h-20 bg-indigo-100 rounded-full flex items-center justify-center">
            <svg
              className="w-10 h-10 text-indigo-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
        </div>

        {/* Title */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">
            {t('verifyEmail.title')}
          </h2>
          <p className="mt-4 text-gray-600">
            {t('verifyEmail.subtitle')}
          </p>
          {email && (
            <p className="mt-2 text-lg font-semibold text-indigo-600">
              {email}
            </p>
          )}
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">
            {t('verifyEmail.instructionsHeading')}
          </h3>
          <ol className="text-sm text-blue-800 space-y-2 list-decimal list-inside">
            <li>{t('verifyEmail.instructionsStep1')}</li>
            <li>{t('verifyEmail.instructionsStep2')}</li>
            <li>{t('verifyEmail.instructionsStep3')}</li>
            <li>{t('verifyEmail.instructionsStep4')}</li>
          </ol>
        </div>

        {/* Warning */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            <strong>⚠️ {t('verifyEmail.warningLabel')}</strong> {t('verifyEmail.expirationWarning')}
          </p>
        </div>

        {/* Resend Section */}
        <div className="space-y-4">
          <div className="text-center text-sm text-gray-600">
            {t('verifyEmail.didntReceive')}
          </div>

          {resendMessage && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
              <p className="text-sm text-green-800 text-center">
                ✅ {resendMessage}
              </p>
            </div>
          )}

          {resendError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-sm text-red-800 text-center">
                ❌ {resendError}
              </p>
            </div>
          )}

          <button
            onClick={handleResend}
            disabled={isResending || !email}
            className="w-full py-3 px-4 border border-indigo-600 text-indigo-600 rounded-lg font-semibold hover:bg-indigo-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isResending ? t('verifyEmail.resendingButton') : t('verifyEmail.resendButton')}
          </button>
        </div>

        {/* Tips */}
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-xs text-gray-600 mb-2">
            <strong>💡 {t('verifyEmail.tipsLabel')}</strong> {t('verifyEmail.tipsSpam')}
          </p>
          <p className="text-xs text-gray-600">
            {t('verifyEmail.tipsAddContact')}
          </p>
        </div>

        {/* Back to Login */}
        <div className="text-center">
          <button
            onClick={() => router.push('/auth/login')}
            className="text-sm text-gray-600 hover:text-indigo-600 transition"
          >
            {t('verifyEmail.backToLogin')}
          </button>
        </div>
      </div>
    </div>
  )
}
