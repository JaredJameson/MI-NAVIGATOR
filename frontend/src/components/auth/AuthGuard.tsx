'use client'

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { getStoredToken } from '@/services/api'

interface AuthGuardProps {
  children: React.ReactNode
}

// Routes that don't require authentication
const publicRoutes = [
  '/auth/login',
  '/auth/register',
  '/auth/forgot-password',
  '/auth/reset-password',
  '/onboarding',
  '/test-table-sorting',
  '/test-print-preview'
]

export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter()
  const pathname = usePathname()

  // Check auth synchronously during initial render
  const token = typeof window !== 'undefined' ? getStoredToken() : null
  const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route))
  const shouldBeAuthenticated = !isPublicRoute
  const isAuthenticated = !!token

  const [hasChecked, setHasChecked] = useState(false)

  useEffect(() => {
    // Redirect if not authenticated and on protected route
    if (!token && shouldBeAuthenticated) {
      // BUGFIX Session 375 (Feature #122): Save intended URL for post-login redirect
      const redirectUrl = encodeURIComponent(pathname)
      router.push(`/auth/login?redirect=${redirectUrl}`)
      return
    }

    // Redirect if authenticated and on auth page
    if (token && pathname.startsWith('/auth/')) {
      router.push('/dashboard')
      return
    }

    setHasChecked(true)
  }, [pathname, router, token, shouldBeAuthenticated])

  // Block rendering for protected routes without token
  if (shouldBeAuthenticated && !isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
      </div>
    )
  }

  // Show loading during redirect
  if (!hasChecked) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
      </div>
    )
  }

  return <>{children}</>
}
