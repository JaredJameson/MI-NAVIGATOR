/**
 * A/B Testing Service
 * Client-side integration with A/B testing API
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api/proxy'

export interface ABTestVariant {
  experiment: string
  variant: 'A' | 'B'
  session_id: string
  user_id: string | null
  timestamp: string
}

/**
 * Get or assign A/B test variant for current user/session
 */
export async function getVariant(experiment: string = 'default_experiment'): Promise<ABTestVariant> {
  const response = await fetch(`${API_BASE}/ab-testing/variant?experiment=${experiment}`, {
    method: 'GET',
    credentials: 'include', // Include cookies
  })

  if (!response.ok) {
    throw new Error(`Failed to get A/B test variant: ${response.statusText}`)
  }

  return response.json()
}

/**
 * Track an A/B test event
 */
export async function trackEvent(
  experiment: string,
  variant: string,
  eventName: string
): Promise<void> {
  const response = await fetch(`${API_BASE}/ab-testing/track`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({
      experiment,
      variant,
      event_name: eventName,
    }),
  })

  if (!response.ok) {
    console.error(`Failed to track A/B test event: ${response.statusText}`)
    // Don't throw - tracking failures shouldn't break the app
  }
}
