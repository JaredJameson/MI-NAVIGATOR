'use client'

import React from 'react'

export interface DataTableColumn {
  key: string
  label: string
  align?: 'left' | 'center' | 'right'
  format?: 'number' | 'currency' | 'percent' | 'text'
}

export interface DataTableRow {
  [key: string]: string | number
}

export interface DataTableData {
  title?: string
  columns: DataTableColumn[]
  rows: DataTableRow[]
}

interface DataTableProps {
  data: DataTableData
}

export function DataTable({ data }: DataTableProps) {
  const formatValue = (value: string | number, format?: string): string => {
    if (typeof value === 'number') {
      switch (format) {
        case 'currency':
          return new Intl.NumberFormat('pl-PL', {
            style: 'currency',
            currency: 'PLN',
          }).format(value)
        case 'percent':
          return `${value.toFixed(2)}%`
        case 'number':
          return new Intl.NumberFormat('pl-PL').format(value)
        default:
          return String(value)
      }
    }
    return String(value)
  }

  return (
    <div className="rounded-lg border bg-white shadow-sm">
      {data.title && (
        <div className="border-b px-4 py-3">
          <h3 className="font-semibold text-gray-900">{data.title}</h3>
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b bg-gray-50">
              {data.columns.map((column) => (
                <th
                  key={column.key}
                  className={`px-4 py-3 text-xs font-semibold text-gray-700 ${
                    column.align === 'right'
                      ? 'text-right'
                      : column.align === 'center'
                      ? 'text-center'
                      : 'text-left'
                  }`}
                >
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row, rowIndex) => (
              <tr key={rowIndex} className="border-b last:border-b-0 hover:bg-gray-50">
                {data.columns.map((column) => (
                  <td
                    key={column.key}
                    className={`px-4 py-3 text-sm text-gray-900 ${
                      column.align === 'right'
                        ? 'text-right'
                        : column.align === 'center'
                        ? 'text-center'
                        : 'text-left'
                    }`}
                  >
                    {formatValue(row[column.key], column.format)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
