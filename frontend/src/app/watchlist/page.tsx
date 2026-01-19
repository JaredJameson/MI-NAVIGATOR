'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { companyApi } from '@/services/api';

export default function WatchlistPage() {
  const router = useRouter();
  const [watchlist, setWatchlist] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadWatchlist() {
      setLoading(true);
      setError(null);

      const result = await companyApi.getWatchlist();
      if (result.error) {
        setError(result.error);
      } else if (result.data) {
        setWatchlist(result.data.watchlist);
      }

      setLoading(false);
    }

    loadWatchlist();
  }, []);

  const handleRemove = async (companyId: string) => {
    const result = await companyApi.removeFromWatchlist(companyId);
    if (result.data) {
      // Remove from local state
      setWatchlist(watchlist.filter(id => id !== companyId));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-slate-600">Ładowanie obserwowanych firm...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-red-600">Błąd: {error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Obserwowane firmy</h1>
              <p className="text-slate-600 mt-2">
                {watchlist.length === 0
                  ? 'Nie obserwujesz żadnych firm'
                  : `Obserwujesz ${watchlist.length} ${watchlist.length === 1 ? 'firmę' : 'firm'}`}
              </p>
            </div>
            <Link
              href="/dashboard"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              ← Wróć do dashboardu
            </Link>
          </div>
        </div>

        {watchlist.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <div className="text-6xl mb-4">⭐</div>
            <h2 className="text-xl font-semibold text-slate-900 mb-2">
              Brak obserwowanych firm
            </h2>
            <p className="text-slate-600 mb-6">
              Dodaj firmy do obserwowanych aby śledzić ich aktualności i zmiany
            </p>
            <Link
              href="/search"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Szukaj firm
            </Link>
          </div>
        ) : (
          <div className="grid gap-4">
            {watchlist.map((companyId) => (
              <div
                key={companyId}
                className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-xl font-bold text-blue-600">
                          {companyId.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-slate-900">
                          Firma ID: {companyId}
                        </h3>
                        <p className="text-sm text-slate-600">
                          Kliknij aby zobaczyć profil
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Link
                      href={`/companies/${companyId}`}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                    >
                      Zobacz profil
                    </Link>
                    <button
                      onClick={() => handleRemove(companyId)}
                      className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-sm"
                    >
                      Usuń z obserwowanych
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
