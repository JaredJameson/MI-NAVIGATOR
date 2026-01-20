'use client';

import { useState } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

interface CompetitorPosition {
  company_name: string;
  x: number;
  y: number;
  size: number;
  color: string;
}

interface CompetitiveAnalysisData {
  target_company: string;
  competitors: CompetitorPosition[];
  x_axis_label: string;
  y_axis_label: string;
}

export default function CompetitivePage() {
  const [companyId, setCompanyId] = useState('fado');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<CompetitiveAnalysisData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadAnalysis = async () => {
    if (!companyId.trim()) {
      setError('Proszę podać ID firmy');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/analysis/competitive/${companyId}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Nie udało się załadować danych');
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const dataPoint = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
          <p className="font-bold text-gray-900">{dataPoint.company_name}</p>
          <p className="text-sm text-gray-600">Jakość: {dataPoint.x.toFixed(1)}</p>
          <p className="text-sm text-gray-600">Wartość: {dataPoint.y.toFixed(1)}</p>
          <p className="text-sm text-gray-600">Udział: {dataPoint.size.toFixed(1)}%</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Mapa pozycjonowania konkurencji
        </h1>

        {/* Input Section */}
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label htmlFor="companyId" className="block text-sm font-medium text-gray-700 mb-2">
                ID Firmy
              </label>
              <input
                id="companyId"
                type="text"
                value={companyId}
                onChange={(e) => setCompanyId(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="np. fado, company_001"
              />
            </div>
            <button
              onClick={loadAnalysis}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Ładowanie...' : 'Analizuj'}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
              ❌ {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        {data && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Pozycjonowanie: {data.target_company}
            </h2>

            {/* Positioning Map */}
            <div className="mb-8">
              <ResponsiveContainer width="100%" height={500}>
                <ScatterChart
                  margin={{ top: 20, right: 20, bottom: 60, left: 60 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    type="number"
                    dataKey="x"
                    name={data.x_axis_label}
                    domain={[0, 10]}
                    label={{
                      value: data.x_axis_label,
                      position: 'insideBottom',
                      offset: -40,
                      style: { fontSize: 14, fontWeight: 600 }
                    }}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis
                    type="number"
                    dataKey="y"
                    name={data.y_axis_label}
                    domain={[0, 10]}
                    label={{
                      value: data.y_axis_label,
                      angle: -90,
                      position: 'insideLeft',
                      offset: -40,
                      style: { fontSize: 14, fontWeight: 600 }
                    }}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend
                    verticalAlign="top"
                    height={36}
                    wrapperStyle={{ paddingBottom: '20px' }}
                    formatter={(value, entry: any) => {
                      const competitor = data.competitors.find(c => c.company_name === entry.payload.company_name);
                      return competitor ? competitor.company_name : value;
                    }}
                  />
                  <Scatter
                    name="Konkurenci"
                    data={data.competitors}
                    dataKey="size"
                  >
                    {data.competitors.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.color}
                        stroke={entry.company_name === data.target_company.split(' ')[0] ? '#000' : 'none'}
                        strokeWidth={entry.company_name === data.target_company.split(' ')[0] ? 2 : 0}
                      />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>

            {/* Legend Table */}
            <div className="mt-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Konkurenci:</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Firma
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Jakość / Innowacyjność
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Wartość
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Udział w rynku (%)
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Kolor
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {data.competitors.map((competitor, index) => (
                      <tr
                        key={index}
                        className={`hover:bg-gray-50 ${
                          competitor.company_name === data.target_company.split(' ')[0]
                            ? 'bg-blue-50 font-semibold'
                            : ''
                        }`}
                      >
                        <td className="px-4 py-3 whitespace-nowrap">
                          {competitor.company_name}
                          {competitor.company_name === data.target_company.split(' ')[0] && (
                            <span className="ml-2 text-xs text-blue-600">(Ty)</span>
                          )}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          {competitor.x.toFixed(1)}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          {competitor.y.toFixed(1)}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          {competitor.size.toFixed(1)}%
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="flex items-center gap-2">
                            <div
                              className="w-6 h-6 rounded-full border border-gray-300"
                              style={{ backgroundColor: competitor.color }}
                            />
                            <span className="text-xs text-gray-500">{competitor.color}</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Insights */}
            <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">📊 Wnioski</h3>
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                <li>
                  <strong>{data.target_company.split(' ')[0]}</strong> znajduje się w{' '}
                  {data.competitors.find(c => c.company_name === data.target_company.split(' ')[0])?.x || 0 > 6
                    ? 'segmencie wysokiej jakości'
                    : 'segmencie niskiej jakości'}
                </li>
                <li>
                  Najsilniejszy konkurent:{' '}
                  <strong>
                    {data.competitors.reduce((max, c) => c.size > max.size ? c : max).company_name}
                  </strong>
                  {' '}({data.competitors.reduce((max, c) => c.size > max.size ? c : max).size.toFixed(1)}% udziału)
                </li>
                <li>
                  Liczba konkurentów na mapie: <strong>{data.competitors.length}</strong>
                </li>
              </ul>
            </div>
          </div>
        )}

        {!data && !loading && (
          <div className="bg-white p-12 rounded-lg shadow text-center text-gray-500">
            <div className="text-6xl mb-4">📈</div>
            <p className="text-lg">Wprowadź ID firmy i kliknij "Analizuj" aby zobaczyć mapę pozycjonowania</p>
          </div>
        )}
      </div>
    </div>
  );
}
