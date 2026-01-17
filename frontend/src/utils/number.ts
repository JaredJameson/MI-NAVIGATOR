/**
 * Number formatting utilities with locale support
 */

/**
 * Format a number according to user's locale
 * @param value - Number to format
 * @param locale - Locale for formatting (default: 'pl-PL')
 * @param options - Intl.NumberFormat options
 * @returns Formatted number string
 */
export function formatNumber(
  value: number,
  locale: string = 'pl-PL',
  options?: Intl.NumberFormatOptions
): string {
  return new Intl.NumberFormat(locale, options).format(value);
}

/**
 * Format a number as currency
 * @param value - Number to format
 * @param locale - Locale for formatting (default: 'pl-PL')
 * @param currency - Currency code (default: 'PLN')
 * @returns Formatted currency string
 */
export function formatCurrency(
  value: number,
  locale: string = 'pl-PL',
  currency: string = 'PLN'
): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
  }).format(value);
}

/**
 * Format a number as percentage
 * @param value - Number to format (0-100)
 * @param locale - Locale for formatting (default: 'pl-PL')
 * @param decimals - Number of decimal places (default: 0)
 * @returns Formatted percentage string
 */
export function formatPercentage(
  value: number,
  locale: string = 'pl-PL',
  decimals: number = 0
): string {
  return new Intl.NumberFormat(locale, {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value / 100);
}

/**
 * Format a number with specific decimal places
 * @param value - Number to format
 * @param locale - Locale for formatting (default: 'pl-PL')
 * @param decimals - Number of decimal places (default: 2)
 * @returns Formatted number string
 */
export function formatDecimal(
  value: number,
  locale: string = 'pl-PL',
  decimals: number = 2
): string {
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format a large number with compact notation (e.g., 1.2K, 3.4M)
 * @param value - Number to format
 * @param locale - Locale for formatting (default: 'pl-PL')
 * @returns Formatted compact number string
 */
export function formatCompactNumber(
  value: number,
  locale: string = 'pl-PL'
): string {
  return new Intl.NumberFormat(locale, {
    notation: 'compact',
    compactDisplay: 'short',
  }).format(value);
}
