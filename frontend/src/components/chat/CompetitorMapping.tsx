/**
 * CompetitorMapping Component
 * Displays competitor analysis with categorization and insights
 */

import React from 'react';

interface Competitor {
  id: number;
  name: string;
  nip: string;
  krs: string;
  category: 'direct' | 'indirect' | 'substitute';
  category_description: string;
  location: string;
  employees: string;
  revenue_estimate: string;
  pkd_main: string;
  products: string[];
  market_position: string;
  competitive_advantage: string;
  website: string;
}

interface TargetCompany {
  name: string;
  nip: string;
  krs: string;
  pkd_main: string;
  pkd_description: string;
  industry: string;
}

interface SearchCriteria {
  method: string;
  pkd_codes: string[];
  geographic_scope: string;
  filters_applied: string[];
}

interface Summary {
  total_competitors: number;
  direct_competitors: number;
  indirect_competitors: number;
  substitute_competitors: number;
  geographic_distribution: Record<string, number>;
  average_revenue: string;
  market_concentration: string;
  competitive_intensity: string;
}

interface CompetitorMappingData {
  target_company: TargetCompany;
  search_criteria: SearchCriteria;
  competitors: Competitor[];
  summary: Summary;
  insights: string[];
  recommended_actions: string[];
  fetched_at: string;
  data_freshness: string;
}

interface CompetitorMappingProps {
  data: CompetitorMappingData;
}

