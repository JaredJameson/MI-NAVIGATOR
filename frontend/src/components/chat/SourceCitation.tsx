'use client'

import { useState } from 'react'
import { FileText, ExternalLink, AlertCircle } from 'lucide-react'

interface Source {
  id: string
  type: 'krs' | 'website' | 'news' | 'document' | 'database'
  title: string
  url?: string
  confidence: number // 0-100
  timestamp?: string
  excerpt?: string
}

interface SourceCitationProps {
  source: Source
  number: number
}

export function SourceCitation({ source, number }: SourceCitationProps) {
  const [showDetails, setShowDetails] = useState(false)

  const getSourceIcon = () => {
    switch (source.type) {
      case 'krs':
        return <FileText className="w-3 h-3" />
      case 'website':
        return <ExternalLink className="w-3 h-3" />
      case 'news':
        return <FileText className="w-3 h-3" />
      case 'document':
        return <FileText className="w-3 h-3" />
      case 'database':
        return <FileText className="w-3 h-3" />
      default:
        return <FileText className="w-3 h-3" />
    }
  }

  const getConfidenceColor = () => {
    if (source.confidence >= 80) return 'text-green-600 bg-green-50'
    if (source.confidence >= 60) return 'text-yellow-600 bg-yellow-50'
    return 'text-orange-600 bg-orange-50'
  }

  const getConfidenceBadge = () => {
    if (source.confidence >= 80) return '●' // Green
    if (source.confidence >= 60) return '●' // Yellow
    return '●' // Orange
  }

  return (
    <span className="relative inline-block">
      {/* Citation number */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="inline-flex items-center gap-0.5 px-1.5 py-0.5 text-xs font-medium text-blue-600 bg-blue-50 rounded hover:bg-blue-100 transition-colors cursor-pointer ml-0.5"
        title={`Source: ${source.title}`}
      >
        [{number}]
      </button>

      {/* Details popover */}
      {showDetails && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowDetails(false)}
          />

          {/* Popover */}
          <div className="absolute left-0 bottom-full mb-2 z-50 w-80 bg-white border border-gray-200 rounded-lg shadow-lg p-4">
            {/* Header */}
            <div className="flex items-start gap-2 mb-3">
              <div className="flex-shrink-0 mt-0.5">
                {getSourceIcon()}
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-semibold text-gray-900 line-clamp-2">
                  {source.title}
                </h4>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-gray-500 uppercase">
                    {source.type}
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${getConfidenceColor()}`}>
                    {getConfidenceBadge()} {source.confidence}% confidence
                  </span>
                </div>
              </div>
            </div>

            {/* Excerpt */}
            {source.excerpt && (
              <div className="mb-3 p-2 bg-gray-50 rounded text-xs text-gray-700 line-clamp-3">
                "{source.excerpt}"
              </div>
            )}

            {/* Timestamp */}
            {source.timestamp && (
              <div className="text-xs text-gray-500 mb-3">
                Retrieved: {new Date(source.timestamp).toLocaleString('pl-PL')}
              </div>
            )}

            {/* Link */}
            {source.url && (
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                <ExternalLink className="w-3 h-3" />
                View source
              </a>
            )}

            {/* No link available */}
            {!source.url && (
              <div className="flex items-center gap-1 text-xs text-gray-400">
                <AlertCircle className="w-3 h-3" />
                Source link not available
              </div>
            )}
          </div>
        </>
      )}
    </span>
  )
}
