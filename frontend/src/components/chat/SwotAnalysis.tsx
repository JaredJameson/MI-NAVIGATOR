"use client";

import { useState } from "react";

interface SwotItem {
  title: string;
  description: string;
  impact: "high" | "medium" | "low";
  data_source: string;
}

interface SwotAnalysisData {
  company_name: string;
  nip: string;
  krs: string;
  industry: string;
  analysis_date: string;
  strengths: SwotItem[];
  weaknesses: SwotItem[];
  opportunities: SwotItem[];
  threats: SwotItem[];
  summary: {
    total_strengths: number;
    total_weaknesses: number;
    total_opportunities: number;
    total_threats: number;
    overall_assessment: string;
    priority_actions: string[];
  };
  data_sources: Array<{
    name: string;
    confidence: number;
  }>;
}

interface SwotAnalysisProps {
  data: SwotAnalysisData;
}

export default function SwotAnalysis({ data }: SwotAnalysisProps) {
  const [activeQuadrant, setActiveQuadrant] = useState<
    "strengths" | "weaknesses" | "opportunities" | "threats" | "summary"
  >("strengths");

  // Helper function to get impact badge color
  const getImpactColor = (impact: string): string => {
    switch (impact) {
      case "high":
        return "bg-red-100 text-red-800 border-red-300";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      case "low":
        return "bg-green-100 text-green-800 border-green-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  // Helper function to get impact label
  const getImpactLabel = (impact: string): string => {
    switch (impact) {
      case "high":
        return "Wysoki wpływ";
      case "medium":
        return "Średni wpływ";
      case "low":
        return "Niski wpływ";
      default:
        return "Nieznany";
    }
  };

  // Format date
  const formatDate = (isoDate: string): string => {
    const date = new Date(isoDate);
    return date.toLocaleDateString("pl-PL", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  // Render SWOT item card
  const renderItem = (item: SwotItem, color: string) => (
    <div
      key={item.title}
      className={`p-4 rounded-lg border-2 ${color} hover:shadow-md transition-shadow`}
    >
      <div className="flex items-start justify-between mb-2">
        <h4 className="font-semibold text-sm">{item.title}</h4>
        <span
          className={`text-xs px-2 py-1 rounded-full border ${getImpactColor(
            item.impact
          )}`}
        >
          {getImpactLabel(item.impact)}
        </span>
      </div>
      <p className="text-sm text-gray-700 mb-2">{item.description}</p>
      <p className="text-xs text-gray-500 italic">
        Źródło: {item.data_source}
      </p>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 my-4">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="text-3xl">🎯</div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">
              Analiza SWOT - {data.company_name}
            </h3>
            <p className="text-sm text-gray-600">
              {data.industry} • NIP: {data.nip}
            </p>
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Data analizy: {formatDate(data.analysis_date)}
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        <button
          onClick={() => setActiveQuadrant("strengths")}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors whitespace-nowrap ${
            activeQuadrant === "strengths"
              ? "bg-green-600 text-white"
              : "bg-green-50 text-green-700 hover:bg-green-100"
          }`}
        >
          💪 Mocne strony ({data.summary.total_strengths})
        </button>
        <button
          onClick={() => setActiveQuadrant("weaknesses")}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors whitespace-nowrap ${
            activeQuadrant === "weaknesses"
              ? "bg-red-600 text-white"
              : "bg-red-50 text-red-700 hover:bg-red-100"
          }`}
        >
          ⚠️ Słabe strony ({data.summary.total_weaknesses})
        </button>
        <button
          onClick={() => setActiveQuadrant("opportunities")}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors whitespace-nowrap ${
            activeQuadrant === "opportunities"
              ? "bg-blue-600 text-white"
              : "bg-blue-50 text-blue-700 hover:bg-blue-100"
          }`}
        >
          🚀 Szanse ({data.summary.total_opportunities})
        </button>
        <button
          onClick={() => setActiveQuadrant("threats")}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors whitespace-nowrap ${
            activeQuadrant === "threats"
              ? "bg-yellow-600 text-white"
              : "bg-yellow-50 text-yellow-700 hover:bg-yellow-100"
          }`}
        >
          ⚡ Zagrożenia ({data.summary.total_threats})
        </button>
        <button
          onClick={() => setActiveQuadrant("summary")}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors whitespace-nowrap ${
            activeQuadrant === "summary"
              ? "bg-purple-600 text-white"
              : "bg-purple-50 text-purple-700 hover:bg-purple-100"
          }`}
        >
          📊 Podsumowanie
        </button>
      </div>

      {/* Content Area */}
      <div className="min-h-[300px]">
        {/* Strengths */}
        {activeQuadrant === "strengths" && (
          <div className="space-y-3">
            <h4 className="font-semibold text-green-800 mb-4">
              💪 Mocne strony firmy ({data.strengths.length})
            </h4>
            {data.strengths.map((item) =>
              renderItem(item, "bg-green-50 border-green-200")
            )}
          </div>
        )}

        {/* Weaknesses */}
        {activeQuadrant === "weaknesses" && (
          <div className="space-y-3">
            <h4 className="font-semibold text-red-800 mb-4">
              ⚠️ Słabe strony firmy ({data.weaknesses.length})
            </h4>
            {data.weaknesses.map((item) =>
              renderItem(item, "bg-red-50 border-red-200")
            )}
          </div>
        )}

        {/* Opportunities */}
        {activeQuadrant === "opportunities" && (
          <div className="space-y-3">
            <h4 className="font-semibold text-blue-800 mb-4">
              🚀 Szanse rynkowe ({data.opportunities.length})
            </h4>
            {data.opportunities.map((item) =>
              renderItem(item, "bg-blue-50 border-blue-200")
            )}
          </div>
        )}

        {/* Threats */}
        {activeQuadrant === "threats" && (
          <div className="space-y-3">
            <h4 className="font-semibold text-yellow-800 mb-4">
              ⚡ Zagrożenia zewnętrzne ({data.threats.length})
            </h4>
            {data.threats.map((item) =>
              renderItem(item, "bg-yellow-50 border-yellow-200")
            )}
          </div>
        )}

        {/* Summary */}
        {activeQuadrant === "summary" && (
          <div className="space-y-6">
            <div>
              <h4 className="font-semibold text-purple-800 mb-3">
                📊 Podsumowanie analizy
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4 text-center">
                  <div className="text-3xl font-bold text-green-700">
                    {data.summary.total_strengths}
                  </div>
                  <div className="text-sm text-green-600 mt-1">
                    Mocne strony
                  </div>
                </div>
                <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 text-center">
                  <div className="text-3xl font-bold text-red-700">
                    {data.summary.total_weaknesses}
                  </div>
                  <div className="text-sm text-red-600 mt-1">Słabe strony</div>
                </div>
                <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 text-center">
                  <div className="text-3xl font-bold text-blue-700">
                    {data.summary.total_opportunities}
                  </div>
                  <div className="text-sm text-blue-600 mt-1">Szanse</div>
                </div>
                <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4 text-center">
                  <div className="text-3xl font-bold text-yellow-700">
                    {data.summary.total_threats}
                  </div>
                  <div className="text-sm text-yellow-600 mt-1">
                    Zagrożenia
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-5">
              <h5 className="font-semibold text-purple-900 mb-3">
                Ogólna ocena:
              </h5>
              <p className="text-sm text-gray-800">
                {data.summary.overall_assessment}
              </p>
            </div>

            <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-5">
              <h5 className="font-semibold text-blue-900 mb-3">
                Priorytetowe działania:
              </h5>
              <ol className="space-y-2">
                {data.summary.priority_actions.map((action, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-3 text-sm text-gray-800"
                  >
                    <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 text-xs font-bold mt-0.5">
                      {index + 1}
                    </span>
                    <span className="flex-1">{action}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        )}
      </div>

      {/* Footer - Data Sources */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h5 className="text-sm font-semibold text-gray-700 mb-3">
          Źródła danych:
        </h5>
        <div className="flex flex-wrap gap-2">
          {data.data_sources.map((source, index) => (
            <div
              key={index}
              className="bg-gray-100 px-3 py-1 rounded-full text-xs text-gray-700"
            >
              {source.name} ({Math.round(source.confidence * 100)}% pewności)
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
