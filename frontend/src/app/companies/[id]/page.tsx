'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { companyApi, CompanyProfile, NewsArticle, TimelineEvent, RefreshResponse, DataQualityDashboard, customFieldsApi, CompanyCustomField, CompanyFinancials } from '@/services/api';
import { formatRelativeTime } from '@/utils/date';

type Tab = 'overview' | 'timeline' | 'news' | 'financials' | 'people' | 'data-quality';

export default function CompanyProfilePage() {
  const params = useParams();
  const router = useRouter();
  const companyId = params.id as string;

  const [company, setCompany] = useState<CompanyProfile | null>(null);
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [loading, setLoading] = useState(true);
  const [newsLoading, setNewsLoading] = useState(false);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newsCategory, setNewsCategory] = useState<string>('');
  const [newsSentiment, setNewsSentiment] = useState<string>('');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');
  const [showDateFilter, setShowDateFilter] = useState(false);
  const [timelineEventType, setTimelineEventType] = useState<string>('');
  const [timelineImpact, setTimelineImpact] = useState<string>('');
  const [selectedEvent, setSelectedEvent] = useState<TimelineEvent | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [refreshMessage, setRefreshMessage] = useState<string | null>(null);
  const [dataQuality, setDataQuality] = useState<DataQualityDashboard | null>(null);
  const [dataQualityLoading, setDataQualityLoading] = useState(false);
  const [customFields, setCustomFields] = useState<CompanyCustomField[]>([]);
  const [customFieldsLoading, setCustomFieldsLoading] = useState(false);
  const [editingFieldId, setEditingFieldId] = useState<string | null>(null);
  const [fieldValues, setFieldValues] = useState<Record<string, string | string[]>>({});
  const [isWatched, setIsWatched] = useState(false);
  const [watchlistLoading, setWatchlistLoading] = useState(false);
  const [financials, setFinancials] = useState<CompanyFinancials | null>(null);
  const [financialsLoading, setFinancialsLoading] = useState(false);

  // Load company profile
  useEffect(() => {
    async function loadCompany() {
      setLoading(true);
      setError(null);

      const result = await companyApi.getCompany(companyId);
      if (result.error) {
        setError(result.error);
      } else if (result.data) {
        setCompany(result.data);
      }
      setLoading(false);
    }

    loadCompany();
  }, [companyId]);

  // Check watchlist status
  useEffect(() => {
    async function checkWatchlistStatus() {
      const result = await companyApi.checkWatchlistStatus(companyId);
      if (result.data) {
        setIsWatched(result.data.is_watched);
      }
    }

    checkWatchlistStatus();
  }, [companyId]);

  // Load news when switching to news tab or filters change
  useEffect(() => {
    async function loadNews() {
      if (activeTab !== 'news' || !company) return;

      setNewsLoading(true);
      const result = await companyApi.getCompanyNews(companyId, {
        limit: 10,
        category: newsCategory || undefined,
        sentiment: newsSentiment || undefined,
        dateFrom: dateFrom || undefined,
        dateTo: dateTo || undefined,
      });
      if (result.data) {
        setNews(result.data.news);
      }
      setNewsLoading(false);
    }

    loadNews();
  }, [activeTab, companyId, company, newsCategory, newsSentiment, dateFrom, dateTo]);

  // Load timeline when switching to timeline tab or filters change
  useEffect(() => {
    async function loadTimeline() {
      if (activeTab !== 'timeline' || !company) return;

      setTimelineLoading(true);
      const result = await companyApi.getCompanyTimeline(companyId, {
        event_type: timelineEventType || undefined,
        impact: timelineImpact || undefined,
      });
      if (result.data) {
        setTimeline(result.data.events);
      }
      setTimelineLoading(false);
    }

    loadTimeline();
  }, [activeTab, companyId, company, timelineEventType, timelineImpact]);

  // Load data quality when switching to data-quality tab
  useEffect(() => {
    async function loadDataQuality() {
      if (activeTab !== 'data-quality' || !company) return;

      setDataQualityLoading(true);
      const result = await companyApi.getDataQuality(companyId);
      if (result.data) {
        setDataQuality(result.data);
      }
      setDataQualityLoading(false);
    }

    loadDataQuality();
  }, [activeTab, companyId, company]);

  // Load financials when switching to financials tab
  useEffect(() => {
    async function loadFinancials() {
      if (activeTab !== 'financials' || !company) return;

      setFinancialsLoading(true);
      const result = await companyApi.getFinancials(companyId);
      if (result.data) {
        setFinancials(result.data);
      }
      setFinancialsLoading(false);
    }

    loadFinancials();
  }, [activeTab, companyId, company]);

  // Load custom fields when company profile loads
  useEffect(() => {
    async function loadCustomFields() {
      if (!company) return;

      setCustomFieldsLoading(true);
      const result = await customFieldsApi.getCompanyFieldValues(companyId);
      if (result.data) {
        setCustomFields(result.data);
        // Initialize field values from existing data
        const values: Record<string, string | string[]> = {};
        result.data.forEach((field) => {
          // For multiselect, use value_json (array), otherwise use value (string)
          if (field.field_definition.field_type === 'multiselect' && field.value_json) {
            values[field.field_definition.id] = field.value_json;
          } else if (field.value) {
            values[field.field_definition.id] = field.value;
          }
        });
        setFieldValues(values);
      }
      setCustomFieldsLoading(false);
    }

    loadCustomFields();
  }, [company, companyId]);

  // Clear date filters
  const clearDateFilters = () => {
    setDateFrom('');
    setDateTo('');
    setShowDateFilter(false);
  };

  // Handle data refresh
  const handleRefresh = async () => {
    setRefreshing(true);
    setRefreshMessage(null);

    const result = await companyApi.refreshCompanyData(companyId);

    if (result.error) {
      setRefreshMessage(`Błąd: ${result.error}`);
    } else if (result.data) {
      setRefreshMessage(result.data.message);

      // Reload company data to get updated timestamp
      const companyResult = await companyApi.getCompany(companyId);
      if (companyResult.data) {
        setCompany(companyResult.data);
      }

      // Clear message after 3 seconds
      setTimeout(() => setRefreshMessage(null), 3000);
    }

    setRefreshing(false);
  };

  const handleToggleWatchlist = async () => {
    setWatchlistLoading(true);

    const result = isWatched
      ? await companyApi.removeFromWatchlist(companyId)
      : await companyApi.addToWatchlist(companyId);

    if (result.data) {
      setIsWatched(result.data.is_watched);
    }

    setWatchlistLoading(false);
  };

  // Handle custom field value save
  const handleSaveFieldValue = async (fieldId: string) => {
    const fieldValue = fieldValues[fieldId];

    // Determine if this is a multiselect field
    const field = customFields.find(f => f.field_definition.id === fieldId);
    const isMultiselect = field?.field_definition.field_type === 'multiselect';

    const result = await customFieldsApi.setFieldValue(companyId, {
      field_definition_id: fieldId,
      value: isMultiselect ? null : (fieldValue as string || ''),
      value_json: isMultiselect ? (fieldValue as string[] || []) : null,
    });

    if (result.data) {
      // Reload custom fields to get updated values
      const fieldsResult = await customFieldsApi.getCompanyFieldValues(companyId);
      if (fieldsResult.data) {
        setCustomFields(fieldsResult.data);
      }
      setEditingFieldId(null);
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    return formatRelativeTime(dateString, 'pl-PL');
  };

  // Sentiment badge
  const getSentimentBadge = (sentiment: string) => {
    const styles: Record<string, { bg: string; text: string; label: string }> = {
      positive: { bg: 'bg-green-100', text: 'text-green-800', label: 'Pozytywny' },
      negative: { bg: 'bg-red-100', text: 'text-red-800', label: 'Negatywny' },
      neutral: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Neutralny' },
    };
    const style = styles[sentiment] || styles.neutral;
    return (
      <span className={`px-2 py-0.5 text-xs rounded-full ${style.bg} ${style.text}`}>
        {style.label}
      </span>
    );
  };

  // Category badge
  const getCategoryBadge = (category: string) => {
    const labels: Record<string, { icon: string; label: string }> = {
      general: { icon: '📰', label: 'Ogólne' },
      financial: { icon: '💰', label: 'Finanse' },
      product: { icon: '📦', label: 'Produkt' },
      hr: { icon: '👥', label: 'Kadry' },
      legal: { icon: '⚖️', label: 'Prawne' },
    };
    const cat = labels[category] || labels.general;
    return (
      <span className="px-2 py-0.5 text-xs bg-blue-50 text-blue-700 rounded-full">
        {cat.icon} {cat.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">Ładowanie profilu firmy...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Błąd</h2>
          <p className="text-slate-600 mb-4">{error}</p>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Wróć
          </button>
        </div>
      </div>
    );
  }

  if (!company) {
    return null;
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link href="/dashboard" className="text-2xl font-bold text-blue-600">
                MI-Navigator
              </Link>
              <span className="text-slate-300">/</span>
              <span className="text-slate-600">Firma</span>
            </div>
            <nav className="flex items-center gap-4">
              <Link href="/reports" className="text-slate-600 hover:text-blue-600">
                Raporty
              </Link>
              <Link href="/search" className="text-slate-600 hover:text-blue-600">
                Wyszukiwanie
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Company Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-start gap-6">
            <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl font-bold text-blue-600">
                {company.name.charAt(0)}
              </span>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold text-slate-900">{company.name}</h1>
                <span
                  className={`px-2 py-0.5 text-xs rounded-full ${
                    company.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {company.status === 'active' ? 'Aktywna' : company.status}
                </span>
              </div>
              <p className="text-slate-600 mt-1">{company.description}</p>
              <div className="flex flex-wrap gap-4 mt-3 text-sm text-slate-500">
                <span>📍 {company.address.city}</span>
                <span>🏢 NIP: {company.nip}</span>
                {company.krs && <span>📋 KRS: {company.krs}</span>}
                <span>📅 Założona: {company.founded}</span>
                {company.employees_range && (
                  <span>👥 {company.employees_range} pracowników</span>
                )}
              </div>
            </div>
            <div className="flex flex-col gap-2 items-end">
              {company.website && (
                <a
                  href={company.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  🌐 Strona www
                </a>
              )}
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className={`px-4 py-2 rounded-lg flex items-center gap-2 text-sm transition-colors ${
                  refreshing
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {refreshing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-slate-700"></div>
                    Odświeżanie...
                  </>
                ) : (
                  <>
                    🔄 Odśwież dane
                  </>
                )}
              </button>
              {company.last_updated && (
                <p className="text-xs text-slate-500">
                  Ostatnia aktualizacja: {formatDate(company.last_updated)}
                </p>
              )}
              {refreshMessage && (
                <div className={`text-xs px-3 py-1 rounded ${
                  refreshMessage.includes('Błąd')
                    ? 'bg-red-100 text-red-700'
                    : 'bg-green-100 text-green-700'
                }`}>
                  {refreshMessage}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex gap-1">
            {[
              { id: 'overview' as Tab, label: 'Przegląd', icon: '📊' },
              { id: 'timeline' as Tab, label: 'Oś czasu', icon: '📅' },
              { id: 'news' as Tab, label: 'Aktualności', icon: '📰' },
              { id: 'financials' as Tab, label: 'Finanse', icon: '💰' },
              { id: 'people' as Tab, label: 'Osoby', icon: '👥' },
              { id: 'data-quality' as Tab, label: 'Jakość Danych', icon: '✓' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Company Details */}
            <div className="lg:col-span-2 space-y-6">
              {/* PKD Codes */}
              <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">
                  Kody PKD
                </h2>
                <div className="space-y-3">
                  {company.pkd_descriptions.map((pkd) => (
                    <div
                      key={pkd.code}
                      className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg"
                    >
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-mono rounded">
                        {pkd.code}
                      </span>
                      <div>
                        <p className="text-sm text-slate-900">{pkd.name}</p>
                        <p className="text-xs text-slate-500">{pkd.category}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Address */}
              <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">
                  Lokalizacja
                </h2>
                <div className="text-slate-600">
                  <p>{company.address.street}</p>
                  <p>
                    {company.address.postal_code} {company.address.city}
                  </p>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="space-y-6">
              <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">
                  Informacje
                </h2>
                <dl className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-slate-500">NIP</dt>
                    <dd className="text-slate-900 font-mono">{company.nip}</dd>
                  </div>
                  {company.krs && (
                    <div className="flex justify-between">
                      <dt className="text-slate-500">KRS</dt>
                      <dd className="text-slate-900 font-mono">{company.krs}</dd>
                    </div>
                  )}
                  {company.regon && (
                    <div className="flex justify-between">
                      <dt className="text-slate-500">REGON</dt>
                      <dd className="text-slate-900 font-mono">{company.regon}</dd>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <dt className="text-slate-500">Rok założenia</dt>
                    <dd className="text-slate-900">{company.founded}</dd>
                  </div>
                  {company.employees_range && (
                    <div className="flex justify-between">
                      <dt className="text-slate-500">Zatrudnienie</dt>
                      <dd className="text-slate-900">{company.employees_range}</dd>
                    </div>
                  )}
                </dl>
              </div>

              {/* Custom Fields */}
              {customFields.length > 0 && (
                <div className="bg-white rounded-xl border border-slate-200 p-6">
                  <h2 className="text-lg font-semibold text-slate-900 mb-4">
                    Custom Fields
                  </h2>
                  {customFieldsLoading ? (
                    <div className="text-center py-4">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {customFields.map((field) => (
                        <div key={field.field_definition.id} className="space-y-2">
                          <label className="text-sm font-medium text-slate-700">
                            {field.field_definition.name}
                            {field.field_definition.is_required && (
                              <span className="text-red-500 ml-1">*</span>
                            )}
                          </label>
                          {field.field_definition.description && (
                            <p className="text-xs text-slate-500">
                              {field.field_definition.description}
                            </p>
                          )}

                          {field.field_definition.field_type === 'select' ? (
                            <div className="flex gap-2">
                              <select
                                value={fieldValues[field.field_definition.id] || ''}
                                onChange={(e) => {
                                  setFieldValues({
                                    ...fieldValues,
                                    [field.field_definition.id]: e.target.value,
                                  });
                                  setEditingFieldId(field.field_definition.id);
                                }}
                                className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                              >
                                <option value="">Select...</option>
                                {field.field_definition.options?.map((option) => (
                                  <option key={option} value={option}>
                                    {option}
                                  </option>
                                ))}
                              </select>
                              {editingFieldId === field.field_definition.id && (
                                <button
                                  onClick={() => handleSaveFieldValue(field.field_definition.id)}
                                  className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                                >
                                  Save
                                </button>
                              )}
                            </div>
                          ) : field.field_definition.field_type === 'multiselect' ? (
                            <div className="space-y-2">
                              <div className="border border-slate-300 rounded-lg p-3 space-y-2 bg-slate-50">
                                {field.field_definition.options?.map((option) => {
                                  const currentValues = (fieldValues[field.field_definition.id] as string[]) || [];
                                  const isChecked = currentValues.includes(option);

                                  return (
                                    <label
                                      key={option}
                                      className="flex items-center gap-2 cursor-pointer hover:bg-slate-100 p-2 rounded transition-colors"
                                    >
                                      <input
                                        type="checkbox"
                                        checked={isChecked}
                                        onChange={(e) => {
                                          let newValues: string[];
                                          if (e.target.checked) {
                                            // Add option
                                            newValues = [...currentValues, option];
                                          } else {
                                            // Remove option
                                            newValues = currentValues.filter(v => v !== option);
                                          }
                                          setFieldValues({
                                            ...fieldValues,
                                            [field.field_definition.id]: newValues,
                                          });
                                          setEditingFieldId(field.field_definition.id);
                                        }}
                                        className="w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-2 focus:ring-blue-500"
                                      />
                                      <span className="text-sm text-slate-700">{option}</span>
                                    </label>
                                  );
                                })}
                              </div>
                              {editingFieldId === field.field_definition.id && (
                                <button
                                  onClick={() => handleSaveFieldValue(field.field_definition.id)}
                                  className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                                >
                                  Save
                                </button>
                              )}
                            </div>
                          ) : field.field_definition.field_type === 'number' ? (
                            <div className="flex gap-2">
                              <input
                                type="number"
                                value={fieldValues[field.field_definition.id] || ''}
                                onChange={(e) => {
                                  setFieldValues({
                                    ...fieldValues,
                                    [field.field_definition.id]: e.target.value,
                                  });
                                  setEditingFieldId(field.field_definition.id);
                                }}
                                className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Enter value..."
                              />
                              {editingFieldId === field.field_definition.id && (
                                <button
                                  onClick={() => handleSaveFieldValue(field.field_definition.id)}
                                  className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                                >
                                  Save
                                </button>
                              )}
                            </div>
                          ) : (
                            <div className="flex gap-2">
                              <input
                                type="text"
                                value={fieldValues[field.field_definition.id] || ''}
                                onChange={(e) => {
                                  setFieldValues({
                                    ...fieldValues,
                                    [field.field_definition.id]: e.target.value,
                                  });
                                  setEditingFieldId(field.field_definition.id);
                                }}
                                className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Enter value..."
                              />
                              {editingFieldId === field.field_definition.id && (
                                <button
                                  onClick={() => handleSaveFieldValue(field.field_definition.id)}
                                  className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                                >
                                  Save
                                </button>
                              )}
                            </div>
                          )}

                          {((field.value && field.field_definition.field_type !== 'multiselect') ||
                            (field.value_json && field.field_definition.field_type === 'multiselect')) &&
                            !editingFieldId && (
                            <div className="text-sm text-slate-600">
                              Current: <span className="font-medium">
                                {field.field_definition.field_type === 'multiselect' && field.value_json
                                  ? field.value_json.join(', ')
                                  : field.value}
                              </span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Actions */}
              <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">
                  Akcje
                </h2>
                <div className="space-y-2">
                  <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                    📊 Generuj raport
                  </button>
                  <button
                    onClick={handleToggleWatchlist}
                    disabled={watchlistLoading}
                    className={`w-full px-4 py-2 rounded-lg text-sm transition-colors ${
                      isWatched
                        ? 'bg-amber-100 text-amber-700 hover:bg-amber-200'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    } ${watchlistLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {watchlistLoading ? '⏳ Przetwarzanie...' : isWatched ? '⭐ Obserwujesz' : '⭐ Dodaj do obserwowanych'}
                  </button>
                  <button className="w-full px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 text-sm">
                    🔔 Ustaw alert
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Timeline Tab */}
        {activeTab === 'timeline' && (
          <div className="space-y-6">
            {/* Filters */}
            <div className="bg-white rounded-xl border border-slate-200 p-4 space-y-4">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm text-slate-600 mr-2">Typ wydarzenia:</span>
                {[
                  { value: '', label: 'Wszystkie' },
                  { value: 'founding', label: '🏛️ Założenie' },
                  { value: 'investment', label: '💰 Inwestycja' },
                  { value: 'partnership', label: '🤝 Partnerstwo' },
                  { value: 'product', label: '📦 Produkt' },
                  { value: 'legal', label: '⚖️ Prawne' },
                  { value: 'hr', label: '👥 Kadry' },
                  { value: 'milestone', label: '🎯 Kamień milowy' },
                ].map((type) => (
                  <button
                    key={type.value}
                    onClick={() => setTimelineEventType(type.value)}
                    className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                      timelineEventType === type.value
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    {type.label}
                  </button>
                ))}
              </div>

              <div className="flex items-center gap-2 flex-wrap pt-3 border-t border-slate-200">
                <span className="text-sm text-slate-600 mr-2">Wpływ:</span>
                {[
                  { value: '', label: 'Wszystkie' },
                  { value: 'high', label: '🔴 Wysoki' },
                  { value: 'medium', label: '🟡 Średni' },
                  { value: 'low', label: '🟢 Niski' },
                ].map((imp) => (
                  <button
                    key={imp.value}
                    onClick={() => setTimelineImpact(imp.value)}
                    className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                      timelineImpact === imp.value
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    {imp.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Timeline Display */}
            {timelineLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-slate-600">Ładowanie osi czasu...</p>
              </div>
            ) : timeline.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
                <div className="text-4xl mb-4">📅</div>
                <h3 className="text-lg font-semibold text-slate-900">Brak wydarzeń</h3>
                <p className="text-slate-600 mt-1">
                  Nie znaleziono wydarzeń dla wybranych kryteriów.
                </p>
              </div>
            ) : (
              <div className="relative">
                {/* Vertical timeline line */}
                <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-slate-200"></div>

                {/* Timeline events */}
                <div className="space-y-6">
                  {timeline.map((event) => {
                    const date = new Date(event.date);
                    const year = date.getFullYear();
                    const month = date.toLocaleDateString('pl-PL', { month: 'long' });
                    const day = date.getDate();

                    // Event type icon
                    const typeIcons: Record<string, string> = {
                      founding: '🏛️',
                      investment: '💰',
                      partnership: '🤝',
                      product: '📦',
                      legal: '⚖️',
                      hr: '👥',
                      milestone: '🎯',
                    };

                    // Impact color
                    const impactColors: Record<string, { bg: string; text: string; border: string }> = {
                      high: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-300' },
                      medium: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-300' },
                      low: { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-300' },
                    };

                    const impactStyle = impactColors[event.impact];

                    return (
                      <div key={event.id} className="relative pl-20 group">
                        {/* Date marker */}
                        <div className="absolute left-0 top-0">
                          <div className="flex flex-col items-center">
                            <div className="w-16 h-16 rounded-full bg-white border-4 border-blue-600 flex items-center justify-center text-2xl z-10 shadow-md">
                              {typeIcons[event.event_type]}
                            </div>
                            <div className="text-center mt-2">
                              <div className="text-lg font-bold text-slate-900">{day}</div>
                              <div className="text-xs text-slate-500">{month}</div>
                              <div className="text-sm font-medium text-slate-700">{year}</div>
                            </div>
                          </div>
                        </div>

                        {/* Event card */}
                        <div
                          onClick={() => setSelectedEvent(selectedEvent?.id === event.id ? null : event)}
                          className={`bg-white rounded-xl border-2 p-6 cursor-pointer transition-all ${
                            selectedEvent?.id === event.id
                              ? `${impactStyle.border} shadow-lg`
                              : 'border-slate-200 hover:border-slate-300 hover:shadow-md'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-4 mb-3">
                            <h3 className="text-lg font-semibold text-slate-900 flex-1">
                              {event.title}
                            </h3>
                            <span className={`px-3 py-1 text-xs rounded-full ${impactStyle.bg} ${impactStyle.text} whitespace-nowrap`}>
                              {event.impact === 'high' && '🔴 Wysoki wpływ'}
                              {event.impact === 'medium' && '🟡 Średni wpływ'}
                              {event.impact === 'low' && '🟢 Niski wpływ'}
                            </span>
                          </div>

                          <p className="text-slate-600 text-sm mb-4">
                            {event.description}
                          </p>

                          {selectedEvent?.id === event.id && event.source && (
                            <div className="mt-4 pt-4 border-t border-slate-200">
                              <div className="flex items-center gap-2 text-xs text-slate-500">
                                <span>📄 Źródło: {event.source}</span>
                                {event.source_url && (
                                  <a
                                    href={event.source_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-600 hover:underline"
                                    onClick={(e) => e.stopPropagation()}
                                  >
                                    Zobacz więcej →
                                  </a>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Timeline summary */}
                <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-slate-900 mb-1">
                        Historia firmy {company?.name}
                      </h4>
                      <p className="text-sm text-slate-600">
                        {timeline.length} {timeline.length === 1 ? 'wydarzenie' : timeline.length < 5 ? 'wydarzenia' : 'wydarzeń'} od {new Date(timeline[0].date).getFullYear()}
                        {timeline.length > 1 && ` do ${new Date(timeline[timeline.length - 1].date).getFullYear()}`}
                      </p>
                    </div>
                    <div className="text-4xl">🎯</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* News Tab */}
        {activeTab === 'news' && (
          <div className="space-y-6">
            {/* Filters */}
            <div className="bg-white rounded-xl border border-slate-200 p-4 space-y-4">
              {/* Category Filter */}
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm text-slate-600 mr-2">Kategoria:</span>
                {[
                  { value: '', label: 'Wszystkie' },
                  { value: 'general', label: '📰 Ogólne' },
                  { value: 'financial', label: '💰 Finanse' },
                  { value: 'product', label: '📦 Produkty' },
                  { value: 'hr', label: '👥 Kadry' },
                  { value: 'legal', label: '⚖️ Prawne' },
                ].map((cat) => (
                  <button
                    key={cat.value}
                    onClick={() => setNewsCategory(cat.value)}
                    className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                      newsCategory === cat.value
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    {cat.label}
                  </button>
                ))}

                {/* Date filter toggle */}
                <div className="ml-auto">
                  <button
                    onClick={() => setShowDateFilter(!showDateFilter)}
                    className={`px-3 py-1.5 text-sm rounded-lg transition-colors flex items-center gap-2 ${
                      showDateFilter || dateFrom || dateTo
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    📅 Zakres dat
                    {(dateFrom || dateTo) && (
                      <span className="bg-white bg-opacity-30 px-1.5 rounded text-xs">
                        Aktywny
                      </span>
                    )}
                  </button>
                </div>
              </div>

              {/* Sentiment Filter */}
              <div className="flex items-center gap-2 flex-wrap pt-3 border-t border-slate-200">
                <span className="text-sm text-slate-600 mr-2">Sentyment:</span>
                {[
                  { value: '', label: 'Wszystkie' },
                  { value: 'positive', label: '✅ Pozytywny' },
                  { value: 'neutral', label: '⚪ Neutralny' },
                  { value: 'negative', label: '❌ Negatywny' },
                ].map((sent) => (
                  <button
                    key={sent.value}
                    onClick={() => setNewsSentiment(sent.value)}
                    className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                      newsSentiment === sent.value
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    {sent.label}
                  </button>
                ))}
              </div>

              {/* Date Range Filter */}
              {showDateFilter && (
                <div className="flex items-center gap-4 pt-3 border-t border-slate-200">
                  <span className="text-sm text-slate-600">Zakres dat:</span>
                  <div className="flex items-center gap-2">
                    <label className="text-xs text-slate-500">Od:</label>
                    <input
                      type="date"
                      value={dateFrom}
                      onChange={(e) => setDateFrom(e.target.value)}
                      className="px-3 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="text-xs text-slate-500">Do:</label>
                    <input
                      type="date"
                      value={dateTo}
                      onChange={(e) => setDateTo(e.target.value)}
                      className="px-3 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  {(dateFrom || dateTo) && (
                    <button
                      onClick={clearDateFilters}
                      className="px-3 py-1.5 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                    >
                      ✕ Wyczyść
                    </button>
                  )}
                </div>
              )}

              {/* Active filters summary */}
              {(dateFrom || dateTo) && (
                <div className="flex items-center gap-2 text-sm text-slate-600 pt-2 border-t border-slate-100">
                  <span>📅 Filtr dat:</span>
                  {dateFrom && (
                    <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded">
                      Od: {new Date(dateFrom).toLocaleDateString('pl-PL')}
                    </span>
                  )}
                  {dateTo && (
                    <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded">
                      Do: {new Date(dateTo).toLocaleDateString('pl-PL')}
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* News List */}
            {newsLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-slate-600">Ładowanie aktualności...</p>
              </div>
            ) : news.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
                <div className="text-4xl mb-4">📭</div>
                <h3 className="text-lg font-semibold text-slate-900">
                  Brak aktualności
                </h3>
                <p className="text-slate-600 mt-1">
                  Nie znaleziono artykułów dla wybranych kryteriów.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {news.map((article) => (
                  <article
                    key={article.id}
                    className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          {getCategoryBadge(article.category)}
                          {getSentimentBadge(article.sentiment)}
                        </div>
                        <h3 className="text-lg font-semibold text-slate-900 mb-2">
                          {article.title}
                        </h3>
                        <p className="text-slate-600 text-sm mb-3">
                          {article.summary}
                        </p>
                        <div className="flex items-center gap-4 text-xs text-slate-500">
                          <span className="flex items-center gap-1">
                            📰 {article.source}
                          </span>
                          <span className="flex items-center gap-1">
                            🕒 {formatDate(article.published_at)}
                          </span>
                        </div>
                      </div>
                      <a
                        href={article.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 text-sm flex items-center gap-2 whitespace-nowrap"
                      >
                        Czytaj więcej →
                      </a>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Financials Tab */}
        {activeTab === 'financials' && (
          <div className="space-y-6">
            {financialsLoading ? (
              <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
                <div className="text-5xl mb-4">💰</div>
                <p className="text-slate-600">Ładowanie danych finansowych...</p>
              </div>
            ) : financials ? (
              <>
                {/* Historical Data Comparison */}
                {financials.statements && financials.statements.length > 1 && (
                  <div className="bg-white rounded-xl border border-slate-200 p-6">
                    <h2 className="text-xl font-semibold text-slate-900 mb-4">
                      Dane Historyczne
                    </h2>

                    {/* Revenue Trend */}
                    <div className="mb-6">
                      <h3 className="text-sm font-medium text-slate-700 mb-3">Przychody (PLN)</h3>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-slate-200">
                              <th className="text-left py-2 px-3 text-slate-600 font-medium">Rok</th>
                              <th className="text-right py-2 px-3 text-slate-600 font-medium">Wartość</th>
                              <th className="text-right py-2 px-3 text-slate-600 font-medium">YoY</th>
                              <th className="text-right py-2 px-3 text-slate-600 font-medium">Wzrost</th>
                            </tr>
                          </thead>
                          <tbody>
                            {financials.statements.map((statement, index) => {
                              const prevStatement = financials.statements[index + 1];
                              const yoyChange = prevStatement
                                ? statement.revenue - prevStatement.revenue
                                : 0;
                              const yoyPercent = prevStatement
                                ? ((statement.revenue - prevStatement.revenue) / prevStatement.revenue * 100)
                                : 0;
                              const isPositive = yoyChange > 0;

                              return (
                                <tr key={statement.year} className="border-b border-slate-100 last:border-0">
                                  <td className="py-2 px-3 font-medium text-slate-900">{statement.year}</td>
                                  <td className="py-2 px-3 text-right font-semibold text-slate-900">
                                    {(statement.revenue / 1_000_000).toFixed(1)}M
                                  </td>
                                  <td className="py-2 px-3 text-right">
                                    {prevStatement ? (
                                      <span className={isPositive ? 'text-green-600' : 'text-red-600'}>
                                        {isPositive ? '+' : ''}{(yoyChange / 1_000_000).toFixed(1)}M
                                      </span>
                                    ) : (
                                      <span className="text-slate-400">-</span>
                                    )}
                                  </td>
                                  <td className="py-2 px-3 text-right">
                                    {prevStatement ? (
                                      <span className={`inline-flex items-center gap-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                                        {isPositive ? '↑' : '↓'} {Math.abs(yoyPercent).toFixed(1)}%
                                      </span>
                                    ) : (
                                      <span className="text-slate-400">-</span>
                                    )}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Net Profit Trend */}
                    <div className="mb-6">
                      <h3 className="text-sm font-medium text-slate-700 mb-3">Zysk netto (PLN)</h3>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-slate-200">
                              <th className="text-left py-2 px-3 text-slate-600 font-medium">Rok</th>
                              <th className="text-right py-2 px-3 text-slate-600 font-medium">Wartość</th>
                              <th className="text-right py-2 px-3 text-slate-600 font-medium">YoY</th>
                              <th className="text-right py-2 px-3 text-slate-600 font-medium">Wzrost</th>
                            </tr>
                          </thead>
                          <tbody>
                            {financials.statements.map((statement, index) => {
                              const prevStatement = financials.statements[index + 1];
                              const yoyChange = prevStatement
                                ? statement.net_profit - prevStatement.net_profit
                                : 0;
                              const yoyPercent = prevStatement
                                ? ((statement.net_profit - prevStatement.net_profit) / prevStatement.net_profit * 100)
                                : 0;
                              const isPositive = yoyChange > 0;

                              return (
                                <tr key={statement.year} className="border-b border-slate-100 last:border-0">
                                  <td className="py-2 px-3 font-medium text-slate-900">{statement.year}</td>
                                  <td className="py-2 px-3 text-right font-semibold text-slate-900">
                                    {(statement.net_profit / 1_000_000).toFixed(1)}M
                                  </td>
                                  <td className="py-2 px-3 text-right">
                                    {prevStatement ? (
                                      <span className={isPositive ? 'text-green-600' : 'text-red-600'}>
                                        {isPositive ? '+' : ''}{(yoyChange / 1_000_000).toFixed(1)}M
                                      </span>
                                    ) : (
                                      <span className="text-slate-400">-</span>
                                    )}
                                  </td>
                                  <td className="py-2 px-3 text-right">
                                    {prevStatement ? (
                                      <span className={`inline-flex items-center gap-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                                        {isPositive ? '↑' : '↓'} {Math.abs(yoyPercent).toFixed(1)}%
                                      </span>
                                    ) : (
                                      <span className="text-slate-400">-</span>
                                    )}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Key Ratios Historical Comparison */}
                    {financials.ratios && financials.ratios.length > 1 && (
                      <div>
                        <h3 className="text-sm font-medium text-slate-700 mb-3">Wskaźniki Rentowności</h3>
                        <div className="overflow-x-auto">
                          <table className="w-full text-sm">
                            <thead>
                              <tr className="border-b border-slate-200">
                                <th className="text-left py-2 px-3 text-slate-600 font-medium">Rok</th>
                                <th className="text-right py-2 px-3 text-slate-600 font-medium">ROE (%)</th>
                                <th className="text-right py-2 px-3 text-slate-600 font-medium">ROA (%)</th>
                                <th className="text-right py-2 px-3 text-slate-600 font-medium">ROS (%)</th>
                              </tr>
                            </thead>
                            <tbody>
                              {financials.ratios.map((ratio, index) => {
                                const prevRatio = financials.ratios[index + 1];

                                return (
                                  <tr key={ratio.year} className="border-b border-slate-100 last:border-0">
                                    <td className="py-2 px-3 font-medium text-slate-900">{ratio.year}</td>
                                    <td className="py-2 px-3 text-right">
                                      <span className="font-semibold text-slate-900">{ratio.roe.toFixed(1)}%</span>
                                      {prevRatio && (
                                        <span className={`ml-2 text-xs ${ratio.roe > prevRatio.roe ? 'text-green-600' : 'text-red-600'}`}>
                                          {ratio.roe > prevRatio.roe ? '↑' : '↓'}
                                        </span>
                                      )}
                                    </td>
                                    <td className="py-2 px-3 text-right">
                                      <span className="font-semibold text-slate-900">{ratio.roa.toFixed(1)}%</span>
                                      {prevRatio && (
                                        <span className={`ml-2 text-xs ${ratio.roa > prevRatio.roa ? 'text-green-600' : 'text-red-600'}`}>
                                          {ratio.roa > prevRatio.roa ? '↑' : '↓'}
                                        </span>
                                      )}
                                    </td>
                                    <td className="py-2 px-3 text-right">
                                      <span className="font-semibold text-slate-900">{ratio.ros.toFixed(1)}%</span>
                                      {prevRatio && (
                                        <span className={`ml-2 text-xs ${ratio.ros > prevRatio.ros ? 'text-green-600' : 'text-red-600'}`}>
                                          {ratio.ros > prevRatio.ros ? '↑' : '↓'}
                                        </span>
                                      )}
                                    </td>
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Latest Financial Ratios */}
                {financials.ratios && financials.ratios.length > 0 && (
                  <div className="bg-white rounded-xl border border-slate-200 p-6">
                    <h2 className="text-xl font-semibold text-slate-900 mb-4">
                      Wskaźniki Finansowe {financials.ratios[0].year}
                    </h2>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="p-4 bg-slate-50 rounded-lg">
                        <div className="text-sm text-slate-600">ROE</div>
                        <div className="text-2xl font-bold text-slate-900">{financials.ratios[0].roe}%</div>
                      </div>
                      <div className="p-4 bg-slate-50 rounded-lg">
                        <div className="text-sm text-slate-600">ROA</div>
                        <div className="text-2xl font-bold text-slate-900">{financials.ratios[0].roa}%</div>
                      </div>
                      <div className="p-4 bg-slate-50 rounded-lg">
                        <div className="text-sm text-slate-600">ROS</div>
                        <div className="text-2xl font-bold text-slate-900">{financials.ratios[0].ros}%</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Industry Benchmarks */}
                {financials.industry_benchmarks && (
                  <div className="bg-white rounded-xl border border-slate-200 p-6">
                    <div className="mb-4">
                      <h2 className="text-xl font-semibold text-slate-900">Porównanie z Branżą</h2>
                      <p className="text-sm text-slate-600 mt-1">{financials.industry_benchmarks.industry}</p>
                      <p className="text-xs text-slate-500 mt-1">
                        Źródło: {financials.industry_benchmarks.source} ({financials.industry_benchmarks.year})
                      </p>
                    </div>

                    <div className="space-y-4">
                      {financials.industry_benchmarks.metrics.map((metric, index) => {
                        const isLowerBetter = metric.metric_name.includes('Debt') || metric.metric_name.includes('DSO');
                        const isAbove = isLowerBetter
                          ? metric.comparison === 'below_average'
                          : metric.comparison === 'above_average';

                        return (
                          <div key={index} className="border-b border-slate-200 pb-4 last:border-0">
                            <div className="flex justify-between items-center mb-2">
                              <div className="font-medium text-slate-900">{metric.metric_name}</div>
                              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                                isAbove ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'
                              }`}>
                                {isAbove ? '✓ Powyżej średniej' : '⚠ Poniżej średniej'}
                              </div>
                            </div>
                            <div className="grid grid-cols-4 gap-4 text-sm">
                              <div>
                                <div className="text-slate-600">Twoja firma</div>
                                <div className="font-bold text-slate-900">{metric.company_value.toFixed(2)}</div>
                              </div>
                              <div>
                                <div className="text-slate-600">Średnia branży</div>
                                <div className="font-medium text-slate-700">{metric.industry_average.toFixed(2)}</div>
                              </div>
                              <div>
                                <div className="text-slate-600">Mediana branży</div>
                                <div className="font-medium text-slate-700">{metric.industry_median.toFixed(2)}</div>
                              </div>
                              <div>
                                <div className="text-slate-600">Percentyl</div>
                                <div className="font-bold text-blue-600">{metric.percentile}%</div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
                <div className="text-5xl mb-4">💰</div>
                <h3 className="text-lg font-semibold text-slate-900">
                  Brak danych finansowych
                </h3>
                <p className="text-slate-600 mt-2">
                  Nie znaleziono danych finansowych dla tej firmy.
                </p>
              </div>
            )}
          </div>
        )}

        {/* People Tab (Placeholder) */}
        {activeTab === 'people' && (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <div className="text-5xl mb-4">👥</div>
            <h3 className="text-lg font-semibold text-slate-900">
              Kluczowe osoby
            </h3>
            <p className="text-slate-600 mt-2">
              Ta sekcja jest w przygotowaniu. Wkrótce będą tutaj informacje o
              zarządzie i kluczowych osobach w firmie.
            </p>
          </div>
        )}

        {/* Data Quality Tab */}
        {activeTab === 'data-quality' && (
          <div className="space-y-6">
            {dataQualityLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                  <p className="mt-2 text-slate-600">Ładowanie metryk jakości...</p>
                </div>
              </div>
            ) : dataQuality ? (
              <>
                {/* Overall Score Card */}
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border-2 border-blue-200 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-2xl font-bold text-slate-900">Jakość Danych</h2>
                      <p className="text-slate-600 mt-1">{dataQuality.company_name}</p>
                    </div>
                    <div className="text-center">
                      <div className={`text-5xl font-bold ${
                        dataQuality.overall_status === 'excellent' ? 'text-green-600' :
                        dataQuality.overall_status === 'good' ? 'text-blue-600' :
                        dataQuality.overall_status === 'fair' ? 'text-amber-600' :
                        'text-red-600'
                      }`}>
                        {Math.round(dataQuality.overall_score)}%
                      </div>
                      <div className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium mt-2 ${
                        dataQuality.overall_status === 'excellent' ? 'bg-green-100 text-green-800' :
                        dataQuality.overall_status === 'good' ? 'bg-blue-100 text-blue-800' :
                        dataQuality.overall_status === 'fair' ? 'bg-amber-100 text-amber-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {dataQuality.overall_status === 'excellent' ? '✓ Doskonała' :
                         dataQuality.overall_status === 'good' ? '✓ Dobra' :
                         dataQuality.overall_status === 'fair' ? '⚠ Wystarczająca' :
                         '✗ Słaba'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Metric Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Completeness */}
                  <div className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-slate-900">📊 Kompletność</h3>
                      <span className={`text-2xl font-bold ${
                        dataQuality.completeness.status === 'excellent' ? 'text-green-600' :
                        dataQuality.completeness.status === 'good' ? 'text-blue-600' :
                        dataQuality.completeness.status === 'fair' ? 'text-amber-600' :
                        'text-red-600'
                      }`}>
                        {Math.round(dataQuality.completeness.score)}%
                      </span>
                    </div>

                    {dataQuality.completeness.details.map((detail, idx) => (
                      detail.section && (
                        <div key={idx} className="mb-3 pb-3 border-b border-slate-100 last:border-0">
                          <div className="flex justify-between items-center mb-1">
                            <span className="text-sm font-medium text-slate-700">{detail.section}</span>
                            <span className="text-xs text-slate-500">{detail.filled}/{detail.total}</span>
                          </div>
                          <div className="w-full bg-slate-100 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                (detail.percentage || 0) >= 80 ? 'bg-green-500' :
                                (detail.percentage || 0) >= 50 ? 'bg-amber-500' :
                                'bg-red-500'
                              }`}
                              style={{ width: `${detail.percentage}%` }}
                            />
                          </div>
                        </div>
                      )
                    ))}
                  </div>

                  {/* Freshness */}
                  <div className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-slate-900">🕐 Świeżość</h3>
                      <span className={`text-2xl font-bold ${
                        dataQuality.freshness.status === 'excellent' ? 'text-green-600' :
                        dataQuality.freshness.status === 'good' ? 'text-blue-600' :
                        dataQuality.freshness.status === 'fair' ? 'text-amber-600' :
                        'text-red-600'
                      }`}>
                        {Math.round(dataQuality.freshness.score)}%
                      </span>
                    </div>

                    {dataQuality.freshness.details.map((detail, idx) => (
                      detail.source && (
                        <div key={idx} className="mb-3 pb-3 border-b border-slate-100 last:border-0">
                          <div className="flex justify-between items-center mb-1">
                            <span className="text-sm font-medium text-slate-700">{detail.source}</span>
                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                              (detail as any).status === 'fresh' ? 'bg-green-100 text-green-700' :
                              (detail as any).status === 'stale' ? 'bg-amber-100 text-amber-700' :
                              'bg-red-100 text-red-700'
                            }`}>
                              {detail.days_ago} dni temu
                            </span>
                          </div>
                        </div>
                      )
                    ))}
                  </div>

                  {/* Source Reliability */}
                  <div className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-slate-900">🛡️ Wiarygodność</h3>
                      <span className={`text-2xl font-bold ${
                        dataQuality.source_reliability.status === 'excellent' ? 'text-green-600' :
                        dataQuality.source_reliability.status === 'good' ? 'text-blue-600' :
                        dataQuality.source_reliability.status === 'fair' ? 'text-amber-600' :
                        'text-red-600'
                      }`}>
                        {Math.round(dataQuality.source_reliability.score)}%
                      </span>
                    </div>

                    {dataQuality.source_reliability.details.map((detail, idx) => (
                      detail.source && (
                        <div key={idx} className="mb-3 pb-3 border-b border-slate-100 last:border-0">
                          <div className="flex justify-between items-center mb-1">
                            <span className="text-sm font-medium text-slate-700">{detail.source}</span>
                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                              (detail.confidence || 0) >= 90 ? 'bg-green-100 text-green-700' :
                              (detail.confidence || 0) >= 75 ? 'bg-blue-100 text-blue-700' :
                              'bg-amber-100 text-amber-700'
                            }`}>
                              {detail.reliability}
                            </span>
                          </div>
                        </div>
                      )
                    ))}
                  </div>
                </div>

                {/* Improvement Suggestions */}
                {dataQuality.improvement_suggestions.length > 0 && (
                  <div className="bg-white rounded-xl border border-slate-200 p-6">
                    <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
                      💡 Sugestie poprawy
                    </h3>
                    <div className="space-y-4">
                      {dataQuality.improvement_suggestions.map((suggestion, idx) => (
                        <div
                          key={idx}
                          className={`p-4 rounded-lg border-l-4 ${
                            suggestion.priority === 'high' ? 'bg-red-50 border-red-500' :
                            suggestion.priority === 'medium' ? 'bg-amber-50 border-amber-500' :
                            'bg-blue-50 border-blue-500'
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                                  suggestion.priority === 'high' ? 'bg-red-200 text-red-800' :
                                  suggestion.priority === 'medium' ? 'bg-amber-200 text-amber-800' :
                                  'bg-blue-200 text-blue-800'
                                }`}>
                                  {suggestion.priority === 'high' ? '🔴 Wysoki' :
                                   suggestion.priority === 'medium' ? '🟡 Średni' :
                                   '🟢 Niski'} priorytet
                                </span>
                                <span className="text-xs text-slate-500">
                                  {suggestion.category}
                                </span>
                              </div>
                              <h4 className="font-semibold text-slate-900 mb-1">
                                {suggestion.title}
                              </h4>
                              <p className="text-sm text-slate-600 mb-2">
                                {suggestion.description}
                              </p>
                              <p className="text-xs text-slate-500 italic">
                                📈 {suggestion.impact}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Last Assessment */}
                <div className="text-center text-sm text-slate-500">
                  Ostatnia ocena: {new Date(dataQuality.last_assessment).toLocaleString('pl-PL')}
                </div>
              </>
            ) : (
              <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
                <div className="text-4xl mb-4">✓</div>
                <h3 className="text-lg font-semibold text-slate-900">Brak danych</h3>
                <p className="text-slate-600 mt-1">
                  Nie można załadować metryk jakości danych.
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
