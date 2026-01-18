'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken, fetchCsrfToken } from '@/services/api'
import { StructuredMessage } from '@/components/chat/StructuredMessage'

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
  const [detectedUrl, setDetectedUrl] = useState<string | null>(null)
  const [detectedNIP, setDetectedNIP] = useState<string | null>(null)
  const [detectedKRS, setDetectedKRS] = useState<string | null>(null)
  const [showSaveDialog, setShowSaveDialog] = useState(false)
  const [projects, setProjects] = useState<any[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState<string>('')
  const [isSavingReport, setIsSavingReport] = useState(false)
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

  // Detect URLs in input
  useEffect(() => {
    const urlRegex = /(https?:\/\/[^\s]+)/gi
    const matches = inputValue.match(urlRegex)

    if (matches && matches.length > 0) {
      setDetectedUrl(matches[0])
    } else {
      setDetectedUrl(null)
    }
  }, [inputValue])

  // Detect NIP and KRS numbers in input
  useEffect(() => {
    // KRS regex: Must have "KRS" prefix OR start with 0000 (e.g., KRS 0000145732 or 0000145732)
    const krsRegex = /\b(?:KRS\s*\d{10})\b|\b0{4}\d{6}\b/gi
    // NIP regex: 10 digits with optional dashes/spaces (e.g., 5260016831 or 526-001-68-31)
    // Exclude numbers starting with 0000 (those are KRS)
    const nipRegex = /\b(?!0{4})\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}\b|\b(?!0{4})\d{10}\b/g

    // Check KRS first (higher priority)
    const krsMatches = inputValue.match(krsRegex)
    const nipMatches = inputValue.match(nipRegex)

    if (krsMatches && krsMatches.length > 0) {
      // Clean KRS: remove "KRS" prefix and spaces
      const cleanKRS = krsMatches[0].replace(/KRS\s*/gi, '').trim()
      setDetectedKRS(cleanKRS)
    } else {
      setDetectedKRS(null)
    }

    if (nipMatches && nipMatches.length > 0) {
      // Clean NIP: remove dashes and spaces
      const cleanNIP = nipMatches[0].replace(/[-\s]/g, '')
      // Don't detect as NIP if already detected as KRS
      if (!krsMatches || !krsMatches.some(krs => krs.replace(/KRS\s*/gi, '').trim() === cleanNIP)) {
        setDetectedNIP(cleanNIP)
      } else {
        setDetectedNIP(null)
      }
    } else {
      setDetectedNIP(null)
    }
  }, [inputValue])

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
    if ((!inputValue.trim() && uploadedFiles.length === 0) || isLoading) return

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

      // Upload files first (if any)
      let fileIds: string[] = []
      if (uploadedFiles.length > 0) {
        console.log('[Files] Uploading', uploadedFiles.length, 'files...')
        fileIds = await uploadFiles(uploadedFiles, conv.id)
        console.log('[Files] Uploaded file IDs:', fileIds)
      }

      // Wait for WebSocket connection (up to 5 seconds)
      console.log('[WS] Waiting for connection...')
      const isConnected = await waitForWebSocketConnection(5000)

      if (!isConnected || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        throw new Error('WebSocket connection timeout')
      }

      console.log('[WS] Connection ready')

      // Prepare message content
      let messageContent = inputValue.trim()
      if (fileIds.length > 0) {
        // Add file information to message
        messageContent += `\n\n[Attached ${fileIds.length} file(s): ${uploadedFiles.map(f => f.name).join(', ')}]`
      }

      // Add user message optimistically
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: messageContent || '[File upload]',
        created_at: new Date().toISOString(),
      }

      setConversation(prev => prev ? {
        ...prev,
        messages: [...prev.messages, userMessage],
      } : null)

      // Send via WebSocket (include file IDs in message)
      const messagePayload = JSON.stringify({
        content: inputValue.trim() || '[File upload]',
        file_ids: fileIds
      })
      console.log('[WS] Sending message with files:', messagePayload)
      wsRef.current.send(messagePayload)

      setInputValue('')
      setUploadedFiles([]) // Clear uploaded files after sending

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

  const startUrlAnalysis = async () => {
    if (!detectedUrl) return

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

      // Wait for WebSocket connection
      console.log('[WS] Waiting for connection...')
      const isConnected = await waitForWebSocketConnection(5000)

      if (!isConnected || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        throw new Error('WebSocket connection timeout')
      }

      console.log('[WS] Connection ready')

      // Prepare message with URL analysis instruction
      const messageContent = `Analyze website: ${detectedUrl}`

      // Add user message optimistically
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: messageContent,
        created_at: new Date().toISOString(),
      }

      setConversation(prev => prev ? {
        ...prev,
        messages: [...prev.messages, userMessage],
      } : null)

      // Send via WebSocket
      const messagePayload = JSON.stringify({
        content: messageContent,
        file_ids: []
      })
      console.log('[WS] Sending URL analysis:', messagePayload)
      wsRef.current.send(messagePayload)

      // Clear detected URL and input
      setDetectedUrl(null)
      setInputValue('')

    } catch (err) {
      console.error('[WS] Send error:', err)
      setError('Failed to send message. Please try again.')
      setIsLoading(false)
    }
  }

  const startCompanyLookup = async (type: 'NIP' | 'KRS') => {
    const number = type === 'NIP' ? detectedNIP : detectedKRS
    if (!number) return

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

      // Wait for WebSocket connection
      console.log('[WS] Waiting for connection...')
      const isConnected = await waitForWebSocketConnection(5000)

      if (!isConnected || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        throw new Error('WebSocket connection timeout')
      }

      console.log('[WS] Connection ready')

      // Prepare message with company lookup instruction
      const messageContent = `Lookup company with ${type}: ${number}`

      // Add user message optimistically
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: messageContent,
        created_at: new Date().toISOString(),
      }

      setConversation(prev => prev ? {
        ...prev,
        messages: [...prev.messages, userMessage],
      } : null)

      // Send via WebSocket
      const messagePayload = JSON.stringify({
        content: messageContent,
        file_ids: []
      })
      console.log(`[WS] Sending ${type} lookup:`, messagePayload)
      wsRef.current.send(messagePayload)

      // Clear detected number and input
      if (type === 'NIP') {
        setDetectedNIP(null)
      } else {
        setDetectedKRS(null)
      }
      setInputValue('')

    } catch (err) {
      console.error('[WS] Send error:', err)
      setError('Failed to send message. Please try again.')
      setIsLoading(false)
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

  const uploadFiles = async (files: File[], conversationId: string): Promise<string[]> => {
    const token = getStoredToken()
    if (!token) return []

    const uploadedFileIds: string[] = []

    for (const file of files) {
      try {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('conversation_id', conversationId)

        const response = await fetch(`${API_BASE_URL}/files/upload`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData,
        })

        if (!response.ok) {
          throw new Error(`Failed to upload ${file.name}`)
        }

        const data = await response.json()
        uploadedFileIds.push(data.id)
      } catch (err) {
        console.error(`Error uploading ${file.name}:`, err)
        setError(`Failed to upload ${file.name}`)
      }
    }

    return uploadedFileIds
  }

  const handleSaveAsReport = async () => {
    if (!conversation || conversation.messages.length === 0) {
      setError('No conversation to save')
      return
    }

    setShowSaveDialog(true)

    // Fetch projects list
    const token = getStoredToken()
    if (!token) {
      setError('Not authenticated')
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/projects/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setProjects(data.items || [])
      }
    } catch (err) {
      console.error('Failed to fetch projects:', err)
      setError('Failed to load projects')
    }
  }

  const saveReport = async () => {
    if (!selectedProjectId) {
      setError('Please select a project')
      return
    }

    if (!conversation) {
      setError('No conversation to save')
      return
    }

    setIsSavingReport(true)
    const token = getStoredToken()

    try {
      // Get CSRF token
      const csrfToken = await fetchCsrfToken()

      // 1. Create report from conversation
      const reportTitle = conversation.title || 'Chat Analysis Report'
      const reportContent = conversation.messages
        .map(m => `**${m.role === 'user' ? 'Question' : 'Answer'}:**\n${m.content}`)
        .join('\n\n')

      const reportPayload = {
        title: reportTitle,
        type: 'chat_analysis',
        content: reportContent,
        conversation_id: conversation.id,
        summary: conversation.messages[0]?.content.substring(0, 200) || 'Chat analysis',
      }

      const reportResponse = await fetch(`${API_BASE_URL}/reports/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken || '',
        },
        body: JSON.stringify(reportPayload),
      })

      if (!reportResponse.ok) {
        throw new Error('Failed to create report')
      }

      const reportData = await reportResponse.json()
      const reportId = reportData.id

      // 2. Associate report with project
      const assignResponse = await fetch(
        `${API_BASE_URL}/projects/${selectedProjectId}/reports?report_id=${reportId}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'X-CSRF-Token': csrfToken || '',
          },
        }
      )

      if (!assignResponse.ok) {
        throw new Error('Failed to assign report to project')
      }

      // Success!
      setShowSaveDialog(false)
      setSelectedProjectId('')
      setIsSavingReport(false)

      // Show success message
      alert('Report saved successfully!')

    } catch (err) {
      console.error('Error saving report:', err)
      setError('Failed to save report. Please try again.')
      setIsSavingReport(false)
    }
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
          <div className="flex items-center gap-2">
            {conversation && conversation.messages.length > 0 && (
              <button
                onClick={handleSaveAsReport}
                className="rounded-lg bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700 flex items-center gap-2"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                </svg>
                Save as Report
              </button>
            )}
            <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">
              New Chat
            </button>
          </div>
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
                    {message.role === 'user' ? (
                      <div className="whitespace-pre-wrap text-sm">
                        {message.content}
                      </div>
                    ) : (
                      <StructuredMessage content={message.content} />
                    )}
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
          {/* URL Detection Suggestion */}
          {detectedUrl && (
            <div className="mb-3 rounded-lg border border-blue-200 bg-blue-50 px-4 py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-blue-900">URL Detected</p>
                    <p className="text-xs text-blue-700">Would you like to analyze this website?</p>
                  </div>
                </div>
                <button
                  onClick={startUrlAnalysis}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                >
                  Analyze Website
                </button>
              </div>
            </div>
          )}

          {/* NIP Detection Suggestion */}
          {detectedNIP && (
            <div className="mb-3 rounded-lg border border-green-200 bg-green-50 px-4 py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-green-900">NIP Detected: {detectedNIP}</p>
                    <p className="text-xs text-green-700">Would you like to lookup this company?</p>
                  </div>
                </div>
                <button
                  onClick={() => startCompanyLookup('NIP')}
                  className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700"
                >
                  Lookup Company
                </button>
              </div>
            </div>
          )}

          {/* KRS Detection Suggestion */}
          {detectedKRS && (
            <div className="mb-3 rounded-lg border border-purple-200 bg-purple-50 px-4 py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <svg className="h-5 w-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-purple-900">KRS Detected: {detectedKRS}</p>
                    <p className="text-xs text-purple-700">Would you like to lookup this company?</p>
                  </div>
                </div>
                <button
                  onClick={() => startCompanyLookup('KRS')}
                  className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700"
                >
                  Lookup Company
                </button>
              </div>
            </div>
          )}

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

      {/* Save Report Dialog */}
      {showSaveDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <h2 className="mb-4 text-xl font-semibold text-gray-900">Save as Report</h2>

            <div className="mb-4">
              <label className="mb-2 block text-sm font-medium text-gray-700">
                Select Project
              </label>
              <select
                value={selectedProjectId}
                onChange={(e) => setSelectedProjectId(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">-- Select a project --</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>
            </div>

            {projects.length === 0 && (
              <div className="mb-4 rounded-lg bg-yellow-50 px-4 py-3 text-sm text-yellow-700">
                No projects found. <Link href="/projects/new" className="underline">Create a new project</Link> first.
              </div>
            )}

            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowSaveDialog(false)
                  setSelectedProjectId('')
                }}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                disabled={isSavingReport}
              >
                Cancel
              </button>
              <button
                onClick={saveReport}
                disabled={!selectedProjectId || isSavingReport}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {isSavingReport ? 'Saving...' : 'Save Report'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
