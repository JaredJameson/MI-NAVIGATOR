'use client';

import { useEffect, useState } from 'react';
import { X } from 'lucide-react';

interface Shortcut {
  keys: string[];
  description: string;
  category: string;
}

const shortcuts: Shortcut[] = [
  // Navigation
  { keys: ['g', 'd'], description: 'Go to Dashboard', category: 'Navigation' },
  { keys: ['g', 'c'], description: 'Go to Chat', category: 'Navigation' },
  { keys: ['g', 'r'], description: 'Go to Reports', category: 'Navigation' },
  { keys: ['g', 'p'], description: 'Go to Projects', category: 'Navigation' },
  { keys: ['g', 's'], description: 'Go to Settings', category: 'Navigation' },

  // Actions
  { keys: ['Ctrl', 'K'], description: 'Open command palette / Search', category: 'Actions' },
  { keys: ['Ctrl', 'N'], description: 'New report', category: 'Actions' },
  { keys: ['Ctrl', 'S'], description: 'Save current work', category: 'Actions' },
  { keys: ['Ctrl', '/'], description: 'Toggle sidebar', category: 'Actions' },
  { keys: ['Escape'], description: 'Close modal / Cancel', category: 'Actions' },

  // Chat
  { keys: ['Enter'], description: 'Send message', category: 'Chat' },
  { keys: ['Shift', 'Enter'], description: 'New line', category: 'Chat' },
  { keys: ['/'], description: 'Slash commands', category: 'Chat' },

  // Help
  { keys: ['?'], description: 'Show this help', category: 'Help' },
];

export default function KeyboardShortcutsHelp() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Open help with '?' key (Shift+/)
      if (e.key === '?' && !e.ctrlKey && !e.altKey && !e.metaKey) {
        // Don't trigger if user is typing in an input
        const target = e.target as HTMLElement;
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
          return;
        }
        e.preventDefault();
        setIsOpen(true);
      }

      // Close with Escape
      if (e.key === 'Escape' && isOpen) {
        e.preventDefault();
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  if (!isOpen) return null;

  // Group shortcuts by category
  const groupedShortcuts = shortcuts.reduce((acc, shortcut) => {
    if (!acc[shortcut.category]) {
      acc[shortcut.category] = [];
    }
    acc[shortcut.category].push(shortcut);
    return acc;
  }, {} as Record<string, Shortcut[]>);

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={() => setIsOpen(false)}
    >
      <div
        className="bg-white rounded-lg shadow-2xl max-w-3xl w-full max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Keyboard Shortcuts</h2>
          <button
            onClick={() => setIsOpen(false)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-4">
          {Object.entries(groupedShortcuts).map(([category, categoryShortcuts]) => (
            <div key={category} className="mb-6 last:mb-0">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
                {category}
              </h3>
              <div className="space-y-2">
                {categoryShortcuts.map((shortcut, index) => (
                  <div
                    key={index}
                    className="flex justify-between items-center py-2 px-3 hover:bg-gray-50 rounded-lg transition-colors"
                  >
                    <span className="text-gray-700">{shortcut.description}</span>
                    <div className="flex gap-1">
                      {shortcut.keys.map((key, keyIndex) => (
                        <kbd
                          key={keyIndex}
                          className="px-3 py-1.5 bg-gray-100 border border-gray-300 rounded text-sm font-mono text-gray-800 shadow-sm"
                        >
                          {key}
                        </kbd>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4">
          <p className="text-sm text-gray-600 text-center">
            Press <kbd className="px-2 py-1 bg-white border border-gray-300 rounded text-xs font-mono">?</kbd> anytime to show this help
          </p>
        </div>
      </div>
    </div>
  );
}
