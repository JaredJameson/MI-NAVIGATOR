"use client"

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useTranslations } from 'next-intl'

type VerificationStatus = 'loading' | 'success' | 'error' | 'already_verified'

export default function VerifyTokenPage() {
  const t = useTranslations('auth')
  const router = useRouter()
  const params = useParams()
  const token = params.token as string

  const [status, setStatus] = useState<VerificationStatus>('loading')
  const [errorMessage, setErrorMessage] = useState('')
  const [countdown, setCountdown] = useState(3)

  useEffect(() => {
    const verifyEmail = async () => {
      if (!token) {
        setStatus('error')
        setErrorMessage(t('verifyToken.error.invalidLink'))
        return
      }

      try {
        const response = await fetch(`http://localhost:8100/api/v1/auth/verify-email/${token}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })

        const data = await response.json()

        if (response.ok) {
          if (data.message === 'Email already verified') {
            setStatus('already_verified')
          } else {
            setStatus('success')
          }
        } else {
          setStatus('error')
          setErrorMessage(data.detail || t('verifyToken.error.verificationFailed'))
        }
      } catch (error) {
        setStatus('error')
        setErrorMessage(t('verifyToken.error.networkError'))
      }
    }

    verifyEmail()
  }, [token])

  useEffect(() => {
    if (status === 'success' && countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown(countdown - 1)
      }, 1000)

      return () => clearTimeout(timer)
    } else if (status === 'success' && countdown === 0) {
      router.push('/dashboard')
    }
  }, [status, countdown, router])

  const renderContent = () => {
    switch (status) {
      case 'loading':
        return (
          <>
            <div className="flex justify-center">
              <div className="w-20 h-20 bg-indigo-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-10 h-10 text-indigo-600 animate-spin"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
              </div>
            </div>

            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900">
                {t('verifyToken.loading.title')}
              </h2>
              <p className="mt-4 text-gray-600">
                {t('verifyToken.loading.message')}
              </p>
            </div>
          </>
        )

      case 'success':
        return (
          <>
            <div className="flex justify-center">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-10 h-10 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>

            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900">
                {t('verifyToken.success.title')}
              </h2>
              <p className="mt-4 text-gray-600">
                {t('verifyToken.success.message')}
              </p>
              <p className="mt-2 text-gray-600">
                {t('verifyToken.success.redirecting', { countdown })}
              </p>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-sm font-semibold text-green-900 mb-3">
                {t('verifyToken.success.accountActiveHeading')}
              </h3>
              <ul className="text-sm text-green-800 space-y-2 list-disc list-inside">
                <li>{t('verifyToken.success.feature1')}</li>
                <li>{t('verifyToken.success.feature2')}</li>
                <li>{t('verifyToken.success.feature3')}</li>
                <li>{t('verifyToken.success.feature4')}</li>
              </ul>
            </div>

            <button
              onClick={() => router.push('/dashboard')}
              className="w-full py-3 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition"
            >
              {t('verifyToken.success.goToDashboard')}
            </button>
          </>
        )

      case 'already_verified':
        return (
          <>
            <div className="flex justify-center">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-10 h-10 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>

            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900">
                {t('verifyToken.alreadyVerified.title')}
              </h2>
              <p className="mt-4 text-gray-600">
                {t('verifyToken.alreadyVerified.message')}
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800 text-center">
                {t('verifyToken.alreadyVerified.infoMessage')}
              </p>
            </div>

            <button
              onClick={() => router.push('/auth/login')}
              className="w-full py-3 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition"
            >
              {t('verifyToken.alreadyVerified.goToLogin')}
            </button>
          </>
        )

      case 'error':
        return (
          <>
            <div className="flex justify-center">
              <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-10 h-10 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>

            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900">
                {t('verifyToken.error.title')}
              </h2>
              <p className="mt-4 text-gray-600">
                {errorMessage || t('verifyToken.error.messageFallback')}
              </p>
            </div>

            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-red-900 mb-2">
                {t('verifyToken.error.possibleReasonsHeading')}
              </h3>
              <ul className="text-sm text-red-800 space-y-1 list-disc list-inside">
                <li>{t('verifyToken.error.reason1')}</li>
                <li>{t('verifyToken.error.reason2')}</li>
                <li>{t('verifyToken.error.reason3')}</li>
              </ul>
            </div>

            <div className="space-y-3">
              <button
                onClick={() => router.push('/auth/login')}
                className="w-full py-3 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition"
              >
                {t('verifyToken.error.goToLogin')}
              </button>

              <button
                onClick={() => router.push('/auth/register')}
                className="w-full py-3 px-4 border border-indigo-600 text-indigo-600 rounded-lg font-semibold hover:bg-indigo-50 transition"
              >
                {t('verifyToken.error.registerAgain')}
              </button>
            </div>
          </>
        )
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-purple-50 px-4">
      <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-lg">
        {renderContent()}
      </div>
    </div>
  )
}
