import React, { useState } from 'react';

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
  const [activeTab, setActiveTab] = useState<'balance' | 'income' | 'summary'>('balance');

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
          <div>
            <h3 className="text-lg font-semibold mb-4 text-gray-900">Podsumowanie wieloletnie ({data.multi_year_summary.years[0]}-{data.multi_year_summary.years[data.multi_year_summary.years.length - 1]})</h3>
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
