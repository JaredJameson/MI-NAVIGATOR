'use client'

import React, { useState } from 'react'

interface DataSource {
  name: string
  confidence: number
}

interface Trend {
  id: number
  name: string
  category: string
  description: string
  impact: 'high' | 'medium' | 'low'
  impact_description: string
  timeline: string
  stage: 'emerging' | 'growing' | 'accelerating' | 'mature'
  adoption_rate: string
  drivers: string[]
  barriers: string[]
  opportunities: string[]
  data_sources: DataSource[]
}

interface Summary {
  total_trends: number
  high_impact: number
  medium_impact: number
  low_impact: number
  categories: Record<string, number>
  key_takeaways: string[]
  recommended_actions: string[]
}

export interface MarketTrendsData {
  industry: string
  region: string
  analysis_date: string
  time_horizon: string
  trends: Trend[]
  summary: Summary
}

interface MarketTrendsProps {
  data: MarketTrendsData
}

const impactColors = {
  high: 'bg-red-100 text-red-800 border-red-200',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  low: 'bg-green-100 text-green-800 border-green-200'
}

const impactIcons = {
  high: '🔴',
  medium: '🟡',
  low: '🟢'
}

const stageColors = {
  emerging: 'bg-blue-100 text-blue-800',
  growing: 'bg-indigo-100 text-indigo-800',
  accelerating: 'bg-purple-100 text-purple-800',
  mature: 'bg-gray-100 text-gray-800'
}

const stageLabels = {
  emerging: 'Emerging',
  growing: 'Growing',
  accelerating: 'Accelerating',
  mature: 'Mature'
}

const categoryIcons: Record<string, string> = {
  'Technology': '💻',
  'Environmental': '🌱',
  'Economic': '💰',
  'Market Structure': '🏢',
  'Market Demand': '📊',
  'Regulatory': '⚖️',
  'Social': '👥'
}

