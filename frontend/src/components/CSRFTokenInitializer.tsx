'use client'

import { useEffect } from 'react'
import { fetchCsrfToken, getCsrfToken } from '@/services/api'

/**
 * Component to initialize CSRF token on app load
 *
 * This ensures that users who remain logged in across sessions
 * have a valid CSRF token for POST/PUT/DELETE/PATCH requests.
 */
export function CSRFTokenInitializer() {
  useEffect(() => {
    const initializeCsrfToken = async () => {
      // Check if CSRF token already exists
      const existingToken = getCsrfToken()

      if (!existingToken) {
        console.log('[CSRF] No token found, fetching new token...')
        const token = await fetchCsrfToken()

        if (token) {
          console.log('[CSRF] Token initialized successfully')
        } else {
          console.error('[CSRF] Failed to fetch token')
        }
      } else {
        console.log('[CSRF] Token already exists')
      }
    }

    initializeCsrfToken()
  }, [])

  // This component doesn't render anything
  return null
}
