'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

// Industry taxonomy based on documentation
const INDUSTRIES = [
  {
    id: 'manufacturing',
    name: 'Przemysł produkcyjny',
    icon: '🏭',
    segments: [
      { id: 'plastics_processing', name: 'Przetwórstwo tworzyw sztucznych' },
      { id: 'injection_molding', name: 'Wtrysk tworzyw sztucznych' },
      { id: 'tooling', name: 'Narzędziownie / Formy' },
      { id: 'cnc_machining', name: 'Obróbka CNC' },
      { id: 'industrial_automation', name: 'Automatyka przemysłowa' },
      { id: 'metal_processing', name: 'Obróbka metali' },
    ]
  },
  {
    id: 'services',
    name: 'Usługi',
    icon: '💼',
    segments: [
      { id: 'consulting', name: 'Doradztwo' },
      { id: 'it_services', name: 'Usługi IT' },
      { id: 'marketing', name: 'Marketing i reklama' },
      { id: 'hr_consulting', name: 'Doradztwo HR' },
      { id: 'legal', name: 'Usługi prawne' },
    ]
  },
  {
    id: 'technology',
    name: 'Technologia',
    icon: '💻',
    segments: [
      { id: 'software_development', name: 'Tworzenie oprogramowania' },
      { id: 'saas', name: 'SaaS' },
      { id: 'hardware', name: 'Sprzęt komputerowy' },
      { id: 'ai_ml', name: 'AI / Machine Learning' },
    ]
  },
  {
    id: 'retail',
    name: 'Handel detaliczny',
    icon: '🛒',
    segments: [
      { id: 'ecommerce', name: 'E-commerce' },
      { id: 'retail_store', name: 'Sklepy stacjonarne' },
      { id: 'wholesale', name: 'Handel hurtowy' },
    ]
  },
  {
    id: 'construction',
    name: 'Budownictwo',
    icon: '🏗️',
    segments: [
      { id: 'general_construction', name: 'Budownictwo ogólne' },
      { id: 'real_estate', name: 'Nieruchomości' },
      { id: 'architecture', name: 'Architektura' },
    ]
  },
  {
    id: 'logistics',
    name: 'Logistyka i transport',
    icon: '🚚',
    segments: [
      { id: 'shipping', name: 'Transport i spedycja' },
      { id: 'warehousing', name: 'Magazynowanie' },
      { id: 'last_mile', name: 'Dostawa ostatniej mili' },
    ]
  },
  {
    id: 'other',
    name: 'Inne',
    icon: '📦',
    segments: [
      { id: 'other_specify', name: 'Inna branża' }
    ]
  }
]

const USER_ROLES = [
  { id: 'ceo', name: 'Zarząd / C-level', icon: '👔' },
  { id: 'strategy', name: 'Strategy / Business Development', icon: '📊' },
  { id: 'sales', name: 'Sales / Marketing', icon: '📈' },
  { id: 'operations', name: 'Operations', icon: '⚙️' },
  { id: 'analyst', name: 'Analyst / Researcher', icon: '🔍' },
  { id: 'other', name: 'Inne', icon: '💡' },
]

const USE_CASES = [
  { id: 'competitive_analysis', name: 'Analiza konkurencji', icon: '⚔️' },
  { id: 'market_research', name: 'Market research', icon: '📊' },
  { id: 'due_diligence', name: 'Due diligence', icon: '🔍' },
  { id: 'lead_generation', name: 'Lead generation', icon: '🎯' },
  { id: 'monitoring', name: 'Monitoring branży', icon: '👁️' },
]

