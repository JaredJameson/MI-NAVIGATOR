'use client';

import { useState, useEffect } from 'react';
import { ArrowLeft, Shield, Calendar, User, FileText, Share2, Trash2, Download } from 'lucide-react';
import Link from 'next/link';

interface AuditLog {
  id: string;
  user_id: string;
  user_email: string;
  action_type: string;
  resource_type: string;
  resource_id: string;
  description: string;
  ip_address: string | null;
  user_agent: string | null;
  extra_data: any;
  created_at: string;
}

export default function AuditLogPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  const fetchAuditLogs = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch('http://localhost:8000/api/v1/reports/audit-logs?limit=50', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch audit logs');
      }

      const data = await response.json();
      setLogs(data.logs || []);
    } catch (err) {
      console.error('Error fetching audit logs:', err);
      setError(err instanceof Error ? err.message : 'Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  };

  const getActionIcon = (actionType: string) => {
    if (actionType.includes('delete')) return <Trash2 className="w-4 h-4 text-red-600" />;
    if (actionType.includes('share')) return <Share2 className="w-4 h-4 text-blue-600" />;
    if (actionType.includes('export')) return <Download className="w-4 h-4 text-green-600" />;
    return <FileText className="w-4 h-4 text-gray-600" />;
  };

  const getActionColor = (actionType: string) => {
    if (actionType.includes('delete')) return 'bg-red-50 border-red-200';
    if (actionType.includes('share')) return 'bg-blue-50 border-blue-200';
    if (actionType.includes('export')) return 'bg-green-50 border-green-200';
    return 'bg-gray-50 border-gray-200';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('pl-PL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(date);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <Link href="/settings" className="hover:bg-gray-100 p-2 rounded-lg transition-colors">
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="flex items-center space-x-3">
                <Shield className="w-6 h-6 text-blue-600" />
                <h1 className="text-2xl font-bold text-gray-900">Audit Trail</h1>
              </div>
            </div>

            <nav className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-gray-700 hover:text-gray-900 font-medium">
                Dashboard
              </Link>
              <Link href="/settings" className="text-gray-700 hover:text-gray-900 font-medium">
                Settings
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">Activity Log</h2>
          <p className="text-sm text-gray-600">
            Track all sensitive operations performed on your account, including deletions, shares, and exports.
          </p>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800 font-medium">{error}</p>
          </div>
        )}

        {/* Audit Logs List */}
        {!loading && !error && (
          <div className="space-y-4">
            {logs.length === 0 ? (
              <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 font-medium">No audit logs yet</p>
                <p className="text-sm text-gray-500 mt-2">
                  Sensitive operations will be logged here for tracking and security purposes.
                </p>
              </div>
            ) : (
              logs.map((log) => (
                <div
                  key={log.id}
                  className={`bg-white rounded-lg border p-4 hover:shadow-md transition-shadow ${getActionColor(
                    log.action_type
                  )}`}
                >
                  <div className="flex items-start space-x-4">
                    {/* Action Icon */}
                    <div className="flex-shrink-0 mt-1">
                      {getActionIcon(log.action_type)}
                    </div>

                    {/* Log Details */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-semibold text-gray-900">
                          {log.description}
                        </h3>
                        <span className="text-xs text-gray-500 flex items-center">
                          <Calendar className="w-3 h-3 mr-1" />
                          {formatDate(log.created_at)}
                        </span>
                      </div>

                      <div className="flex items-center space-x-4 text-xs text-gray-600">
                        <span className="flex items-center">
                          <User className="w-3 h-3 mr-1" />
                          {log.user_email}
                        </span>
                        <span className="px-2 py-1 bg-white rounded border border-gray-300">
                          {log.action_type}
                        </span>
                        <span className="text-gray-500">
                          {log.resource_type}: {log.resource_id.substring(0, 8)}...
                        </span>
                      </div>

                      {/* IP Address */}
                      {log.ip_address && (
                        <div className="mt-2 text-xs text-gray-500">
                          IP: {log.ip_address}
                        </div>
                      )}

                      {/* Extra Data */}
                      {log.extra_data && (
                        <details className="mt-2">
                          <summary className="text-xs text-blue-600 cursor-pointer hover:text-blue-800">
                            View Details
                          </summary>
                          <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                            {JSON.stringify(log.extra_data, null, 2)}
                          </pre>
                        </details>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </main>
    </div>
  );
}
