'use client'

import React from 'react'
import { TrendChart } from '@/components/chat/TrendChart'
import { FinancialStatements } from '@/components/chat/FinancialStatements'

export default function TestChartColorsPage() {
  // Test data for TrendChart with multiple series
  const multiSeriesTrendData = {
    title: 'Multi-Series Trend Chart (4 series)',
    type: 'line' as const,
    data: [
      { month: 'Jan', series1: 4000, series2: 2400, series3: 3200, series4: 2800 },
      { month: 'Feb', series1: 3000, series2: 1398, series3: 2800, series4: 2400 },
      { month: 'Mar', series1: 2000, series2: 9800, series3: 4500, series4: 3200 },
      { month: 'Apr', series1: 2780, series2: 3908, series3: 2900, series4: 4100 },
      { month: 'May', series1: 1890, series2: 4800, series3: 3800, series4: 3500 },
      { month: 'Jun', series1: 2390, series2: 3800, series3: 4200, series4: 2900 },
    ],
    xKey: 'month',
    yKey: 'series1',
    yLabel: 'Value',
  }

  // Financial statements test data
  const financialData = {
    company_name: 'Test Company Sp. z o.o.',
    year: 2023,
    source: 'KRS',
    balance_sheet: {
      assets: {
        current_assets: {
          cash: 500000,
          receivables: 750000,
          inventory: 300000,
          other: 50000,
          total: 1600000,
        },
        fixed_assets: {
          property_plant_equipment: 2000000,
          intangible_assets: 300000,
          long_term_investments: 500000,
          other: 100000,
          total: 2900000,
        },
        total_assets: 4500000,
      },
      liabilities: {
        current_liabilities: {
          short_term_debt: 400000,
          accounts_payable: 350000,
          accrued_expenses: 150000,
          other: 50000,
          total: 950000,
        },
        long_term_liabilities: {
          long_term_debt: 1200000,
          deferred_tax: 100000,
          other: 50000,
          total: 1350000,
        },
        total_liabilities: 2300000,
      },
      equity: {
        share_capital: 500000,
        retained_earnings: 1500000,
        reserves: 200000,
        total_equity: 2200000,
      },
      total_liabilities_and_equity: 4500000,
    },
    income_statement: {
      revenue: {
        sales_revenue: 5000000,
        other_revenue: 100000,
        total_revenue: 5100000,
      },
      costs: {
        cost_of_goods_sold: 3000000,
        gross_profit: 2100000,
        operating_expenses: {
          selling_expenses: 500000,
          administrative_expenses: 400000,
          rd_expenses: 100000,
          total: 1000000,
        },
        operating_profit: 1100000,
        financial_costs: 100000,
        profit_before_tax: 1000000,
        income_tax: 190000,
        net_profit: 810000,
      },
      margins: {
        gross_margin: 41.2,
        operating_margin: 21.6,
        net_margin: 15.9,
      },
    },
    multi_year_summary: {
      years: [2019, 2020, 2021, 2022, 2023],
      revenue: [3500000, 4000000, 4500000, 4800000, 5100000],
      net_profit: [450000, 550000, 650000, 720000, 810000],
      total_assets: [3000000, 3500000, 4000000, 4200000, 4500000],
      equity: [1500000, 1700000, 1900000, 2050000, 2200000],
    },
    financial_ratios: {
      liquidity: {
        current_ratio: {
          value: 1.68,
          benchmark: 1.5,
          explanation: 'Stosunek aktywów obrotowych do zobowiązań krótkoterminowych',
        },
        quick_ratio: {
          value: 1.37,
          benchmark: 1.0,
          explanation: 'Stosunek najbardziej płynnych aktywów do zobowiązań krótkoterminowych',
        },
      },
      profitability: {
        roe: {
          value: 36.8,
          benchmark: 15.0,
          explanation: 'Zwrot z kapitału własnego',
        },
        roa: {
          value: 18.0,
          benchmark: 8.0,
          explanation: 'Zwrot z aktywów',
        },
        ros: {
          value: 15.9,
          benchmark: 10.0,
          explanation: 'Zwrot ze sprzedaży',
        },
      },
      leverage: {
        debt_ratio: {
          value: 51.1,
          benchmark: 60.0,
          explanation: 'Stosunek zobowiązań do aktywów',
        },
        debt_to_equity: {
          value: 1.05,
          benchmark: 1.5,
          explanation: 'Stosunek zobowiązań do kapitału własnego',
        },
      },
      efficiency: {
        inventory_turnover: {
          value: 16.7,
          benchmark: 12.0,
          explanation: 'Szybkość rotacji zapasów',
        },
        asset_turnover: {
          value: 1.13,
          benchmark: 1.0,
          explanation: 'Efektywność wykorzystania aktywów',
        },
      },
    },
    fetched_at: new Date().toISOString(),
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Chart Color Accessibility Test - Feature #194
          </h1>
          <p className="text-gray-600">
            Testing chart colors for distinctiveness and accessibility (including colorblind simulation)
          </p>
        </div>

        {/* Color Accessibility Guide */}
        <div className="mb-8 p-6 bg-white rounded-lg border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            🎨 Color Accessibility Guidelines
          </h2>
          <div className="space-y-2 text-sm text-gray-700">
            <p><strong>✓ Good palette should:</strong></p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Use colors distinguishable by people with color vision deficiencies</li>
              <li>Maintain sufficient contrast ratios (WCAG 2.1 AA minimum)</li>
              <li>Use patterns/shapes in addition to colors when possible</li>
              <li>Provide alternative text descriptions of data</li>
              <li>Include legends with clear labels</li>
            </ul>
          </div>
        </div>

        {/* Current Color Palette */}
        <div className="mb-8 p-6 bg-white rounded-lg border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Current Color Palette
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <div className="h-20 rounded" style={{ backgroundColor: '#3b82f6' }}></div>
              <p className="text-sm font-mono">#3b82f6</p>
              <p className="text-xs text-gray-600">Blue (Revenue)</p>
            </div>
            <div className="space-y-2">
              <div className="h-20 rounded" style={{ backgroundColor: '#10b981' }}></div>
              <p className="text-sm font-mono">#10b981</p>
              <p className="text-xs text-gray-600">Green (Profit)</p>
            </div>
            <div className="space-y-2">
              <div className="h-20 rounded" style={{ backgroundColor: '#8b5cf6' }}></div>
              <p className="text-sm font-mono">#8b5cf6</p>
              <p className="text-xs text-gray-600">Purple (Assets)</p>
            </div>
            <div className="space-y-2">
              <div className="h-20 rounded" style={{ backgroundColor: '#f59e0b' }}></div>
              <p className="text-sm font-mono">#f59e0b</p>
              <p className="text-xs text-gray-600">Amber (Equity)</p>
            </div>
          </div>
        </div>

        {/* Test Instructions */}
        <div className="mb-8 p-6 bg-blue-50 rounded-lg border border-blue-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            📋 Test Steps
          </h2>
          <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
            <li><strong>Visual Inspection:</strong> Verify colors are distinct from each other</li>
            <li><strong>Colorblind Simulation:</strong> Use browser extensions or tools to simulate different types of color vision deficiencies</li>
            <li><strong>Legend Clarity:</strong> Check if legend labels are clear and readable</li>
            <li><strong>Data Table Alternative:</strong> Verify "Show data table" buttons work and provide accessible alternatives</li>
            <li><strong>Pattern Support:</strong> Consider if patterns/dashes should be added to line charts</li>
          </ol>
        </div>

        {/* Chart Examples */}
        <div className="space-y-8">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              1. Basic Trend Chart (Single Series)
            </h2>
            <TrendChart data={{
              title: 'Revenue Trend 2019-2023',
              type: 'line',
              data: [
                { year: '2019', value: 3500000 },
                { year: '2020', value: 4000000 },
                { year: '2021', value: 4500000 },
                { year: '2022', value: 4800000 },
                { year: '2023', value: 5100000 },
              ],
              xKey: 'year',
              yKey: 'value',
              yLabel: 'Revenue (PLN)',
            }} />
          </div>

          <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              2. Bar Chart
            </h2>
            <TrendChart data={{
              title: 'Quarterly Sales 2023',
              type: 'bar',
              data: [
                { quarter: 'Q1', sales: 1200000 },
                { quarter: 'Q2', sales: 1350000 },
                { quarter: 'Q3', sales: 1280000 },
                { quarter: 'Q4', sales: 1270000 },
              ],
              xKey: 'quarter',
              yKey: 'sales',
              yLabel: 'Sales (PLN)',
            }} />
          </div>

          <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              3. Financial Statements (Multi-Series Line Charts)
            </h2>
            <FinancialStatements data={financialData} />
          </div>
        </div>

        {/* Colorblind Simulation Instructions */}
        <div className="mt-8 p-6 bg-yellow-50 rounded-lg border border-yellow-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            🔍 Colorblind Simulation Tools
          </h2>
          <div className="space-y-2 text-sm text-gray-700">
            <p><strong>Browser Extensions:</strong></p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li><strong>Chrome/Edge:</strong> "Colorblindly" or "NoCoffee Vision Simulator"</li>
              <li><strong>Firefox:</strong> Built-in accessibility simulator in DevTools</li>
            </ul>
            <p className="mt-4"><strong>Test with these vision types:</strong></p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li><strong>Protanopia:</strong> Red-blind (affects ~1% of males)</li>
              <li><strong>Deuteranopia:</strong> Green-blind (affects ~1% of males)</li>
              <li><strong>Tritanopia:</strong> Blue-blind (rare, affects ~0.001% of population)</li>
              <li><strong>Achromatopsia:</strong> Complete color blindness (very rare)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
