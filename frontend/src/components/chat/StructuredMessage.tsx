'use client'

import React from 'react'
import { CompanyCard, CompanyCardData } from './CompanyCard'
import { DataTable, DataTableData } from './DataTable'
import { TrendChart, TrendChartData } from './TrendChart'

export interface StructuredMessageData {
  type: 'company_card' | 'data_table' | 'trend_chart' | 'text'
  data: CompanyCardData | DataTableData | TrendChartData | { text: string }
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

    case 'text':
    default:
      return (
        <div className="whitespace-pre-wrap text-sm text-gray-900">
          {(structuredData.data as { text: string }).text || content}
        </div>
      )
  }
}
