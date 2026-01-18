import React, { useState } from 'react';

interface PestleFactor {
  factor: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  timeline: 'short-term' | 'medium-term' | 'long-term';
  sentiment: 'opportunity' | 'threat';
}

interface PestleCategory {
  factors: PestleFactor[];
}

interface PestleSummary {
  opportunities_count: number;
  threats_count: number;
  high_impact_count: number;
  overall_outlook: string;
  key_insights: string[];
  strategic_priorities: string[];
}

interface DataSource {
  name: string;
  confidence: number;
}

interface PestleAnalysisData {
  industry_name: string;
  region: string;
  analysis_date: string;
  political: PestleCategory;
  economic: PestleCategory;
  social: PestleCategory;
  technological: PestleCategory;
  legal: PestleCategory;
  environmental: PestleCategory;
  summary: PestleSummary;
  data_sources: DataSource[];
}

interface PestleAnalysisProps {
  data: PestleAnalysisData;
}

type TabId = 'political' | 'economic' | 'social' | 'technological' | 'legal' | 'environmental' | 'summary';

const PestleAnalysis: React.FC<PestleAnalysisProps> = ({ data }) => {
  const [activeTab, setActiveTab] = useState<TabId>('political');

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getSentimentColor = (sentiment: string) => {
    return sentiment === 'opportunity'
      ? 'bg-green-50 border-green-200'
      : 'bg-red-50 border-red-200';
  };

  const getSentimentIcon = (sentiment: string) => {
    return sentiment === 'opportunity' ? '✅' : '⚠️';
  };

  const getTimelineBadge = (timeline: string) => {
    const labels: Record<string, string> = {
      'short-term': 'Krótkoterminowe',
      'medium-term': 'Średnioterminowe',
      'long-term': 'Długoterminowe'
    };
    return labels[timeline] || timeline;
  };

  const tabs: { id: TabId; label: string; icon: string; color: string }[] = [
    { id: 'political', label: 'Polityczne', icon: '🏛️', color: 'text-purple-600' },
    { id: 'economic', label: 'Ekonomiczne', icon: '💰', color: 'text-blue-600' },
    { id: 'social', label: 'Społeczne', icon: '👥', color: 'text-pink-600' },
    { id: 'technological', label: 'Technologiczne', icon: '🔬', color: 'text-cyan-600' },
    { id: 'legal', label: 'Prawne', icon: '⚖️', color: 'text-amber-600' },
    { id: 'environmental', label: 'Środowiskowe', icon: '🌍', color: 'text-green-600' },
    { id: 'summary', label: 'Podsumowanie', icon: '📊', color: 'text-indigo-600' }
  ];

  const renderFactors = (category: PestleCategory, categoryName: string, icon: string, color: string) => {
    const opportunities = category.factors.filter(f => f.sentiment === 'opportunity').length;
    const threats = category.factors.filter(f => f.sentiment === 'threat').length;

    return (
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h4 className={`text-xl font-semibold flex items-center gap-2 ${color}`}>
            <span className="text-2xl">{icon}</span>
            <span>Czynniki {categoryName.toLowerCase()}</span>
          </h4>
          <div className="flex gap-2 text-sm">
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full">
              ✅ Szanse: {opportunities}
            </span>
            <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full">
              ⚠️ Zagrożenia: {threats}
            </span>
          </div>
        </div>

        {/* Factors */}
        <div className="space-y-3">
          {category.factors.map((factor, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg border-2 ${getSentimentColor(factor.sentiment)} transition-shadow hover:shadow-md`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg">{getSentimentIcon(factor.sentiment)}</span>
                    <h5 className="font-semibold text-gray-900">{factor.factor}</h5>
                  </div>
                  <p className="text-gray-700 text-sm mb-3">{factor.description}</p>
                  <div className="flex gap-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getImpactColor(factor.impact)}`}>
                      {factor.impact === 'high' ? 'Wysoki wpływ' : factor.impact === 'medium' ? 'Średni wpływ' : 'Niski wpływ'}
                    </span>
                    <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                      {getTimelineBadge(factor.timeline)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderSummary = () => {
    return (
      <div className="space-y-6">
        {/* Overall Outlook */}
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-lg border-2 border-indigo-200">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-xl font-semibold text-indigo-900 flex items-center gap-2">
              <span className="text-2xl">📊</span>
              Ogólna perspektywa
            </h4>
            <span className={`px-4 py-2 rounded-full text-sm font-semibold ${
              data.summary.overall_outlook === 'challenging'
                ? 'bg-orange-100 text-orange-800'
                : data.summary.overall_outlook === 'positive'
                ? 'bg-green-100 text-green-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}>
              {data.summary.overall_outlook === 'challenging' ? 'Wymagające' :
               data.summary.overall_outlook === 'positive' ? 'Pozytywne' : 'Neutralne'}
            </span>
          </div>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="bg-white p-3 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{data.summary.opportunities_count}</div>
              <div className="text-sm text-gray-600">Szanse</div>
            </div>
            <div className="bg-white p-3 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{data.summary.threats_count}</div>
              <div className="text-sm text-gray-600">Zagrożenia</div>
            </div>
            <div className="bg-white p-3 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{data.summary.high_impact_count}</div>
              <div className="text-sm text-gray-600">Czynniki o wysokim wpływie</div>
            </div>
          </div>
        </div>

        {/* Key Insights */}
        <div className="bg-blue-50 p-6 rounded-lg border-2 border-blue-200">
          <h5 className="text-lg font-semibold text-blue-900 mb-4 flex items-center gap-2">
            <span className="text-xl">💡</span>
            Kluczowe spostrzeżenia
          </h5>
          <ul className="space-y-2">
            {data.summary.key_insights.map((insight, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="text-blue-500 mt-1">✓</span>
                <span>{insight}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Strategic Priorities */}
        <div className="bg-purple-50 p-6 rounded-lg border-2 border-purple-200">
          <h5 className="text-lg font-semibold text-purple-900 mb-4 flex items-center gap-2">
            <span className="text-xl">🎯</span>
            Priorytety strategiczne
          </h5>
          <div className="space-y-2">
            {data.summary.strategic_priorities.map((priority, index) => (
              <div key={index} className="flex items-start gap-3 bg-white p-3 rounded-lg">
                <span className="flex-shrink-0 w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  {index + 1}
                </span>
                <span className="text-sm text-gray-700">{priority}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 my-4">
      {/* Header */}
      <div className="mb-6 pb-4 border-b border-gray-200">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-3xl">⚡</span>
          <div>
            <h3 className="text-xl font-semibold text-gray-900">
              Analiza PESTLE - {data.industry_name}
            </h3>
            <p className="text-sm text-gray-500">
              {data.region} • Data analizy: {new Date(data.analysis_date).toLocaleDateString('pl-PL', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="flex flex-wrap gap-2">
          {tabs.map((tab) => {
            const factorsCount = tab.id === 'summary' ? undefined : data[tab.id]?.factors?.length || 0;
            return (
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
                {factorsCount !== undefined && ` (${factorsCount})`}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="min-h-[400px]">
        {activeTab === 'political' && renderFactors(data.political, 'Polityczne', '🏛️', 'text-purple-600')}
        {activeTab === 'economic' && renderFactors(data.economic, 'Ekonomiczne', '💰', 'text-blue-600')}
        {activeTab === 'social' && renderFactors(data.social, 'Społeczne', '👥', 'text-pink-600')}
        {activeTab === 'technological' && renderFactors(data.technological, 'Technologiczne', '🔬', 'text-cyan-600')}
        {activeTab === 'legal' && renderFactors(data.legal, 'Prawne', '⚖️', 'text-amber-600')}
        {activeTab === 'environmental' && renderFactors(data.environmental, 'Środowiskowe', '🌍', 'text-green-600')}
        {activeTab === 'summary' && renderSummary()}
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

export default PestleAnalysis;
