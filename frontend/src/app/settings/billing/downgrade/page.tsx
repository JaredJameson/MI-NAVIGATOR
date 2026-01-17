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
}

const ALL_PLANS: Plan[] = [
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
    ]
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

export default function DowngradePlanPage() {
  const router = useRouter()

  // Get current plan from billing page (hardcoded for testing - in production would come from API)
  const currentPlanName = 'Professional'
  const currentPlanIndex = ALL_PLANS.findIndex(p => p.name === currentPlanName)
  const currentPlan = ALL_PLANS[currentPlanIndex]

  // Only show plans lower than current plan
  const availablePlans = ALL_PLANS.slice(0, currentPlanIndex)

  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null)
  const [step, setStep] = useState<'select' | 'review' | 'confirm'>('select')
  const [processing, setProcessing] = useState(false)

  // Billing period for display
  const billingPeriodEnd = '2026-01-31'

  const handleSelectPlan = (plan: Plan) => {
    setSelectedPlan(plan)
    setStep('review')
  }

  const handleConfirmDowngrade = async () => {
    setProcessing(true)

    // Simulate API call
    setTimeout(() => {
      setProcessing(false)
      setStep('confirm')
    }, 1500)
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/settings/billing" className="text-sm text-gray-600 hover:text-gray-900">
            ← Back to Billing
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">Downgrade Your Plan</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {step === 'select' && (
          <div>
            {/* Current Plan Info */}
            <div className="mb-8 rounded-lg bg-blue-50 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-600">Current Plan</div>
                  <div className="text-2xl font-bold text-gray-900">{currentPlan.name}</div>
                  <div className="text-sm text-gray-600">
                    ${currentPlan.price}/{currentPlan.period}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-600">Renews on</div>
                  <div className="font-medium text-gray-900">{formatDate(billingPeriodEnd)}</div>
                </div>
              </div>
            </div>

            {availablePlans.length === 0 ? (
              <div className="rounded-lg bg-white p-8 text-center shadow-sm">
                <svg className="mx-auto mb-4 h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h2 className="mb-2 text-xl font-semibold text-gray-900">No Lower Plans Available</h2>
                <p className="mb-6 text-gray-600">
                  You are already on the lowest tier plan. There are no plans to downgrade to.
                </p>
                <Link
                  href="/settings/billing"
                  className="inline-block rounded-lg bg-blue-600 px-6 py-2 font-medium text-white hover:bg-blue-700"
                >
                  Back to Billing
                </Link>
              </div>
            ) : (
              <div>
                <h2 className="mb-6 text-center text-xl font-semibold text-gray-900">Choose a Lower Tier Plan</h2>
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {availablePlans.map((plan) => (
                    <div
                      key={plan.id}
                      className="relative rounded-lg bg-white p-6 shadow-sm"
                    >
                      <div className="mb-4">
                        <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
                        <div className="mt-2 flex items-baseline">
                          <span className="text-4xl font-bold text-gray-900">${plan.price}</span>
                          <span className="ml-1 text-gray-600">/{plan.period}</span>
                        </div>
                        <div className="mt-2 text-sm text-green-600 font-medium">
                          Save ${currentPlan.price - plan.price}/month
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
                        className="w-full rounded-lg bg-gray-100 px-4 py-2 font-medium text-gray-900 hover:bg-gray-200"
                      >
                        Select Plan
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {step === 'review' && selectedPlan && (
          <div className="mx-auto max-w-2xl">
            <div className="rounded-lg bg-white p-6 shadow-sm">
              <h2 className="mb-6 text-lg font-semibold text-gray-900">Review Downgrade</h2>

              {/* Impact Notice */}
              <div className="mb-6 rounded-lg bg-yellow-50 border border-yellow-200 p-4">
                <div className="flex">
                  <svg className="h-5 w-5 text-yellow-600 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h3 className="font-medium text-yellow-900">Important Information</h3>
                    <p className="mt-1 text-sm text-yellow-700">
                      Your plan will be downgraded at the end of your current billing period on <strong>{formatDate(billingPeriodEnd)}</strong>. You'll continue to have access to all {currentPlan.name} features until then.
                    </p>
                  </div>
                </div>
              </div>

              {/* Plan Comparison */}
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  {/* Current Plan */}
                  <div className="rounded-lg bg-gray-50 p-4">
                    <div className="mb-2 text-sm text-gray-600">Current Plan</div>
                    <div className="text-xl font-bold text-gray-900">{currentPlan.name}</div>
                    <div className="text-gray-600">${currentPlan.price}/{currentPlan.period}</div>
                    <div className="mt-3 space-y-2 text-sm">
                      <div className="text-gray-700">{currentPlan.analyses} analyses/month</div>
                      <div className="text-gray-700">{currentPlan.storage} GB storage</div>
                    </div>
                  </div>

                  {/* New Plan */}
                  <div className="rounded-lg bg-blue-50 p-4">
                    <div className="mb-2 text-sm text-gray-600">New Plan (from {formatDate(billingPeriodEnd)})</div>
                    <div className="text-xl font-bold text-gray-900">{selectedPlan.name}</div>
                    <div className="text-gray-600">${selectedPlan.price}/{selectedPlan.period}</div>
                    <div className="mt-3 space-y-2 text-sm">
                      <div className="text-gray-700">{selectedPlan.analyses} analyses/month</div>
                      <div className="text-gray-700">{selectedPlan.storage} GB storage</div>
                    </div>
                  </div>
                </div>

                {/* Savings */}
                <div className="rounded-lg bg-green-50 p-4">
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-600">Monthly Savings</div>
                    <div className="text-2xl font-bold text-green-600">
                      ${currentPlan.price - selectedPlan.price}
                    </div>
                  </div>
                </div>

                {/* What you'll lose */}
                <div className="rounded-lg bg-red-50 border border-red-200 p-4">
                  <h3 className="mb-2 font-medium text-red-900">Features You'll Lose</h3>
                  <ul className="space-y-1 text-sm text-red-700">
                    {currentPlan.features
                      .filter(feature => !selectedPlan.features.includes(feature))
                      .map((feature, idx) => (
                        <li key={idx} className="flex items-start">
                          <svg className="mr-2 h-5 w-5 flex-shrink-0 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                          </svg>
                          {feature}
                        </li>
                      ))}
                  </ul>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-6 flex gap-4">
                <button
                  onClick={() => setStep('select')}
                  className="flex-1 rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50"
                >
                  Back
                </button>
                <button
                  onClick={handleConfirmDowngrade}
                  disabled={processing}
                  className="flex-1 rounded-lg bg-red-600 px-4 py-2 font-medium text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {processing ? 'Processing...' : 'Confirm Downgrade'}
                </button>
              </div>
            </div>
          </div>
        )}

        {step === 'confirm' && selectedPlan && (
          <div className="mx-auto max-w-2xl">
            <div className="rounded-lg bg-white p-8 text-center shadow-sm">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
                <svg className="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="mb-2 text-2xl font-bold text-gray-900">Downgrade Scheduled</h2>
              <p className="mb-6 text-gray-600">
                Your plan will be downgraded to {selectedPlan.name} at the end of your current billing period.
              </p>

              {/* Timeline */}
              <div className="mb-6 rounded-lg bg-gray-50 p-6 text-left">
                <div className="space-y-4">
                  <div className="flex items-start">
                    <div className="mr-4 mt-1 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-green-100">
                      <svg className="h-4 w-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">Now - {formatDate(billingPeriodEnd)}</div>
                      <div className="text-sm text-gray-600">
                        Continue using all {currentPlan.name} features
                      </div>
                    </div>
                  </div>

                  <div className="flex items-start">
                    <div className="mr-4 mt-1 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-blue-100">
                      <svg className="h-4 w-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">{formatDate(billingPeriodEnd)}</div>
                      <div className="text-sm text-gray-600">
                        Downgrade to {selectedPlan.name} plan (${selectedPlan.price}/month)
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* New Plan Summary */}
              <div className="mb-6 rounded-lg bg-blue-50 p-4">
                <div className="text-sm text-gray-600">New Plan (starting {formatDate(billingPeriodEnd)})</div>
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
