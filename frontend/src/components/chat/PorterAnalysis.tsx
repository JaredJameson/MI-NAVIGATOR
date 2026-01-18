"use client";

import { useState } from "react";

interface Factor {
  factor: string;
  description: string;
  impact: "high" | "medium" | "low";
}

interface Force {
  score: number;
  level: string;
  factors: Factor[];
  data_source: string;
}

interface PorterAnalysisData {
  industry_name: string;
  region: string;
  analysis_date: string;
  supplier_power: Force;
  buyer_power: Force;
  competitive_rivalry: Force;
  threat_of_substitution: Force;
  threat_of_new_entry: Force;
  overall_assessment: {
    average_score: number;
    industry_attractiveness: string;
    summary: string;
    key_recommendations: string[];
  };
  data_sources: Array<{
    name: string;
    confidence: number;
  }>;
}

interface PorterAnalysisProps {
  data: PorterAnalysisData;
}

export default function PorterAnalysis({ data }: PorterAnalysisProps) {
  const [activeForce, setActiveForce] = useState<
    "supplier" | "buyer" | "rivalry" | "substitution" | "entry" | "summary"
  >("supplier");

  // Helper function to get score color
  const getScoreColor = (score: number): string => {
    if (score >= 7) return "text-red-600";
    if (score >= 5) return "text-yellow-600";
    return "text-green-600";
  };

  // Helper function to get level badge color
  const getLevelBadgeColor = (level: string): string => {
    if (level.includes("high")) return "bg-red-100 text-red-800 border-red-300";
    if (level.includes("medium")) return "bg-yellow-100 text-yellow-800 border-yellow-300";
    return "bg-green-100 text-green-800 border-green-300";
  };

  // Helper function to get impact color
  const getImpactColor = (impact: string): string => {
    switch (impact) {
      case "high":
        return "bg-red-50 border-red-200";
      case "medium":
        return "bg-yellow-50 border-yellow-200";
      case "low":
        return "bg-green-50 border-green-200";
      default:
        return "bg-gray-50 border-gray-200";
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

  // Render force card
  const renderForce = (force: Force, title: string, icon: string) => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <span>{icon}</span>
          {title}
        </h4>
        <div className="flex items-center gap-3">
          <span className={`text-3xl font-bold ${getScoreColor(force.score)}`}>
            {force.score}/10
          </span>
          <span
            className={`text-sm px-3 py-1 rounded-full border ${getLevelBadgeColor(
              force.level
            )}`}
          >
            {force.level}
          </span>
        </div>
      </div>

      <div className="space-y-3">
        {force.factors.map((factor, idx) => (
          <div
            key={idx}
            className={`p-4 rounded-lg border-2 ${getImpactColor(
              factor.impact
            )} hover:shadow-md transition-shadow`}
          >
            <div className="flex items-start justify-between mb-2">
              <h5 className="font-semibold text-sm">{factor.factor}</h5>
              <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-700 border border-gray-300">
                {getImpactLabel(factor.impact)}
              </span>
            </div>
            <p className="text-sm text-gray-700">{factor.description}</p>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 italic">
          Źródło: {force.data_source}
        </p>
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-start gap-3 mb-2">
          <div className="text-3xl">⚔️</div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900">
              Analiza Pięciu Sił Portera - {data.industry_name}
            </h3>
            <p className="text-sm text-gray-600">
              {data.region} • Data analizy: {formatDate(data.analysis_date)}
            </p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6 border-b border-gray-200">
        <div className="flex gap-2 overflow-x-auto pb-2">
          <button
            onClick={() => setActiveForce("supplier")}
            className={`px-4 py-2 rounded-t-lg font-medium text-sm whitespace-nowrap transition-colors ${
              activeForce === "supplier"
                ? "bg-purple-500 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            🏭 Siła dostawców ({data.supplier_power.score})
          </button>
          <button
            onClick={() => setActiveForce("buyer")}
            className={`px-4 py-2 rounded-t-lg font-medium text-sm whitespace-nowrap transition-colors ${
              activeForce === "buyer"
                ? "bg-blue-500 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            🛒 Siła nabywców ({data.buyer_power.score})
          </button>
          <button
            onClick={() => setActiveForce("rivalry")}
            className={`px-4 py-2 rounded-t-lg font-medium text-sm whitespace-nowrap transition-colors ${
              activeForce === "rivalry"
                ? "bg-red-500 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            ⚔️ Rywalizacja ({data.competitive_rivalry.score})
          </button>
          <button
            onClick={() => setActiveForce("substitution")}
            className={`px-4 py-2 rounded-t-lg font-medium text-sm whitespace-nowrap transition-colors ${
              activeForce === "substitution"
                ? "bg-orange-500 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            🔄 Substytuty ({data.threat_of_substitution.score})
          </button>
          <button
            onClick={() => setActiveForce("entry")}
            className={`px-4 py-2 rounded-t-lg font-medium text-sm whitespace-nowrap transition-colors ${
              activeForce === "entry"
                ? "bg-green-500 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            🚪 Nowe wejścia ({data.threat_of_new_entry.score})
          </button>
          <button
            onClick={() => setActiveForce("summary")}
            className={`px-4 py-2 rounded-t-lg font-medium text-sm whitespace-nowrap transition-colors ${
              activeForce === "summary"
                ? "bg-indigo-500 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            📊 Podsumowanie
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="min-h-[400px]">
        {activeForce === "supplier" &&
          renderForce(
            data.supplier_power,
            "Siła przetargowa dostawców",
            "🏭"
          )}
        {activeForce === "buyer" &&
          renderForce(data.buyer_power, "Siła przetargowa nabywców", "🛒")}
        {activeForce === "rivalry" &&
          renderForce(
            data.competitive_rivalry,
            "Intensywność rywalizacji konkurencyjnej",
            "⚔️"
          )}
        {activeForce === "substitution" &&
          renderForce(
            data.threat_of_substitution,
            "Zagrożenie substytutami",
            "🔄"
          )}
        {activeForce === "entry" &&
          renderForce(
            data.threat_of_new_entry,
            "Zagrożenie nowymi wejściami",
            "🚪"
          )}

        {activeForce === "summary" && (
          <div className="space-y-6">
            {/* Overall Score */}
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-lg border-2 border-indigo-200">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-bold text-gray-900">
                  📊 Ogólna ocena atrakcyjności branży
                </h4>
                <div className="text-right">
                  <div className={`text-3xl font-bold ${getScoreColor(data.overall_assessment.average_score)}`}>
                    {data.overall_assessment.average_score.toFixed(1)}/10
                  </div>
                  <div className="text-sm text-gray-600 capitalize">
                    {data.overall_assessment.industry_attractiveness}
                  </div>
                </div>
              </div>
              <p className="text-sm text-gray-700 leading-relaxed">
                {data.overall_assessment.summary}
              </p>
            </div>

            {/* Key Recommendations */}
            <div>
              <h5 className="font-bold text-gray-900 mb-3">
                💡 Kluczowe rekomendacje strategiczne:
              </h5>
              <ol className="space-y-2">
                {data.overall_assessment.key_recommendations.map(
                  (rec, idx) => (
                    <li
                      key={idx}
                      className="flex gap-3 p-3 bg-amber-50 rounded-lg border border-amber-200"
                    >
                      <span className="flex-shrink-0 w-6 h-6 bg-amber-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                        {idx + 1}
                      </span>
                      <span className="text-sm text-gray-800">{rec}</span>
                    </li>
                  )
                )}
              </ol>
            </div>
          </div>
        )}
      </div>

      {/* Footer - Data Sources */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h5 className="font-semibold text-sm text-gray-700 mb-3">
          Źródła danych:
        </h5>
        <div className="flex flex-wrap gap-2">
          {data.data_sources.map((source, idx) => (
            <span
              key={idx}
              className="text-xs px-3 py-1 bg-blue-50 text-blue-700 rounded-full border border-blue-200"
            >
              {source.name} ({Math.round(source.confidence * 100)}% pewności)
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
