import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface RatioData {
  value: number;
  benchmark: number;
  explanation: string;
}

interface FinancialStatementsData {
  company_name: string;
  year: number;
  source: string;
  balance_sheet: {
    assets: {
      current_assets: {
        cash: number;
        receivables: number;
        inventory: number;
        other: number;
        total: number;
      };
      fixed_assets: {
        property_plant_equipment: number;
        intangible_assets: number;
        long_term_investments: number;
        other: number;
        total: number;
      };
      total_assets: number;
    };
    liabilities: {
      current_liabilities: {
        short_term_debt: number;
        accounts_payable: number;
        accrued_expenses: number;
        other: number;
        total: number;
      };
      long_term_liabilities: {
        long_term_debt: number;
        deferred_tax: number;
        other: number;
        total: number;
      };
      total_liabilities: number;
    };
    equity: {
      share_capital: number;
      retained_earnings: number;
      reserves: number;
      total_equity: number;
    };
    total_liabilities_and_equity: number;
  };
  income_statement: {
    revenue: {
      sales_revenue: number;
      other_revenue: number;
      total_revenue: number;
    };
    costs: {
      cost_of_goods_sold: number;
      gross_profit: number;
      operating_expenses: {
        selling_expenses: number;
        administrative_expenses: number;
        rd_expenses: number;
        total: number;
      };
      operating_profit: number;
      financial_costs: number;
      profit_before_tax: number;
      income_tax: number;
      net_profit: number;
    };
    margins: {
      gross_margin: number;
      operating_margin: number;
      net_margin: number;
    };
  };
  multi_year_summary?: {
    years: number[];
    revenue: number[];
    net_profit: number[];
    total_assets: number[];
    equity: number[];
  };
  financial_ratios?: {
    liquidity: {
      current_ratio: RatioData;
      quick_ratio: RatioData;
    };
    profitability: {
      roe: RatioData;
      roa: RatioData;
      ros: RatioData;
    };
    leverage: {
      debt_ratio: RatioData;
      debt_to_equity: RatioData;
    };
    efficiency: {
      inventory_turnover: RatioData;
      asset_turnover: RatioData;
    };
  };
  fetched_at: string;
}

