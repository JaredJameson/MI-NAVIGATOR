/**
 * CompetitorBenchmarking Component
 * Displays side-by-side competitor comparison table with visualizations
 */

import React, { useState } from 'react';

interface Competitor {
  name: string;
  is_target: boolean;
  location: string;
  employees: number;
  revenue_2023: number;
  revenue_2022: number;
  revenue_2021: number;
  revenue_growth_yoy: number;
  profit_margin: number;
  roe: number;
  roa: number;
  debt_ratio: number;
  current_ratio: number;
  market_share: number;
  certifications: string[];
  export_markets: boolean;
  r_and_d_investment: boolean;
  website_quality: number;
  linkedin_followers: number;
}

interface Metric {
  key: string;
  label: string;
  unit: string;
  format: 'number' | 'decimal' | 'list' | 'boolean';
  higher_is_better?: boolean;
}

interface MetricCategory {
  name: string;
  metrics: Metric[];
}

interface CompetitorBenchmarkingData {
  target_company: {
    name: string;
    nip: string;
    krs: string;
  };
  competitors: Competitor[];
  metrics: {
    categories: MetricCategory[];
  };
  insights: {
    strengths: string[];
    weaknesses: string[];
    opportunities: string[];
  };
  fetched_at: string;
}

interface CompetitorBenchmarkingProps {
  data: CompetitorBenchmarkingData;
}

