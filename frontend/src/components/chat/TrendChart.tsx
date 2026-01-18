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
  const chartColor = data.color || '#3b82f6'

  return (
    <div className="rounded-lg border bg-white p-4 shadow-sm">
      {data.title && (
        <h3 className="mb-4 font-semibold text-gray-900">{data.title}</h3>
      )}
      <ResponsiveContainer width="100%" height={300}>
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
  )
}
