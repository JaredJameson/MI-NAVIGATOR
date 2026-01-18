/**
 * KeyPeople Component
 * Displays key company personnel including management board, supervisory board, and proxies
 */

import React, { useState } from 'react';

interface OtherPosition {
  company: string;
  role: string;
  since: string;
}

interface Person {
  name: string;
  role: string;
  role_en: string;
  since: string;
  tenure_years: number;
  other_positions: OtherPosition[];
  linkedin?: string | null;
  photo?: string | null;
  scope?: string; // for prokurenci
  scope_en?: string;
}

interface KeyPersonRisk {
  level: string;
  factors: string[];
}

interface KeyPeopleData {
  company_name: string;
  nip: string;
  krs: string;
  source: string;
  management_board: Person[];
  supervisory_board: Person[];
  prokurenci: Person[];
  key_person_risk: KeyPersonRisk;
  fetched_at: string;
}

interface KeyPeopleProps {
  data: KeyPeopleData;
}

type TabType = 'management' | 'supervisory' | 'prokurenci' | 'risk';

const KeyPeople: React.FC<KeyPeopleProps> = ({ data }) => {
  const [activeTab, setActiveTab] = useState<TabType>('management');

  const formatDate = (dateStr: string): string => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('pl-PL', { year: 'numeric', month: 'long', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const getTenureColor = (years: number): string => {
    if (years >= 15) return 'text-green-700 bg-green-100';
    if (years >= 5) return 'text-blue-700 bg-blue-100';
    return 'text-gray-700 bg-gray-100';
  };

  const getRiskColor = (level: string): string => {
    switch (level.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const renderPersonCard = (person: Person, showScope: boolean = false) => (
    <div key={person.name} className="bg-teal-50 border border-teal-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      {/* Header with name and role */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-start space-x-3">
          {/* Avatar placeholder */}
          <div className="w-12 h-12 bg-teal-200 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-teal-700 text-xl font-bold">
              {person.name.split(' ').map(n => n[0]).join('')}
            </span>
          </div>

          <div>
            <h4 className="text-lg font-bold text-gray-900">{person.name}</h4>
            <p className="text-sm text-teal-700 font-medium">{person.role}</p>
            {person.role_en && (
              <p className="text-xs text-gray-500 italic">{person.role_en}</p>
            )}
          </div>
        </div>

        {/* LinkedIn link */}
        {person.linkedin && (
          <a
            href={person.linkedin}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 flex items-center space-x-1"
            title="LinkedIn profile"
          >
            <span className="text-sm">in</span>
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
            </svg>
          </a>
        )}
      </div>

      {/* Tenure information */}
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <div className="flex items-center space-x-2 text-sm">
          <span className="text-gray-600">W funkcji od:</span>
          <span className="font-medium text-gray-900">{formatDate(person.since)}</span>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTenureColor(person.tenure_years)}`}>
          {person.tenure_years} {person.tenure_years === 1 ? 'rok' : person.tenure_years < 5 ? 'lata' : 'lat'}
        </span>
      </div>

      {/* Scope for prokurenci */}
      {showScope && person.scope && (
        <div className="mb-3 text-sm">
          <span className="text-gray-600">Zakres prokury: </span>
          <span className="font-medium text-gray-900">{person.scope}</span>
          {person.scope_en && <span className="text-gray-500 italic"> ({person.scope_en})</span>}
        </div>
      )}

      {/* Other positions */}
      {person.other_positions && person.other_positions.length > 0 && (
        <div className="mt-3 pt-3 border-t border-teal-200">
          <h5 className="text-xs font-semibold text-gray-700 mb-2 uppercase">Inne funkcje:</h5>
          <div className="space-y-2">
            {person.other_positions.map((pos, idx) => (
              <div key={idx} className="text-sm">
                <div className="font-medium text-gray-900">{pos.company}</div>
                <div className="text-gray-600 text-xs">
                  {pos.role} • od {formatDate(pos.since)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-teal-500 to-teal-600 p-4 flex items-center space-x-3">
        <div className="text-2xl">👥</div>
        <div className="flex-1">
          <div className="text-xs text-teal-100 uppercase tracking-wide">Dane z {data.source}</div>
          <div className="text-white font-semibold">Kluczowe osoby • {data.company_name}</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 bg-gray-50 flex space-x-1 p-1">
        <button
          onClick={() => setActiveTab('management')}
          className={`flex-1 px-4 py-2 text-sm font-medium rounded transition-colors ${
            activeTab === 'management'
              ? 'bg-white text-teal-700 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Zarząd ({data.management_board.length})
        </button>
        <button
          onClick={() => setActiveTab('supervisory')}
          className={`flex-1 px-4 py-2 text-sm font-medium rounded transition-colors ${
            activeTab === 'supervisory'
              ? 'bg-white text-teal-700 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Rada Nadzorcza ({data.supervisory_board.length})
        </button>
        {data.prokurenci && data.prokurenci.length > 0 && (
          <button
            onClick={() => setActiveTab('prokurenci')}
            className={`flex-1 px-4 py-2 text-sm font-medium rounded transition-colors ${
              activeTab === 'prokurenci'
                ? 'bg-white text-teal-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Prokurenci ({data.prokurenci.length})
          </button>
        )}
        <button
          onClick={() => setActiveTab('risk')}
          className={`flex-1 px-4 py-2 text-sm font-medium rounded transition-colors ${
            activeTab === 'risk'
              ? 'bg-white text-teal-700 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Ryzyko
        </button>
      </div>

      {/* Tab content */}
      <div className="p-6">
        {/* Management Board Tab */}
        {activeTab === 'management' && (
          <div className="space-y-4">
            <div className="flex items-center space-x-2 mb-4">
              <h3 className="text-xl font-bold text-gray-900">Zarząd</h3>
              <span className="text-sm text-gray-500">({data.management_board.length} członków)</span>
            </div>
            {data.management_board.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Brak danych o zarządzie
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.management_board.map(person => renderPersonCard(person))}
              </div>
            )}
          </div>
        )}

        {/* Supervisory Board Tab */}
        {activeTab === 'supervisory' && (
          <div className="space-y-4">
            <div className="flex items-center space-x-2 mb-4">
              <h3 className="text-xl font-bold text-gray-900">Rada Nadzorcza</h3>
              <span className="text-sm text-gray-500">({data.supervisory_board.length} członków)</span>
            </div>
            {data.supervisory_board.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Brak rady nadzorczej lub dane niedostępne
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.supervisory_board.map(person => renderPersonCard(person))}
              </div>
            )}
          </div>
        )}

        {/* Prokurenci Tab */}
        {activeTab === 'prokurenci' && (
          <div className="space-y-4">
            <div className="flex items-center space-x-2 mb-4">
              <h3 className="text-xl font-bold text-gray-900">Prokurenci</h3>
              <span className="text-sm text-gray-500">({data.prokurenci?.length || 0})</span>
            </div>
            {!data.prokurenci || data.prokurenci.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Brak prokurentów
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.prokurenci.map(person => renderPersonCard(person, true))}
              </div>
            )}
          </div>
        )}

        {/* Risk Assessment Tab */}
        {activeTab === 'risk' && (
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Ocena ryzyka kluczowych osób</h3>

            <div className={`border-2 rounded-lg p-4 ${getRiskColor(data.key_person_risk.level)}`}>
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-semibold uppercase">Poziom ryzyka</span>
                <span className="text-lg font-bold uppercase">{data.key_person_risk.level}</span>
              </div>
              <div className="text-sm space-y-2">
                <p className="font-medium">Czynniki ryzyka:</p>
                <ul className="list-disc list-inside space-y-1">
                  {data.key_person_risk.factors.map((factor, idx) => (
                    <li key={idx}>{factor}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Summary statistics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div className="text-2xl font-bold text-teal-700">{data.management_board.length}</div>
                <div className="text-sm text-gray-600">Członków zarządu</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div className="text-2xl font-bold text-teal-700">{data.supervisory_board.length}</div>
                <div className="text-sm text-gray-600">Członków rady nadzorczej</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div className="text-2xl font-bold text-teal-700">
                  {data.management_board.reduce((sum, p) => sum + p.tenure_years, 0) / data.management_board.length || 0}
                </div>
                <div className="text-sm text-gray-600">Średni staż zarządu (lata)</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="bg-gray-50 px-6 py-3 text-xs text-gray-500 border-t border-gray-200">
        Dane pobrano: {new Date(data.fetched_at).toLocaleString('pl-PL')}
      </div>
    </div>
  );
};

export default KeyPeople;
