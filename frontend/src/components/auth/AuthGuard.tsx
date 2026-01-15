'use client'

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { getStoredToken } from '@/services/api'

interface AuthGuardProps {
  children: React.ReactNode
}

// Routes that don't require authentication
const publicRoutes = ['/auth/login', '/auth/register', '/auth/forgot-password', '/auth/reset-password']

export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter()
  const pathname = usePathname()
  const [isChecking, setIsChecking] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const checkAuth = () => {
      const token = getStoredToken()
      const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route))

      if (!token && !isPublicRoute) {
        // Not authenticated and trying to access protected route
        router.push('/auth/login')
        return
      }

      if (token && pathname.startsWith('/auth/')) {
        // Already authenticated, redirect to dashboard
        router.push('/dashboard')
        return
      }

      setIsAuthenticated(!!token || isPublicRoute)
      setIsChecking(false)
    }

    checkAuth()
  }, [pathname, router])

  if (isChecking) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return <>{children}</>
}
