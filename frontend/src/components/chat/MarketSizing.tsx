import React, { useState } from 'react';

interface MarketSegment {
  name: string;
  share: number;
  value: string;
}

interface YearBreakdown {
  year: number;
  revenue: string;
  share: string;
  customers: string;
}

interface DataSource {
  name: string;
  confidence: number;
}

interface MarketLevel {
  value: number;
  value_formatted: string;
  description: string;
  methodology: string;
  calculation_steps: string[];
  growth_rate?: number;
  growth_rate_formatted?: string;
  market_segments?: MarketSegment[];
  data_sources?: string[];
  filters_applied?: string[];
  target_customers?: string[];
  competitive_landscape?: string;
  market_share_target?: number;
  market_share_formatted?: string;
  timeline?: string;
  year_breakdown?: YearBreakdown[];
  key_assumptions?: string[];
  barriers_to_entry?: string[];
}

interface FunnelVisualization {
  tam_percentage: number;
  sam_percentage: number;
  som_percentage: number;
  tam_to_sam_ratio: number;
  sam_to_som_ratio: number;
  tam_to_som_ratio: number;
}

interface MarketSizingData {
  industry: string;
  region: string;
  year: number;
  analysis_date: string;
  tam: MarketLevel;
  sam: MarketLevel;
  som: MarketLevel;
  funnel_visualization: FunnelVisualization;
  strategic_insights: string[];
  risks_and_challenges: string[];
  next_steps: string[];
  data_sources: DataSource[];
}

interface MarketSizingProps {
  data: MarketSizingData;
}

type TabId = 'overview' | 'tam' | 'sam' | 'som' | 'insights';