interface FinancialStatementsProps {
  data: FinancialStatementsData;
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

const formatPercent = (value: number): string => {
  return `${value.toFixed(1)}%`;
};

export const FinancialStatements: React.FC<FinancialStatementsProps> = ({ data }) => {
  const [activeTab, setActiveTab] = useState<'balance' | 'income' | 'summary' | 'ratios'>('balance');

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleString('pl-PL', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className="border rounded-lg shadow-sm bg-white overflow-hidden">
      {/* Header */}
      <div className="bg-purple-50 px-6 py-4 border-b">
        <div className="flex items-center gap-3">
          <div className="text-2xl">📊</div>
          <div className="flex-1">
            <div className="text-xs font-semibold text-purple-900 uppercase tracking-wide">
              Dane z {data.source}
            </div>
            <div className="text-sm text-purple-700">
              Sprawozdanie finansowe {data.company_name} za {data.year} rok
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b bg-gray-50">
        <button
          onClick={() => setActiveTab('balance')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'balance'
              ? 'border-b-2 border-purple-600 text-purple-900 bg-white'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          }`}
        >
          Bilans
        </button>
        <button
          onClick={() => setActiveTab('income')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'income'
              ? 'border-b-2 border-purple-600 text-purple-900 bg-white'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          }`}
        >
          Rachunek zysków i strat
        </button>
        {data.multi_year_summary && (
          <button
            onClick={() => setActiveTab('summary')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'summary'
                ? 'border-b-2 border-purple-600 text-purple-900 bg-white'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            Podsumowanie wieloletnie
          </button>
        )}
        {data.financial_ratios && (
          <button
            onClick={() => setActiveTab('ratios')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'ratios'
                ? 'border-b-2 border-purple-600 text-purple-900 bg-white'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            Wskaźniki finansowe
          </button>
        )}
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Balance Sheet Tab */}
        {activeTab === 'balance' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-900">AKTYWA</h3>

              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Aktywa obrotowe</h4>
                <div className="bg-gray-50 rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <tbody>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Środki pieniężne</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.assets.current_assets.cash)}</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Należności</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.assets.current_assets.receivables)}</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Zapasy</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.assets.current_assets.inventory)}</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Inne</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.assets.current_assets.other)}</td>
                      </tr>
                      <tr className="bg-purple-50">
                        <td className="px-4 py-2 font-semibold text-gray-900">Razem aktywa obrotowe</td>
                        <td className="px-4 py-2 text-right font-mono font-semibold text-gray-900">{formatCurrency(data.balance_sheet.assets.current_assets.total)}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Aktywa trwałe</h4>
                <div className="bg-gray-50 rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <tbody>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Rzeczowe aktywa trwałe</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.assets.fixed_assets.property_plant_equipment)}</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Wartości niematerialne</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.assets.fixed_assets.intangible_assets)}</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Inwestycje długoterminowe</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.assets.fixed_assets.long_term_investments)}</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Inne</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.assets.fixed_assets.other)}</td>
                      </tr>
                      <tr className="bg-purple-50">
                        <td className="px-4 py-2 font-semibold text-gray-900">Razem aktywa trwałe</td>
                        <td className="px-4 py-2 text-right font-mono font-semibold text-gray-900">{formatCurrency(data.balance_sheet.assets.fixed_assets.total)}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="bg-purple-100 rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-bold text-gray-900">AKTYWA OGÓŁEM</span>
                  <span className="text-lg font-mono font-bold text-gray-900">{formatCurrency(data.balance_sheet.assets.total_assets)}</span>
                </div>
              </div>
            </div>

            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-900">PASYWA</h3>

              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Zobowiązania krótkoterminowe</h4>
                <div className="bg-gray-50 rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <tbody>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Kredyty i pożyczki krótkoterminowe</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.liabilities.current_liabilities.short_term_debt)}</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Zobowiązania z tytułu dostaw i usług</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.liabilities.current_liabilities.accounts_payable)}</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Rozliczenia międzyokresowe</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.liabilities.current_liabilities.accrued_expenses)}</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Inne</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.liabilities.current_liabilities.other)}</td>
                      </tr>
                      <tr className="bg-purple-50">
                        <td className="px-4 py-2 font-semibold text-gray-900">Razem zobowiązania krótkoterminowe</td>
                        <td className="px-4 py-2 text-right font-mono font-semibold text-gray-900">{formatCurrency(data.balance_sheet.liabilities.current_liabilities.total)}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Zobowiązania długoterminowe</h4>
                <div className="bg-gray-50 rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <tbody>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Kredyty i pożyczki długoterminowe</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.liabilities.long_term_liabilities.long_term_debt)}</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Rezerwa na podatek odroczony</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.liabilities.long_term_liabilities.deferred_tax)}</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Inne</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.liabilities.long_term_liabilities.other)}</td>
                      </tr>
                      <tr className="bg-purple-50">
                        <td className="px-4 py-2 font-semibold text-gray-900">Razem zobowiązania długoterminowe</td>
                        <td className="px-4 py-2 text-right font-mono font-semibold text-gray-900">{formatCurrency(data.balance_sheet.liabilities.long_term_liabilities.total)}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Kapitał własny</h4>
                <div className="bg-gray-50 rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <tbody>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Kapitał zakładowy</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.equity.share_capital)}</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Zyski zatrzymane</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.equity.retained_earnings)}</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="px-4 py-2 text-gray-700">Kapitały rezerwowe</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-900">{formatCurrency(data.balance_sheet.equity.reserves)}</td>
                      </tr>
                      <tr className="bg-purple-50">
                        <td className="px-4 py-2 font-semibold text-gray-900">Razem kapitał własny</td>
                        <td className="px-4 py-2 text-right font-mono font-semibold text-gray-900">{formatCurrency(data.balance_sheet.equity.total_equity)}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="bg-purple-100 rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-bold text-gray-900">PASYWA OGÓŁEM</span>
                  <span className="text-lg font-mono font-bold text-gray-900">{formatCurrency(data.balance_sheet.total_liabilities_and_equity)}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Income Statement Tab */}
        {activeTab === 'income' && (
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <tbody>
                  <tr className="border-b border-gray-200">
                    <td className="px-4 py-3 text-gray-700">Przychody ze sprzedaży</td>
                    <td className="px-4 py-3 text-right font-mono text-gray-900">{formatCurrency(data.income_statement.revenue.sales_revenue)}</td>
                  </tr>
                  <tr className="border-b border-gray-200">
                    <td className="px-4 py-3 text-gray-700">Pozostałe przychody operacyjne</td>
                    <td className="px-4 py-3 text-right font-mono text-gray-900">{formatCurrency(data.income_statement.revenue.other_revenue)}</td>
                  </tr>
                  <tr className="bg-blue-50">
                    <td className="px-4 py-3 font-semibold text-gray-900">Przychody ogółem</td>
                    <td className="px-4 py-3 text-right font-mono font-semibold text-gray-900">{formatCurrency(data.income_statement.revenue.total_revenue)}</td>
                  </tr>
                  <tr className="border-b border-gray-200">
                    <td className="px-4 py-3 text-gray-700">Koszt własny sprzedaży</td>
                    <td className="px-4 py-3 text-right font-mono text-red-600">-{formatCurrency(data.income_statement.costs.cost_of_goods_sold)}</td>
                  </tr>
                  <tr className="bg-green-50">
                    <td className="px-4 py-3 font-semibold text-gray-900">Zysk brutto ze sprzedaży</td>
                    <td className="px-4 py-3 text-right font-mono font-semibold text-green-700">{formatCurrency(data.income_statement.costs.gross_profit)}</td>
                  </tr>
                  <tr className="border-b border-gray-200">
                    <td className="px-4 py-3 text-gray-700 pl-8">→ Koszty sprzedaży</td>
                    <td className="px-4 py-3 text-right font-mono text-red-600">-{formatCurrency(data.income_statement.costs.operating_expenses.selling_expenses)}</td>
                  </tr>
                  <tr className="border-b border-gray-200">
                    <td className="px-4 py-3 text-gray-700 pl-8">→ Koszty administracyjne</td>
                    <td className="px-4 py-3 text-right font-mono text-red-600">-{formatCurrency(data.income_statement.costs.operating_expenses.administrative_expenses)}</td>
                  </tr>
                  <tr className="border-b border-gray-200">
                    <td className="px-4 py-3 text-gray-700 pl-8">→ Koszty B+R</td>
                    <td className="px-4 py-3 text-right font-mono text-red-600">-{formatCurrency(data.income_statement.costs.operating_expenses.rd_expenses)}</td>
                  </tr>
                  <tr className="bg-purple-50">
                    <td className="px-4 py-3 font-semibold text-gray-900">Zysk z działalności operacyjnej</td>
                    <td className="px-4 py-3 text-right font-mono font-semibold text-purple-700">{formatCurrency(data.income_statement.costs.operating_profit)}</td>
                  </tr>
                  <tr className="border-b border-gray-200">
                    <td className="px-4 py-3 text-gray-700">Koszty finansowe</td>
                    <td className="px-4 py-3 text-right font-mono text-red-600">-{formatCurrency(data.income_statement.costs.financial_costs)}</td>
                  </tr>
                  <tr className="bg-yellow-50">
                    <td className="px-4 py-3 font-semibold text-gray-900">Zysk przed opodatkowaniem</td>
                    <td className="px-4 py-3 text-right font-mono font-semibold text-gray-900">{formatCurrency(data.income_statement.costs.profit_before_tax)}</td>
                  </tr>
                  <tr className="border-b border-gray-200">
                    <td className="px-4 py-3 text-gray-700">Podatek dochodowy</td>
                    <td className="px-4 py-3 text-right font-mono text-red-600">-{formatCurrency(data.income_statement.costs.income_tax)}</td>
                  </tr>
                  <tr className="bg-purple-100">
                    <td className="px-4 py-3 text-lg font-bold text-gray-900">ZYSK NETTO</td>
                    <td className="px-4 py-3 text-right text-lg font-mono font-bold text-purple-700">{formatCurrency(data.income_statement.costs.net_profit)}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-6">
              <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                <div className="text-xs text-green-700 font-semibold uppercase mb-1">Marża brutto</div>
                <div className="text-2xl font-bold text-green-700">{formatPercent(data.income_statement.margins.gross_margin)}</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                <div className="text-xs text-purple-700 font-semibold uppercase mb-1">Marża operacyjna</div>
                <div className="text-2xl font-bold text-purple-700">{formatPercent(data.income_statement.margins.operating_margin)}</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <div className="text-xs text-blue-700 font-semibold uppercase mb-1">Marża netto</div>
                <div className="text-2xl font-bold text-blue-700">{formatPercent(data.income_statement.margins.net_margin)}</div>
              </div>
            </div>
          </div>
        )}

        {/* Multi-Year Summary Tab */}
        {activeTab === 'summary' && data.multi_year_summary && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-900">Podsumowanie wieloletnie ({data.multi_year_summary.years[0]}-{data.multi_year_summary.years[data.multi_year_summary.years.length - 1]})</h3>

            {/* Charts Section */}
            <div className="space-y-6">
              {/* Revenue & Profit Trend Chart */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h4 className="text-md font-semibold text-gray-900 mb-4">Trend przychodów i zysków</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart
                    data={data.multi_year_summary.years.map((year, idx) => ({
                      year: year.toString(),
                      revenue: data.multi_year_summary!.revenue[idx] / 1000000, // Convert to millions
                      net_profit: data.multi_year_summary!.net_profit[idx] / 1000000,
                    }))}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="year" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" label={{ value: 'Wartość (mln PLN)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip
                      formatter={(value: number) => `${value.toFixed(2)} mln PLN`}
                      contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '6px' }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="revenue"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      name="Przychody"
                      dot={{ fill: '#3b82f6', r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="net_profit"
                      stroke="#10b981"
                      strokeWidth={2}
                      name="Zysk netto"
                      dot={{ fill: '#10b981', r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Assets & Equity Trend Chart */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h4 className="text-md font-semibold text-gray-900 mb-4">Trend aktywów i kapitału własnego</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart
                    data={data.multi_year_summary.years.map((year, idx) => ({
                      year: year.toString(),
                      total_assets: data.multi_year_summary!.total_assets[idx] / 1000000,
                      equity: data.multi_year_summary!.equity[idx] / 1000000,
                    }))}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="year" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" label={{ value: 'Wartość (mln PLN)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip
                      formatter={(value: number) => `${value.toFixed(2)} mln PLN`}
                      contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '6px' }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="total_assets"
                      stroke="#8b5cf6"
                      strokeWidth={2}
                      name="Aktywa ogółem"
                      dot={{ fill: '#8b5cf6', r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="equity"
                      stroke="#f59e0b"
                      strokeWidth={2}
                      name="Kapitał własny"
                      dot={{ fill: '#f59e0b', r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Data Table */}
            <div className="bg-gray-50 rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-purple-100">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold text-gray-900">Wskaźnik</th>
                    {data.multi_year_summary.years.map((year) => (
                      <th key={year} className="px-4 py-3 text-right font-semibold text-gray-900">{year}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-gray-200">
                    <td className="px-4 py-3 text-gray-700 font-medium">Przychody</td>
                    {data.multi_year_summary.revenue.map((value, idx) => (
                      <td key={idx} className="px-4 py-3 text-right font-mono text-gray-900">{formatCurrency(value)}</td>
                    ))}
                  </tr>
                  <tr className="border-b border-gray-200">
                    <td className="px-4 py-3 text-gray-700 font-medium">Zysk netto</td>
                    {data.multi_year_summary.net_profit.map((value, idx) => (
                      <td key={idx} className="px-4 py-3 text-right font-mono text-gray-900">{formatCurrency(value)}</td>
                    ))}
                  </tr>
                  <tr className="border-b border-gray-200">
                    <td className="px-4 py-3 text-gray-700 font-medium">Aktywa ogółem</td>
                    {data.multi_year_summary.total_assets.map((value, idx) => (
                      <td key={idx} className="px-4 py-3 text-right font-mono text-gray-900">{formatCurrency(value)}</td>
                    ))}
                  </tr>
                  <tr className="border-b border-gray-200">
                    <td className="px-4 py-3 text-gray-700 font-medium">Kapitał własny</td>
                    {data.multi_year_summary.equity.map((value, idx) => (
                      <td key={idx} className="px-4 py-3 text-right font-mono text-gray-900">{formatCurrency(value)}</td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Financial Ratios Tab */}
        {activeTab === 'ratios' && data.financial_ratios && (
          <div className="space-y-8">
            {/* Liquidity Ratios */}
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-900 flex items-center gap-2">
                <span className="text-blue-600">💧</span>
                Wskaźniki płynności
              </h3>
              <div className="space-y-4">
                {/* Current Ratio */}
                <div className="bg-gradient-to-r from-blue-50 to-white border border-blue-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold text-gray-900">Wskaźnik płynności bieżącej (Current Ratio)</h4>
                      <p className="text-sm text-gray-600 mt-1">{data.financial_ratios.liquidity.current_ratio.explanation}</p>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-2xl font-bold text-blue-700">{data.financial_ratios.liquidity.current_ratio.value.toFixed(2)}</div>
                      <div className="text-xs text-gray-500">Benchmark: {data.financial_ratios.liquidity.current_ratio.benchmark.toFixed(2)}</div>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="flex items-center gap-2 text-sm">
                      {data.financial_ratios.liquidity.current_ratio.value >= data.financial_ratios.liquidity.current_ratio.benchmark ? (
                        <span className="text-green-600 font-semibold">✓ Powyżej benchmarku</span>
                      ) : (
                        <span className="text-orange-600 font-semibold">⚠ Poniżej benchmarku</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Quick Ratio */}
                <div className="bg-gradient-to-r from-blue-50 to-white border border-blue-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold text-gray-900">Wskaźnik płynności szybkiej (Quick Ratio)</h4>
                      <p className="text-sm text-gray-600 mt-1">{data.financial_ratios.liquidity.quick_ratio.explanation}</p>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-2xl font-bold text-blue-700">{data.financial_ratios.liquidity.quick_ratio.value.toFixed(2)}</div>
                      <div className="text-xs text-gray-500">Benchmark: {data.financial_ratios.liquidity.quick_ratio.benchmark.toFixed(2)}</div>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="flex items-center gap-2 text-sm">
                      {data.financial_ratios.liquidity.quick_ratio.value >= data.financial_ratios.liquidity.quick_ratio.benchmark ? (
                        <span className="text-green-600 font-semibold">✓ Powyżej benchmarku</span>
                      ) : (
                        <span className="text-orange-600 font-semibold">⚠ Poniżej benchmarku</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Profitability Ratios */}
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-900 flex items-center gap-2">
                <span className="text-green-600">📈</span>
                Wskaźniki rentowności
              </h3>
              <div className="space-y-4">
                {/* ROE */}
                <div className="bg-gradient-to-r from-green-50 to-white border border-green-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold text-gray-900">ROE (Return on Equity)</h4>
                      <p className="text-sm text-gray-600 mt-1">{data.financial_ratios.profitability.roe.explanation}</p>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-2xl font-bold text-green-700">{data.financial_ratios.profitability.roe.value.toFixed(1)}%</div>
                      <div className="text-xs text-gray-500">Benchmark: {data.financial_ratios.profitability.roe.benchmark.toFixed(1)}%</div>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="flex items-center gap-2 text-sm">
                      {data.financial_ratios.profitability.roe.value >= data.financial_ratios.profitability.roe.benchmark ? (
                        <span className="text-green-600 font-semibold">✓ Powyżej benchmarku</span>
                      ) : (
                        <span className="text-orange-600 font-semibold">⚠ Poniżej benchmarku</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* ROA */}
                <div className="bg-gradient-to-r from-green-50 to-white border border-green-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold text-gray-900">ROA (Return on Assets)</h4>
                      <p className="text-sm text-gray-600 mt-1">{data.financial_ratios.profitability.roa.explanation}</p>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-2xl font-bold text-green-700">{data.financial_ratios.profitability.roa.value.toFixed(1)}%</div>
                      <div className="text-xs text-gray-500">Benchmark: {data.financial_ratios.profitability.roa.benchmark.toFixed(1)}%</div>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="flex items-center gap-2 text-sm">
                      {data.financial_ratios.profitability.roa.value >= data.financial_ratios.profitability.roa.benchmark ? (
                        <span className="text-green-600 font-semibold">✓ Powyżej benchmarku</span>
                      ) : (
                        <span className="text-orange-600 font-semibold">⚠ Poniżej benchmarku</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* ROS */}
                <div className="bg-gradient-to-r from-green-50 to-white border border-green-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold text-gray-900">ROS (Return on Sales)</h4>
                      <p className="text-sm text-gray-600 mt-1">{data.financial_ratios.profitability.ros.explanation}</p>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-2xl font-bold text-green-700">{data.financial_ratios.profitability.ros.value.toFixed(1)}%</div>
                      <div className="text-xs text-gray-500">Benchmark: {data.financial_ratios.profitability.ros.benchmark.toFixed(1)}%</div>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="flex items-center gap-2 text-sm">
                      {data.financial_ratios.profitability.ros.value >= data.financial_ratios.profitability.ros.benchmark ? (
                        <span className="text-green-600 font-semibold">✓ Powyżej benchmarku</span>
                      ) : (
                        <span className="text-orange-600 font-semibold">⚠ Poniżej benchmarku</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Leverage Ratios */}
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-900 flex items-center gap-2">
                <span className="text-red-600">⚖️</span>
                Wskaźniki zadłużenia
              </h3>
              <div className="space-y-4">
                {/* Debt Ratio */}
                <div className="bg-gradient-to-r from-red-50 to-white border border-red-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold text-gray-900">Wskaźnik zadłużenia ogólnego (Debt Ratio)</h4>
                      <p className="text-sm text-gray-600 mt-1">{data.financial_ratios.leverage.debt_ratio.explanation}</p>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-2xl font-bold text-red-700">{data.financial_ratios.leverage.debt_ratio.value.toFixed(1)}%</div>
                      <div className="text-xs text-gray-500">Benchmark: {data.financial_ratios.leverage.debt_ratio.benchmark.toFixed(1)}%</div>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="flex items-center gap-2 text-sm">
                      {data.financial_ratios.leverage.debt_ratio.value <= data.financial_ratios.leverage.debt_ratio.benchmark ? (
                        <span className="text-green-600 font-semibold">✓ Poniżej benchmarku (lepiej)</span>
                      ) : (
                        <span className="text-orange-600 font-semibold">⚠ Powyżej benchmarku</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Debt to Equity */}
                <div className="bg-gradient-to-r from-red-50 to-white border border-red-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold text-gray-900">Wskaźnik zadłużenia kapitału własnego (D/E)</h4>
                      <p className="text-sm text-gray-600 mt-1">{data.financial_ratios.leverage.debt_to_equity.explanation}</p>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-2xl font-bold text-red-700">{data.financial_ratios.leverage.debt_to_equity.value.toFixed(2)}</div>
                      <div className="text-xs text-gray-500">Benchmark: {data.financial_ratios.leverage.debt_to_equity.benchmark.toFixed(2)}</div>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="flex items-center gap-2 text-sm">
                      {data.financial_ratios.leverage.debt_to_equity.value <= data.financial_ratios.leverage.debt_to_equity.benchmark ? (
                        <span className="text-green-600 font-semibold">✓ Poniżej benchmarku (lepiej)</span>
                      ) : (
                        <span className="text-orange-600 font-semibold">⚠ Powyżej benchmarku</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Efficiency Ratios */}
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-900 flex items-center gap-2">
                <span className="text-purple-600">⚡</span>
                Wskaźniki efektywności
              </h3>
              <div className="space-y-4">
                {/* Inventory Turnover */}
                <div className="bg-gradient-to-r from-purple-50 to-white border border-purple-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold text-gray-900">Rotacja zapasów (Inventory Turnover)</h4>
                      <p className="text-sm text-gray-600 mt-1">{data.financial_ratios.efficiency.inventory_turnover.explanation}</p>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-2xl font-bold text-purple-700">{data.financial_ratios.efficiency.inventory_turnover.value.toFixed(1)}x</div>
                      <div className="text-xs text-gray-500">Benchmark: {data.financial_ratios.efficiency.inventory_turnover.benchmark.toFixed(1)}x</div>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="flex items-center gap-2 text-sm">
                      {data.financial_ratios.efficiency.inventory_turnover.value >= data.financial_ratios.efficiency.inventory_turnover.benchmark ? (
                        <span className="text-green-600 font-semibold">✓ Powyżej benchmarku</span>
                      ) : (
                        <span className="text-orange-600 font-semibold">⚠ Poniżej benchmarku</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Asset Turnover */}
                <div className="bg-gradient-to-r from-purple-50 to-white border border-purple-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold text-gray-900">Rotacja aktywów (Asset Turnover)</h4>
                      <p className="text-sm text-gray-600 mt-1">{data.financial_ratios.efficiency.asset_turnover.explanation}</p>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-2xl font-bold text-purple-700">{data.financial_ratios.efficiency.asset_turnover.value.toFixed(2)}x</div>
                      <div className="text-xs text-gray-500">Benchmark: {data.financial_ratios.efficiency.asset_turnover.benchmark.toFixed(2)}x</div>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="flex items-center gap-2 text-sm">
                      {data.financial_ratios.efficiency.asset_turnover.value >= data.financial_ratios.efficiency.asset_turnover.benchmark ? (
                        <span className="text-green-600 font-semibold">✓ Powyżej benchmarku</span>
                      ) : (
                        <span className="text-orange-600 font-semibold">⚠ Poniżej benchmarku</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t bg-gray-50 px-6 py-3">
        <div className="text-xs text-gray-500">
          Dane pobrano: {formatDate(data.fetched_at)}
        </div>
      </div>
    </div>
  );
};
