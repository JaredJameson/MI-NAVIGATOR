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
}

// Generic fetch wrapper
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
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

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

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

  async login(email: string, password: string): Promise<ApiResponse<TokenResponse>> {
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

    const data: TokenResponse = await response.json();

    // Store tokens
    setTokens(data.access_token, data.refresh_token);

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

export default fetchApi;