export default function OnboardingPage() {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    industry: '',
    industry_segment: '',
    user_role: '',
    use_cases: [] as string[],
    preferred_language: 'pl',
    preferred_depth: 'standard',
    preferred_format: 'pdf',
  })

  const selectedIndustry = INDUSTRIES.find(ind => ind.id === formData.industry)

  const handleIndustrySelect = (industryId: string) => {
    setFormData(prev => ({
      ...prev,
      industry: industryId,
      industry_segment: '' // Reset segment when industry changes
    }))
    setStep(3)
  }

  const handleSegmentSelect = (segmentId: string) => {
    setFormData(prev => ({ ...prev, industry_segment: segmentId }))
    setStep(4)
  }

  const handleRoleSelect = (roleId: string) => {
    setFormData(prev => ({ ...prev, user_role: roleId }))
    setStep(5)
  }

  const handleUseCaseToggle = (useCaseId: string) => {
    setFormData(prev => ({
      ...prev,
      use_cases: prev.use_cases.includes(useCaseId)
        ? prev.use_cases.filter(id => id !== useCaseId)
        : [...prev.use_cases, useCaseId]
    }))
  }

  const handleComplete = async () => {
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/v1/users/onboarding', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          industry: formData.industry,
          industry_segment: formData.industry_segment,
          user_role: formData.user_role,
          use_cases: formData.use_cases,
          preferred_language: formData.preferred_language,
          preferred_depth: formData.preferred_depth,
          preferred_format: formData.preferred_format,
        }),
      })

      if (response.ok) {
        // Redirect to chat
        router.push('/chat')
      } else {
        console.error('Failed to save onboarding data')
        // For dev mode, still proceed
        router.push('/chat')
      }
    } catch (error) {
      console.error('Error saving onboarding:', error)
      // For dev mode, still proceed
      router.push('/chat')
    } finally {
      setLoading(false)
    }
  }

  const canProceed = () => {
    if (step === 4) {
      return formData.use_cases.length > 0
    }
    return true
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Krok {step} z 5</span>
            <span className="text-sm text-gray-500">{Math.round((step / 5) * 100)}%</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${(step / 5) * 100}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Step 1: Welcome */}
          {step === 1 && (
            <div className="text-center space-y-6">
              <div className="inline-block p-4 bg-blue-100 rounded-full">
                <svg className="w-16 h-16 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h1 className="text-3xl font-bold text-gray-900">Witaj w MI-Navigator!</h1>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Zanim rozpoczniesz, pomóż nam dostosować platformę do Twoich potrzeb.
                Odpowiedz na kilka pytań - zajmie to tylko 2 minuty.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="text-3xl mb-2">🎯</div>
                  <h3 className="font-semibold text-gray-900">Spersonalizowane</h3>
                  <p className="text-sm text-gray-600">Analizy dostosowane do Twojej branży</p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="text-3xl mb-2">⚡</div>
                  <h3 className="font-semibold text-gray-900">Szybsze</h3>
                  <p className="text-sm text-gray-600">Relevantne źródła i terminologia</p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="text-3xl mb-2">📊</div>
                  <h3 className="font-semibold text-gray-900">Dokładniejsze</h3>
                  <p className="text-sm text-gray-600">Branżowe KPI i metryki</p>
                </div>
              </div>
              <button
                onClick={() => setStep(2)}
                className="mt-8 px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
              >
                Rozpocznij →
              </button>
            </div>
          )}

          {/* Step 2: Industry Selection */}
          {step === 2 && (
            <div className="space-y-6">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-gray-900">W jakiej branży działasz?</h2>
                <p className="text-gray-600 mt-2">Wybierz główną branżę Twojej działalności</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                {INDUSTRIES.map(industry => (
                  <button
                    key={industry.id}
                    onClick={() => handleIndustrySelect(industry.id)}
                    className={`p-6 border-2 rounded-xl text-left transition-all hover:border-blue-500 hover:shadow-md ${
                      formData.industry === industry.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-4xl">{industry.icon}</span>
                      <div>
                        <h3 className="font-semibold text-gray-900">{industry.name}</h3>
                        <p className="text-sm text-gray-500">{industry.segments.length} segmentów</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>

              <div className="flex justify-between mt-8">
                <button
                  onClick={() => setStep(1)}
                  className="px-6 py-2 text-gray-600 hover:text-gray-900"
                >
                  ← Wstecz
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Segment Selection */}
          {step === 3 && selectedIndustry && (
            <div className="space-y-6">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-gray-900">Wybierz segment</h2>
                <p className="text-gray-600 mt-2">
                  <span className="inline-flex items-center">
                    <span className="text-2xl mr-2">{selectedIndustry.icon}</span>
                    {selectedIndustry.name}
                  </span>
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                {selectedIndustry.segments.map(segment => (
                  <button
                    key={segment.id}
                    onClick={() => handleSegmentSelect(segment.id)}
                    className={`p-6 border-2 rounded-xl text-left transition-all hover:border-blue-500 hover:shadow-md ${
                      formData.industry_segment === segment.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200'
                    }`}
                  >
                    <h3 className="font-semibold text-gray-900">{segment.name}</h3>
                  </button>
                ))}
              </div>

              <div className="flex justify-between mt-8">
                <button
                  onClick={() => setStep(2)}
                  className="px-6 py-2 text-gray-600 hover:text-gray-900"
                >
                  ← Wstecz
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Role Selection */}
          {step === 4 && (
            <div className="space-y-6">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-gray-900">Jaka jest Twoja rola?</h2>
                <p className="text-gray-600 mt-2">Pomoże nam dopasować format analiz</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                {USER_ROLES.map(role => (
                  <button
                    key={role.id}
                    onClick={() => handleRoleSelect(role.id)}
                    className={`p-6 border-2 rounded-xl text-left transition-all hover:border-blue-500 hover:shadow-md ${
                      formData.user_role === role.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-3xl">{role.icon}</span>
                      <h3 className="font-semibold text-gray-900">{role.name}</h3>
                    </div>
                  </button>
                ))}
              </div>

              <div className="flex justify-between mt-8">
                <button
                  onClick={() => setStep(3)}
                  className="px-6 py-2 text-gray-600 hover:text-gray-900"
                >
                  ← Wstecz
                </button>
              </div>
            </div>
          )}

          {/* Step 5: Use Cases */}
          {step === 5 && (
            <div className="space-y-6">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-gray-900">Do czego będziesz używać platformy?</h2>
                <p className="text-gray-600 mt-2">Możesz wybrać kilka opcji</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                {USE_CASES.map(useCase => (
                  <button
                    key={useCase.id}
                    onClick={() => handleUseCaseToggle(useCase.id)}
                    className={`p-6 border-2 rounded-xl text-left transition-all hover:border-blue-500 hover:shadow-md ${
                      formData.use_cases.includes(useCase.id)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-3xl">{useCase.icon}</span>
                        <h3 className="font-semibold text-gray-900">{useCase.name}</h3>
                      </div>
                      {formData.use_cases.includes(useCase.id) && (
                        <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                  </button>
                ))}
              </div>

              <div className="flex justify-between mt-8">
                <button
                  onClick={() => setStep(4)}
                  className="px-6 py-2 text-gray-600 hover:text-gray-900"
                >
                  ← Wstecz
                </button>
                <button
                  onClick={handleComplete}
                  disabled={!canProceed() || loading}
                  className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Zapisywanie...' : 'Zakończ konfigurację →'}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Skip button */}
        {step > 1 && step < 5 && (
          <div className="text-center mt-4">
            <button
              onClick={() => setStep(5)}
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              Pomiń →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
