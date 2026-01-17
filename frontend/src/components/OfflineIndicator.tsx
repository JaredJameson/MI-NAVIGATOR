'use client';

import { useOnlineStatus } from '@/hooks/useOnlineStatus';
import { useEffect, useState } from 'react';

export function OfflineIndicator() {
  const isOnline = useOnlineStatus();
  const [showIndicator, setShowIndicator] = useState(false);

  useEffect(() => {
    if (!isOnline) {
      // Show offline indicator
      setShowIndicator(true);
    } else {
      // Hide offline indicator after a short delay when back online
      const timeout = setTimeout(() => {
        setShowIndicator(false);
      }, 500);
      return () => clearTimeout(timeout);
    }
  }, [isOnline]);

  if (!showIndicator) {
    return null;
  }

  return (
    <div
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isOnline ? 'translate-y-0' : 'translate-y-0'
      }`}
      role="alert"
      aria-live="assertive"
    >
      {!isOnline ? (
        // Offline banner (red)
        <div className="bg-red-600 text-white px-4 py-3 shadow-lg">
          <div className="container mx-auto flex items-center justify-center gap-3">
            <svg
              className="w-5 h-5 animate-pulse"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414"
              />
            </svg>
            <span className="font-medium">
              Brak połączenia z internetem. Niektóre funkcje mogą być niedostępne.
            </span>
          </div>
        </div>
      ) : (
        // Back online banner (green) - shows briefly then fades
        <div className="bg-green-600 text-white px-4 py-3 shadow-lg animate-fadeIn">
          <div className="container mx-auto flex items-center justify-center gap-3">
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            <span className="font-medium">Połączenie przywrócone</span>
          </div>
        </div>
      )}
    </div>
  );
}
