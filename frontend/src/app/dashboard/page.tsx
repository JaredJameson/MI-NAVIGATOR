'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { authApi } from '@/services/api'

export default function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const router = useRouter()

  const handleLogout = async () => {
    setIsLoggingOut(true)
    try {
      await authApi.logout()
      router.push('/auth/login')
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      setIsLoggingOut(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">MI-Navigator</h1>
            <nav className="flex items-center space-x-4">
              <Link href="/reports" className="text-gray-600 hover:text-gray-900">
                Reports
              </Link>
              <Link href="/projects" className="text-gray-600 hover:text-gray-900">
                Projects
              </Link>
              <Link href="/settings" className="text-gray-600 hover:text-gray-900">
                Settings
              </Link>
              <button
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="rounded-md bg-red-600 px-3 py-1.5 text-sm text-white hover:bg-red-700 disabled:opacity-50"
              >
                {isLoggingOut ? 'Logging out...' : 'Logout'}
              </button>
            </nav>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Quick Search */}
        <div className="mb-8 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white">
          <h2 className="mb-4 text-xl font-semibold">Rozpocznij badanie</h2>
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Szukaj firmy, osoby, wklej URL do analizy..."
              className="w-full rounded-lg bg-white px-4 py-3 pl-12 text-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-white"
            />
            <svg
              className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="text-sm text-blue-200">Ostatnie:</span>
            <button className="rounded bg-white/20 px-2 py-1 text-sm hover:bg-white/30">
              FADO Sp. z o.o.
            </button>
            <button className="rounded bg-white/20 px-2 py-1 text-sm hover:bg-white/30">
              Splast S.A.
            </button>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Active Research Card */}
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <h3 className="mb-4 font-semibold text-gray-900">Active Research</h3>
            <div className="rounded-lg bg-gray-50 p-4">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />
                <span className="text-sm font-medium">Analiza FADO</span>
              </div>
              <div className="mt-2">
                <div className="text-sm text-gray-500">Progress: 67%</div>
                <div className="mt-1 h-2 rounded-full bg-gray-200">
                  <div className="h-full w-2/3 rounded-full bg-blue-500" />
                </div>
              </div>
            </div>
            <Link
              href="/chat"
              className="mt-4 inline-block rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
            >
              Start New Research
            </Link>
          </div>

          {/* Recent Activity Card */}
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <h3 className="mb-4 font-semibold text-gray-900">Recent Activity</h3>
            <ul className="space-y-3">
              <li className="text-sm">
                <span className="text-gray-500">14:32</span> - Raport FADO zakończony
              </li>
              <li className="text-sm">
                <span className="text-gray-500">12:15</span> - Nowy alert: Konkurent X
              </li>
              <li className="text-sm">
                <span className="text-gray-500">11:45</span> - Upload: raport_q3.pdf
              </li>
            </ul>
            <Link href="/activity" className="mt-4 inline-block text-sm text-blue-600 hover:underline">
              Zobacz wszystkie →
            </Link>
          </div>

          {/* Usage Stats Card */}
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <h3 className="mb-4 font-semibold text-gray-900">Usage Stats</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Analyses this month</span>
                  <span className="font-medium">42/100</span>
                </div>
                <div className="mt-1 h-2 rounded-full bg-gray-200">
                  <div className="h-full w-[42%] rounded-full bg-blue-500" />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Storage</span>
                  <span className="font-medium">2.4 GB / 10 GB</span>
                </div>
                <div className="mt-1 h-2 rounded-full bg-gray-200">
                  <div className="h-full w-[24%] rounded-full bg-green-500" />
                </div>
              </div>
              <div className="text-sm text-gray-600">
                API calls: <span className="font-medium">8,432</span>
              </div>
            </div>
          </div>
        </div>

        {/* My Projects Section */}
        <section className="mt-8">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">My Projects</h2>
            <Link
              href="/projects/new"
              className="rounded-md bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700"
            >
              + New
            </Link>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {['Due Diligence - ACME Corp', 'Market Entry - Germany', 'Competitive Watch'].map(
              (project) => (
                <div
                  key={project}
                  className="cursor-pointer rounded-xl bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">📁</span>
                    <div>
                      <h3 className="font-medium text-gray-900">{project}</h3>
                      <div className="mt-2 flex gap-4 text-sm text-gray-500">
                        <span>📄 5 reports</span>
                        <span>🔔 3 alerts</span>
                      </div>
                      <div className="mt-2 text-xs text-gray-400">Updated: 2 days ago</div>
                    </div>
                  </div>
                </div>
              )
            )}
          </div>
        </section>

        {/* Alerts Section */}
        <section className="mt-8">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Alerts & Monitoring</h2>
          <div className="space-y-2">
            <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-3">
              <span>🔴</span>
              <div>
                <p className="text-sm font-medium text-red-800">Konkurent X: nowy produkt</p>
                <p className="text-xs text-red-600">Wykryto ogłoszenie nowego produktu</p>
              </div>
            </div>
            <div className="flex items-start gap-2 rounded-lg border border-yellow-200 bg-yellow-50 p-3">
              <span>🟡</span>
              <div>
                <p className="text-sm font-medium text-yellow-800">FADO: zmiana w zarządzie</p>
                <p className="text-xs text-yellow-600">Nowy członek zarządu</p>
              </div>
            </div>
            <div className="flex items-start gap-2 rounded-lg border border-green-200 bg-green-50 p-3">
              <span>🟢</span>
              <div>
                <p className="text-sm font-medium text-green-800">Rynek +5% vs prognoza</p>
                <p className="text-xs text-green-600">Pozytywny trend rynkowy</p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