export default function MarketTrends({ data }: MarketTrendsProps) {
  const [selectedTrend, setSelectedTrend] = useState<Trend | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'details'>('overview')

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 text-4xl">📈</div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">
            Market Trends - {data.industry}
          </h3>
          <p className="text-sm text-gray-600">
            {data.region} • {data.time_horizon}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => { setActiveTab('overview'); setSelectedTrend(null); }}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'overview'
              ? 'border-b-2 border-indigo-600 text-indigo-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          📊 Overview
        </button>
        <button
          onClick={() => setActiveTab('details')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'details'
              ? 'border-b-2 border-indigo-600 text-indigo-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          🔍 Trend Details
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="text-2xl font-bold text-gray-900">{data.summary.total_trends}</div>
              <div className="text-sm text-gray-600">Total Trends</div>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="text-2xl font-bold text-red-800">{data.summary.high_impact}</div>
              <div className="text-sm text-red-700">High Impact</div>
            </div>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="text-2xl font-bold text-yellow-800">{data.summary.medium_impact}</div>
              <div className="text-sm text-yellow-700">Medium Impact</div>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="text-2xl font-bold text-green-800">{data.summary.low_impact}</div>
              <div className="text-sm text-green-700">Low Impact</div>
            </div>
          </div>

          {/* Categories Breakdown */}
          <div className="bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">Trend Categories</h4>
            <div className="flex flex-wrap gap-3">
              {Object.entries(data.summary.categories).map(([category, count]) => (
                <div key={category} className="flex items-center gap-2 bg-white rounded-lg px-3 py-2 border border-gray-200">
                  <span className="text-xl">{categoryIcons[category] || '📌'}</span>
                  <span className="text-sm font-medium text-gray-900">{category}</span>
                  <span className="text-xs bg-indigo-100 text-indigo-800 rounded-full px-2 py-0.5">{count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Trends Grid */}
          <div className="grid gap-4">
            {data.trends.map((trend) => (
              <div
                key={trend.id}
                className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => {
                  setSelectedTrend(trend)
                  setActiveTab('details')
                }}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">{categoryIcons[trend.category] || '📌'}</span>
                      <h4 className="text-base font-semibold text-gray-900">{trend.name}</h4>
                      <span className={`text-xs px-2 py-1 rounded-full ${stageColors[trend.stage]}`}>
                        {stageLabels[trend.stage]}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{trend.description}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-600">
                      <span>📅 {trend.timeline}</span>
                      <span>📈 {trend.adoption_rate}</span>
                    </div>
                  </div>
                  <div className={`flex-shrink-0 flex items-center gap-2 px-3 py-1 rounded-lg border ${impactColors[trend.impact]}`}>
                    <span>{impactIcons[trend.impact]}</span>
                    <span className="text-xs font-semibold uppercase">{trend.impact}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Key Takeaways */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <span>💡</span> Key Takeaways
            </h4>
            <ul className="space-y-2">
              {data.summary.key_takeaways.map((takeaway, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-gray-800">
                  <span className="flex-shrink-0 text-blue-600">✓</span>
                  <span>{takeaway}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Recommended Actions */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <span>🎯</span> Recommended Actions
            </h4>
            <ul className="space-y-2">
              {data.summary.recommended_actions.map((action, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-gray-800">
                  <span className="flex-shrink-0 font-semibold text-green-700">{index + 1}.</span>
                  <span>{action}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Details Tab */}
      {activeTab === 'details' && (
        <div className="space-y-4">
          {/* Trend Selector */}
          {!selectedTrend && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <p className="text-sm text-gray-600 text-center">
                Select a trend from the list below to view detailed analysis
              </p>
            </div>
          )}

          {/* Trend List for Selection */}
          <div className="grid gap-3">
            {data.trends.map((trend) => (
              <button
                key={trend.id}
                onClick={() => setSelectedTrend(trend)}
                className={`text-left p-3 rounded-lg border transition-colors ${
                  selectedTrend?.id === trend.id
                    ? 'border-indigo-600 bg-indigo-50'
                    : 'border-gray-200 bg-white hover:border-indigo-300'
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2 flex-1">
                    <span className="text-xl">{categoryIcons[trend.category] || '📌'}</span>
                    <span className="text-sm font-medium text-gray-900">{trend.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-1 rounded-full ${stageColors[trend.stage]}`}>
                      {stageLabels[trend.stage]}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full border ${impactColors[trend.impact]}`}>
                      {impactIcons[trend.impact]} {trend.impact}
                    </span>
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Selected Trend Details */}
          {selectedTrend && (
            <div className="space-y-4 mt-6">
              {/* Trend Header */}
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg p-6">
                <div className="flex items-start gap-4">
                  <span className="text-4xl">{categoryIcons[selectedTrend.category] || '📌'}</span>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold mb-2">{selectedTrend.name}</h3>
                    <p className="text-indigo-100 mb-3">{selectedTrend.description}</p>
                    <div className="flex flex-wrap gap-2">
                      <span className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-sm">
                        {selectedTrend.category}
                      </span>
                      <span className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-sm">
                        📅 {selectedTrend.timeline}
                      </span>
                      <span className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-sm">
                        {impactIcons[selectedTrend.impact]} {selectedTrend.impact} impact
                      </span>
                      <span className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-sm">
                        {stageLabels[selectedTrend.stage]}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Impact & Adoption */}
              <div className="grid md:grid-cols-2 gap-4">
                <div className={`border rounded-lg p-4 ${impactColors[selectedTrend.impact].replace('text-', 'bg-').replace('-800', '-50')}`}>
                  <h4 className="text-sm font-semibold text-gray-900 mb-2">💥 Impact Assessment</h4>
                  <p className="text-sm text-gray-800">{selectedTrend.impact_description}</p>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="text-sm font-semibold text-gray-900 mb-2">📈 Adoption Rate</h4>
                  <p className="text-sm text-gray-800">{selectedTrend.adoption_rate}</p>
                </div>
              </div>

              {/* Drivers */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <span>🚀</span> Drivers
                </h4>
                <ul className="space-y-2">
                  {selectedTrend.drivers.map((driver, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm text-gray-800">
                      <span className="flex-shrink-0 text-green-600">▸</span>
                      <span>{driver}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Barriers */}
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <span>🚧</span> Barriers
                </h4>
                <ul className="space-y-2">
                  {selectedTrend.barriers.map((barrier, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm text-gray-800">
                      <span className="flex-shrink-0 text-red-600">▸</span>
                      <span>{barrier}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Opportunities */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <span>⭐</span> Opportunities
                </h4>
                <ul className="space-y-2">
                  {selectedTrend.opportunities.map((opportunity, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm text-gray-800">
                      <span className="flex-shrink-0 text-yellow-600">▸</span>
                      <span>{opportunity}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Data Sources */}
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-900 mb-3">📚 Data Sources</h4>
                <div className="space-y-2">
                  {selectedTrend.data_sources.map((source, index) => (
                    <div key={index} className="flex items-center justify-between text-sm">
                      <span className="text-gray-800">{source.name}</span>
                      <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">
                        {source.confidence}% confidence
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
