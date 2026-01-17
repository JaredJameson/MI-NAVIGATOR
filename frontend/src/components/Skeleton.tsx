import React from 'react'

interface SkeletonProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
  animation?: 'pulse' | 'wave' | 'none'
}

/**
 * Skeleton loading component for displaying placeholder content
 * while data is being fetched.
 */
export function Skeleton({
  className = '',
  variant = 'text',
  width,
  height,
  animation = 'pulse',
}: SkeletonProps) {
  const baseClasses = 'bg-gray-200'

  const variantClasses = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-md',
  }

  const animationClasses = {
    pulse: 'animate-pulse',
    wave: 'animate-shimmer',
    none: '',
  }

  const style: React.CSSProperties = {}
  if (width) style.width = typeof width === 'number' ? `${width}px` : width
  if (height) style.height = typeof height === 'number' ? `${height}px` : height

  return (
    <div
      className={`${baseClasses} ${variantClasses[variant]} ${animationClasses[animation]} ${className}`}
      style={style}
      aria-hidden="true"
    />
  )
}

/**
 * Dashboard skeleton - matches dashboard layout
 */
export function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Skeleton */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <Skeleton width={150} height={32} />
          <div className="flex items-center gap-4">
            <Skeleton width={80} height={36} />
            <Skeleton width={80} height={36} />
            <Skeleton width={80} height={36} />
            <Skeleton width={90} height={36} variant="rectangular" />
          </div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section Skeleton */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-8 mb-8">
          <Skeleton width={200} height={32} className="bg-blue-400 mb-4" />
          <Skeleton height={48} className="bg-white/20" />
          <div className="flex gap-2 mt-4">
            <Skeleton width={120} height={32} className="bg-blue-400" />
            <Skeleton width={120} height={32} className="bg-blue-400" />
          </div>
        </div>

        {/* Widgets Grid Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Recent Activity Widget */}
          <div className="bg-white rounded-lg shadow p-6">
            <Skeleton width={150} height={24} className="mb-4" />
            <div className="space-y-3">
              <div>
                <Skeleton width="100%" height={16} />
                <Skeleton width="80%" height={14} className="mt-1" />
              </div>
              <div>
                <Skeleton width="100%" height={16} />
                <Skeleton width="70%" height={14} className="mt-1" />
              </div>
              <div>
                <Skeleton width="100%" height={16} />
                <Skeleton width="90%" height={14} className="mt-1" />
              </div>
            </div>
          </div>

          {/* Active Research Widget */}
          <div className="bg-white rounded-lg shadow p-6">
            <Skeleton width={150} height={24} className="mb-4" />
            <div>
              <Skeleton width="80%" height={18} className="mb-2" />
              <Skeleton width="60%" height={14} className="mb-3" />
              <Skeleton width="100%" height={8} className="mb-4" />
            </div>
            <div className="flex gap-2 mt-4">
              <Skeleton width={120} height={36} variant="rectangular" />
              <Skeleton width={120} height={36} variant="rectangular" />
            </div>
          </div>

          {/* Usage Stats Widget */}
          <div className="bg-white rounded-lg shadow p-6">
            <Skeleton width={120} height={24} className="mb-4" />
            <div className="space-y-4">
              <div>
                <Skeleton width="100%" height={16} className="mb-2" />
                <Skeleton width="100%" height={8} />
              </div>
              <div>
                <Skeleton width="100%" height={16} className="mb-2" />
                <Skeleton width="100%" height={8} />
              </div>
              <div>
                <Skeleton width="100%" height={16} className="mb-2" />
                <Skeleton width="70%" height={14} />
              </div>
            </div>
          </div>
        </div>

        {/* Projects Section Skeleton */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <Skeleton width={120} height={28} />
            <Skeleton width={100} height={36} variant="rectangular" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="border border-gray-200 rounded-lg p-4">
                <Skeleton width="80%" height={20} className="mb-2" />
                <Skeleton width="100%" height={14} className="mb-3" />
                <div className="flex gap-2">
                  <Skeleton width={60} height={24} variant="rectangular" />
                  <Skeleton width={60} height={24} variant="rectangular" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}

/**
 * Card skeleton - for lists of cards
 */
export function CardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <Skeleton width="80%" height={24} className="mb-3" />
      <Skeleton width="100%" height={16} className="mb-2" />
      <Skeleton width="90%" height={16} className="mb-4" />
      <div className="flex gap-2">
        <Skeleton width={80} height={32} variant="rectangular" />
        <Skeleton width={80} height={32} variant="rectangular" />
      </div>
    </div>
  )
}

/**
 * Table row skeleton
 */
export function TableRowSkeleton({ columns = 4 }: { columns?: number }) {
  return (
    <tr>
      {Array.from({ length: columns }).map((_, i) => (
        <td key={i} className="px-6 py-4">
          <Skeleton height={16} />
        </td>
      ))}
    </tr>
  )
}

/**
 * List skeleton - for vertical lists
 */
export function ListSkeleton({ items = 5 }: { items?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <Skeleton variant="circular" width={40} height={40} />
          <div className="flex-1">
            <Skeleton width="60%" height={16} className="mb-1" />
            <Skeleton width="40%" height={14} />
          </div>
        </div>
      ))}
    </div>
  )
}

/**
 * Report list skeleton - for reports page
 */
export function ReportListSkeleton({ items = 5 }: { items?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <Skeleton width="70%" height={24} className="mb-2" />
              <Skeleton width="40%" height={16} />
            </div>
            <Skeleton width={100} height={28} variant="rectangular" />
          </div>
          <Skeleton width="100%" height={16} className="mb-2" />
          <Skeleton width="85%" height={16} className="mb-4" />
          <div className="flex items-center gap-4">
            <Skeleton width={120} height={20} />
            <Skeleton width={80} height={20} />
            <Skeleton width={100} height={20} />
          </div>
        </div>
      ))}
    </div>
  )
}