export default function CompetitorMapping({ data }: CompetitorMappingProps) {
  const [activeTab, setActiveTab] = React.useState<'all' | 'direct' | 'indirect' | 'substitute' | 'insights'>('all');

  const getCategoryBadgeColor = (category: string) => {
    switch (category) {
      case 'direct':
        return 'bg-red-100 text-red-800';
      case 'indirect':
        return 'bg-yellow-100 text-yellow-800';
      case 'substitute':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'direct':
        return 'Bezpośredni';
      case 'indirect':
        return 'Pośredni';
      case 'substitute':
        return 'Substytut';
      default:
        return category;
    }
  };

  const filteredCompetitors = activeTab === 'all'
    ? data.competitors
    : data.competitors.filter(c => c.category === activeTab);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 my-4">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4 mb-4">
        <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          🎯 Mapowanie Konkurencji
        </h3>
        <div className="mt-2 text-sm text-gray-600">
          Dla: <span className="font-semibold">{data.target_company.name}</span>
          <span className="ml-2">({data.target_company.industry})</span>
        </div>
        <div className="mt-1 text-xs text-gray-500">
          PKD: {data.target_company.pkd_main} - {data.target_company.pkd_description}
        </div>
      </div>

      {/* Search Criteria */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
        <h4 className="text-sm font-semibold text-amber-900 mb-2">🔍 Kryteria wyszukiwania</h4>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span className="text-amber-700 font-medium">Metoda:</span>{' '}
            <span className="text-amber-900">{data.search_criteria.method}</span>
          </div>
          <div>
            <span className="text-amber-700 font-medium">Zakres:</span>{' '}
            <span className="text-amber-900">{data.search_criteria.geographic_scope}</span>
          </div>
          <div className="col-span-2">
            <span className="text-amber-700 font-medium">Kody PKD:</span>{' '}
            {data.search_criteria.pkd_codes.map((code, idx) => (
              <span key={idx} className="inline-block bg-amber-100 px-2 py-0.5 rounded text-amber-900 ml-1">
                {code}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
          <div className="text-2xl font-bold text-gray-900">{data.summary.total_competitors}</div>
          <div className="text-xs text-gray-600">Konkurentów</div>
        </div>
        <div className="bg-red-50 rounded-lg p-3 border border-red-200">
          <div className="text-2xl font-bold text-red-900">{data.summary.direct_competitors}</div>
          <div className="text-xs text-red-700">Bezpośrednich</div>
        </div>
        <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-200">
          <div className="text-2xl font-bold text-yellow-900">{data.summary.indirect_competitors}</div>
          <div className="text-xs text-yellow-700">Pośrednich</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
          <div className="text-2xl font-bold text-purple-900">{data.summary.substitute_competitors}</div>
          <div className="text-xs text-purple-700">Substytutów</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-4">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'all'
                ? 'border-amber-600 text-amber-700'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Wszyscy ({data.summary.total_competitors})
          </button>
          <button
            onClick={() => setActiveTab('direct')}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'direct'
                ? 'border-red-600 text-red-700'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Bezpośredni ({data.summary.direct_competitors})
          </button>
          <button
            onClick={() => setActiveTab('indirect')}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'indirect'
                ? 'border-yellow-600 text-yellow-700'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Pośredni ({data.summary.indirect_competitors})
          </button>
          <button
            onClick={() => setActiveTab('substitute')}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'substitute'
                ? 'border-purple-600 text-purple-700'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Substytuty ({data.summary.substitute_competitors})
          </button>
          <button
            onClick={() => setActiveTab('insights')}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'insights'
                ? 'border-blue-600 text-blue-700'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Insighty
          </button>
        </div>
      </div>

      {/* Competitors List */}
      {activeTab !== 'insights' && (
        <div className="space-y-3">
          {filteredCompetitors.map((competitor) => (
            <div
              key={competitor.id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="text-lg font-semibold text-gray-900">{competitor.name}</h4>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${getCategoryBadgeColor(competitor.category)}`}>
                      {getCategoryLabel(competitor.category)}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mb-1">{competitor.category_description}</div>
                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    <span>📍 {competitor.location}</span>
                    <span>👥 {competitor.employees} pracowników</span>
                    <span>💰 ~{competitor.revenue_estimate}</span>
                    <span>PKD: {competitor.pkd_main}</span>
                  </div>
                </div>
                {competitor.website && (
                  <a
                    href={competitor.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1"
                  >
                    🌐 Strona
                  </a>
                )}
              </div>

              <div className="grid grid-cols-2 gap-3 mt-3 pt-3 border-t border-gray-100">
                <div>
                  <div className="text-xs font-medium text-gray-700 mb-1">Produkty/Usługi</div>
                  <div className="flex flex-wrap gap-1">
                    {competitor.products.map((product, idx) => (
                      <span key={idx} className="text-xs bg-gray-100 px-2 py-0.5 rounded text-gray-700">
                        {product}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="text-xs font-medium text-gray-700 mb-1">Przewaga konkurencyjna</div>
                  <div className="text-xs text-gray-600">{competitor.competitive_advantage}</div>
                </div>
                <div>
                  <div className="text-xs font-medium text-gray-700 mb-1">Pozycja rynkowa</div>
                  <div className="text-xs text-gray-600">{competitor.market_position}</div>
                </div>
                <div>
                  <div className="text-xs font-medium text-gray-700 mb-1">Dane rejestrowe</div>
                  <div className="text-xs text-gray-600">
                    NIP: {competitor.nip} | KRS: {competitor.krs}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Insights Tab */}
      {activeTab === 'insights' && (
        <div className="space-y-6">
          {/* Market Overview */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-blue-900 mb-3 flex items-center gap-2">
              📊 Przegląd rynku
            </h4>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-blue-700 font-medium">Średni przychód:</span>{' '}
                <span className="text-blue-900">{data.summary.average_revenue}</span>
              </div>
              <div>
                <span className="text-blue-700 font-medium">Koncentracja rynku:</span>{' '}
                <span className="text-blue-900">{data.summary.market_concentration}</span>
              </div>
              <div className="col-span-2">
                <span className="text-blue-700 font-medium">Intensywność konkurencji:</span>{' '}
                <span className="text-blue-900">{data.summary.competitive_intensity}</span>
              </div>
            </div>
          </div>

          {/* Geographic Distribution */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
              🗺️ Rozkład geograficzny
            </h4>
            <div className="grid grid-cols-3 gap-2">
              {Object.entries(data.summary.geographic_distribution).map(([region, count]) => (
                <div key={region} className="bg-gray-50 border border-gray-200 rounded px-3 py-2">
                  <div className="text-sm font-medium text-gray-900">{region}</div>
                  <div className="text-xs text-gray-600">{count} {count === 1 ? 'konkurent' : 'konkurentów'}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Key Insights */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
              💡 Kluczowe wnioski
            </h4>
            <ul className="space-y-2">
              {data.insights.map((insight, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="text-green-600 mt-0.5">✓</span>
                  <span>{insight}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Recommended Actions */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
              🎯 Rekomendowane działania
            </h4>
            <ul className="space-y-2">
              {data.recommended_actions.map((action, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
                  <span className="text-amber-600 font-bold">{idx + 1}.</span>
                  <span>{action}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-gray-200 text-xs text-gray-500 flex items-center justify-between">
        <div>
          Źródło: {data.search_criteria.method} | Świeżość danych: {data.data_freshness}
        </div>
        <div>
          Pobrano: {new Date(data.fetched_at).toLocaleString('pl-PL')}
        </div>
      </div>
    </div>
  );
}
