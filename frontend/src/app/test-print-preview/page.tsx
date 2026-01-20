'use client'

import { useState } from 'react'

export default function TestPrintPreviewPage() {
  const handlePrint = () => {
    window.print()
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      {/* Page Header - with actions (hidden in print) */}
      <div className="mb-8 flex items-center justify-between rounded-lg bg-white p-6 shadow-md">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Test Print Preview - Feature #224</h1>
          <p className="mt-2 text-gray-600">Kliknij przycisk "Drukuj" aby zobaczyć podgląd wydruku (Ctrl+P)</p>
        </div>

        <div className="no-print flex gap-3">
          <button
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
          >
            Udostępnij
          </button>
          <button
            onClick={handlePrint}
            className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
            title="Drukuj raport (Ctrl+P)"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            Drukuj
          </button>
          <button
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          >
            Eksportuj PDF
          </button>
        </div>
      </div>

      {/* Report Content - will be printed */}
      <div className="mx-auto max-w-4xl rounded-lg bg-white p-8 shadow-md">
        {/* Report Title */}
        <header className="mb-8 border-b pb-6">
          <h1 className="mb-2 text-4xl font-bold text-gray-900">
            Analiza Rynku: Branża Automotive w Polsce
          </h1>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <span>Data utworzenia: 20 stycznia 2026</span>
            <span>•</span>
            <span>Typ: Analiza rynku</span>
            <span>•</span>
            <span>Status: Ukończony</span>
          </div>
        </header>

        {/* Executive Summary */}
        <section className="mb-8">
          <h2 className="mb-4 text-2xl font-bold text-gray-900">Podsumowanie wykonawcze</h2>
          <p className="mb-4 leading-relaxed text-gray-700">
            Polska branża automotive przeżywa obecnie okres intensywnych zmian napędzanych
            transformacją energetyczną i rosnącym udziałem pojazdów elektrycznych. Wartość
            rynku szacowana jest na 150 mld PLN rocznie, z prognozowanym wzrostem na
            poziomie 8% CAGR w latach 2024-2028.
          </p>
          <p className="leading-relaxed text-gray-700">
            Kluczowe wnioski analizy wskazują na rosnącą konkurencję ze strony producentów
            azjatyckich oraz potrzebę dalszej automatyzacji procesów produkcyjnych.
          </p>
        </section>

        {/* Market Size */}
        <section className="mb-8">
          <h2 className="mb-4 text-2xl font-bold text-gray-900">Wielkość rynku</h2>
          <div className="rounded-lg bg-blue-50 p-6">
            <div className="mb-4 grid grid-cols-3 gap-4">
              <div>
                <div className="text-sm text-gray-600">TAM</div>
                <div className="text-2xl font-bold text-blue-600">250 mld PLN</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">SAM</div>
                <div className="text-2xl font-bold text-blue-600">150 mld PLN</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">SOM</div>
                <div className="text-2xl font-bold text-blue-600">45 mld PLN</div>
              </div>
            </div>
            <p className="text-sm text-gray-700">
              Prognozowany wzrost: <strong>8% CAGR (2024-2028)</strong>
            </p>
          </div>
        </section>

        {/* Competitive Landscape */}
        <section className="mb-8">
          <h2 className="mb-4 text-2xl font-bold text-gray-900">Krajobraz konkurencyjny</h2>
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b-2 border-gray-300">
                <th className="py-3 text-left font-semibold text-gray-900">Firma</th>
                <th className="py-3 text-left font-semibold text-gray-900">Udział rynku</th>
                <th className="py-3 text-left font-semibold text-gray-900">Segment</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-200">
                <td className="py-3 text-gray-700">Volkswagen Poznań</td>
                <td className="py-3 text-gray-700">18.5%</td>
                <td className="py-3 text-gray-700">Samochody osobowe</td>
              </tr>
              <tr className="border-b border-gray-200">
                <td className="py-3 text-gray-700">Fiat Poland</td>
                <td className="py-3 text-gray-700">12.3%</td>
                <td className="py-3 text-gray-700">Małe samochody</td>
              </tr>
              <tr className="border-b border-gray-200">
                <td className="py-3 text-gray-700">Opel Manufacturing</td>
                <td className="py-3 text-gray-700">9.8%</td>
                <td className="py-3 text-gray-700">Vany i SUV</td>
              </tr>
              <tr className="border-b border-gray-200">
                <td className="py-3 text-gray-700">Toyota Motor Poland</td>
                <td className="py-3 text-gray-700">7.2%</td>
                <td className="py-3 text-gray-700">Hybrydowe</td>
              </tr>
            </tbody>
          </table>
        </section>

        {/* Key Findings */}
        <section className="mb-8">
          <h2 className="mb-4 text-2xl font-bold text-gray-900">Kluczowe wnioski</h2>
          <ul className="space-y-3">
            <li className="flex gap-3">
              <span className="text-green-600">✓</span>
              <span className="text-gray-700">
                <strong>Wzrost elektromobilności:</strong> Udział pojazdów elektrycznych wzrósł
                z 2% do 8% w ciągu ostatnich 2 lat.
              </span>
            </li>
            <li className="flex gap-3">
              <span className="text-green-600">✓</span>
              <span className="text-gray-700">
                <strong>Inwestycje w automatyzację:</strong> Branża inwestuje 15 mld PLN
                rocznie w nowe technologie produkcji.
              </span>
            </li>
            <li className="flex gap-3">
              <span className="text-yellow-600">⚠</span>
              <span className="text-gray-700">
                <strong>Presja cenowa:</strong> Rosnąca konkurencja ze strony producentów
                azjatyckich wpływa na marże.
              </span>
            </li>
            <li className="flex gap-3">
              <span className="text-red-600">✗</span>
              <span className="text-gray-700">
                <strong>Niedobór talentów:</strong> Brak wykwalifikowanych pracowników
                hamuje rozwój branży.
              </span>
            </li>
          </ul>
        </section>

        {/* Recommendations */}
        <section className="mb-8">
          <h2 className="mb-4 text-2xl font-bold text-gray-900">Rekomendacje</h2>
          <div className="space-y-4">
            <div className="rounded-lg border-l-4 border-blue-600 bg-blue-50 p-4">
              <h3 className="mb-2 font-semibold text-gray-900">1. Przyspieszenie transformacji elektrycznej</h3>
              <p className="text-sm text-gray-700">
                Firmy powinny zwiększyć inwestycje w rozwój platform elektrycznych oraz
                budowę infrastruktury ładowania.
              </p>
            </div>
            <div className="rounded-lg border-l-4 border-green-600 bg-green-50 p-4">
              <h3 className="mb-2 font-semibold text-gray-900">2. Rozwój kompetencji cyfrowych</h3>
              <p className="text-sm text-gray-700">
                Inwestycje w szkolenia pracowników w zakresie nowych technologii produkcji
                i digitalizacji procesów.
              </p>
            </div>
            <div className="rounded-lg border-l-4 border-purple-600 bg-purple-50 p-4">
              <h3 className="mb-2 font-semibold text-gray-900">3. Współpraca z start-upami</h3>
              <p className="text-sm text-gray-700">
                Partnerstwa z firmami technologicznymi mogą przyspieszyć innowacje i
                obniżyć koszty R&D.
              </p>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t pt-6 text-center text-sm text-gray-500">
          <p>Raport wygenerowany przez MI-Navigator • Market Intelligence Platform</p>
          <p className="mt-1">© 2026 MI-Navigator. Wszystkie prawa zastrzeżone.</p>
        </footer>
      </div>

      {/* Instructions (hidden in print) */}
      <div className="no-print mt-8 rounded-lg bg-yellow-50 p-6 text-center">
        <h2 className="mb-2 text-lg font-semibold text-gray-900">Instrukcje testowania:</h2>
        <ol className="mx-auto max-w-2xl space-y-2 text-left text-sm text-gray-700">
          <li><strong>Krok 1:</strong> Kliknij przycisk "Drukuj" powyżej lub naciśnij Ctrl+P</li>
          <li><strong>Krok 2:</strong> Sprawdź czy podgląd wydruku się pojawił</li>
          <li><strong>Krok 3:</strong> Zweryfikuj że przyciski akcji (Udostępnij, Drukuj, Eksportuj) NIE są widoczne</li>
          <li><strong>Krok 4:</strong> Zweryfikuj że formatowanie jest poprawne (czcionki, odstępy, kolory)</li>
          <li><strong>Krok 5:</strong> Zweryfikuj że podziały stron są odpowiednie (brak ciętych nagłówków/tabel)</li>
        </ol>
      </div>
    </div>
  )
}