const CompetitorBenchmarking: React.FC<CompetitorBenchmarkingProps> = ({ data }) => {
  const [activeCategory, setActiveCategory] = useState(0);

  // Helper function to format values
  const formatValue = (value: any, metric: Metric): string | React.ReactNode => {
    if (value === null || value === undefined) return '-';

    switch (metric.format) {
      case 'number':
        return typeof value === 'number' ? value.toLocaleString('pl-PL') : value;
      case 'decimal':
        return typeof value === 'number' ? value.toFixed(1) : value;
      case 'boolean':
        return value ? '✓ Tak' : '✗ Nie';
      case 'list':
        if (Array.isArray(value)) {
          return (
            <div className="flex flex-wrap gap-1">
              {value.map((item, i) => (
                <span key={i} className="inline-block px-2 py-0.5 bg-emerald-100 text-emerald-800 text-xs rounded">
                  {item}
                </span>
              ))}
            </div>
          );
        }
        return value;
      default:
        return String(value);
    }
  };

  // Helper function to get cell color based on performance
  const getCellColor = (competitor: Competitor, metric: Metric, allCompetitors: Competitor[]): string => {
    const value = (competitor as any)[metric.key];
    if (value === null || value === undefined || metric.format === 'list') return '';

    // Skip coloring for boolean and list types
    if (metric.format === 'boolean') {
      if (value === true) return 'bg-emerald-50';
      if (value === false) return 'bg-gray-50';
      return '';
    }

    // For numerical values, compare with others
    if (metric.format === 'number' || metric.format === 'decimal') {
      const values = allCompetitors
        .map(c => (c as any)[metric.key])
        .filter(v => typeof v === 'number');

      if (values.length === 0) return '';

      const max = Math.max(...values);
      const min = Math.min(...values);

      // If all values are the same, no coloring
      if (max === min) return '';

      const isHigher = metric.higher_is_better !== false; // Default to true
      const isBest = (isHigher && value === max) || (!isHigher && value === min);
      const isWorst = (isHigher && value === min) || (!isHigher && value === max);

      if (isBest) return 'bg-emerald-50 font-semibold text-emerald-900';
      if (isWorst) return 'bg-red-50 text-red-900';
    }

    return '';
  };

  // Get indicator icon for metric
  const getIndicator = (competitor: Competitor, metric: Metric, allCompetitors: Competitor[]): React.ReactNode => {
    const value = (competitor as any)[metric.key];
    if (value === null || value === undefined || metric.format === 'list' || metric.format === 'boolean') return null;

    if (metric.format === 'number' || metric.format === 'decimal') {
      const values = allCompetitors
        .map(c => (c as any)[metric.key])
        .filter(v => typeof v === 'number');

      if (values.length === 0) return null;

      const max = Math.max(...values);
      const min = Math.min(...values);

      if (max === min) return null;

      const isHigher = metric.higher_is_better !== false;
      const isBest = (isHigher && value === max) || (!isHigher && value === min);
      const isWorst = (isHigher && value === min) || (!isHigher && value === max);

      if (isBest) return <span className="ml-1 text-emerald-600">▲</span>;
      if (isWorst) return <span className="ml-1 text-red-600">▼</span>;
    }

    return null;
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden my-4">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-indigo-500 text-white p-6">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-3xl">📊</span>
          <h2 className="text-2xl font-bold">Porównanie konkurentów</h2>
        </div>
        <p className="text-indigo-100">
          Analiza benchmarkingowa: {data.target_company.name} vs {data.competitors.length - 1} konkurentów
        </p>
      </div>

      {/* Category Tabs */}
      <div className="bg-gray-50 border-b border-gray-200 px-6">
        <div className="flex gap-2 overflow-x-auto">
          {data.metrics.categories.map((category, index) => (
            <button
              key={index}
              onClick={() => setActiveCategory(index)}
              className={`px-4 py-3 font-medium whitespace-nowrap border-b-2 transition-colors ${
                activeCategory === index
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
              }`}
            >
              {category.name}
            </button>
          ))}
        </div>
      </div>

      {/* Comparison Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 sticky left-0 bg-gray-50 z-10 min-w-[200px]">
                Metryka
              </th>
              {data.competitors.map((competitor, index) => (
                <th
                  key={index}
                  className={`px-6 py-4 text-center text-sm font-semibold min-w-[150px] ${
                    competitor.is_target
                      ? 'bg-indigo-100 text-indigo-900'
                      : 'text-gray-900'
                  }`}
                >
                  <div className="flex flex-col gap-1">
                    <div className="font-bold">{competitor.name}</div>
                    {competitor.is_target && (
                      <div className="inline-flex items-center justify-center px-2 py-0.5 bg-indigo-600 text-white text-xs rounded">
                        Twoja firma
                      </div>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.metrics.categories[activeCategory].metrics.map((metric, metricIndex) => (
              <tr key={metricIndex} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm text-gray-900 font-medium sticky left-0 bg-white z-10 border-r border-gray-200">
                  <div className="flex flex-col">
                    <span>{metric.label}</span>
                    {metric.unit && (
                      <span className="text-xs text-gray-500 mt-0.5">({metric.unit})</span>
                    )}
                  </div>
                </td>
                {data.competitors.map((competitor, compIndex) => (
                  <td
                    key={compIndex}
                    className={`px-6 py-4 text-sm text-center ${
                      competitor.is_target ? 'bg-indigo-50' : ''
                    } ${getCellColor(competitor, metric, data.competitors)}`}
                  >
                    <div className="flex items-center justify-center gap-1">
                      {formatValue((competitor as any)[metric.key], metric)}
                      {getIndicator(competitor, metric, data.competitors)}
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="bg-gray-50 px-6 py-3 border-t border-gray-200">
        <div className="flex items-center gap-6 text-xs text-gray-600">
          <div className="flex items-center gap-2">
            <span className="text-emerald-600 font-bold">▲</span>
            <span>Najlepszy wynik</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-red-600 font-bold">▼</span>
            <span>Najsłabszy wynik</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-indigo-50 border border-indigo-200 rounded"></div>
            <span>Twoja firma</span>
          </div>
        </div>
      </div>

      {/* Insights Section */}
      <div className="p-6 bg-gray-50 border-t border-gray-200">
        <h3 className="text-lg font-bold text-gray-900 mb-4">💡 Kluczowe wnioski</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Strengths */}
          <div className="bg-white rounded-lg p-4 border border-emerald-200">
            <h4 className="font-semibold text-emerald-900 mb-2 flex items-center gap-2">
              <span>✓</span>
              <span>Mocne strony</span>
            </h4>
            <ul className="space-y-1 text-sm text-gray-700">
              {data.insights.strengths.map((strength, index) => (
                <li key={index} className="flex gap-2">
                  <span className="text-emerald-600 flex-shrink-0">•</span>
                  <span>{strength}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Weaknesses */}
          <div className="bg-white rounded-lg p-4 border border-orange-200">
            <h4 className="font-semibold text-orange-900 mb-2 flex items-center gap-2">
              <span>!</span>
              <span>Obszary do poprawy</span>
            </h4>
            <ul className="space-y-1 text-sm text-gray-700">
              {data.insights.weaknesses.map((weakness, index) => (
                <li key={index} className="flex gap-2">
                  <span className="text-orange-600 flex-shrink-0">•</span>
                  <span>{weakness}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Opportunities */}
          <div className="bg-white rounded-lg p-4 border border-blue-200">
            <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
              <span>→</span>
              <span>Szanse</span>
            </h4>
            <ul className="space-y-1 text-sm text-gray-700">
              {data.insights.opportunities.map((opportunity, index) => (
                <li key={index} className="flex gap-2">
                  <span className="text-blue-600 flex-shrink-0">•</span>
                  <span>{opportunity}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-6 py-3 bg-gray-100 border-t border-gray-200 flex justify-between items-center text-xs text-gray-600">
        <div>
          <span className="font-medium">Źródło danych:</span> KRS, e-sprawozdania, analiza rynkowa
        </div>
        <div>
          Wygenerowano: {new Date(data.fetched_at).toLocaleString('pl-PL')}
        </div>
      </div>
    </div>
  );
};

export default CompetitorBenchmarking;
