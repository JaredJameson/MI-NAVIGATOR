'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

interface Conversation {
  id: string
  title: string | null
  messages: Message[]
  created_at: string
  updated_at: string
}

export default function ChatPage() {
  const router = useRouter()
  const [conversation, setConversation] = useState<Conversation | null>(null)
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [conversation?.messages])

  const createConversation = async (): Promise<Conversation | null> => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return null
    }

    try {
      const response = await fetch(`${API_BASE_URL}/chat/conversations`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error('Failed to create conversation')
      }

      const conv = await response.json()
      setConversation(conv)
      return conv
    } catch (err) {
      setError('Failed to start conversation')
      return null
    }
  }

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setError('')
    setIsLoading(true)

    try {
      // Create conversation if needed
      let conv = conversation
      if (!conv) {
        conv = await createConversation()
        if (!conv) return
      }

      // Add user message optimistically
      const userMessage: Message = {
        id: `temp-${Date.now()}`,
        role: 'user',
        content: inputValue,
        created_at: new Date().toISOString(),
      }

      setConversation(prev => prev ? {
        ...prev,
        messages: [...prev.messages, userMessage],
      } : null)

      setInputValue('')

      // Send to API
      const response = await fetch(
        `${API_BASE_URL}/chat/conversations/${conv.id}/messages`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content: inputValue }),
        }
      )

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const aiResponse = await response.json()

      // Update with AI response
      setConversation(prev => {
        if (!prev) return null
        // Remove temp message and add both user and AI messages
        const messages = prev.messages.filter(m => !m.id.startsWith('temp-'))
        return {
          ...prev,
          messages: [
            ...messages,
            { ...userMessage, id: `user-${Date.now()}` },
            aiResponse,
          ],
        }
      })

    } catch (err) {
      setError('Failed to send message. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white px-4 py-3">
        <div className="mx-auto flex max-w-4xl items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </Link>
            <h1 className="text-lg font-semibold text-gray-900">
              {conversation?.title || 'New Research'}
            </h1>
          </div>
          <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">
            New Chat
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-4xl px-4 py-6">
          {conversation?.messages.length === 0 || !conversation ? (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="mb-6 rounded-full bg-blue-100 p-4">
                <svg className="h-12 w-12 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h2 className="mb-2 text-xl font-semibold text-gray-900">Start Your Research</h2>
              <p className="mb-6 max-w-md text-center text-gray-600">
                Ask me about any company, market, or business topic. I can analyze companies,
                generate reports, and provide market intelligence.
              </p>
              <div className="grid gap-3 sm:grid-cols-2">
                {[
                  'Analyze company FADO Sp. z o.o.',
                  'Generate Due Diligence report',
                  'Compare competitors in logistics',
                  'Market trends in e-commerce',
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setInputValue(suggestion)}
                    className="rounded-lg border bg-white px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {conversation.messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white shadow-sm border'
                    }`}
                  >
                    <div className="whitespace-pre-wrap text-sm">
                      {message.content}
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] rounded-2xl bg-white px-4 py-3 shadow-sm border">
                    <div className="flex items-center gap-2 text-gray-500">
                      <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400" style={{ animationDelay: '0ms' }}></div>
                      <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400" style={{ animationDelay: '150ms' }}></div>
                      <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="mx-auto max-w-4xl px-4">
          <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600">
            {error}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="border-t bg-white px-4 py-4">
        <div className="mx-auto max-w-4xl">
          <div className="flex gap-3">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about a company, request analysis, or generate a report..."
              rows={1}
              className="flex-1 resize-none rounded-xl border bg-gray-50 px-4 py-3 text-sm focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <button
              onClick={sendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="rounded-xl bg-blue-600 px-6 py-3 text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
          <p className="mt-2 text-center text-xs text-gray-400">
            MI-Navigator uses AI to analyze markets and companies. Results may vary.
          </p>
        </div>
      </div>
    </div>
  )
}
