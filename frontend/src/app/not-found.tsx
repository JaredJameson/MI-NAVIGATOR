'use client'

import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-md text-center">
        {/* 404 Icon */}
        <div className="mb-8">
          <div className="mx-auto flex h-32 w-32 items-center justify-center rounded-full bg-blue-100">
            <svg
              className="h-16 w-16 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
        </div>

        {/* Error Code */}
        <h1 className="mb-4 text-7xl font-bold text-gray-800">404</h1>

        {/* Error Message */}
        <h2 className="mb-2 text-2xl font-semibold text-gray-700">
          Strona nie znaleziona
        </h2>
        <p className="mb-8 text-gray-600">
          Strona której szukasz nie istnieje lub została przeniesiona.
        </p>

        {/* Navigation Options */}
        <div className="flex flex-col gap-3">
          <Link
            href="/dashboard"
            className="rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Przejdź do Dashboardu
          </Link>
          <Link
            href="/chat"
            className="rounded-lg border border-gray-300 bg-white px-6 py-3 font-medium text-gray-700 transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Rozpocznij nowe badanie
          </Link>
          <button
            onClick={() => window.history.back()}
            className="rounded-lg px-6 py-3 font-medium text-gray-600 transition-colors hover:text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            ← Wróć
          </button>
        </div>

        {/* Helpful Links */}
        <div className="mt-8 border-t border-gray-200 pt-6">
          <p className="mb-3 text-sm text-gray-500">Potrzebujesz pomocy? Wypróbuj:</p>
          <div className="flex flex-wrap justify-center gap-4 text-sm">
            <Link
              href="/reports"
              className="text-blue-600 hover:underline focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Raporty
            </Link>
            <Link
              href="/projects"
              className="text-blue-600 hover:underline focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Projekty
            </Link>
            <Link
              href="/settings"
              className="text-blue-600 hover:underline focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Ustawienia
            </Link>
            <Link
              href="/search"
              className="text-blue-600 hover:underline focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Wyszukiwanie
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
