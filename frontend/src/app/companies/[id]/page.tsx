'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { companyApi, CompanyProfile, NewsArticle } from '@/services/api';

type Tab = 'overview' | 'news' | 'financials' | 'people';

export default function CompanyProfilePage() {
  const params = useParams();
  const router = useRouter();
  const companyId = params.id as string;

  const [company, setCompany] = useState<CompanyProfile | null>(null);
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [loading, setLoading] = useState(true);
  const [newsLoading, setNewsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newsCategory, setNewsCategory] = useState<string>('');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');
  const [showDateFilter, setShowDateFilter] = useState(false);

  // Load company profile
  useEffect(() => {
    async function loadCompany() {
      setLoading(true);
      setError(null);

      const result = await companyApi.getCompany(companyId);
      if (result.error) {
        setError(result.error);
      } else if (result.data) {
        setCompany(result.data);
      }
      setLoading(false);
    }

    loadCompany();
  }, [companyId]);

  // Load news when switching to news tab or filters change
  useEffect(() => {
    async function loadNews() {
      if (activeTab !== 'news' || !company) return;

      setNewsLoading(true);
      const result = await companyApi.getCompanyNews(companyId, {
        limit: 10,
        category: newsCategory || undefined,
        dateFrom: dateFrom || undefined,
        dateTo: dateTo || undefined,
      });
      if (result.data) {
        setNews(result.data.news);
      }
      setNewsLoading(false);
    }

    loadNews();
  }, [activeTab, companyId, company, newsCategory, dateFrom, dateTo]);

  // Clear date filters
  const clearDateFilters = () => {
    setDateFrom('');
    setDateTo('');
    setShowDateFilter(false);
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      if (diffHours === 0) {
        const diffMinutes = Math.floor(diffMs / (1000 * 60));
        return `${diffMinutes} min temu`;
      }
      return `${diffHours} godz. temu`;
    } else if (diffDays === 1) {
      return 'wczoraj';
    } else if (diffDays < 7) {
      return `${diffDays} dni temu`;
    } else {
      return date.toLocaleDateString('pl-PL', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      });
    }
  };

  // Sentiment badge
  const getSentimentBadge = (sentiment: string) => {
    const styles: Record<string, { bg: string; text: string; label: string }> = {
      positive: { bg: 'bg-green-100', text: 'text-green-800', label: 'Pozytywny' },
      negative: { bg: 'bg-red-100', text: 'text-red-800', label: 'Negatywny' },
      neutral: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Neutralny' },
    };
    const style = styles[sentiment] || styles.neutral;
    return (
      <span className={`px-2 py-0.5 text-xs rounded-full ${style.bg} ${style.text}`}>
        {style.label}
      </span>
    );
  };

  // Category badge
  const getCategoryBadge = (category: string) => {
    const labels: Record<string, { icon: string; label: string }> = {
      general: { icon: '📰', label: 'Ogólne' },
      financial: { icon: '💰', label: 'Finanse' },
      product: { icon: '📦', label: 'Produkt' },
      hr: { icon: '👥', label: 'Kadry' },
      legal: { icon: '⚖️', label: 'Prawne' },
    };
    const cat = labels[category] || labels.general;
    return (
      <span className="px-2 py-0.5 text-xs bg-blue-50 text-blue-700 rounded-full">
        {cat.icon} {cat.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">Ładowanie profilu firmy...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Błąd</h2>
          <p className="text-slate-600 mb-4">{error}</p>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Wróć
          </button>
        </div>
      </div>
    );
  }

  if (!company) {
    return null;
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link href="/dashboard" className="text-2xl font-bold text-blue-600">
                MI-Navigator
              </Link>
              <span className="text-slate-300">/</span>
              <span className="text-slate-600">Firma</span>
            </div>
            <nav className="flex items-center gap-4">
              <Link href="/reports" className="text-slate-600 hover:text-blue-600">
                Raporty
              </Link>
              <Link href="/search" className="text-slate-600 hover:text-blue-600">
                Wyszukiwanie
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Company Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-start gap-6">
            <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl font-bold text-blue-600">
                {company.name.charAt(0)}
              </span>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold text-slate-900">{company.name}</h1>
                <span
                  className={`px-2 py-0.5 text-xs rounded-full ${
                    company.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {company.status === 'active' ? 'Aktywna' : company.status}
                </span>
              </div>
              <p className="text-slate-600 mt-1">{company.description}</p>
              <div className="flex flex-wrap gap-4 mt-3 text-sm text-slate-500">
                <span>📍 {company.address.city}</span>
                <span>🏢 NIP: {company.nip}</span>
                {company.krs && <span>📋 KRS: {company.krs}</span>}
                <span>📅 Założona: {company.founded}</span>
                {company.employees_range && (
                  <span>👥 {company.employees_range} pracowników</span>
                )}
              </div>
            </div>
            {company.website && (
              <a
                href={company.website}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                🌐 Strona www
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex gap-1">
            {[
              { id: 'overview' as Tab, label: 'Przegląd', icon: '📊' },
              { id: 'news' as Tab, label: 'Aktualności', icon: '📰' },
              { id: 'financials' as Tab, label: 'Finanse', icon: '💰' },
              { id: 'people' as Tab, label: 'Osoby', icon: '👥' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Company Details */}
            <div className="lg:col-span-2 space-y-6">
              {/* PKD Codes */}
              <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">
                  Kody PKD
                </h2>
                <div className="space-y-3">
                  {company.pkd_descriptions.map((pkd) => (
                    <div
                      key={pkd.code}
                      className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg"
                    >
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-mono rounded">
                        {pkd.code}
                      </span>
                      <div>
                        <p className="text-sm text-slate-900">{pkd.name}</p>
                        <p className="text-xs text-slate-500">{pkd.category}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Address */}
              <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">
                  Lokalizacja
                </h2>
                <div className="text-slate-600">
                  <p>{company.address.street}</p>
                  <p>
                    {company.address.postal_code} {company.address.city}
                  </p>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="space-y-6">
              <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">
                  Informacje
                </h2>
                <dl className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-slate-500">NIP</dt>
                    <dd className="text-slate-900 font-mono">{company.nip}</dd>
                  </div>
                  {company.krs && (
                    <div className="flex justify-between">
                      <dt className="text-slate-500">KRS</dt>
                      <dd className="text-slate-900 font-mono">{company.krs}</dd>
                    </div>
                  )}
                  {company.regon && (
                    <div className="flex justify-between">
                      <dt className="text-slate-500">REGON</dt>
                      <dd className="text-slate-900 font-mono">{company.regon}</dd>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <dt className="text-slate-500">Rok założenia</dt>
                    <dd className="text-slate-900">{company.founded}</dd>
                  </div>
                  {company.employees_range && (
                    <div className="flex justify-between">
                      <dt className="text-slate-500">Zatrudnienie</dt>
                      <dd className="text-slate-900">{company.employees_range}</dd>
                    </div>
                  )}
                </dl>
              </div>

              {/* Actions */}
              <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">
                  Akcje
                </h2>
                <div className="space-y-2">
                  <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                    📊 Generuj raport
                  </button>
                  <button className="w-full px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 text-sm">
                    ⭐ Dodaj do obserwowanych
                  </button>
                  <button className="w-full px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 text-sm">
                    🔔 Ustaw alert
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* News Tab */}
        {activeTab === 'news' && (
          <div className="space-y-6">
            {/* Filters */}
            <div className="bg-white rounded-xl border border-slate-200 p-4 space-y-4">
              {/* Category Filter */}
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm text-slate-600 mr-2">Kategoria:</span>
                {[
                  { value: '', label: 'Wszystkie' },
                  { value: 'general', label: '📰 Ogólne' },
                  { value: 'financial', label: '💰 Finanse' },
                  { value: 'product', label: '📦 Produkty' },
                  { value: 'hr', label: '👥 Kadry' },
                  { value: 'legal', label: '⚖️ Prawne' },
                ].map((cat) => (
                  <button
                    key={cat.value}
                    onClick={() => setNewsCategory(cat.value)}
                    className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                      newsCategory === cat.value
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    {cat.label}
                  </button>
                ))}

                {/* Date filter toggle */}
                <div className="ml-auto">
                  <button
                    onClick={() => setShowDateFilter(!showDateFilter)}
                    className={`px-3 py-1.5 text-sm rounded-lg transition-colors flex items-center gap-2 ${
                      showDateFilter || dateFrom || dateTo
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    📅 Zakres dat
                    {(dateFrom || dateTo) && (
                      <span className="bg-white bg-opacity-30 px-1.5 rounded text-xs">
                        Aktywny
                      </span>
                    )}
                  </button>
                </div>
              </div>

              {/* Date Range Filter */}
              {showDateFilter && (
                <div className="flex items-center gap-4 pt-3 border-t border-slate-200">
                  <span className="text-sm text-slate-600">Zakres dat:</span>
                  <div className="flex items-center gap-2">
                    <label className="text-xs text-slate-500">Od:</label>
                    <input
                      type="date"
                      value={dateFrom}
                      onChange={(e) => setDateFrom(e.target.value)}
                      className="px-3 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="text-xs text-slate-500">Do:</label>
                    <input
                      type="date"
                      value={dateTo}
                      onChange={(e) => setDateTo(e.target.value)}
                      className="px-3 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  {(dateFrom || dateTo) && (
                    <button
                      onClick={clearDateFilters}
                      className="px-3 py-1.5 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                    >
                      ✕ Wyczyść
                    </button>
                  )}
                </div>
              )}

              {/* Active filters summary */}
              {(dateFrom || dateTo) && (
                <div className="flex items-center gap-2 text-sm text-slate-600 pt-2 border-t border-slate-100">
                  <span>📅 Filtr dat:</span>
                  {dateFrom && (
                    <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded">
                      Od: {new Date(dateFrom).toLocaleDateString('pl-PL')}
                    </span>
                  )}
                  {dateTo && (
                    <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded">
                      Do: {new Date(dateTo).toLocaleDateString('pl-PL')}
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* News List */}
            {newsLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-slate-600">Ładowanie aktualności...</p>
              </div>
            ) : news.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
                <div className="text-4xl mb-4">📭</div>
                <h3 className="text-lg font-semibold text-slate-900">
                  Brak aktualności
                </h3>
                <p className="text-slate-600 mt-1">
                  Nie znaleziono artykułów dla wybranych kryteriów.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {news.map((article) => (
                  <article
                    key={article.id}
                    className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          {getCategoryBadge(article.category)}
                          {getSentimentBadge(article.sentiment)}
                        </div>
                        <h3 className="text-lg font-semibold text-slate-900 mb-2">
                          {article.title}
                        </h3>
                        <p className="text-slate-600 text-sm mb-3">
                          {article.summary}
                        </p>
                        <div className="flex items-center gap-4 text-xs text-slate-500">
                          <span className="flex items-center gap-1">
                            📰 {article.source}
                          </span>
                          <span className="flex items-center gap-1">
                            🕒 {formatDate(article.published_at)}
                          </span>
                        </div>
                      </div>
                      <a
                        href={article.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 text-sm flex items-center gap-2 whitespace-nowrap"
                      >
                        Czytaj więcej →
                      </a>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Financials Tab (Placeholder) */}
        {activeTab === 'financials' && (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <div className="text-5xl mb-4">💰</div>
            <h3 className="text-lg font-semibold text-slate-900">
              Dane finansowe
            </h3>
            <p className="text-slate-600 mt-2">
              Ta sekcja jest w przygotowaniu. Wkrótce będą tutaj dostępne dane
              finansowe firmy.
            </p>
          </div>
        )}

        {/* People Tab (Placeholder) */}
        {activeTab === 'people' && (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <div className="text-5xl mb-4">👥</div>
            <h3 className="text-lg font-semibold text-slate-900">
              Kluczowe osoby
            </h3>
            <p className="text-slate-600 mt-2">
              Ta sekcja jest w przygotowaniu. Wkrótce będą tutaj informacje o
              zarządzie i kluczowych osobach w firmie.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
