'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { companyApi, CompanyComparison, CompanyProfile } from '@/services/api';

export default function CompareCompaniesPage() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const company1IdParam = searchParams.get('company1');
  const company2IdParam = searchParams.get('company2');

  const [company1Id, setCompany1Id] = useState(company1IdParam || '');
  const [company2Id, setCompany2Id] = useState(company2IdParam || '');
  const [comparison, setComparison] = useState<CompanyComparison | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchResults1, setSearchResults1] = useState<CompanyProfile[]>([]);
  const [searchResults2, setSearchResults2] = useState<CompanyProfile[]>([]);
  const [showDropdown1, setShowDropdown1] = useState(false);
  const [showDropdown2, setShowDropdown2] = useState(false);

  // Mock company suggestions (in real app, this would fetch from API)
  const mockCompanies = [
    { id: '1111111111', name: 'FADO Sp. z o.o.', nip: '1111111111', krs: '0000111111' },
    { id: '2222222222', name: 'PlastPak Sp. z o.o.', nip: '2222222222', krs: '0000222222' },
    { id: '3333333333', name: 'MetalPro S.A.', nip: '3333333333', krs: '0000333333' },
  ];

  // Load comparison when both companies are selected
  useEffect(() => {
    if (company1Id && company2Id) {
      loadComparison();
    }
  }, [company1Id, company2Id]);

  async function loadComparison() {
    setLoading(true);
    setError(null);

    const result = await companyApi.compareCompanies(company1Id, company2Id);
    if (result.error) {
      setError(result.error);
    } else if (result.data) {
      setComparison(result.data);
      // Update URL
      const params = new URLSearchParams();
      params.set('company1', company1Id);
      params.set('company2', company2Id);
      router.push(`/compare?${params.toString()}`, { scroll: false });
    }
    setLoading(false);
  }

  function handleCompany1Select(companyId: string) {
    setCompany1Id(companyId);
    setShowDropdown1(false);
  }

  function handleCompany2Select(companyId: string) {
    setCompany2Id(companyId);
    setShowDropdown2(false);
  }

  function getWinnerClass(winner?: string, position?: 'company1' | 'company2') {
    if (!winner || winner === 'tie') return '';
    return winner === position ? 'bg-green-50 border-green-300' : 'bg-gray-50';
  }

  function getWinnerBadge(winner?: string) {
    if (!winner) return null;
    if (winner === 'tie') {
      return <span className="ml-2 px-2 py-0.5 bg-gray-200 text-gray-700 text-xs rounded">≈</span>;
    }
    return <span className="ml-2 px-2 py-0.5 bg-green-200 text-green-700 text-xs rounded">✓</span>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Porównanie firm</h1>
              <p className="mt-2 text-gray-600">Porównaj dwie firmy obok siebie</p>
            </div>
            <Link
              href="/dashboard"
              className="text-gray-600 hover:text-gray-900"
            >
              ← Powrót
            </Link>
          </div>
        </div>

        {/* Company Selection */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Wybierz firmy do porównania</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Company 1 Selector */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Firma 1
              </label>
              <input
                type="text"
                value={company1Id}
                onChange={(e) => {
                  setCompany1Id(e.target.value);
                  setShowDropdown1(e.target.value.length > 0);
                }}
                onFocus={() => setShowDropdown1(company1Id.length > 0)}
                placeholder="Wpisz NIP, KRS, REGON lub nazwę..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              {showDropdown1 && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                  {mockCompanies.map((company) => (
                    <button
                      key={company.id}
                      onClick={() => handleCompany1Select(company.id)}
                      className="w-full text-left px-4 py-2 hover:bg-blue-50 transition-colors"
                    >
                      <div className="font-medium">{company.name}</div>
                      <div className="text-sm text-gray-600">NIP: {company.nip}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Company 2 Selector */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Firma 2
              </label>
              <input
                type="text"
                value={company2Id}
                onChange={(e) => {
                  setCompany2Id(e.target.value);
                  setShowDropdown2(e.target.value.length > 0);
                }}
                onFocus={() => setShowDropdown2(company2Id.length > 0)}
                placeholder="Wpisz NIP, KRS, REGON lub nazwę..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              {showDropdown2 && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                  {mockCompanies.map((company) => (
                    <button
                      key={company.id}
                      onClick={() => handleCompany2Select(company.id)}
                      className="w-full text-left px-4 py-2 hover:bg-blue-50 transition-colors"
                    >
                      <div className="font-medium">{company.name}</div>
                      <div className="text-sm text-gray-600">NIP: {company.nip}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {company1Id && company2Id && (
            <button
              onClick={loadComparison}
              disabled={loading}
              className="mt-4 w-full md:w-auto px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
            >
              {loading ? 'Ładowanie...' : 'Porównaj'}
            </button>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Comparison Results */}
        {comparison && (
          <div className="bg-white rounded-lg shadow">
            {/* Company Headers */}
            <div className="grid grid-cols-3 gap-4 p-6 border-b border-gray-200">
              <div className="text-center">
                <div className="text-sm text-gray-600 mb-1">Metryka</div>
              </div>
              <div className="text-center">
                <Link
                  href={`/companies/${comparison.company1.id}`}
                  className="block hover:text-blue-600 transition-colors"
                >
                  <h3 className="text-lg font-semibold">{comparison.company1.name}</h3>
                  <p className="text-sm text-gray-600">NIP: {comparison.company1.nip}</p>
                  {comparison.summary.overall_winner === 'company1' && (
                    <div className="mt-2">
                      <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                        🏆 Zwycięzca
                      </span>
                    </div>
                  )}
                </Link>
              </div>
              <div className="text-center">
                <Link
                  href={`/companies/${comparison.company2.id}`}
                  className="block hover:text-blue-600 transition-colors"
                >
                  <h3 className="text-lg font-semibold">{comparison.company2.name}</h3>
                  <p className="text-sm text-gray-600">NIP: {comparison.company2.nip}</p>
                  {comparison.summary.overall_winner === 'company2' && (
                    <div className="mt-2">
                      <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                        🏆 Zwycięzca
                      </span>
                    </div>
                  )}
                </Link>
              </div>
            </div>

            {/* Metrics Rows */}
            <div className="divide-y divide-gray-200">
              {comparison.metrics.map((metric, index) => (
                <div key={index} className="grid grid-cols-3 gap-4 p-4 hover:bg-gray-50 transition-colors">
                  {/* Metric Name */}
                  <div className="flex items-center">
                    <span className="font-medium text-gray-900">{metric.metric_name}</span>
                  </div>

                  {/* Company 1 Value */}
                  <div className={`flex items-center justify-center px-4 py-2 rounded border ${getWinnerClass(metric.winner, 'company1')}`}>
                    <span className="font-semibold">{metric.company1_formatted || 'Brak danych'}</span>
                    {metric.winner === 'company1' && getWinnerBadge(metric.winner)}
                  </div>

                  {/* Company 2 Value */}
                  <div className={`flex items-center justify-center px-4 py-2 rounded border ${getWinnerClass(metric.winner, 'company2')}`}>
                    <span className="font-semibold">{metric.company2_formatted || 'Brak danych'}</span>
                    {metric.winner === 'company2' && getWinnerBadge(metric.winner)}
                  </div>
                </div>
              ))}
            </div>

            {/* Summary */}
            <div className="p-6 bg-gray-50 border-t border-gray-200">
              <h3 className="text-lg font-semibold mb-4">Podsumowanie</h3>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-gray-900">{comparison.summary.company1_wins}</div>
                  <div className="text-sm text-gray-600">Wygranych metryk</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">{comparison.summary.ties}</div>
                  <div className="text-sm text-gray-600">Remisów</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">{comparison.summary.company2_wins}</div>
                  <div className="text-sm text-gray-600">Wygranych metryk</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!comparison && !loading && !error && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-6xl mb-4">⚖️</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Wybierz dwie firmy do porównania
            </h3>
            <p className="text-gray-600">
              Użyj pól wyboru powyżej, aby wybrać firmy które chcesz porównać
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
