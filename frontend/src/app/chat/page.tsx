'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1'

const getCsrfToken = async (): Promise<string | null> => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/csrf-token`)
    if (response.ok) {
      const data = await response.json()
      return data.csrf_token
    }
  } catch (err) {
    console.error('Failed to get CSRF token:', err)
  }
  return null
}

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
  const searchParams = useSearchParams()
  const [conversation, setConversation] = useState<Conversation | null>(null)
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [wsConnected, setWsConnected] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [conversation?.messages])

  const connectWebSocket = (conversationId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('[WS] Already connected')
      return
    }

    const token = getStoredToken()
    const wsUrl = `${WS_BASE_URL}/chat/ws/${conversationId}${token ? `?token=${token}` : ''}`
    console.log('[WS] Connecting to:', wsUrl.replace(/token=[^&]+/, 'token=***'))

    try {
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('[WS] Connected')
        setWsConnected(true)
        setError('')
      }

      ws.onmessage = (event) => {
        console.log('[WS] Message received:', event.data)
        const aiMessage: Message = {
          id: `ai-${Date.now()}`,
          role: 'assistant',
          content: event.data,
          created_at: new Date().toISOString(),
        }

        setConversation(prev => prev ? {
          ...prev,
          messages: [...prev.messages, aiMessage],
        } : null)

        setIsLoading(false)
      }

      ws.onerror = (error) => {
        console.error('[WS] Error:', error)
        setError('WebSocket connection error')
        setWsConnected(false)
      }

      ws.onclose = () => {
        console.log('[WS] Disconnected')
        setWsConnected(false)

        // Auto-reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('[WS] Attempting reconnect...')
          connectWebSocket(conversationId)
        }, 3000)
      }

      wsRef.current = ws
    } catch (err) {
      console.error('[WS] Connection failed:', err)
      setError('Failed to connect to chat')
      setWsConnected(false)
    }
  }

  const disconnectWebSocket = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setWsConnected(false)
  }

  useEffect(() => {
    if (conversation?.id) {
      connectWebSocket(conversation.id)
    }

    return () => {
      disconnectWebSocket()
    }
  }, [conversation?.id])

  const createConversation = async (): Promise<Conversation | null> => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return null
    }

    try {
      const csrfToken = await getCsrfToken()
      if (!csrfToken) {
        throw new Error('Failed to get CSRF token')
      }

      const response = await fetch(`${API_BASE_URL}/chat/conversations`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to create conversation')
      }

      const conv = await response.json()
      setConversation(conv)
      // Update URL with conversation ID for persistence
      router.push(`/chat?conversation_id=${conv.id}`, { scroll: false })
      return conv
    } catch (err) {
      setError('Failed to start conversation')
      return null
    }
  }

  const loadConversation = async (conversationId: string): Promise<void> => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    try {
      setIsLoading(true)
      const response = await fetch(`${API_BASE_URL}/chat/conversations/${conversationId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to load conversation')
      }

      const conv = await response.json()
      setConversation(conv)
      setError('')
    } catch (err) {
      setError('Failed to load conversation history')
      console.error('Load conversation error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  // Load conversation from URL parameter on mount
  useEffect(() => {
    const conversationId = searchParams.get('conversation_id')
    if (conversationId) {
      // Load conversation if URL has conversation_id and it's different from current
      if (!conversation || conversation.id !== conversationId) {
        console.log('[Chat] Loading conversation:', conversationId)
        loadConversation(conversationId)
      }
    }
  }, [searchParams]) // Re-run when URL changes

  // Helper function to wait for WebSocket connection
  const waitForWebSocketConnection = (maxWait = 5000): Promise<boolean> => {
    return new Promise((resolve) => {
      const startTime = Date.now()

      const checkConnection = () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          resolve(true)
          return
        }

        if (Date.now() - startTime > maxWait) {
          resolve(false)
          return
        }

        setTimeout(checkConnection, 100)
      }

      checkConnection()
    })
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

      // Wait for WebSocket connection (up to 5 seconds)
      console.log('[WS] Waiting for connection...')
      const isConnected = await waitForWebSocketConnection(5000)

      if (!isConnected || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        throw new Error('WebSocket connection timeout')
      }

      console.log('[WS] Connection ready')

      // Add user message optimistically
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: inputValue,
        created_at: new Date().toISOString(),
      }

      setConversation(prev => prev ? {
        ...prev,
        messages: [...prev.messages, userMessage],
      } : null)

      // Send via WebSocket
      console.log('[WS] Sending message:', inputValue)
      wsRef.current.send(inputValue)

      setInputValue('')

    } catch (err) {
      console.error('[WS] Send error:', err)
      setError('Failed to send message. Please try again.')
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    const validFiles: File[] = []
    const maxSize = 50 * 1024 * 1024 // 50MB
    const supportedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv', 'image/png', 'image/jpeg']

    Array.from(files).forEach(file => {
      if (file.size > maxSize) {
        setError(`File ${file.name} is too large. Max size is 50MB.`)
        return
      }

      if (!supportedTypes.includes(file.type)) {
        setError(`File type ${file.type} is not supported.`)
        return
      }

      validFiles.push(file)
    })

    setUploadedFiles(prev => [...prev, ...validFiles])
    setError('')

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-white px-4 py-3">
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
            {/* WebSocket Status Indicator */}
            {conversation && (
              <div className="flex items-center gap-2">
                <div className={`h-2 w-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-500">
                  {wsConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            )}
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
          {/* Uploaded Files Preview */}
          {uploadedFiles.length > 0 && (
            <div className="mb-3 flex flex-wrap gap-2">
              {uploadedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 rounded-lg border bg-gray-50 px-3 py-2"
                >
                  <svg className="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span className="text-sm text-gray-700">{file.name}</span>
                  <span className="text-xs text-gray-400">({(file.size / 1024).toFixed(0)} KB)</span>
                  <button
                    onClick={() => removeFile(index)}
                    className="ml-2 text-gray-400 hover:text-red-500"
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-3">
            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileSelect}
              accept=".pdf,.docx,.xlsx,.csv,.png,.jpg,.jpeg"
              multiple
              className="hidden"
            />

            {/* File upload button */}
            <button
              onClick={() => fileInputRef.current?.click()}
              className="rounded-xl border border-gray-300 px-4 py-3 text-gray-600 transition-colors hover:bg-gray-50"
              title="Upload file (PDF, DOCX, XLSX, CSV, PNG, JPG - max 50MB)"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
              </svg>
            </button>

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
              disabled={(!inputValue.trim() && uploadedFiles.length === 0) || isLoading}
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
