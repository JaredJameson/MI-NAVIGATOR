'use client'

import React from 'react'
import { CompanyCard, CompanyCardData } from './CompanyCard'
import { CompanyProfileKRS, CompanyProfileKRSData } from './CompanyProfileKRS'
import { CompanyProfileCEIDG, CompanyProfileCEIDGData } from './CompanyProfileCEIDG'
import { DataTable, DataTableData } from './DataTable'
import { TrendChart, TrendChartData } from './TrendChart'
import { SourceCitation } from './SourceCitation'
import { FinancialStatements } from './FinancialStatements'
import { OwnershipStructure, OwnershipStructureData } from './OwnershipStructure'
import KeyPeople from './KeyPeople'
import { WebsiteAnalysis, WebsiteAnalysisData } from './WebsiteAnalysis'
import CompetitorMapping from './CompetitorMapping'
import CompetitorBenchmarking from './CompetitorBenchmarking'
import SwotAnalysis from './SwotAnalysis'
import PorterAnalysis from './PorterAnalysis'
import PestleAnalysis from './PestleAnalysis'
import MarketSizing from './MarketSizing'

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
  type: 'company_card' | 'company_profile_krs' | 'company_profile_ceidg' | 'data_table' | 'trend_chart' | 'financial_statements' | 'ownership_structure' | 'key_people' | 'website_analysis' | 'competitor_mapping' | 'competitor_benchmarking' | 'swot_analysis' | 'porter_analysis' | 'pestle_analysis' | 'market_sizing' | 'text' | 'text_with_sources' | 'error'
  data: CompanyCardData | CompanyProfileKRSData | CompanyProfileCEIDGData | DataTableData | TrendChartData | OwnershipStructureData | WebsiteAnalysisData | any | { text: string } | { text: string; sources: Source[] } | { message: string; suggestion?: string }
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

    case 'company_profile_krs':
      return <CompanyProfileKRS data={structuredData.data as CompanyProfileKRSData} />

    case 'company_profile_ceidg':
      return <CompanyProfileCEIDG data={structuredData.data as CompanyProfileCEIDGData} />

    case 'data_table':
      return <DataTable data={structuredData.data as DataTableData} />

    case 'trend_chart':
      return <TrendChart data={structuredData.data as TrendChartData} />

    case 'financial_statements':
      return <FinancialStatements data={structuredData.data as any} />

    case 'ownership_structure':
      return <OwnershipStructure data={structuredData.data as OwnershipStructureData} />

    case 'key_people':
      return <KeyPeople data={structuredData.data as any} />

    case 'website_analysis':
      return <WebsiteAnalysis data={structuredData.data as WebsiteAnalysisData} />

    case 'competitor_mapping':
      return <CompetitorMapping data={structuredData.data as any} />

    case 'competitor_benchmarking':
      return <CompetitorBenchmarking data={structuredData.data as any} />

    case 'swot_analysis':
      return <SwotAnalysis data={structuredData.data as any} />

    case 'porter_analysis':
      return <PorterAnalysis data={structuredData.data as any} />

    case 'pestle_analysis':
      return <PestleAnalysis data={structuredData.data as any} />

    case 'market_sizing':
      return <MarketSizing data={structuredData.data as any} />

    case 'text_with_sources': {
      const messageData = structuredData.data as { text: string; sources: Source[] }
      return <TextWithSources text={messageData.text} sources={messageData.sources} />
    }

    case 'error': {
      const errorData = structuredData.data as { message: string; suggestion?: string }
      return (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <div className="flex items-start gap-3">
            <svg className="h-5 w-5 flex-shrink-0 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-red-800">{errorData.message}</p>
              {errorData.suggestion && (
                <p className="mt-1 text-sm text-red-700">{errorData.suggestion}</p>
              )}
            </div>
          </div>
        </div>
      )
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
