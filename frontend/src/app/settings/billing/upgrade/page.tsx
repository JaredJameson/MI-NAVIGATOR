'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

interface Plan {
  id: string
  name: string
  price: number
  period: string
  analyses: number
  storage: number
  features: string[]
  popular?: boolean
}

const PLANS: Plan[] = [
  {
    id: 'starter',
    name: 'Starter',
    price: 49,
    period: 'month',
    analyses: 25,
    storage: 5,
    features: [
      '25 analyses per month',
      '5 GB storage',
      'Basic reports',
      'Email support'
    ]
  },
  {
    id: 'professional',
    name: 'Professional',
    price: 149,
    period: 'month',
    analyses: 100,
    storage: 10,
    features: [
      '100 analyses per month',
      '10 GB storage',
      'Advanced reports',
      'PDF, DOCX, PPTX exports',
      'Priority support',
      'API access'
    ],
    popular: true
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 499,
    period: 'month',
    analyses: -1, // unlimited
    storage: 50,
    features: [
      'Unlimited analyses',
      '50 GB storage',
      'Custom reports',
      'All export formats',
      'Dedicated support',
      'API access',
      'Custom integrations',
      'Team collaboration'
    ]
  }
]

export default function UpgradePlanPage() {
  const router = useRouter()
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null)
  const [step, setStep] = useState<'select' | 'payment' | 'confirm'>('select')
  const [paymentInfo, setPaymentInfo] = useState({
    cardNumber: '',
    cardName: '',
    expiryDate: '',
    cvv: ''
  })
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState('')

  const handleSelectPlan = (plan: Plan) => {
    setSelectedPlan(plan)
    setStep('payment')
  }

  const handlePaymentChange = (field: string, value: string) => {
    setPaymentInfo(prev => ({ ...prev, [field]: value }))
    setError('')
  }

  const handleConfirmUpgrade = async () => {
    // Validate payment info
    if (!paymentInfo.cardNumber || !paymentInfo.cardName || !paymentInfo.expiryDate || !paymentInfo.cvv) {
      setError('Please fill in all payment fields')
      return
    }

    if (paymentInfo.cardNumber.replace(/\s/g, '').length !== 16) {
      setError('Card number must be 16 digits')
      return
    }

    if (paymentInfo.cvv.length !== 3) {
      setError('CVV must be 3 digits')
      return
    }

    setProcessing(true)

    // Simulate API call
    setTimeout(() => {
      setProcessing(false)
      setStep('confirm')
    }, 2000)
  }

  const formatCardNumber = (value: string) => {
    const cleaned = value.replace(/\s/g, '')
    const chunks = cleaned.match(/.{1,4}/g) || []
    return chunks.join(' ').substr(0, 19) // Max 16 digits + 3 spaces
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/settings/billing" className="text-sm text-gray-600 hover:text-gray-900">
            ← Back to Billing
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">Upgrade Your Plan</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {step === 'select' && (
          <div>
            <h2 className="mb-6 text-center text-xl font-semibold text-gray-900">Choose Your Plan</h2>
            <div className="grid gap-6 md:grid-cols-3">
              {PLANS.map((plan) => (
                <div
                  key={plan.id}
                  className={`relative rounded-lg bg-white p-6 shadow-sm ${
                    plan.popular ? 'ring-2 ring-blue-600' : ''
                  }`}
                >
                  {plan.popular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-blue-600 px-4 py-1 text-xs font-medium text-white">
                      Most Popular
                    </div>
                  )}
                  <div className="mb-4">
                    <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
                    <div className="mt-2 flex items-baseline">
                      <span className="text-4xl font-bold text-gray-900">${plan.price}</span>
                      <span className="ml-1 text-gray-600">/{plan.period}</span>
                    </div>
                  </div>
                  <ul className="mb-6 space-y-3">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start text-sm">
                        <svg className="mr-2 h-5 w-5 flex-shrink-0 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <button
                    onClick={() => handleSelectPlan(plan)}
                    className={`w-full rounded-lg px-4 py-2 font-medium ${
                      plan.popular
                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                        : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                    }`}
                  >
                    Select Plan
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {step === 'payment' && selectedPlan && (
          <div className="mx-auto max-w-2xl">
            <div className="mb-6 rounded-lg bg-blue-50 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-semibold text-gray-900">{selectedPlan.name} Plan</div>
                  <div className="text-sm text-gray-600">
                    ${selectedPlan.price}/{selectedPlan.period}
                  </div>
                </div>
                <button
                  onClick={() => setStep('select')}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  Change Plan
                </button>
              </div>
            </div>

            <div className="rounded-lg bg-white p-6 shadow-sm">
              <h2 className="mb-6 text-lg font-semibold text-gray-900">Payment Information</h2>

              {error && (
                <div className="mb-4 rounded-lg bg-red-50 p-4 text-sm text-red-600">
                  {error}
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Card Number
                  </label>
                  <input
                    type="text"
                    placeholder="1234 5678 9012 3456"
                    value={paymentInfo.cardNumber}
                    onChange={(e) => handlePaymentChange('cardNumber', formatCardNumber(e.target.value))}
                    className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    maxLength={19}
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Cardholder Name
                  </label>
                  <input
                    type="text"
                    placeholder="John Doe"
                    value={paymentInfo.cardName}
                    onChange={(e) => handlePaymentChange('cardName', e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-gray-700">
                      Expiry Date
                    </label>
                    <input
                      type="text"
                      placeholder="MM/YY"
                      value={paymentInfo.expiryDate}
                      onChange={(e) => {
                        let value = e.target.value.replace(/\D/g, '')
                        if (value.length >= 2) {
                          value = value.slice(0, 2) + '/' + value.slice(2, 4)
                        }
                        handlePaymentChange('expiryDate', value)
                      }}
                      className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                      maxLength={5}
                    />
                  </div>

                  <div>
                    <label className="mb-1 block text-sm font-medium text-gray-700">
                      CVV
                    </label>
                    <input
                      type="text"
                      placeholder="123"
                      value={paymentInfo.cvv}
                      onChange={(e) => handlePaymentChange('cvv', e.target.value.replace(/\D/g, '').slice(0, 3))}
                      className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                      maxLength={3}
                    />
                  </div>
                </div>
              </div>

              <div className="mt-6 flex gap-4">
                <button
                  onClick={() => setStep('select')}
                  className="flex-1 rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50"
                >
                  Back
                </button>
                <button
                  onClick={handleConfirmUpgrade}
                  disabled={processing}
                  className="flex-1 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {processing ? 'Processing...' : `Pay $${selectedPlan.price}`}
                </button>
              </div>
            </div>
          </div>
        )}

        {step === 'confirm' && selectedPlan && (
          <div className="mx-auto max-w-2xl">
            <div className="rounded-lg bg-white p-8 text-center shadow-sm">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
                <svg className="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="mb-2 text-2xl font-bold text-gray-900">Upgrade Successful!</h2>
              <p className="mb-6 text-gray-600">
                Your plan has been upgraded to {selectedPlan.name}. You now have access to all premium features.
              </p>
              <div className="mb-6 rounded-lg bg-gray-50 p-4">
                <div className="text-sm text-gray-600">New Plan</div>
                <div className="text-xl font-bold text-gray-900">{selectedPlan.name}</div>
                <div className="text-gray-600">${selectedPlan.price}/{selectedPlan.period}</div>
              </div>
              <Link
                href="/settings/billing"
                className="inline-block rounded-lg bg-blue-600 px-6 py-2 font-medium text-white hover:bg-blue-700"
              >
                Back to Billing
              </Link>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
