'use client'

import React, { useState } from 'react'

interface Shareholder {
  name: string
  type: 'person' | 'company'
  nip?: string
  krs?: string
  shares_count: number
  shares_percentage: number
  shares_value: number
  voting_rights: number
  since: string
}

interface BeneficialOwner {
  name: string
  percentage: number
  direct: boolean
  source: string
}

interface RelatedCompany {
  name: string
  nip: string
  krs: string
  relationship: 'subsidiary' | 'parent' | 'associate'
  ownership_percentage: number
  description: string
}

interface OwnershipChainNode {
  level: number
  entity: string
  type: 'target' | 'person' | 'company' | 'fund'
  percentage?: number
  nip?: string
  via?: string
}

interface CapitalInfo {
  share_capital: number
  total_shares: number
  share_value: number
  currency: string
}

export interface OwnershipStructureData {
  company_name: string
  nip: string
  krs: string
  source: string
  shareholders: Shareholder[]
  beneficial_owners: BeneficialOwner[]
  related_companies: RelatedCompany[]
  ownership_chain: OwnershipChainNode[]
  capital_info: CapitalInfo
  fetched_at: string
}

interface OwnershipStructureProps {
  data: OwnershipStructureData
}

export function OwnershipStructure({ data }: OwnershipStructureProps) {
  const {
    company_name,
    nip,
    krs,
    source,
    shareholders,
    beneficial_owners,
    related_companies,
    ownership_chain,
    capital_info,
    fetched_at
  } = data

  // State for active tab
  const [activeTab, setActiveTab] = useState<'shareholders' | 'beneficial' | 'related' | 'tree'>('shareholders')

  // Helper function to format currency
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'decimal',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value) + ' zł'
  }

  // Helper function to format percentage
  const formatPercentage = (value: number): string => {
    return value.toFixed(1) + '%'
  }

  // Helper function to format date
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('pl-PL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(date)
  }

  // Get icon for shareholder type
  const getShareholderIcon = (type: string) => {
    if (type === 'person') {
      return (
        <svg className="h-5 w-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      )
    }
    return (
      <svg className="h-5 w-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
      </svg>
    )
  }

  // Get badge color for relationship
  const getRelationshipColor = (relationship: string) => {
    switch (relationship) {
      case 'subsidiary':
        return 'bg-green-100 text-green-800'
      case 'parent':
        return 'bg-blue-100 text-blue-800'
      case 'associate':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  // Get relationship label
  const getRelationshipLabel = (relationship: string) => {
    switch (relationship) {
      case 'subsidiary':
        return 'Spółka zależna'
      case 'parent':
        return 'Spółka dominująca'
      case 'associate':
        return 'Spółka powiązana'
      default:
        return relationship
    }
  }

  return (
    <div className="rounded-lg border bg-white shadow-sm">
      {/* Header */}
      <div className="border-b bg-orange-50 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <h3 className="text-sm font-semibold text-orange-900">Struktura właścicielska</h3>
          </div>
          <span className="text-xs text-orange-700">Źródło: {source}</span>
        </div>
      </div>

      <div className="p-4">
        {/* Company Name */}
        <div className="mb-4 border-b pb-3">
          <h4 className="text-lg font-bold text-gray-900">{company_name}</h4>
          <div className="mt-1 flex gap-4 text-xs text-gray-500">
            <span>NIP: <span className="font-mono font-semibold text-gray-900">{nip}</span></span>
            <span>KRS: <span className="font-mono font-semibold text-gray-900">{krs}</span></span>
          </div>
        </div>

        {/* Capital Information */}
        <div className="mb-4 rounded-lg bg-orange-50 p-3">
          <h5 className="mb-2 text-xs font-semibold uppercase text-orange-900">Kapitał zakładowy</h5>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-orange-700">Kapitał zakładowy</p>
              <p className="mt-0.5 font-mono text-sm font-bold text-orange-900">{formatCurrency(capital_info.share_capital)}</p>
            </div>
            <div>
              <p className="text-xs text-orange-700">Liczba udziałów</p>
              <p className="mt-0.5 font-mono text-sm font-bold text-orange-900">{capital_info.total_shares.toLocaleString('pl-PL')}</p>
            </div>
            <div>
              <p className="text-xs text-orange-700">Wartość udziału</p>
              <p className="mt-0.5 font-mono text-sm font-bold text-orange-900">{formatCurrency(capital_info.share_value)}</p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-4 border-b">
          <div className="flex gap-4">
            <button
              onClick={() => setActiveTab('shareholders')}
              className={`border-b-2 px-3 py-2 text-sm font-medium transition-colors ${
                activeTab === 'shareholders'
                  ? 'border-orange-600 text-orange-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Wspólnicy ({shareholders.length})
            </button>
            <button
              onClick={() => setActiveTab('beneficial')}
              className={`border-b-2 px-3 py-2 text-sm font-medium transition-colors ${
                activeTab === 'beneficial'
                  ? 'border-orange-600 text-orange-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Beneficjenci rzeczywiści ({beneficial_owners.length})
            </button>
            <button
              onClick={() => setActiveTab('related')}
              className={`border-b-2 px-3 py-2 text-sm font-medium transition-colors ${
                activeTab === 'related'
                  ? 'border-orange-600 text-orange-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Powiązania ({related_companies.length})
            </button>
            <button
              onClick={() => setActiveTab('tree')}
              className={`border-b-2 px-3 py-2 text-sm font-medium transition-colors ${
                activeTab === 'tree'
                  ? 'border-orange-600 text-orange-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Drzewo właścicielskie
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="min-h-[300px]">
          {/* Shareholders Tab */}
          {activeTab === 'shareholders' && (
            <div className="space-y-3">
              {shareholders.map((shareholder, index) => (
                <div
                  key={index}
                  className="rounded-lg border border-orange-100 bg-orange-50/50 p-3 hover:bg-orange-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      <div className="mt-0.5">
                        {getShareholderIcon(shareholder.type)}
                      </div>
                      <div className="flex-1">
                        <h6 className="font-semibold text-gray-900">{shareholder.name}</h6>
                        {shareholder.nip && (
                          <p className="mt-0.5 text-xs text-gray-500">
                            NIP: <span className="font-mono">{shareholder.nip}</span>
                            {shareholder.krs && <> • KRS: <span className="font-mono">{shareholder.krs}</span></>}
                          </p>
                        )}
                        <p className="mt-1 text-xs text-gray-600">Wspólnik od: {formatDate(shareholder.since)}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-orange-600">{formatPercentage(shareholder.shares_percentage)}</div>
                      <p className="mt-0.5 text-xs text-gray-600">{shareholder.shares_count.toLocaleString('pl-PL')} udziałów</p>
                      <p className="mt-0.5 text-xs text-gray-500">{formatCurrency(shareholder.shares_value)}</p>
                      <p className="mt-1 text-xs text-gray-500">Głosy: {formatPercentage(shareholder.voting_rights)}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Beneficial Owners Tab */}
          {activeTab === 'beneficial' && (
            <div className="space-y-3">
              <div className="rounded-lg bg-blue-50 p-3 text-sm text-blue-900">
                <p className="font-medium">ℹ️ Beneficjenci rzeczywiści</p>
                <p className="mt-1 text-xs text-blue-700">
                  Osoby fizyczne sprawujące bezpośrednią lub pośrednią kontrolę nad spółką (posiadające ponad 25% udziałów/głosów).
                </p>
              </div>
              {beneficial_owners.map((owner, index) => (
                <div
                  key={index}
                  className="rounded-lg border border-gray-200 p-3"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h6 className="font-semibold text-gray-900">{owner.name}</h6>
                        {owner.direct ? (
                          <span className="rounded bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800">
                            Bezpośredni
                          </span>
                        ) : (
                          <span className="rounded bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800">
                            Pośredni
                          </span>
                        )}
                      </div>
                      <p className="mt-1 text-xs text-gray-600">{owner.source}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-gray-900">{formatPercentage(owner.percentage)}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Related Companies Tab */}
          {activeTab === 'related' && (
            <div className="space-y-3">
              {related_companies.map((company, index) => (
                <div
                  key={index}
                  className="rounded-lg border border-gray-200 p-3 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h6 className="font-semibold text-gray-900">{company.name}</h6>
                        <span className={`rounded px-2 py-0.5 text-xs font-medium ${getRelationshipColor(company.relationship)}`}>
                          {getRelationshipLabel(company.relationship)}
                        </span>
                      </div>
                      <p className="mt-1 text-xs text-gray-500">
                        NIP: <span className="font-mono">{company.nip}</span> • KRS: <span className="font-mono">{company.krs}</span>
                      </p>
                      <p className="mt-2 text-sm text-gray-700">{company.description}</p>
                    </div>
                    <div className="ml-4 text-right">
                      <div className="text-lg font-bold text-gray-900">{formatPercentage(company.ownership_percentage)}</div>
                      <p className="text-xs text-gray-500">własności</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Ownership Tree Tab */}
          {activeTab === 'tree' && (
            <div className="space-y-2">
              <div className="rounded-lg bg-purple-50 p-3 text-sm text-purple-900 mb-4">
                <p className="font-medium">🌳 Drzewo właścicielskie</p>
                <p className="mt-1 text-xs text-purple-700">
                  Wizualizacja struktury właścicielskiej - od spółki docelowej do ostatecznych właścicieli.
                </p>
              </div>
              {ownership_chain.map((node, index) => {
                const indentLevel = node.level * 40
                const isTarget = node.type === 'target'
                const isPerson = node.type === 'person'
                const isCompany = node.type === 'company'
                const isFund = node.type === 'fund'

                return (
                  <div
                    key={index}
                    className="flex items-center"
                    style={{ paddingLeft: `${indentLevel}px` }}
                  >
                    {node.level > 0 && (
                      <div className="flex items-center mr-2">
                        <div className="h-0.5 w-6 bg-gray-300"></div>
                        <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    )}
                    <div className={`flex-1 rounded-lg border p-2 ${
                      isTarget
                        ? 'border-orange-300 bg-orange-100'
                        : isPerson
                        ? 'border-blue-200 bg-blue-50'
                        : isCompany
                        ? 'border-green-200 bg-green-50'
                        : 'border-purple-200 bg-purple-50'
                    }`}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {isPerson && (
                            <svg className="h-4 w-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                          )}
                          {(isCompany || isTarget) && (
                            <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                            </svg>
                          )}
                          {isFund && (
                            <svg className="h-4 w-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          )}
                          <span className="text-sm font-semibold text-gray-900">{node.entity}</span>
                        </div>
                        <div className="text-right">
                          {node.percentage !== undefined && (
                            <span className="text-sm font-bold text-gray-900">{formatPercentage(node.percentage)}</span>
                          )}
                        </div>
                      </div>
                      {node.nip && (
                        <p className="mt-0.5 text-xs text-gray-500">NIP: <span className="font-mono">{node.nip}</span></p>
                      )}
                      {node.via && (
                        <p className="mt-0.5 text-xs text-gray-600 italic">poprzez: {node.via}</p>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-4 border-t pt-3 text-xs text-gray-500">
          <p>Dane pobrane: {new Date(fetched_at).toLocaleString('pl-PL', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })}</p>
        </div>
      </div>
    </div>
  )
}
