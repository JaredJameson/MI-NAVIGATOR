'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface HelpArticle {
  id: string
  category: string
  title: string
  summary: string
  tags: string[]
}

interface HelpArticleDetail extends HelpArticle {
  category_label: string
  content: string
}

interface HelpCategory {
  id: string
  label: string
  icon: string
  article_count: number
}

// Category icons
const CATEGORY_ICONS: Record<string, string> = {
  'rocket': '🚀',
  'document': '📄',
  'folder': '📁',
  'search': '🔍',
  'bell': '🔔',
  'cog': '⚙️',
  'user': '👤',
  'question': '❓',
}

export default function HelpPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [articles, setArticles] = useState<HelpArticle[]>([])
  const [categories, setCategories] = useState<HelpCategory[]>([])
  const [selectedArticle, setSelectedArticle] = useState<HelpArticleDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [activeSearch, setActiveSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')

  useEffect(() => {
    fetchCategories()
  }, [])

  useEffect(() => {
    fetchArticles()
  }, [activeSearch, selectedCategory])

  useEffect(() => {
    const articleId = searchParams.get('article')
    if (articleId) {
      fetchArticle(articleId)
    } else {
      setSelectedArticle(null)
    }
  }, [searchParams])

  const fetchCategories = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/help/categories`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setCategories(data.categories || [])
      }
    } catch (err) {
      console.error('Failed to fetch categories:', err)
    }
  }

  const fetchArticles = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const params = new URLSearchParams()
      if (activeSearch) {
        params.append('search', activeSearch)
      }
      if (selectedCategory) {
        params.append('category', selectedCategory)
      }

      const response = await fetch(`${API_BASE_URL}/help/articles?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        if (response.status === 401) {
          router.push('/auth/login')
          return
        }
        throw new Error('Failed to fetch articles')
      }

      const data = await response.json()
      setArticles(data.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load articles')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchArticle = async (articleId: string) => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/help/articles/${articleId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        if (!data.error) {
          setSelectedArticle(data)
        }
      }
    } catch (err) {
      console.error('Failed to fetch article:', err)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setActiveSearch(searchQuery)
    setSelectedCategory('')
    router.push('/help')
  }

  const handleCategoryClick = (categoryId: string) => {
    setSelectedCategory(categoryId === selectedCategory ? '' : categoryId)
    setActiveSearch('')
    setSearchQuery('')
    router.push('/help')
  }

  const handleArticleClick = (articleId: string) => {
    router.push(`/help?article=${articleId}`)
  }

  const renderMarkdown = (content: string) => {
    // Simple markdown rendering
    return content
      .split('\n')
      .map((line, i) => {
        if (line.startsWith('# ')) {
          return <h1 key={i} className="text-2xl font-bold mt-6 mb-4">{line.slice(2)}</h1>
        }
        if (line.startsWith('## ')) {
          return <h2 key={i} className="text-xl font-semibold mt-5 mb-3">{line.slice(3)}</h2>
        }
        if (line.startsWith('- **')) {
          const match = line.match(/- \*\*(.+?)\*\* - (.+)/)
          if (match) {
            return (
              <li key={i} className="ml-4 mb-2">
                <strong>{match[1]}</strong> - {match[2]}
              </li>
            )
          }
        }
        if (line.startsWith('- ')) {
          return <li key={i} className="ml-4 mb-1">{line.slice(2)}</li>
        }
        if (line.match(/^\d+\. /)) {
          return <li key={i} className="ml-4 mb-1 list-decimal">{line.replace(/^\d+\. /, '')}</li>
        }
        if (line.startsWith('**') && line.endsWith('**')) {
          return <p key={i} className="font-semibold mt-4 mb-2">{line.slice(2, -2)}</p>
        }
        if (line.trim() === '') {
          return <br key={i} />
        }
        return <p key={i} className="mb-2">{line}</p>
      })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-3xl">❓</span>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Centrum pomocy</h1>
                <p className="mt-1 text-sm text-gray-500">
                  Znajdz odpowiedzi na swoje pytania
                </p>
              </div>
            </div>
            <Link
              href="/dashboard"
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
            >
              ← Powrot do dashboardu
            </Link>
          </div>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="mt-6">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Szukaj w pomocy..."
                className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                🔍
              </span>
              <button
                type="submit"
                className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
              >
                Szukaj
              </button>
            </div>
          </form>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {selectedArticle ? (
          /* Article Detail View */
          <div className="bg-white rounded-lg shadow-sm p-8">
            <button
              onClick={() => router.push('/help')}
              className="mb-6 text-blue-600 hover:text-blue-800 flex items-center gap-2"
            >
              ← Powrot do listy artykulow
            </button>
            <div className="mb-4">
              <span className="inline-block px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded-full">
                {selectedArticle.category_label}
              </span>
            </div>
            <div className="prose max-w-none">
              {renderMarkdown(selectedArticle.content)}
            </div>
            <div className="mt-8 pt-6 border-t">
              <p className="text-sm text-gray-500">Tagi:</p>
              <div className="flex flex-wrap gap-2 mt-2">
                {selectedArticle.tags.map(tag => (
                  <span key={tag} className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* Article List View */
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Categories Sidebar */}
            <div className="w-full lg:w-64 flex-shrink-0">
              <div className="bg-white rounded-lg shadow-sm p-4">
                <h3 className="font-semibold text-gray-900 mb-4">Kategorie</h3>
                <div className="space-y-2">
                  <button
                    onClick={() => handleCategoryClick('')}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                      !selectedCategory
                        ? 'bg-blue-100 text-blue-800 font-medium'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    Wszystkie artykuly
                  </button>
                  {categories.map((category) => (
                    <button
                      key={category.id}
                      onClick={() => handleCategoryClick(category.id)}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center justify-between ${
                        selectedCategory === category.id
                          ? 'bg-blue-100 text-blue-800 font-medium'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <span className="flex items-center gap-2">
                        <span>{CATEGORY_ICONS[category.icon] || '📌'}</span>
                        <span>{category.label}</span>
                      </span>
                      <span className="text-xs bg-gray-200 px-2 py-0.5 rounded-full">
                        {category.article_count}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Articles List */}
            <div className="flex-1">
              {activeSearch && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg flex items-center justify-between">
                  <span className="text-sm text-blue-800">
                    Wyniki wyszukiwania dla: <strong>{activeSearch}</strong> ({articles.length} wynikow)
                  </span>
                  <button
                    onClick={() => {
                      setActiveSearch('')
                      setSearchQuery('')
                    }}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Wyczysc
                  </button>
                </div>
              )}

              {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                  {error}
                </div>
              )}

              {isLoading ? (
                <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="mt-4 text-gray-500">Ladowanie artykulow...</p>
                </div>
              ) : articles.length === 0 ? (
                <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                  <span className="text-4xl">📚</span>
                  <p className="mt-4 text-gray-500">Nie znaleziono artykulow</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {articles.map((article) => {
                    const category = categories.find(c => c.id === article.category)
                    return (
                      <div
                        key={article.id}
                        onClick={() => handleArticleClick(article.id)}
                        className="bg-white rounded-lg shadow-sm p-6 cursor-pointer hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start gap-4">
                          <div className="flex-shrink-0 w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                            <span className="text-2xl">
                              {category ? CATEGORY_ICONS[category.icon] || '📄' : '📄'}
                            </span>
                          </div>
                          <div className="flex-1">
                            <h3 className="text-lg font-medium text-gray-900 hover:text-blue-600">
                              {article.title}
                            </h3>
                            <p className="mt-1 text-sm text-gray-600">
                              {article.summary}
                            </p>
                            <div className="mt-3 flex flex-wrap gap-2">
                              {article.tags.slice(0, 3).map(tag => (
                                <span key={tag} className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
