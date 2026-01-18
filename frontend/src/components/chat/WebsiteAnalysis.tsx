'use client'

import React from 'react'

export interface WebsiteAnalysisData {
  url: string
  basic_info: {
    title: string
    description: string
    language: string
    status: string
    ssl_enabled: boolean
    mobile_friendly: boolean
  }
  contact_info: {
    email?: string
    phone?: string
    address?: string
    company_name?: string
    nip?: string
  }
  social_media: {
    facebook?: string | null
    linkedin?: string | null
    twitter?: string | null
    instagram?: string | null
    youtube?: string | null
  }
  tech_stack?: {
    cms?: string
    analytics?: string[]
    hosting?: string
    frameworks?: string[]
  }
  content_summary?: {
    page_count?: number
    has_blog?: boolean
    has_products?: boolean
    has_team?: boolean
    has_contact_form?: boolean
    last_updated?: string
  }
  crawled_at: string
  crawl_status: string
}

interface WebsiteAnalysisProps {
  data: WebsiteAnalysisData
}

export function WebsiteAnalysis({ data }: WebsiteAnalysisProps) {
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString('pl-PL', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateString
    }
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">🌐</span>
              <h3 className="text-xl font-semibold text-gray-900">{data.basic_info.title}</h3>
            </div>
            <p className="text-sm text-gray-600 mb-2">{data.basic_info.description}</p>
            <a
              href={data.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-600 hover:text-blue-800 hover:underline break-all"
            >
              {data.url}
            </a>
          </div>
          <div className="flex flex-col gap-2 items-end">
            {data.basic_info.ssl_enabled && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                🔒 SSL
              </span>
            )}
            {data.basic_info.mobile_friendly && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                📱 Mobile
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Contact Information */}
      {data.contact_info && (Object.keys(data.contact_info).some(key => data.contact_info[key as keyof typeof data.contact_info])) && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span>📞</span>
            Informacje kontaktowe
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {data.contact_info.company_name && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">Nazwa firmy</div>
                <div className="text-sm font-medium text-gray-900">{data.contact_info.company_name}</div>
              </div>
            )}
            {data.contact_info.email && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">Email</div>
                <a href={`mailto:${data.contact_info.email}`} className="text-sm font-medium text-blue-600 hover:text-blue-800">
                  {data.contact_info.email}
                </a>
              </div>
            )}
            {data.contact_info.phone && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">Telefon</div>
                <a href={`tel:${data.contact_info.phone}`} className="text-sm font-medium text-blue-600 hover:text-blue-800">
                  {data.contact_info.phone}
                </a>
              </div>
            )}
            {data.contact_info.address && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">Adres</div>
                <div className="text-sm font-medium text-gray-900">{data.contact_info.address}</div>
              </div>
            )}
            {data.contact_info.nip && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">NIP</div>
                <div className="text-sm font-medium text-gray-900">{data.contact_info.nip}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Social Media */}
      {data.social_media && Object.values(data.social_media).some(link => link) && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span>📱</span>
            Media społecznościowe
          </h4>
          <div className="flex flex-wrap gap-2">
            {data.social_media.facebook && (
              <a
                href={data.social_media.facebook}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-3 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors text-sm"
              >
                <span>📘</span>
                Facebook
              </a>
            )}
            {data.social_media.linkedin && (
              <a
                href={data.social_media.linkedin}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-3 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors text-sm"
              >
                <span>💼</span>
                LinkedIn
              </a>
            )}
            {data.social_media.twitter && (
              <a
                href={data.social_media.twitter}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-3 py-2 bg-sky-50 text-sky-700 rounded-lg hover:bg-sky-100 transition-colors text-sm"
              >
                <span>🐦</span>
                Twitter
              </a>
            )}
            {data.social_media.instagram && (
              <a
                href={data.social_media.instagram}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-3 py-2 bg-pink-50 text-pink-700 rounded-lg hover:bg-pink-100 transition-colors text-sm"
              >
                <span>📷</span>
                Instagram
              </a>
            )}
            {data.social_media.youtube && (
              <a
                href={data.social_media.youtube}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-3 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors text-sm"
              >
                <span>🎥</span>
                YouTube
              </a>
            )}
          </div>
        </div>
      )}

      {/* Tech Stack */}
      {data.tech_stack && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span>⚙️</span>
            Stack technologiczny
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {data.tech_stack.cms && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">CMS</div>
                <div className="text-sm font-medium text-gray-900">{data.tech_stack.cms}</div>
              </div>
            )}
            {data.tech_stack.hosting && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">Hosting</div>
                <div className="text-sm font-medium text-gray-900">{data.tech_stack.hosting}</div>
              </div>
            )}
            {data.tech_stack.analytics && data.tech_stack.analytics.length > 0 && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">Analityka</div>
                <div className="text-sm font-medium text-gray-900">{data.tech_stack.analytics.join(', ')}</div>
              </div>
            )}
            {data.tech_stack.frameworks && data.tech_stack.frameworks.length > 0 && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">Frameworks</div>
                <div className="text-sm font-medium text-gray-900">{data.tech_stack.frameworks.join(', ')}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Content Summary */}
      {data.content_summary && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span>📄</span>
            Podsumowanie treści
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {typeof data.content_summary.page_count === 'number' && (
              <div className="bg-gray-50 p-3 rounded text-center">
                <div className="text-2xl font-bold text-gray-900">{data.content_summary.page_count}</div>
                <div className="text-xs text-gray-500 mt-1">Stron</div>
              </div>
            )}
            {data.content_summary.has_blog && (
              <div className="bg-green-50 p-3 rounded text-center">
                <div className="text-2xl">📝</div>
                <div className="text-xs text-gray-700 mt-1">Blog</div>
              </div>
            )}
            {data.content_summary.has_products && (
              <div className="bg-blue-50 p-3 rounded text-center">
                <div className="text-2xl">🛍️</div>
                <div className="text-xs text-gray-700 mt-1">Produkty</div>
              </div>
            )}
            {data.content_summary.has_team && (
              <div className="bg-purple-50 p-3 rounded text-center">
                <div className="text-2xl">👥</div>
                <div className="text-xs text-gray-700 mt-1">Zespół</div>
              </div>
            )}
            {data.content_summary.has_contact_form && (
              <div className="bg-orange-50 p-3 rounded text-center">
                <div className="text-2xl">✉️</div>
                <div className="text-xs text-gray-700 mt-1">Formularz</div>
              </div>
            )}
            {data.content_summary.last_updated && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">Ostatnia aktualizacja</div>
                <div className="text-sm font-medium text-gray-900">{formatDate(data.content_summary.last_updated)}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="border-t border-gray-200 pt-4">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Dane pobrane: {formatDate(data.crawled_at)}</span>
          <span className={`inline-flex items-center px-2 py-1 rounded ${
            data.crawl_status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {data.crawl_status === 'success' ? '✓ Sukces' : '✗ Błąd'}
          </span>
        </div>
      </div>
    </div>
  )
}
