'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface ScheduleConfig {
  company_id: string;
  company_name: string;
  frequency: string;
  time: string;
  enabled: boolean;
  last_run: string | null;
  next_run: string | null;
}

interface ScheduleNotification {
  id: string;
  type: string;
  company_id: string;
  company_name: string;
  message: string;
  timestamp: string;
  read: boolean;
}

export default function SchedulesPage() {
  const [schedules, setSchedules] = useState<ScheduleConfig[]>([]);
  const [notifications, setNotifications] = useState<ScheduleNotification[]>([]);
  const [loading, setLoading] = useState(true);
  const [showConfigureForm, setShowConfigureForm] = useState(false);

  // Form state
  const [companyId, setCompanyId] = useState('1');
  const [frequency, setFrequency] = useState('daily');
  const [time, setTime] = useState('09:00');
  const [configureMessage, setConfigureMessage] = useState<string | null>(null);

  // Load all schedules
  const loadSchedules = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/companies/schedules/all');
      const data = await response.json();
      setSchedules(data.schedules || []);
    } catch (error) {
      console.error('Failed to load schedules:', error);
    }
  };

  // Load notifications
  const loadNotifications = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/companies/schedules/notifications');
      const data = await response.json();
      setNotifications(data.notifications || []);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  };

  // Initial load
  useEffect(() => {
    const load = async () => {
      setLoading(true);
      await Promise.all([loadSchedules(), loadNotifications()]);
      setLoading(false);
    };
    load();

    // Reload every 15 seconds
    const interval = setInterval(() => {
      loadSchedules();
      loadNotifications();
    }, 15000);

    return () => clearInterval(interval);
  }, []);

  // Configure schedule
  const handleConfigure = async (e: React.FormEvent) => {
    e.preventDefault();
    setConfigureMessage(null);

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/companies/${companyId}/schedule?frequency=${frequency}&time=${time}&enabled=true`,
        { method: 'POST' }
      );
      const data = await response.json();

      if (data.success) {
        setConfigureMessage(`✅ ${data.message}`);
        setShowConfigureForm(false);
        await loadSchedules();
      } else {
        setConfigureMessage(`❌ Błąd: ${data.message}`);
      }
    } catch (error) {
      setConfigureMessage('❌ Błąd połączenia z serwerem');
    }
  };

  // Delete schedule
  const handleDelete = async (companyId: string, companyName: string) => {
    if (!confirm(`Czy na pewno usunąć harmonogram dla ${companyName}?`)) return;

    try {
      const response = await fetch(`http://localhost:8000/api/v1/companies/${companyId}/schedule`, {
        method: 'DELETE',
      });
      const data = await response.json();

      if (data.success) {
        alert(`✅ ${data.message}`);
        await loadSchedules();
      }
    } catch (error) {
      alert('❌ Błąd usuwania harmonogramu');
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Nigdy';
    const date = new Date(dateStr);
    return date.toLocaleString('pl-PL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getFrequencyLabel = (freq: string) => {
    const labels: Record<string, string> = {
      daily: 'Codziennie',
      weekly: 'Co tydzień',
      monthly: 'Co miesiąc',
    };
    return labels[freq] || freq;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="mt-4 text-gray-600">Ładowanie harmonogramów...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Harmonogramy automatycznych aktualizacji
              </h1>
              <p className="mt-2 text-gray-600">
                Konfiguruj automatyczne odświeżanie danych firmowych
              </p>
            </div>
            <Link
              href="/dashboard"
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
            >
              ← Dashboard
            </Link>
          </div>
        </div>

        {/* Configure message */}
        {configureMessage && (
          <div className={`mb-6 p-4 rounded-lg ${configureMessage.startsWith('✅') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {configureMessage}
          </div>
        )}

        {/* Configure button */}
        <div className="mb-6">
          <button
            onClick={() => setShowConfigureForm(!showConfigureForm)}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            {showConfigureForm ? '❌ Anuluj' : '➕ Dodaj nowy harmonogram'}
          </button>
        </div>

        {/* Configure form */}
        {showConfigureForm && (
          <div className="mb-8 bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold mb-4">Nowy harmonogram</h2>
            <form onSubmit={handleConfigure} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Firma
                </label>
                <select
                  value={companyId}
                  onChange={(e) => setCompanyId(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="1">FADO Sp. z o.o.</option>
                  <option value="2">Splast S.A.</option>
                  <option value="3">PlastPak Sp. z o.o.</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Częstotliwość
                </label>
                <select
                  value={frequency}
                  onChange={(e) => setFrequency(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="daily">Codziennie</option>
                  <option value="weekly">Co tydzień</option>
                  <option value="monthly">Co miesiąc</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Godzina (HH:MM)
                </label>
                <input
                  type="time"
                  value={time}
                  onChange={(e) => setTime(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <button
                type="submit"
                className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
              >
                ✅ Zapisz harmonogram
              </button>
            </form>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Schedules list */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Skonfigurowane harmonogramy ({schedules.length})
            </h2>

            {schedules.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
                Brak skonfigurowanych harmonogramów
              </div>
            ) : (
              <div className="space-y-4">
                {schedules.map((schedule) => (
                  <div
                    key={schedule.company_id}
                    className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-bold text-gray-900">
                          {schedule.company_name}
                        </h3>
                        <p className="text-sm text-gray-600">ID: {schedule.company_id}</p>
                      </div>
                      <button
                        onClick={() =>
                          handleDelete(schedule.company_id, schedule.company_name)
                        }
                        className="text-red-600 hover:text-red-800 text-sm font-medium"
                      >
                        🗑️ Usuń
                      </button>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-700">
                          Częstotliwość:
                        </span>
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm font-medium">
                          {getFrequencyLabel(schedule.frequency)}
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-700">
                          Godzina:
                        </span>
                        <span className="text-sm text-gray-900">{schedule.time}</span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-700">
                          Status:
                        </span>
                        <span
                          className={`px-2 py-1 rounded text-sm font-medium ${
                            schedule.enabled
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {schedule.enabled ? '✅ Aktywny' : '⏸️ Wyłączony'}
                        </span>
                      </div>

                      <div className="pt-2 border-t border-gray-200 mt-3">
                        <div className="text-sm text-gray-600">
                          <strong>Ostatnia aktualizacja:</strong>{' '}
                          {formatDate(schedule.last_run)}
                        </div>
                        <div className="text-sm text-gray-600">
                          <strong>Następna aktualizacja:</strong>{' '}
                          {formatDate(schedule.next_run)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Notifications */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Powiadomienia ({notifications.filter((n) => !n.read).length} nowych)
            </h2>

            {notifications.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
                Brak powiadomień
              </div>
            ) : (
              <div className="space-y-3">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`bg-white rounded-lg shadow-md p-4 border-l-4 ${
                      notification.read
                        ? 'border-gray-300 opacity-60'
                        : 'border-green-500'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          {notification.message}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {formatDate(notification.timestamp)}
                        </p>
                      </div>
                      {!notification.read && (
                        <span className="inline-block w-2 h-2 bg-green-500 rounded-full"></span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
