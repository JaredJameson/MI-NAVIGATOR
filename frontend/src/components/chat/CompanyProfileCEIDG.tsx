'use client'

import React, { useState } from 'react'

interface PKDCode {
  code: string
  name: string
  category: string
}

interface BasicInfo {
  business_name: string
  owner_name: string
  nip: string
  regon: string
  address: string
  status: string
  founded: string
}

export interface CompanyProfileCEIDGData {
  lookup_type: string
  identifier: string
  basic_info: BasicInfo
  pkd_codes: PKDCode[]
  source: string
  fetched_at: string
}

interface CompanyProfileCEIDGProps {
  data: CompanyProfileCEIDGData
}

export function CompanyProfileCEIDG({ data }: CompanyProfileCEIDGProps) {
  const { basic_info, pkd_codes, source, fetched_at, lookup_type, identifier } = data

  // State for expandable sections
  const [expandedSections, setExpandedSections] = useState({
    registration: true,
    address: true,
    pkd: true
  })

  const toggleSection = (section: 'registration' | 'address' | 'pkd') => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  return (
    <div className="rounded-lg border bg-white shadow-sm">
      {/* Header with source badge */}
      <div className="border-b bg-green-50 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <h3 className="text-sm font-semibold text-green-900">Dane z {source}</h3>
          </div>
          <span className="text-xs text-green-700">Wyszukano po {lookup_type}: {identifier}</span>
        </div>
      </div>

      <div className="p-4">
        {/* Business Name & Owner */}
        <div className="mb-4 border-b pb-3">
          <div className="flex items-start justify-between">
            <div>
              <h4 className="text-lg font-bold text-gray-900">{basic_info.business_name}</h4>
              <p className="mt-1 text-sm text-gray-600">
                Właściciel: <span className="font-medium text-gray-900">{basic_info.owner_name}</span>
              </p>
              <p className="mt-1 text-sm text-gray-500">
                Status: <span className={`font-medium ${basic_info.status.toLowerCase() === 'active' ? 'text-green-600' : 'text-gray-600'}`}>{basic_info.status}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Registration Data */}
        <div className="mb-4">
          <button
            onClick={() => toggleSection('registration')}
            className="flex w-full items-center justify-between text-left hover:bg-gray-50 rounded px-1 py-1 transition-colors"
          >
            <h5 className="text-xs font-semibold uppercase text-gray-700">Dane rejestrowe</h5>
            <svg
              className={`h-4 w-4 text-gray-500 transition-transform ${expandedSections.registration ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          {expandedSections.registration && (
            <div className="mt-2 grid grid-cols-2 gap-3">
              <div className="rounded-md bg-gray-50 p-2">
                <p className="text-xs font-medium text-gray-500">NIP</p>
                <p className="mt-0.5 font-mono text-sm font-semibold text-gray-900">{basic_info.nip}</p>
              </div>
              <div className="rounded-md bg-gray-50 p-2">
                <p className="text-xs font-medium text-gray-500">REGON</p>
                <p className="mt-0.5 font-mono text-sm font-semibold text-gray-900">{basic_info.regon}</p>
              </div>
              <div className="rounded-md bg-gray-50 p-2 col-span-2">
                <p className="text-xs font-medium text-gray-500">Data rozpoczęcia działalności</p>
                <p className="mt-0.5 text-sm font-semibold text-gray-900">{basic_info.founded}</p>
              </div>
            </div>
          )}
        </div>

        {/* Address */}
        <div className="mb-4">
          <button
            onClick={() => toggleSection('address')}
            className="flex w-full items-center justify-between text-left hover:bg-gray-50 rounded px-1 py-1 transition-colors"
          >
            <h5 className="text-xs font-semibold uppercase text-gray-700">Adres prowadzenia działalności</h5>
            <svg
              className={`h-4 w-4 text-gray-500 transition-transform ${expandedSections.address ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          {expandedSections.address && (
            <div className="mt-2 rounded-md bg-gray-50 p-2">
              <p className="text-sm text-gray-900">{basic_info.address}</p>
            </div>
          )}
        </div>

        {/* PKD Codes */}
        {pkd_codes && pkd_codes.length > 0 && (
          <div className="mb-4">
            <button
              onClick={() => toggleSection('pkd')}
              className="flex w-full items-center justify-between text-left hover:bg-gray-50 rounded px-1 py-1 transition-colors"
            >
              <h5 className="text-xs font-semibold uppercase text-gray-700">
                Przedmiot przeważającej działalności (PKD)
              </h5>
              <svg
                className={`h-4 w-4 text-gray-500 transition-transform ${expandedSections.pkd ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {expandedSections.pkd && (
              <div className="mt-2 space-y-2">
                {pkd_codes.map((pkd, index) => (
                  <div key={index} className="rounded-md border border-gray-200 bg-white p-2">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="rounded bg-green-100 px-2 py-0.5 font-mono text-xs font-semibold text-green-800">
                            {pkd.code}
                          </span>
                          <span className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                            {pkd.category}
                          </span>
                        </div>
                        <p className="mt-1 text-sm text-gray-700">{pkd.name}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Footer with timestamp */}
        <div className="border-t pt-3 text-center">
          <p className="text-xs text-gray-500">
            Dane pobrano: {new Date(fetched_at).toLocaleString('pl-PL')}
          </p>
        </div>
      </div>
    </div>
  )
}
