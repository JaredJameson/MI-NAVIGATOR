'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

interface UsageData {
  analyses_this_month: number
  analyses_limit: number
  storage_used_gb: number
  storage_limit_gb: number
  api_calls: number
  billing_period_start: string
  billing_period_end: string
  current_plan: string
}

export default function BillingPage() {
  const router = useRouter()
  const [usage, setUsage] = useState<UsageData>({
    analyses_this_month: 42,
    analyses_limit: 100,
    storage_used_gb: 2.4,
    storage_limit_gb: 10,
    api_calls: 8432,
    billing_period_start: '2026-01-01',
    billing_period_end: '2026-01-31',
    current_plan: 'Professional'
  })
  const [loading, setLoading] = useState(false)

  // Calculate percentages for progress bars
  const analysesPercentage = Math.round((usage.analyses_this_month / usage.analyses_limit) * 100)
  const storagePercentage = Math.round((usage.storage_used_gb / usage.storage_limit_gb) * 100)

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/settings" className="text-sm text-gray-600 hover:text-gray-900">
            ← Back to Settings
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">Billing & Usage</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {/* Current Plan */}
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Current Plan</h2>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-blue-600">{usage.current_plan}</div>
                <div className="mt-1 text-sm text-gray-600">
                  Billing period: {formatDate(usage.billing_period_start)} - {formatDate(usage.billing_period_end)}
                </div>
              </div>
              <div className="flex gap-3">
                <Link href="/settings/billing/downgrade" className="rounded-lg border border-gray-300 bg-white px-6 py-2 text-gray-700 hover:bg-gray-50">
                  Downgrade
                </Link>
                <Link href="/settings/billing/upgrade" className="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700">
                  Upgrade Plan
                </Link>
              </div>
            </div>
          </div>

          {/* Usage Statistics */}
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <h2 className="mb-6 text-lg font-semibold text-gray-900">Usage Statistics</h2>

            <div className="space-y-6">
              {/* Analyses */}
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-900">Analyses</div>
                    <div className="text-sm text-gray-600">Company profiles, market reports, etc.</div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900">
                      {usage.analyses_this_month} / {usage.analyses_limit}
                    </div>
                    <div className="text-sm text-gray-600">{analysesPercentage}% used</div>
                  </div>
                </div>
                <div className="h-2 rounded-full bg-gray-200">
                  <div
                    className={`h-full rounded-full ${
                      analysesPercentage >= 90 ? 'bg-red-500' :
                      analysesPercentage >= 75 ? 'bg-yellow-500' :
                      'bg-blue-500'
                    }`}
                    style={{ width: `${analysesPercentage}%` }}
                  />
                </div>
              </div>

              {/* Storage */}
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-900">Storage</div>
                    <div className="text-sm text-gray-600">Reports, exports, uploaded files</div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900">
                      {usage.storage_used_gb} GB / {usage.storage_limit_gb} GB
                    </div>
                    <div className="text-sm text-gray-600">{storagePercentage}% used</div>
                  </div>
                </div>
                <div className="h-2 rounded-full bg-gray-200">
                  <div
                    className={`h-full rounded-full ${
                      storagePercentage >= 90 ? 'bg-red-500' :
                      storagePercentage >= 75 ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                    style={{ width: `${storagePercentage}%` }}
                  />
                </div>
              </div>

              {/* API Calls */}
              <div>
                <div className="flex items-center justify-between rounded-lg bg-gray-50 p-4">
                  <div>
                    <div className="font-medium text-gray-900">API Calls</div>
                    <div className="text-sm text-gray-600">External data sources usage</div>
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {usage.api_calls.toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Billing Period */}
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Billing Period</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-600">Period Start</div>
                <div className="mt-1 font-medium text-gray-900">{formatDate(usage.billing_period_start)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Period End</div>
                <div className="mt-1 font-medium text-gray-900">{formatDate(usage.billing_period_end)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Days Remaining</div>
                <div className="mt-1 font-medium text-gray-900">
                  {Math.ceil((new Date(usage.billing_period_end).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Next Billing Date</div>
                <div className="mt-1 font-medium text-gray-900">{formatDate(usage.billing_period_end)}</div>
              </div>
            </div>
          </div>

          {/* Payment Methods */}
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Payment Methods</h2>
              <Link href="/settings/billing/payment-methods" className="text-blue-600 hover:text-blue-700">
                Manage →
              </Link>
            </div>
            <p className="text-gray-600">Manage your credit cards and payment methods</p>
          </div>

          {/* Billing History */}
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Billing History</h2>
            <div className="overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Invoice
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  <tr>
                    <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900">
                      #INV-2026-001
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-600">
                      Jan 1, 2026
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                      $99.00
                    </td>
                    <td className="whitespace-nowrap px-6 py-4">
                      <span className="inline-flex rounded-full bg-green-100 px-2 py-1 text-xs font-semibold text-green-800">
                        Paid
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-right text-sm">
                      <button
                        onClick={() => {
                          window.open(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/billing/invoices/INV-2026-001/download`, '_blank')
                        }}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Download PDF
                      </button>
                    </td>
                  </tr>
                  <tr>
                    <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900">
                      #INV-2025-012
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-600">
                      Dec 1, 2025
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                      $99.00
                    </td>
                    <td className="whitespace-nowrap px-6 py-4">
                      <span className="inline-flex rounded-full bg-green-100 px-2 py-1 text-xs font-semibold text-green-800">
                        Paid
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-right text-sm">
                      <button
                        onClick={() => {
                          window.open(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/billing/invoices/INV-2025-012/download`, '_blank')
                        }}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Download PDF
                      </button>
                    </td>
                  </tr>
                  <tr>
                    <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900">
                      #INV-2025-011
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-600">
                      Nov 1, 2025
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                      $99.00
                    </td>
                    <td className="whitespace-nowrap px-6 py-4">
                      <span className="inline-flex rounded-full bg-green-100 px-2 py-1 text-xs font-semibold text-green-800">
                        Paid
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-right text-sm">
                      <button
                        onClick={() => {
                          window.open(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/billing/invoices/INV-2025-011/download`, '_blank')
                        }}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Download PDF
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Plan Details */}
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Plan Features</h2>
            <ul className="space-y-3">
              <li className="flex items-start">
                <svg className="mr-3 h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">100 analyses per month</span>
              </li>
              <li className="flex items-start">
                <svg className="mr-3 h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">10 GB storage</span>
              </li>
              <li className="flex items-start">
                <svg className="mr-3 h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Unlimited API calls</span>
              </li>
              <li className="flex items-start">
                <svg className="mr-3 h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">PDF, DOCX, PPTX exports</span>
              </li>
              <li className="flex items-start">
                <svg className="mr-3 h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Priority support</span>
              </li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  )
}
