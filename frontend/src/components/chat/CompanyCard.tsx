'use client'

import React from 'react'

export interface CompanyCardData {
  name: string
  nip?: string
  krs?: string
  address?: string
  industry?: string
  status?: string
  capital?: string
  founded?: string
  employees?: string
  description?: string
  industry_specific?: {
    machinery_type?: string
    production_capacity_tons?: string
    mold_count?: string
    material_types?: string[]
    certifications?: string[]
    cycle_time_efficiency?: string
    oee?: string
    scrap_rate?: string
  }
  terminology_note?: string
}

interface CompanyCardProps {
  data: CompanyCardData
}

export function CompanyCard({ data }: CompanyCardProps) {
  return (
    <div className="rounded-lg border bg-white p-4 shadow-sm">
      {/* Header */}
      <div className="mb-4 border-b pb-3">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-bold text-gray-900">{data.name}</h3>
            {data.industry && (
              <p className="mt-1 text-sm text-gray-600">{data.industry}</p>
            )}
          </div>
          {data.status && (
            <span
              className={`rounded-full px-3 py-1 text-xs font-medium ${
                data.status.toLowerCase() === 'active' || data.status.toLowerCase() === 'aktywna'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {data.status}
            </span>
          )}
        </div>
      </div>

      {/* Company Details Grid */}
      <div className="grid grid-cols-2 gap-4">
        {data.nip && (
          <div>
            <p className="text-xs font-medium text-gray-500">NIP</p>
            <p className="mt-1 text-sm font-semibold text-gray-900">{data.nip}</p>
          </div>
        )}
        {data.krs && (
          <div>
            <p className="text-xs font-medium text-gray-500">KRS</p>
            <p className="mt-1 text-sm font-semibold text-gray-900">{data.krs}</p>
          </div>
        )}
        {data.founded && (
          <div>
            <p className="text-xs font-medium text-gray-500">Founded</p>
            <p className="mt-1 text-sm font-semibold text-gray-900">{data.founded}</p>
          </div>
        )}
        {data.employees && (
          <div>
            <p className="text-xs font-medium text-gray-500">Employees</p>
            <p className="mt-1 text-sm font-semibold text-gray-900">{data.employees}</p>
          </div>
        )}
        {data.capital && (
          <div>
            <p className="text-xs font-medium text-gray-500">Capital</p>
            <p className="mt-1 text-sm font-semibold text-gray-900">{data.capital}</p>
          </div>
        )}
        {data.address && (
          <div className="col-span-2">
            <p className="text-xs font-medium text-gray-500">Address</p>
            <p className="mt-1 text-sm text-gray-900">{data.address}</p>
          </div>
        )}
      </div>

      {/* Description */}
      {data.description && (
        <div className="mt-4 border-t pt-3">
          <p className="text-xs font-medium text-gray-500">Description</p>
          <p className="mt-2 text-sm text-gray-700">{data.description}</p>
        </div>
      )}

      {/* Industry-Specific Fields */}
      {data.industry_specific && (
        <div className="mt-4 border-t pt-3">
          <p className="mb-3 text-xs font-medium text-blue-600">Industry-Specific Information</p>

          <div className="grid grid-cols-2 gap-4">
            {data.industry_specific.machinery_type && (
              <div className="col-span-2">
                <p className="text-xs font-medium text-gray-500">Machinery</p>
                <p className="mt-1 text-sm text-gray-900">{data.industry_specific.machinery_type}</p>
              </div>
            )}
            {data.industry_specific.production_capacity_tons && (
              <div>
                <p className="text-xs font-medium text-gray-500">Production Capacity</p>
                <p className="mt-1 text-sm font-semibold text-gray-900">{data.industry_specific.production_capacity_tons}</p>
              </div>
            )}
            {data.industry_specific.mold_count && (
              <div>
                <p className="text-xs font-medium text-gray-500">Mold Count</p>
                <p className="mt-1 text-sm font-semibold text-gray-900">{data.industry_specific.mold_count}</p>
              </div>
            )}
            {data.industry_specific.cycle_time_efficiency && (
              <div>
                <p className="text-xs font-medium text-gray-500">Cycle Time Efficiency</p>
                <p className="mt-1 text-sm font-semibold text-green-600">{data.industry_specific.cycle_time_efficiency}</p>
              </div>
            )}
            {data.industry_specific.oee && (
              <div>
                <p className="text-xs font-medium text-gray-500">OEE</p>
                <p className="mt-1 text-sm font-semibold text-green-600">{data.industry_specific.oee}</p>
              </div>
            )}
            {data.industry_specific.scrap_rate && (
              <div>
                <p className="text-xs font-medium text-gray-500">Scrap Rate</p>
                <p className="mt-1 text-sm font-semibold text-gray-900">{data.industry_specific.scrap_rate}</p>
              </div>
            )}
            {data.industry_specific.material_types && data.industry_specific.material_types.length > 0 && (
              <div className="col-span-2">
                <p className="text-xs font-medium text-gray-500">Material Types</p>
                <div className="mt-1 flex flex-wrap gap-2">
                  {data.industry_specific.material_types.map((material, idx) => (
                    <span key={idx} className="rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-700">
                      {material}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {data.industry_specific.certifications && data.industry_specific.certifications.length > 0 && (
              <div className="col-span-2">
                <p className="text-xs font-medium text-gray-500">Certifications</p>
                <div className="mt-1 flex flex-wrap gap-2">
                  {data.industry_specific.certifications.map((cert, idx) => (
                    <span key={idx} className="rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800">
                      {cert}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Terminology Note */}
      {data.terminology_note && (
        <div className="mt-3 rounded bg-blue-50 p-2">
          <p className="text-xs text-blue-700">
            <span className="font-medium">ℹ️ </span>
            {data.terminology_note}
          </p>
        </div>
      )}
    </div>
  )
}
