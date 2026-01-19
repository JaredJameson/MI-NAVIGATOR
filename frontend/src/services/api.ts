/**
 * API Service - Base HTTP client for backend communication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Token storage
const TOKEN_KEY = 'mi_navigator_token';
const REFRESH_TOKEN_KEY = 'mi_navigator_refresh_token';
const CSRF_TOKEN_KEY = 'mi_navigator_csrf_token';

export function getStoredToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setTokens(accessToken: string, refreshToken: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearTokens(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(CSRF_TOKEN_KEY);
}

// CSRF Token management
export function getCsrfToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(CSRF_TOKEN_KEY);
}

export function setCsrfToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(CSRF_TOKEN_KEY, token);
}

export async function fetchCsrfToken(): Promise<string | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/csrf-token`);
    if (!response.ok) return null;

    const data = await response.json();
    if (data.csrf_token) {
      setCsrfToken(data.csrf_token);
      return data.csrf_token;
    }
    return null;
  } catch {
    return null;
  }
}

// Flag to prevent infinite refresh loops
let isRefreshing = false;
let refreshPromise: Promise<ApiResponse<TokenResponse>> | null = null;

// Generic fetch wrapper with automatic token refresh on 401
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {},
  retryCount = 0
): Promise<ApiResponse<T>> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add auth token if available
  const token = getStoredToken();
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  // Add CSRF token for non-safe methods
  if (options.method && !['GET', 'HEAD', 'OPTIONS'].includes(options.method.toUpperCase())) {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      (headers as Record<string, string>)['X-CSRF-Token'] = csrfToken;
    }
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle 503 Service Unavailable - maintenance mode
    if (response.status === 503) {
      // Check if we're already on the maintenance page to avoid redirect loop
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/maintenance')) {
        window.location.href = '/maintenance';
      }
      return { error: 'System is under maintenance' };
    }

    // Handle 401 Unauthorized - token expired
    if (response.status === 401 && retryCount === 0) {
      // Don't try to refresh if we're already on the auth endpoints
      if (endpoint.includes('/auth/')) {
        const errorData = await response.json().catch(() => ({}));
        return {
          error: errorData.detail || 'Authentication failed',
        };
      }

      // Wait for ongoing refresh or start new one
      if (isRefreshing && refreshPromise) {
        await refreshPromise;
      } else {
        isRefreshing = true;
        refreshPromise = authApi.refreshToken();
        const refreshResult = await refreshPromise;
        isRefreshing = false;
        refreshPromise = null;

        if (refreshResult.error) {
          // Refresh failed - clear tokens and redirect to login
          clearTokens();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          return { error: 'Session expired. Please login again.' };
        }
      }

      // Retry the original request with new token
      return fetchApi<T>(endpoint, options, retryCount + 1);
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return {
        error: errorData.detail || `HTTP error! status: ${response.status}`,
      };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
}

// Auth API
export const authApi = {
  async register(email: string, password: string, confirmPassword: string, name?: string): Promise<ApiResponse<any>> {
    return fetchApi('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        confirm_password: confirmPassword,
        name,
      }),
    });
  },

  async login(email: string, password: string): Promise<ApiResponse<TokenResponse | any>> {
    // OAuth2 form data format
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return {
        error: errorData.detail || 'Login failed',
      };
    }

    const data: any = await response.json();

    // Check if 2FA is required
    if (data.requires_2fa) {
      // Return 2FA response without storing tokens
      return { data };
    }

    // Normal login - store tokens
    setTokens(data.access_token, data.refresh_token);

    // Fetch CSRF token after successful login
    await fetchCsrfToken();

    return { data };
  },

  async logout(): Promise<ApiResponse<{ message: string }>> {
    const result = await fetchApi<{ message: string }>('/auth/logout', {
      method: 'POST',
    });

    // Clear tokens regardless of API result
    clearTokens();

    return result;
  },

  async getCurrentUser(): Promise<ApiResponse<any>> {
    return fetchApi('/auth/me');
  },

  async refreshToken(): Promise<ApiResponse<TokenResponse>> {
    const refreshToken = getStoredRefreshToken();
    if (!refreshToken) {
      return { error: 'No refresh token' };
    }

    const response = await fetch(`${API_BASE_URL}/auth/refresh?refresh_token=${encodeURIComponent(refreshToken)}`, {
      method: 'POST',
    });

    if (!response.ok) {
      clearTokens();
      return { error: 'Token refresh failed' };
    }

    const data: TokenResponse = await response.json();
    setTokens(data.access_token, data.refresh_token);

    return { data };
  },

  async forgotPassword(email: string): Promise<ApiResponse<{ message: string }>> {
    return fetchApi('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  async resetPassword(token: string, password: string, confirmPassword: string): Promise<ApiResponse<{ message: string }>> {
    return fetchApi('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({
        token,
        password,
        confirm_password: confirmPassword,
      }),
    });
  },
};

// Search API
export interface SearchSuggestion {
  id: string;
  name: string;
  type: 'company' | 'report' | 'person' | 'pkd';
  subtitle?: string;
  url: string;
}

export interface SuggestionsResponse {
  suggestions: SearchSuggestion[];
  query: string;
}

export const searchApi = {
  async getSuggestions(query: string, limit: number = 8): Promise<ApiResponse<SuggestionsResponse>> {
    return fetchApi(`/search/suggestions?q=${encodeURIComponent(query)}&limit=${limit}`);
  },
};

// Company API
export interface CompanyAddress {
  city: string;
  street: string;
  postal_code: string;
}

export interface PKDDescription {
  code: string;
  name: string;
  category: string;
}

export interface CompanyProfile {
  id: string;
  name: string;
  nip: string;
  krs: string;
  regon: string;
  address: CompanyAddress;
  pkd_codes: string[];
  pkd_descriptions: PKDDescription[];
  status: string;
  founded: string;
  description?: string;
  website?: string;
  employees_range?: string;
  last_updated?: string;  // ISO timestamp of last data refresh
}

export interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  source: string;
  source_url: string;
  published_at: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  category: 'general' | 'financial' | 'product' | 'hr' | 'legal';
}

export interface CompanyNews {
  company_id: string;
  company_name: string;
  news: NewsArticle[];
  total_count: number;
}

export interface NewsFilterOptions {
  limit?: number;
  category?: string;
  sentiment?: string;  // positive, negative, neutral
  dateFrom?: string;  // ISO format YYYY-MM-DD
  dateTo?: string;    // ISO format YYYY-MM-DD
}

export interface TimelineEvent {
  id: string;
  date: string;  // ISO format date
  title: string;
  description: string;
  event_type: 'founding' | 'investment' | 'partnership' | 'product' | 'legal' | 'hr' | 'milestone';
  impact: 'high' | 'medium' | 'low';
  source?: string;
  source_url?: string;
}

export interface CompanyTimeline {
  company_id: string;
  company_name: string;
  events: TimelineEvent[];
  total_count: number;
}

export interface TimelineFilterOptions {
  event_type?: string;
  impact?: string;
  year_from?: number;
  year_to?: number;
}

export interface RefreshResponse {
  success: boolean;
  message: string;
  last_updated: string;
  company_id: string;
}

export interface DataQualityMetric {
  score: number;  // 0-100
  status: 'excellent' | 'good' | 'fair' | 'poor';
  details: Array<{
    section?: string;
    filled?: number;
    total?: number;
    percentage?: number;
    fields?: Record<string, boolean>;
    source?: string;
    last_updated?: string;
    days_ago?: number;
    reliability?: string;
    confidence?: number;
    last_verification?: string;
  }>;
}

export interface DataQualityDashboard {
  company_id: string;
  company_name: string;
  overall_score: number;  // 0-100
  overall_status: 'excellent' | 'good' | 'fair' | 'poor';
  completeness: DataQualityMetric;
  freshness: DataQualityMetric;
  source_reliability: DataQualityMetric;
  improvement_suggestions: Array<{
    priority: 'high' | 'medium' | 'low';
    category: string;
    title: string;
    description: string;
    impact: string;
  }>;
  last_assessment: string;  // ISO timestamp
}

export const companyApi = {
  async getCompany(identifier: string): Promise<ApiResponse<CompanyProfile>> {
    return fetchApi(`/companies/${encodeURIComponent(identifier)}`);
  },

  async getCompanyNews(identifier: string, options: NewsFilterOptions = {}): Promise<ApiResponse<CompanyNews>> {
    const { limit = 10, category, sentiment, dateFrom, dateTo } = options;
    let url = `/companies/${encodeURIComponent(identifier)}/news?limit=${limit}`;
    if (category) {
      url += `&category=${encodeURIComponent(category)}`;
    }
    if (sentiment) {
      url += `&sentiment=${encodeURIComponent(sentiment)}`;
    }
    if (dateFrom) {
      url += `&date_from=${encodeURIComponent(dateFrom)}`;
    }
    if (dateTo) {
      url += `&date_to=${encodeURIComponent(dateTo)}`;
    }
    return fetchApi(url);
  },

  async getCompanyTimeline(identifier: string, options: TimelineFilterOptions = {}): Promise<ApiResponse<CompanyTimeline>> {
    const { event_type, impact, year_from, year_to } = options;
    let url = `/companies/${encodeURIComponent(identifier)}/timeline?`;
    const params = [];
    if (event_type) params.push(`event_type=${encodeURIComponent(event_type)}`);
    if (impact) params.push(`impact=${encodeURIComponent(impact)}`);
    if (year_from) params.push(`year_from=${year_from}`);
    if (year_to) params.push(`year_to=${year_to}`);
    url += params.join('&');
    return fetchApi(url);
  },

  async refreshCompanyData(identifier: string): Promise<ApiResponse<RefreshResponse>> {
    return fetchApi(`/companies/${encodeURIComponent(identifier)}/refresh`, {
      method: 'POST',
    });
  },

  async getDataQuality(identifier: string): Promise<ApiResponse<DataQualityDashboard>> {
    return fetchApi(`/companies/${encodeURIComponent(identifier)}/data-quality`);
  },

  async checkWatchlistStatus(identifier: string): Promise<ApiResponse<{is_watched: boolean}>> {
    return fetchApi(`/companies/${encodeURIComponent(identifier)}/watchlist`);
  },

  async addToWatchlist(identifier: string): Promise<ApiResponse<{message: string, is_watched: boolean}>> {
    return fetchApi(`/companies/${encodeURIComponent(identifier)}/watchlist`, {
      method: 'POST',
    });
  },

  async removeFromWatchlist(identifier: string): Promise<ApiResponse<{message: string, is_watched: boolean}>> {
    return fetchApi(`/companies/${encodeURIComponent(identifier)}/watchlist`, {
      method: 'DELETE',
    });
  },

  async getWatchlist(): Promise<ApiResponse<{watchlist: string[], count: number}>> {
    return fetchApi('/companies/watchlist');
  },
};

// Custom Fields API Types
export interface CustomFieldDefinition {
  id: string;
  name: string;
  field_type: string;
  description: string | null;
  is_required: boolean;
  is_active: boolean;
  options: string[] | null;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface CustomFieldValue {
  id: string;
  field_definition_id: string;
  company_id: string;
  value: string | null;
  value_json: any | null;
  created_at: string;
  updated_at: string;
}

export interface CompanyCustomField {
  field_definition: CustomFieldDefinition;
  value: string | null;
  value_json: any | null;
}

export interface SetCustomFieldValueRequest {
  field_definition_id: string;
  value: string | null;
  value_json: any | null;
}

export const customFieldsApi = {
  async getDefinitions(): Promise<ApiResponse<CustomFieldDefinition[]>> {
    return fetchApi('/custom-fields/definitions');
  },

  async getCompanyFieldValues(companyId: string): Promise<ApiResponse<CompanyCustomField[]>> {
    return fetchApi(`/custom-fields/values/${encodeURIComponent(companyId)}`);
  },

  async setFieldValue(
    companyId: string,
    data: SetCustomFieldValueRequest
  ): Promise<ApiResponse<CustomFieldValue>> {
    return fetchApi(`/custom-fields/values/${encodeURIComponent(companyId)}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

export default fetchApi;
