'use client'

import React from 'react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

export interface TrendChartDataPoint {
  label: string
  value: number
  [key: string]: string | number
}

export interface TrendChartData {
  title?: string
  type: 'line' | 'bar'
  data: TrendChartDataPoint[]
  xKey: string
  yKey: string
  yLabel?: string
  color?: string
}

interface TrendChartProps {
  data: TrendChartData
}

export function TrendChart({ data }: TrendChartProps) {
  const [showDataTable, setShowDataTable] = React.useState(false)
  const chartColor = data.color || '#3b82f6'

  // Generate accessible description
  const getChartDescription = () => {
    const chartType = data.type === 'line' ? 'Wykres liniowy' : 'Wykres słupkowy'
    const dataPoints = data.data.length
    const values = data.data.map(d => d[data.yKey] as number)
    const min = Math.min(...values)
    const max = Math.max(...values)
    return `${chartType} pokazujący ${dataPoints} punktów danych. Wartości od ${min} do ${max}.`
  }

  return (
    <div className="rounded-lg border bg-white p-4 shadow-sm">
      {data.title && (
        <h3 className="mb-4 font-semibold text-gray-900">{data.title}</h3>
      )}

      {/* Toggle button for data table */}
      <div className="mb-3 flex justify-end">
        <button
          onClick={() => setShowDataTable(!showDataTable)}
          className="text-sm text-blue-600 hover:text-blue-800 underline focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded px-2 py-1"
          aria-expanded={showDataTable}
          aria-controls="chart-data-table"
        >
          {showDataTable ? 'Ukryj tabelę danych' : 'Pokaż tabelę danych'}
        </button>
      </div>

      {/* Screen reader only description */}
      <div className="sr-only" aria-live="polite">
        {getChartDescription()}
      </div>

      <div
        role="img"
        aria-label={data.title ? `${data.title}: ${getChartDescription()}` : getChartDescription()}
      >
        <ResponsiveContainer
          width="100%"
          height={300}
        >
        {data.type === 'line' ? (
          <LineChart data={data.data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey={data.xKey}
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
            />
            <YAxis
              label={
                data.yLabel
                  ? { value: data.yLabel, angle: -90, position: 'insideLeft', style: { fontSize: 12 } }
                  : undefined
              }
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                fontSize: '12px',
              }}
            />
            <Legend wrapperStyle={{ fontSize: '12px' }} />
            <Line
              type="monotone"
              dataKey={data.yKey}
              stroke={chartColor}
              strokeWidth={2}
              dot={{ fill: chartColor, r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        ) : (
          <BarChart data={data.data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey={data.xKey}
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
            />
            <YAxis
              label={
                data.yLabel
                  ? { value: data.yLabel, angle: -90, position: 'insideLeft', style: { fontSize: 12 } }
                  : undefined
              }
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                fontSize: '12px',
              }}
            />
            <Legend wrapperStyle={{ fontSize: '12px' }} />
            <Bar dataKey={data.yKey} fill={chartColor} radius={[4, 4, 0, 0]} />
          </BarChart>
        )}
      </ResponsiveContainer>
      </div>

      {/* Accessible data table */}
      {showDataTable && (
        <div id="chart-data-table" className="mt-4 border-t pt-4">
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Dane wykresu</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-gray-200 rounded">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left font-semibold text-gray-900 border-b">
                    {data.xKey}
                  </th>
                  <th className="px-4 py-2 text-right font-semibold text-gray-900 border-b">
                    {data.yLabel || data.yKey}
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.data.map((point, idx) => (
                  <tr key={idx} className="border-b last:border-b-0 hover:bg-gray-50">
                    <td className="px-4 py-2 text-gray-700">
                      {point[data.xKey]}
                    </td>
                    <td className="px-4 py-2 text-right font-mono text-gray-900">
                      {typeof point[data.yKey] === 'number'
                        ? point[data.yKey].toLocaleString('pl-PL')
                        : point[data.yKey]}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
