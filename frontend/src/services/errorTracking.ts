/**
 * Error tracking service for logging errors to the backend.
 */

interface ErrorLog {
  error_type: string;
  error_message: string;
  stack_trace?: string;
  url?: string;
  metadata?: Record<string, any>;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Log an error to the backend error tracking system.
 */
export async function logError(error: Error, metadata?: Record<string, any>): Promise<void> {
  try {
    const errorLog: ErrorLog = {
      error_type: error.name || 'Error',
      error_message: error.message,
      stack_trace: error.stack,
      url: typeof window !== 'undefined' ? window.location.href : undefined,
      metadata: {
        ...metadata,
        userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : undefined,
        timestamp: new Date().toISOString(),
      }
    };

    await fetch(`${API_BASE_URL}/errors/log`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(errorLog),
    });

    // Don't throw if error logging fails - we don't want to create an error loop
  } catch (e) {
    console.error('Failed to log error to backend:', e);
  }
}

/**
 * Set up global error handlers to catch unhandled errors.
 */
export function setupGlobalErrorHandlers(): void {
  if (typeof window === 'undefined') return;

  // Catch unhandled JavaScript errors
  window.addEventListener('error', (event) => {
    logError(event.error || new Error(event.message), {
      type: 'unhandled_error',
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
    });
  });

  // Catch unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    const error = event.reason instanceof Error
      ? event.reason
      : new Error(String(event.reason));

    logError(error, {
      type: 'unhandled_rejection',
    });
  });
}
