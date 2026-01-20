/**
 * useABTest Hook
 * React hook for A/B testing
 */

import { useState, useEffect } from 'react'
import { getVariant, trackEvent, ABTestVariant } from '@/services/abTesting'

export function useABTest(experimentName: string = 'default_experiment') {
  const [variant, setVariant] = useState<'A' | 'B' | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [variantData, setVariantData] = useState<ABTestVariant | null>(null)

  useEffect(() => {
    let isMounted = true

    async function fetchVariant() {
      try {
        setIsLoading(true)
        const data = await getVariant(experimentName)

        if (isMounted) {
          setVariant(data.variant)
          setVariantData(data)
          setError(null)

          // Log assignment to console (for debugging)
          console.log(`[A/B Test] Assigned to variant ${data.variant} for experiment "${experimentName}"`)
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to get variant')
          // Default to variant A on error
          setVariant('A')
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    fetchVariant()

    return () => {
      isMounted = false
    }
  }, [experimentName])

  /**
   * Track an event for this experiment
   */
  const track = async (eventName: string) => {
    if (!variant || !variantData) {
      console.warn('[A/B Test] Cannot track event - variant not assigned yet')
      return
    }

    try {
      await trackEvent(experimentName, variant, eventName)
      console.log(`[A/B Test] Tracked event "${eventName}" for variant ${variant}`)
    } catch (err) {
      console.error('[A/B Test] Failed to track event:', err)
    }
  }

  return {
    variant,
    isLoading,
    error,
    track,
    variantData,
  }
}
