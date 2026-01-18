'use client'

import { useEffect, useState } from 'react'

export default function TestPWAPage() {
  const [swStatus, setSwStatus] = useState<string>('Checking...')
  const [swDetails, setSwDetails] = useState<any>(null)

  useEffect(() => {
    checkServiceWorker()
  }, [])

  const checkServiceWorker = async () => {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.getRegistration()
        if (registration) {
          setSwStatus('✅ Service Worker Registered!')
          setSwDetails({
            scope: registration.scope,
            state: registration.active?.state || registration.installing?.state || registration.waiting?.state,
            scriptURL: registration.active?.scriptURL || registration.installing?.scriptURL || registration.waiting?.scriptURL,
          })
        } else {
          setSwStatus('❌ Service Worker NOT Registered')
          // Try to register manually
          const reg = await navigator.serviceWorker.register('/sw.js')
          setSwStatus('✅ Service Worker Registered Manually!')
          setSwDetails({
            scope: reg.scope,
            state: 'installing',
            scriptURL: reg.installing?.scriptURL,
          })
        }
      } catch (error) {
        setSwStatus(`❌ Error: ${error}`)
      }
    } else {
      setSwStatus('❌ Service Workers not supported')
    }
  }

  const testCache = async () => {
    const cache = await caches.open('offlineCache')
    const keys = await cache.keys()
    console.log('Cached resources:', keys.length)
    return keys.length
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">PWA Service Worker Test</h1>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Service Worker Status</h2>
          <p className="text-lg mb-4">{swStatus}</p>

          {swDetails && (
            <div className="bg-gray-100 p-4 rounded">
              <p className="text-sm font-mono mb-2"><strong>Scope:</strong> {swDetails.scope}</p>
              <p className="text-sm font-mono mb-2"><strong>State:</strong> {swDetails.state}</p>
              <p className="text-sm font-mono"><strong>Script URL:</strong> {swDetails.scriptURL}</p>
            </div>
          )}

          <button
            onClick={checkServiceWorker}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Recheck Service Worker
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Test Instructions</h2>
          <ol className="list-decimal list-inside space-y-2">
            <li>Load this page (Step 1: Load application) ✅</li>
            <li>Check service worker registration status above (Step 2) ✅</li>
            <li>Open DevTools → Application → Service Workers to verify</li>
            <li>Go offline (DevTools → Network → Offline checkbox) (Step 3)</li>
            <li>Try navigating to /dashboard (Step 4: Verify cached pages accessible)</li>
            <li>Check offline indicator appears (Step 5: Verify appropriate offline UX)</li>
          </ol>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Manual Tests</h2>
          <div className="space-y-2">
            <button
              onClick={async () => {
                const count = await testCache()
                alert(`Cached resources: ${count}`)
              }}
              className="block w-full px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              Test Cache (Check Console)
            </button>
            <a
              href="/dashboard"
              className="block w-full px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 text-center"
            >
              Go to Dashboard (Test Offline Navigation)
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
