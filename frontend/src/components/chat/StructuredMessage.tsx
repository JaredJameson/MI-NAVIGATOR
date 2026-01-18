'use client'

import React from 'react'
import { CompanyCard, CompanyCardData } from './CompanyCard'
import { DataTable, DataTableData } from './DataTable'
import { TrendChart, TrendChartData } from './TrendChart'
import { SourceCitation } from './SourceCitation'

interface Source {
  id: string
  type: 'krs' | 'website' | 'news' | 'document' | 'database'
  title: string
  url?: string
  confidence: number
  timestamp?: string
  excerpt?: string
}

export interface StructuredMessageData {
  type: 'company_card' | 'data_table' | 'trend_chart' | 'text' | 'text_with_sources'
  data: CompanyCardData | DataTableData | TrendChartData | { text: string } | { text: string; sources: Source[] }
}

interface StructuredMessageProps {
  content: string
}

export function StructuredMessage({ content }: StructuredMessageProps) {
  // Try to parse content as JSON structured data
  let structuredData: StructuredMessageData | null = null

  try {
    // Check if content contains structured data markers
    if (content.includes('```json') || content.startsWith('{')) {
      // Extract JSON from markdown code blocks
      const jsonMatch = content.match(/```json\s*([\s\S]*?)\s*```/) ||
                       content.match(/```\s*([\s\S]*?)\s*```/)

      if (jsonMatch) {
        structuredData = JSON.parse(jsonMatch[1])
      } else if (content.startsWith('{')) {
        // Try direct JSON parse
        structuredData = JSON.parse(content)
      }
    }
  } catch (error) {
    // If parsing fails, treat as plain text
    structuredData = null
  }

  // If no structured data found, render as plain text
  if (!structuredData) {
    return (
      <div className="whitespace-pre-wrap text-sm text-gray-900">
        {content}
      </div>
    )
  }

  // Render appropriate component based on type
  switch (structuredData.type) {
    case 'company_card':
      return <CompanyCard data={structuredData.data as CompanyCardData} />

    case 'data_table':
      return <DataTable data={structuredData.data as DataTableData} />

    case 'trend_chart':
      return <TrendChart data={structuredData.data as TrendChartData} />

    case 'text_with_sources': {
      const messageData = structuredData.data as { text: string; sources: Source[] }
      return <TextWithSources text={messageData.text} sources={messageData.sources} />
    }

    case 'text':
    default:
      return (
        <div className="whitespace-pre-wrap text-sm text-gray-900">
          {(structuredData.data as { text: string }).text || content}
        </div>
      )
  }
}

// Component to render text with inline source citations
function TextWithSources({ text, sources }: { text: string; sources: Source[] }) {
  // Parse text and insert source citations
  // Format: [1], [2], etc. in the text
  const parts = text.split(/(\[\d+\])/g)

  return (
    <div className="text-sm text-gray-900">
      {parts.map((part, index) => {
        const match = part.match(/\[(\d+)\]/)
        if (match) {
          const sourceNumber = parseInt(match[1])
          const source = sources[sourceNumber - 1]
          if (source) {
            return <SourceCitation key={index} source={source} number={sourceNumber} />
          }
        }
        return <span key={index} className="whitespace-pre-wrap">{part}</span>
      })}
    </div>
  )
}
