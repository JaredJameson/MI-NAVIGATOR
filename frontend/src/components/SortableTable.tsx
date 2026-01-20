'use client'

import { useState } from 'react'
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react'

type SortDirection = 'asc' | 'desc' | null

interface Column {
  key: string
  label: string
  sortable?: boolean
}

interface SortableTableProps {
  columns: Column[]
  data: Record<string, any>[]
  className?: string
}

export function SortableTable({ columns, data, className = '' }: SortableTableProps) {
  const [sortColumn, setSortColumn] = useState<string | null>(null)
  const [sortDirection, setSortDirection] = useState<SortDirection>(null)

  const handleSort = (columnKey: string) => {
    const column = columns.find(col => col.key === columnKey)
    if (!column?.sortable) return

    if (sortColumn === columnKey) {
      // Cycle through: asc -> desc -> null
      if (sortDirection === 'asc') {
        setSortDirection('desc')
      } else if (sortDirection === 'desc') {
        setSortColumn(null)
        setSortDirection(null)
      }
    } else {
      setSortColumn(columnKey)
      setSortDirection('asc')
    }
  }

  const sortedData = [...data]
  if (sortColumn && sortDirection) {
    sortedData.sort((a, b) => {
      const aVal = a[sortColumn]
      const bVal = b[sortColumn]

      // Handle null/undefined
      if (aVal == null && bVal == null) return 0
      if (aVal == null) return 1
      if (bVal == null) return -1

      // Numeric comparison
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal
      }

      // String comparison
      const aStr = String(aVal).toLowerCase()
      const bStr = String(bVal).toLowerCase()

      if (sortDirection === 'asc') {
        return aStr.localeCompare(bStr)
      } else {
        return bStr.localeCompare(aStr)
      }
    })
  }

  const getSortIcon = (columnKey: string) => {
    const column = columns.find(col => col.key === columnKey)
    if (!column?.sortable) return null

    if (sortColumn !== columnKey) {
      return <ChevronsUpDown className="w-4 h-4 text-gray-400" />
    }

    if (sortDirection === 'asc') {
      return <ChevronUp className="w-4 h-4 text-blue-600" />
    } else {
      return <ChevronDown className="w-4 h-4 text-blue-600" />
    }
  }

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                onClick={() => handleSort(column.key)}
                className={`px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider ${
                  column.sortable ? 'cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 select-none' : ''
                }`}
                role={column.sortable ? 'button' : undefined}
                aria-sort={
                  sortColumn === column.key
                    ? sortDirection === 'asc'
                      ? 'ascending'
                      : 'descending'
                    : undefined
                }
              >
                <div className="flex items-center gap-2">
                  <span>{column.label}</span>
                  {getSortIcon(column.key)}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
          {sortedData.map((row, idx) => (
            <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-800">
              {columns.map((column) => (
                <td
                  key={column.key}
                  className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100"
                >
                  {row[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
