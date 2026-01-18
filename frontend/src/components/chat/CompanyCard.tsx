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
    </div>
  )
}
