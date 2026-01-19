'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export function useKeyboardShortcuts() {
  const router = useRouter();

  useEffect(() => {
    let keySequence: string[] = [];
    let sequenceTimeout: NodeJS.Timeout;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in an input
      const target = e.target as HTMLElement;
      const isTyping = target.tagName === 'INPUT' ||
                       target.tagName === 'TEXTAREA' ||
                       target.isContentEditable;

      // Navigation shortcuts (g + letter)
      if (!e.ctrlKey && !e.altKey && !e.metaKey && !isTyping) {
        // Clear sequence after 1 second
        clearTimeout(sequenceTimeout);
        sequenceTimeout = setTimeout(() => {
          keySequence = [];
        }, 1000);

        keySequence.push(e.key.toLowerCase());

        // Keep only last 2 keys
        if (keySequence.length > 2) {
          keySequence.shift();
        }

        const sequence = keySequence.join('');

        // Navigation shortcuts
        if (sequence === 'gd') {
          e.preventDefault();
          router.push('/dashboard');
          keySequence = [];
        } else if (sequence === 'gc') {
          e.preventDefault();
          router.push('/chat');
          keySequence = [];
        } else if (sequence === 'gr') {
          e.preventDefault();
          router.push('/reports');
          keySequence = [];
        } else if (sequence === 'gp') {
          e.preventDefault();
          router.push('/projects');
          keySequence = [];
        } else if (sequence === 'gs') {
          e.preventDefault();
          router.push('/settings');
          keySequence = [];
        }
      }

      // Ctrl+K - New Search (Feature #226)
      if ((e.ctrlKey || e.metaKey) && e.key === 'k' && !isTyping) {
        e.preventDefault();
        router.push('/search');
      }

      // Ctrl+N - New Project (Feature #226)
      if ((e.ctrlKey || e.metaKey) && e.key === 'n' && !isTyping) {
        e.preventDefault();
        router.push('/projects/new');
      }

      // Ctrl+/ - Toggle sidebar (placeholder)
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        console.log('Ctrl+/ pressed - Toggle sidebar (not implemented yet)');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      clearTimeout(sequenceTimeout);
    };
  }, [router]);
}
