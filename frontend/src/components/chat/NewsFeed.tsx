'use client'

import React, { useState } from 'react'

interface NewsArticle {
  id: string
  title: string
  summary: string
  source: string
  source_url: string
  published_at: string
  sentiment: 'positive' | 'negative' | 'neutral'
  category: string
  days_ago: number
}

interface NewsSummary {
  total_articles: number
  positive: number
  negative: number
  neutral: number
  unique_sources: number
  most_recent_days: number
  date_range: string
}

export interface NewsFeedData {
  company_name: string
  company_id: string
  articles: NewsArticle[]
  summary: NewsSummary
  fetched_at: string
}

interface NewsFeedProps {
  data: NewsFeedData
}

const sentimentColors = {
  positive: 'bg-green-100 text-green-800 border-green-200',
  negative: 'bg-red-100 text-red-800 border-red-200',
  neutral: 'bg-gray-100 text-gray-800 border-gray-200'
}

const sentimentIcons = {
  positive: '✅',
  negative: '⚠️',
  neutral: '📄'
}

const categoryIcons: Record<string, string> = {
  'financial': '💰',
  'product': '🛍️',
  'hr': '👥',
  'legal': '⚖️',
  'general': '📰',
  'partnership': '🤝',
  'investment': '💸'
}

const categoryLabels: Record<string, string> = {
  'financial': 'Finanse',
  'product': 'Produkty',
  'hr': 'Kadry',
  'legal': 'Prawo',
  'general': 'Ogólne',
  'partnership': 'Partnerstwa',
  'investment': 'Inwestycje'
}

export default function NewsFeed({ data }: NewsFeedProps) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedSentiment, setSelectedSentiment] = useState<string | null>(null)

  // Filter articles
  const filteredArticles = data.articles.filter(article => {
    if (selectedCategory && article.category !== selectedCategory) return false
    if (selectedSentiment && article.sentiment !== selectedSentiment) return false
    return true
  })

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('pl-PL', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  }

  const getDaysAgoLabel = (days: number) => {
    if (days === 0) return 'Dziś'
    if (days === 1) return 'Wczoraj'
    if (days < 7) return `${days} dni temu`
    if (days < 14) return 'Tydzień temu'
    if (days < 30) return `${Math.floor(days / 7)} tygodni temu`
    return `${Math.floor(days / 30)} miesięcy temu`
  }

  // Get unique categories
  const categories = Array.from(new Set(data.articles.map(a => a.category)))

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 text-4xl">📰</div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">
            News Feed - {data.company_name}
          </h3>
          <p className="text-sm text-gray-600">
            {data.summary.total_articles} articles • {data.summary.unique_sources} sources • {data.summary.date_range}
          </p>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-white border border-gray-200 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-gray-900">{data.summary.total_articles}</div>
          <div className="text-xs text-gray-600">Total Articles</div>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-green-700">{data.summary.positive}</div>
          <div className="text-xs text-green-600">Positive</div>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-red-700">{data.summary.negative}</div>
          <div className="text-xs text-red-600">Negative</div>
        </div>
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-gray-700">{data.summary.neutral}</div>
          <div className="text-xs text-gray-600">Neutral</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        <span className="text-sm text-gray-600 self-center">Filter:</span>

        {/* Category Filters */}
        <button
          onClick={() => setSelectedCategory(null)}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
            selectedCategory === null
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All Categories
        </button>
        {categories.map(category => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              selectedCategory === category
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {categoryIcons[category] || '📄'} {categoryLabels[category] || category}
          </button>
        ))}

        <span className="text-gray-300">|</span>

        {/* Sentiment Filters */}
        <button
          onClick={() => setSelectedSentiment(null)}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
            selectedSentiment === null
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All Sentiment
        </button>
        <button
          onClick={() => setSelectedSentiment('positive')}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
            selectedSentiment === 'positive'
              ? 'bg-green-600 text-white'
              : 'bg-green-50 text-green-700 hover:bg-green-100'
          }`}
        >
          ✅ Positive
        </button>
        <button
          onClick={() => setSelectedSentiment('negative')}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
            selectedSentiment === 'negative'
              ? 'bg-red-600 text-white'
              : 'bg-red-50 text-red-700 hover:bg-red-100'
          }`}
        >
          ⚠️ Negative
        </button>
        <button
          onClick={() => setSelectedSentiment('neutral')}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
            selectedSentiment === 'neutral'
              ? 'bg-gray-600 text-white'
              : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
          }`}
        >
          📄 Neutral
        </button>
      </div>

      {/* Articles List */}
      <div className="space-y-3">
        {filteredArticles.length === 0 ? (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
            <p className="text-gray-600">No articles match the selected filters.</p>
          </div>
        ) : (
          filteredArticles.map(article => (
            <div
              key={article.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              {/* Article Header */}
              <div className="flex items-start gap-3 mb-2">
                <div className="flex-shrink-0 text-2xl">
                  {sentimentIcons[article.sentiment]}
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-gray-900 mb-1 leading-snug">
                    {article.title}
                  </h4>
                  <div className="flex flex-wrap items-center gap-2 text-xs">
                    <span className={`px-2 py-0.5 rounded-full border ${sentimentColors[article.sentiment]}`}>
                      {article.sentiment.charAt(0).toUpperCase() + article.sentiment.slice(1)}
                    </span>
                    <span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 border border-blue-200">
                      {categoryIcons[article.category] || '📄'} {categoryLabels[article.category] || article.category}
                    </span>
                    <span className="text-gray-500">•</span>
                    <span className="text-gray-600">{getDaysAgoLabel(article.days_ago)}</span>
                    <span className="text-gray-500">•</span>
                    <a
                      href={article.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {article.source}
                    </a>
                  </div>
                </div>
              </div>

              {/* Article Summary */}
              <p className="text-sm text-gray-700 leading-relaxed pl-11">
                {article.summary}
              </p>

              {/* Article Footer */}
              <div className="flex items-center gap-2 mt-3 pl-11">
                <a
                  href={article.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:underline font-medium"
                >
                  Read full article →
                </a>
                <span className="text-xs text-gray-400">•</span>
                <span className="text-xs text-gray-500">
                  {formatDate(article.published_at)}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500 pt-2">
        <div>
          Showing {filteredArticles.length} of {data.summary.total_articles} articles
        </div>
        <div>
          Updated {new Date(data.fetched_at).toLocaleString('pl-PL')}
        </div>
      </div>
    </div>
  )
}
