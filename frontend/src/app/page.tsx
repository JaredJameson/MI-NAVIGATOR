'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to dashboard or login based on auth status
    // For now, redirect to login
    router.push('/auth/login')
  }, [router])

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="animate-pulse text-lg text-muted-foreground">
        Loading MI-Navigator...
      </div>
    </div>
  )
}
