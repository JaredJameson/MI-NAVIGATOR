/**
 * Hook to access user's timezone preference
 */

import { useState, useEffect } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface UserPreferences {
  preferred_language: string;
  preferred_depth: string;
  preferred_format: string;
  timezone: string;
}

/**
 * Hook to get user's timezone setting
 * @returns User's timezone (defaults to 'Europe/Warsaw')
 */
export function useUserTimezone(): string {
  const [timezone, setTimezone] = useState<string>('Europe/Warsaw');

  useEffect(() => {
    const fetchTimezone = async () => {
      try {
        const token = localStorage.getItem('mi_navigator_token');
        if (!token) {
          return;
        }

        const response = await fetch(`${API_BASE_URL}/users/me/preferences`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const prefs: UserPreferences = await response.json();
          setTimezone(prefs.timezone || 'Europe/Warsaw');
        }
      } catch (error) {
        console.error('Failed to fetch user timezone:', error);
        // Keep default timezone
      }
    };

    fetchTimezone();
  }, []);

  return timezone;
}

/**
 * Hook to get user's locale setting
 * @returns User's locale (defaults to 'pl-PL')
 */
export function useUserLocale(): string {
  const [locale, setLocale] = useState<string>('pl-PL');

  useEffect(() => {
    const fetchLocale = async () => {
      try {
        const token = localStorage.getItem('mi_navigator_token');
        if (!token) {
          return;
        }

        const response = await fetch(`${API_BASE_URL}/users/me/preferences`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const prefs: UserPreferences = await response.json();
          const lang = prefs.preferred_language || 'pl';
          setLocale(lang === 'en' ? 'en-US' : 'pl-PL');
        }
      } catch (error) {
        console.error('Failed to fetch user locale:', error);
        // Keep default locale
      }
    };

    fetchLocale();
  }, []);

  return locale;
}
