import { useState, useEffect } from 'react'
import { getStoredToken } from '@/services/api'
import enMessages from '@/locales/en.json'
import plMessages from '@/locales/pl.json'

type Messages = typeof enMessages
type MessageKey = string

const messages: Record<string, Messages> = {
  en: enMessages,
  pl: plMessages,
}

export function useLocale() {
  const [locale, setLocale] = useState<string>('en')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Get locale from user profile
    const fetchUserLocale = async () => {
      try {
        const token = getStoredToken()
        if (!token) {
          console.log('[useLocale] No token found, using default locale')
          setIsLoading(false)
          return
        }

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api/proxy';
        const response = await fetch(`${apiUrl}/users/me`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        })

        if (response.ok) {
          const data = await response.json()
          const userLocale = data.preferred_language || 'en'
          console.log('[useLocale] Loaded user locale:', userLocale)
          setLocale(userLocale)
        } else {
          console.log('[useLocale] Failed to fetch profile, status:', response.status)
        }
      } catch (error) {
        console.error('[useLocale] Failed to fetch user locale:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchUserLocale()
  }, [])

  const t = (key: MessageKey, defaultValue?: string): string => {
    const keys = key.split('.')
    let value: any = messages[locale]

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k]
      } else {
        console.log(`[useLocale] Translation not found for key: ${key}, locale: ${locale}`)
        return defaultValue || key
      }
    }

    const result = typeof value === 'string' ? value : defaultValue || key
    console.log(`[useLocale] t("${key}") = "${result}" (locale: ${locale})`)
    return result
  }

  return { locale, t, isLoading }
}
