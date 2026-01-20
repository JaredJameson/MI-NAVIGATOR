'use client'

import { SortableTable } from '@/components/SortableTable'

export default function TableTestPage() {
  const columns = [
    { key: 'company', label: 'Company', sortable: true },
    { key: 'revenue', label: 'Revenue (PLN)', sortable: true },
    { key: 'employees', label: 'Employees', sortable: true },
    { key: 'year', label: 'Year', sortable: true },
    { key: 'status', label: 'Status', sortable: true },
  ]

  const data = [
    { company: 'Plastmet Poland', revenue: 45000000, employees: 250, year: 2023, status: 'Active' },
    { company: 'TechnoForm', revenue: 12500000, employees: 85, year: 2023, status: 'Active' },
    { company: 'MoldWorks', revenue: 28000000, employees: 150, year: 2022, status: 'Active' },
    { company: 'PolyPro Industries', revenue: 67000000, employees: 320, year: 2023, status: 'Active' },
    { company: 'InjectionTech', revenue: 8900000, employees: 45, year: 2023, status: 'Inactive' },
    { company: 'PrecisionMold', revenue: 34000000, employees: 180, year: 2022, status: 'Active' },
    { company: 'AutoPlast', revenue: 52000000, employees: 280, year: 2023, status: 'Active' },
    { company: 'RapidForm', revenue: 19000000, employees: 95, year: 2022, status: 'Active' },
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Table Sorting Test - Feature #222
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Click column headers to sort. Click again to reverse sort. Click a third time to clear sorting.
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Market Competitors - Financial Data
          </h2>
          <SortableTable columns={columns} data={data} />
        </div>

        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">Test Instructions:</h3>
          <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
            <li>✓ Click "Company" header to sort alphabetically A-Z</li>
            <li>✓ Click again to sort Z-A</li>
            <li>✓ Click third time to return to original order</li>
            <li>✓ Try sorting by Revenue to see numeric sorting</li>
            <li>✓ Try sorting by different columns</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
