'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface PaymentMethod {
  id: string
  card_last4: string
  card_brand: string
  card_exp_month: number
  card_exp_year: number
  is_default: boolean
  created_at: string
}

export default function PaymentMethodsPage() {
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  // Form state
  const [cardNumber, setCardNumber] = useState('')
  const [cardholderName, setCardholderName] = useState('')
  const [expMonth, setExpMonth] = useState('')
  const [expYear, setExpYear] = useState('')
  const [cvc, setCvc] = useState('')

  useEffect(() => {
    fetchPaymentMethods()
  }, [])

  const fetchPaymentMethods = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/billing/payment-methods')
      if (response.ok) {
        const data = await response.json()
        setPaymentMethods(data)
      }
    } catch (error) {
      console.error('Failed to fetch payment methods:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddPaymentMethod = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)

    try {
      const response = await fetch('http://localhost:8000/api/v1/billing/payment-methods', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          card_number: cardNumber.replace(/\s/g, ''),
          card_exp_month: parseInt(expMonth),
          card_exp_year: parseInt(expYear),
          card_cvc: cvc,
          cardholder_name: cardholderName
        })
      })

      if (response.ok) {
        // Reset form
        setCardNumber('')
        setCardholderName('')
        setExpMonth('')
        setExpYear('')
        setCvc('')
        setShowAddModal(false)

        // Refresh list
        fetchPaymentMethods()
      } else {
        alert('Failed to add payment method')
      }
    } catch (error) {
      console.error('Error adding payment method:', error)
      alert('Error adding payment method')
    } finally {
      setSubmitting(false)
    }
  }

  const handleSetDefault = async (paymentMethodId: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/billing/payment-methods/set-default', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          payment_method_id: paymentMethodId
        })
      })

      if (response.ok) {
        fetchPaymentMethods()
      } else {
        alert('Failed to set default payment method')
      }
    } catch (error) {
      console.error('Error setting default:', error)
      alert('Error setting default payment method')
    }
  }

  const handleRemove = async (paymentMethodId: string) => {
    if (!confirm('Are you sure you want to remove this payment method?')) {
      return
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/billing/payment-methods/${paymentMethodId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        fetchPaymentMethods()
      } else {
        alert('Failed to remove payment method')
      }
    } catch (error) {
      console.error('Error removing payment method:', error)
      alert('Error removing payment method')
    }
  }

  const formatCardBrand = (brand: string) => {
    return brand.charAt(0).toUpperCase() + brand.slice(1)
  }

  const getCardIcon = (brand: string) => {
    // Return appropriate emoji/icon for card brand
    switch (brand.toLowerCase()) {
      case 'visa':
        return '💳'
      case 'mastercard':
        return '💳'
      case 'amex':
        return '💳'
      default:
        return '💳'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/settings/billing" className="text-sm text-gray-600 hover:text-gray-900">
            ← Back to Billing
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">Payment Methods</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Add Payment Method Button */}
        <div className="mb-6">
          <button
            onClick={() => setShowAddModal(true)}
            className="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700"
          >
            + Add Payment Method
          </button>
        </div>

        {/* Payment Methods List */}
        <div className="space-y-4">
          {loading ? (
            <div className="text-center text-gray-600">Loading...</div>
          ) : paymentMethods.length === 0 ? (
            <div className="rounded-lg bg-white p-8 text-center shadow-sm">
              <div className="text-gray-500">No payment methods added yet</div>
            </div>
          ) : (
            paymentMethods.map((pm) => (
              <div
                key={pm.id}
                className="flex items-center justify-between rounded-lg bg-white p-6 shadow-sm"
              >
                <div className="flex items-center gap-4">
                  <div className="text-3xl">{getCardIcon(pm.card_brand)}</div>
                  <div>
                    <div className="font-semibold text-gray-900">
                      {formatCardBrand(pm.card_brand)} •••• {pm.card_last4}
                    </div>
                    <div className="text-sm text-gray-600">
                      Expires {pm.card_exp_month.toString().padStart(2, '0')}/{pm.card_exp_year}
                    </div>
                    {pm.is_default && (
                      <div className="mt-1 inline-flex items-center rounded bg-green-100 px-2 py-1 text-xs font-medium text-green-700">
                        Default
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  {!pm.is_default && (
                    <button
                      onClick={() => handleSetDefault(pm.id)}
                      className="rounded border border-blue-600 px-4 py-2 text-sm text-blue-600 hover:bg-blue-50"
                    >
                      Set as Default
                    </button>
                  )}
                  <button
                    onClick={() => handleRemove(pm.id)}
                    className="rounded border border-red-600 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </main>

      {/* Add Payment Method Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <h2 className="mb-4 text-xl font-bold text-gray-900">Add Payment Method</h2>
            <form onSubmit={handleAddPaymentMethod} className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Card Number
                </label>
                <input
                  type="text"
                  value={cardNumber}
                  onChange={(e) => setCardNumber(e.target.value)}
                  placeholder="4242 4242 4242 4242"
                  maxLength={19}
                  required
                  className="w-full rounded border border-gray-300 px-3 py-2"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Cardholder Name
                </label>
                <input
                  type="text"
                  value={cardholderName}
                  onChange={(e) => setCardholderName(e.target.value)}
                  placeholder="John Doe"
                  required
                  className="w-full rounded border border-gray-300 px-3 py-2"
                />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Month
                  </label>
                  <input
                    type="text"
                    value={expMonth}
                    onChange={(e) => setExpMonth(e.target.value)}
                    placeholder="MM"
                    maxLength={2}
                    required
                    className="w-full rounded border border-gray-300 px-3 py-2"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Year
                  </label>
                  <input
                    type="text"
                    value={expYear}
                    onChange={(e) => setExpYear(e.target.value)}
                    placeholder="YYYY"
                    maxLength={4}
                    required
                    className="w-full rounded border border-gray-300 px-3 py-2"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    CVC
                  </label>
                  <input
                    type="text"
                    value={cvc}
                    onChange={(e) => setCvc(e.target.value)}
                    placeholder="123"
                    maxLength={4}
                    required
                    className="w-full rounded border border-gray-300 px-3 py-2"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="rounded border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {submitting ? 'Adding...' : 'Add Card'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