const MarketSizing: React.FC<MarketSizingProps> = ({ data }) => {
  const [activeTab, setActiveTab] = useState<TabId>('overview');

  const tabs: { id: TabId; label: string; icon: string }[] = [
    { id: 'overview', label: 'Przegląd', icon: '📊' },
    { id: 'tam', label: 'TAM', icon: '🌍' },
    { id: 'sam', label: 'SAM', icon: '🎯' },
    { id: 'som', label: 'SOM', icon: '🚀' },
    { id: 'insights', label: 'Wnioski', icon: '💡' }
  ];

  const renderOverview = () => {
    const { tam, sam, som, funnel_visualization } = data;

    return (
      <div className="space-y-6">
        {/* Funnel Visualization */}
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 p-6 rounded-lg border-2 border-blue-200">
          <h4 className="text-lg font-semibold text-blue-900 mb-4 flex items-center gap-2">
            <span className="text-2xl">📊</span>
            Lejek rynkowy
          </h4>

          <div className="space-y-3">
            {/* TAM */}
            <div className="relative">
              <div className="bg-blue-600 text-white p-4 rounded-lg" style={{width: '100%'}}>
                <div className="flex justify-between items-center">
                  <span className="font-semibold">TAM (Total Addressable Market)</span>
                  <span className="text-xl font-bold">{tam.value_formatted}</span>
                </div>
                <div className="text-sm mt-1 opacity-90">{tam.description}</div>
              </div>
            </div>

            {/* SAM */}
            <div className="flex justify-center">
              <div className="bg-green-600 text-white p-4 rounded-lg" style={{width: `${funnel_visualization.sam_percentage}%`, minWidth: '60%'}}>
                <div className="flex justify-between items-center">
                  <span className="font-semibold">SAM ({Math.round(funnel_visualization.tam_to_sam_ratio * 100)}% TAM)</span>
                  <span className="text-xl font-bold">{sam.value_formatted}</span>
                </div>
                <div className="text-sm mt-1 opacity-90">{sam.description}</div>
              </div>
            </div>

            {/* SOM */}
            <div className="flex justify-center">
              <div className="bg-orange-600 text-white p-4 rounded-lg" style={{width: `${funnel_visualization.sam_percentage}%`, minWidth: '40%'}}>
                <div className="flex justify-between items-center">
                  <span className="font-semibold">SOM ({Math.round(funnel_visualization.sam_to_som_ratio * 100)}% SAM)</span>
                  <span className="text-xl font-bold">{som.value_formatted}</span>
                </div>
                <div className="text-sm mt-1 opacity-90">{som.description}</div>
              </div>
            </div>
          </div>

          {/* Summary Stats */}
          <div className="mt-6 grid grid-cols-3 gap-4">
            <div className="bg-white p-3 rounded text-center">
              <div className="text-sm text-gray-600">TAM → SAM</div>
              <div className="text-2xl font-bold text-blue-600">{Math.round(funnel_visualization.tam_to_sam_ratio * 100)}%</div>
            </div>
            <div className="bg-white p-3 rounded text-center">
              <div className="text-sm text-gray-600">SAM → SOM</div>
              <div className="text-2xl font-bold text-green-600">{Math.round(funnel_visualization.sam_to_som_ratio * 100)}%</div>
            </div>
            <div className="bg-white p-3 rounded text-center">
              <div className="text-sm text-gray-600">TAM → SOM</div>
              <div className="text-2xl font-bold text-orange-600">{(funnel_visualization.tam_to_som_ratio * 100).toFixed(1)}%</div>
            </div>
          </div>
        </div>

        {/* Quick Summary */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <div className="text-sm text-blue-600 font-medium">TAM</div>
            <div className="text-2xl font-bold text-blue-900">{tam.value_formatted}</div>
            <div className="text-xs text-blue-700 mt-1">{tam.methodology}</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <div className="text-sm text-green-600 font-medium">SAM</div>
            <div className="text-2xl font-bold text-green-900">{sam.value_formatted}</div>
            <div className="text-xs text-green-700 mt-1">{sam.methodology}</div>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
            <div className="text-sm text-orange-600 font-medium">SOM</div>
            <div className="text-2xl font-bold text-orange-900">{som.value_formatted}</div>
            <div className="text-xs text-orange-700 mt-1">{som.timeline}</div>
          </div>
        </div>
      </div>
    );
  };

  const renderTAM = () => {
    const { tam } = data;
    return (
      <div className="space-y-4">
        <div className="bg-blue-50 p-6 rounded-lg border-2 border-blue-200">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-xl font-semibold text-blue-900 flex items-center gap-2">
              <span className="text-2xl">🌍</span>
              TAM - Total Addressable Market
            </h4>
            <div className="text-3xl font-bold text-blue-600">{tam.value_formatted}</div>
          </div>
          <p className="text-gray-700 mb-4">{tam.description}</p>
          <div className="flex items-center gap-2 text-sm">
            <span className="px-3 py-1 bg-blue-200 text-blue-800 rounded-full font-medium">
              Metodologia: {tam.methodology}
            </span>
            {tam.growth_rate_formatted && (
              <span className="px-3 py-1 bg-green-200 text-green-800 rounded-full font-medium">
                Wzrost: {tam.growth_rate_formatted}
              </span>
            )}
          </div>
        </div>

        {/* Calculation Steps */}
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <h5 className="font-semibold text-gray-900 mb-3">Kroki obliczeń:</h5>
          <ol className="space-y-2">
            {tam.calculation_steps.map((step, index) => (
              <li key={index} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  {index + 1}
                </span>
                <span className="text-sm text-gray-700">{step}</span>
              </li>
            ))}
          </ol>
        </div>

        {/* Market Segments */}
        {tam.market_segments && tam.market_segments.length > 0 && (
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h5 className="font-semibold text-gray-900 mb-3">Segmenty rynku:</h5>
            <div className="space-y-2">
              {tam.market_segments.map((segment, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <div className="flex items-center gap-3">
                    <div className="w-16 text-sm font-medium text-gray-600">{Math.round(segment.share * 100)}%</div>
                    <div className="font-medium text-gray-900">{segment.name}</div>
                  </div>
                  <div className="text-blue-600 font-semibold">{segment.value}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Data Sources */}
        {tam.data_sources && tam.data_sources.length > 0 && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <h5 className="font-semibold text-gray-700 mb-2 text-sm">Źródła danych:</h5>
            <ul className="space-y-1">
              {tam.data_sources.map((source, index) => (
                <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                  <span className="text-blue-500">•</span>
                  <span>{source}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  const renderSAM = () => {
    const { sam } = data;
    return (
      <div className="space-y-4">
        <div className="bg-green-50 p-6 rounded-lg border-2 border-green-200">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-xl font-semibold text-green-900 flex items-center gap-2">
              <span className="text-2xl">🎯</span>
              SAM - Serviceable Addressable Market
            </h4>
            <div className="text-3xl font-bold text-green-600">{sam.value_formatted}</div>
          </div>
          <p className="text-gray-700 mb-4">{sam.description}</p>
          <span className="px-3 py-1 bg-green-200 text-green-800 rounded-full font-medium text-sm">
            Metodologia: {sam.methodology}
          </span>
        </div>

        {/* Calculation Steps */}
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <h5 className="font-semibold text-gray-900 mb-3">Kroki obliczeń:</h5>
          <ol className="space-y-2">
            {sam.calculation_steps.map((step, index) => (
              <li key={index} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  {index + 1}
                </span>
                <span className="text-sm text-gray-700">{step}</span>
              </li>
            ))}
          </ol>
        </div>

        {/* Filters */}
        {sam.filters_applied && sam.filters_applied.length > 0 && (
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h5 className="font-semibold text-gray-900 mb-3">Zastosowane filtry:</h5>
            <div className="space-y-2">
              {sam.filters_applied.map((filter, index) => (
                <div key={index} className="flex items-start gap-2 text-sm">
                  <span className="text-green-500 mt-1">✓</span>
                  <span className="text-gray-700">{filter}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Target Customers */}
        {sam.target_customers && sam.target_customers.length > 0 && (
          <div className="bg-green-50 p-4 rounded-lg">
            <h5 className="font-semibold text-green-900 mb-3">Docelowi klienci:</h5>
            <ul className="space-y-1">
              {sam.target_customers.map((customer, index) => (
                <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                  <span className="text-green-600">•</span>
                  <span>{customer}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {sam.competitive_landscape && (
          <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
            <h5 className="font-semibold text-yellow-900 mb-2 flex items-center gap-2">
              <span>⚠️</span>
              Krajobraz konkurencyjny
            </h5>
            <p className="text-sm text-gray-700">{sam.competitive_landscape}</p>
          </div>
        )}
      </div>
    );
  };

  const renderSOM = () => {
    const { som } = data;
    return (
      <div className="space-y-4">
        <div className="bg-orange-50 p-6 rounded-lg border-2 border-orange-200">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-xl font-semibold text-orange-900 flex items-center gap-2">
              <span className="text-2xl">🚀</span>
              SOM - Serviceable Obtainable Market
            </h4>
            <div>
              <div className="text-3xl font-bold text-orange-600">{som.value_formatted}</div>
              <div className="text-sm text-orange-700 text-right">{som.market_share_formatted}</div>
            </div>
          </div>
          <p className="text-gray-700 mb-4">{som.description}</p>
          <span className="px-3 py-1 bg-orange-200 text-orange-800 rounded-full font-medium text-sm">
            Timeline: {som.timeline}
          </span>
        </div>

        {/* Calculation Steps */}
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <h5 className="font-semibold text-gray-900 mb-3">Kroki obliczeń:</h5>
          <ol className="space-y-2">
            {som.calculation_steps.map((step, index) => (
              <li key={index} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-orange-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  {index + 1}
                </span>
                <span className="text-sm text-gray-700">{step}</span>
              </li>
            ))}
          </ol>
        </div>

        {/* Year Breakdown */}
        {som.year_breakdown && som.year_breakdown.length > 0 && (
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h5 className="font-semibold text-gray-900 mb-3">Plan 3-letni:</h5>
            <div className="space-y-3">
              {som.year_breakdown.map((year, index) => (
                <div key={index} className="bg-gradient-to-r from-orange-50 to-yellow-50 p-4 rounded-lg border border-orange-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-gray-900">Rok {year.year}</span>
                    <span className="text-xl font-bold text-orange-600">{year.revenue}</span>
                  </div>
                  <div className="flex gap-4 text-sm text-gray-600">
                    <span>Udział: {year.share}</span>
                    <span>•</span>
                    <span>Klienci: {year.customers}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Key Assumptions */}
        {som.key_assumptions && som.key_assumptions.length > 0 && (
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <h5 className="font-semibold text-blue-900 mb-3">Kluczowe założenia:</h5>
            <ul className="space-y-2">
              {som.key_assumptions.map((assumption, index) => (
                <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                  <span className="text-blue-500 mt-1">•</span>
                  <span>{assumption}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Barriers */}
        {som.barriers_to_entry && som.barriers_to_entry.length > 0 && (
          <div className="bg-red-50 p-4 rounded-lg border border-red-200">
            <h5 className="font-semibold text-red-900 mb-3 flex items-center gap-2">
              <span>🚧</span>
              Bariery wejścia
            </h5>
            <ul className="space-y-2">
              {som.barriers_to_entry.map((barrier, index) => (
                <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                  <span className="text-red-500 mt-1">•</span>
                  <span>{barrier}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  const renderInsights = () => {
    return (
      <div className="space-y-4">
        {/* Strategic Insights */}
        <div className="bg-blue-50 p-6 rounded-lg border-2 border-blue-200">
          <h4 className="text-lg font-semibold text-blue-900 mb-4 flex items-center gap-2">
            <span className="text-2xl">💡</span>
            Wnioski strategiczne
          </h4>
          <ul className="space-y-2">
            {data.strategic_insights.map((insight, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="text-blue-500 mt-1">✓</span>
                <span>{insight}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Risks */}
        <div className="bg-red-50 p-6 rounded-lg border-2 border-red-200">
          <h4 className="text-lg font-semibold text-red-900 mb-4 flex items-center gap-2">
            <span className="text-2xl">⚠️</span>
            Ryzyka i wyzwania
          </h4>
          <ul className="space-y-2">
            {data.risks_and_challenges.map((risk, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="text-red-500 mt-1">•</span>
                <span>{risk}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Next Steps */}
        <div className="bg-green-50 p-6 rounded-lg border-2 border-green-200">
          <h4 className="text-lg font-semibold text-green-900 mb-4 flex items-center gap-2">
            <span className="text-2xl">🎯</span>
            Następne kroki
          </h4>
          <ol className="space-y-2">
            {data.next_steps.map((step, index) => (
              <li key={index} className="flex items-start gap-3 text-sm text-gray-700">
                <span className="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  {index + 1}
                </span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 my-4">
      {/* Header */}
      <div className="mb-6 pb-4 border-b border-gray-200">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-3xl">📈</span>
          <div>
            <h3 className="text-xl font-semibold text-gray-900">
              Market Sizing - {data.industry}
            </h3>
            <p className="text-sm text-gray-500">
              {data.region} • {data.year}
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="flex flex-wrap gap-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <span className="mr-1">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="min-h-[400px]">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'tam' && renderTAM()}
        {activeTab === 'sam' && renderSAM()}
        {activeTab === 'som' && renderSOM()}
        {activeTab === 'insights' && renderInsights()}
      </div>

      {/* Data Sources Footer */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <h5 className="text-sm font-semibold text-gray-700 mb-2">Źródła danych:</h5>
        <div className="flex flex-wrap gap-2">
          {data.data_sources.map((source, index) => (
            <span
              key={index}
              className="text-xs px-3 py-1 bg-blue-50 text-blue-700 rounded-full border border-blue-200"
            >
              {source.name} ({Math.round(source.confidence * 100)}% pewności)
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MarketSizing;
