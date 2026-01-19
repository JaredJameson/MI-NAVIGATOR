'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { FeatureFlagProvider } from '@/contexts/FeatureFlagContext'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { setupGlobalErrorHandlers } from '@/services/errorTracking'
import { OfflineIndicator } from '@/components/OfflineIndicator'
import { SyncManager } from '@/components/SyncManager'
import { ServiceWorkerRegister } from '@/components/ServiceWorkerRegister'
import { CSRFTokenInitializer } from '@/components/CSRFTokenInitializer'
import KeyboardShortcutsHelp from '@/components/KeyboardShortcutsHelp'
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            refetchOnWindowFocus: false,
          },
        },
      })
  )

  // Setup global error handlers
  useEffect(() => {
    setupGlobalErrorHandlers();
  }, []);

  // Setup global keyboard shortcuts
  useKeyboardShortcuts();

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <FeatureFlagProvider>
          <CSRFTokenInitializer />
          <ServiceWorkerRegister />
          <OfflineIndicator />
          <SyncManager />
          <KeyboardShortcutsHelp />
          <AuthGuard>
            {children}
          </AuthGuard>
        </FeatureFlagProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}
