'use client'

import { SortableTable } from '@/components/SortableTable'

export default function TestTableSortingPage() {
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
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Feature #222: Table Sorting Test
          </h1>
          <p className="text-gray-600">
            This is a standalone test page for table sorting functionality.
            No authentication required.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Market Competitors - Financial Data
          </h2>
          <SortableTable columns={columns} data={data} />
        </div>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">Test Instructions:</h3>
          <ol className="text-sm text-blue-800 space-y-2 list-decimal list-inside">
            <li><strong>Step 1:</strong> Click "Company" header to sort alphabetically (A-Z)</li>
            <li><strong>Step 2:</strong> Verify companies are sorted alphabetically</li>
            <li><strong>Step 3:</strong> Click "Company" header again to reverse sort (Z-A)</li>
            <li><strong>Step 4:</strong> Verify companies are sorted in reverse</li>
            <li><strong>Step 5:</strong> Try sorting by "Revenue" column to test numeric sorting</li>
          </ol>
        </div>

        <div className="mt-4 p-4 bg-green-50 rounded-lg">
          <h3 className="font-semibold text-green-900 mb-2">Expected Behavior:</h3>
          <ul className="text-sm text-green-800 space-y-1 list-disc list-inside">
            <li>Clicking header shows up/down arrow icon</li>
            <li>Data reorders immediately</li>
            <li>String columns sort alphabetically</li>
            <li>Number columns sort numerically</li>
            <li>Clicking again reverses sort direction</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
