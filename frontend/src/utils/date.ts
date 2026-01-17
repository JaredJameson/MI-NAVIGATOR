/**
 * Date formatting utilities with timezone support
 */

/**
 * Format a date string in the user's timezone
 * @param dateString - ISO date string from backend (UTC)
 * @param userTimezone - IANA timezone identifier (e.g., 'Europe/Warsaw')
 * @param locale - Locale for formatting (default: 'pl-PL')
 * @returns Formatted date string
 */
export function formatDateInTimezone(
  dateString: string,
  userTimezone: string = 'Europe/Warsaw',
  locale: string = 'pl-PL'
): string {
  const date = new Date(dateString);

  return date.toLocaleDateString(locale, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: userTimezone
  });
}

/**
 * Format a date string with full details in the user's timezone
 * @param dateString - ISO date string from backend (UTC)
 * @param userTimezone - IANA timezone identifier
 * @param locale - Locale for formatting (default: 'pl-PL')
 * @returns Formatted date string with seconds
 */
export function formatDateTimeFull(
  dateString: string,
  userTimezone: string = 'Europe/Warsaw',
  locale: string = 'pl-PL'
): string {
  const date = new Date(dateString);

  return date.toLocaleString(locale, {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZone: userTimezone
  });
}

/**
 * Format a date string as relative time (e.g., "2 hours ago")
 * This doesn't need timezone as it calculates difference
 * @param dateString - ISO date string from backend (UTC)
 * @param locale - Locale for formatting (default: 'pl-PL')
 * @returns Relative time string
 */
export function formatRelativeTime(
  dateString: string,
  locale: string = 'pl-PL'
): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) {
    return locale === 'pl-PL' ? 'przed chwilą' : 'just now';
  } else if (diffMin < 60) {
    return locale === 'pl-PL'
      ? `${diffMin} ${diffMin === 1 ? 'minuta' : 'minut'} temu`
      : `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
  } else if (diffHour < 24) {
    return locale === 'pl-PL'
      ? `${diffHour} ${diffHour === 1 ? 'godzina' : diffHour < 5 ? 'godziny' : 'godzin'} temu`
      : `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
  } else if (diffDay < 7) {
    return locale === 'pl-PL'
      ? `${diffDay} ${diffDay === 1 ? 'dzień' : 'dni'} temu`
      : `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;
  } else {
    // Fall back to formatted date for older dates
    return formatDateInTimezone(dateString, 'Europe/Warsaw', locale);
  }
}
