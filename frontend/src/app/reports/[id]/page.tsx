'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { getStoredToken } from '@/services/api'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { toast } from 'sonner'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// Helper function to get CSRF token
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

interface ReportSection {
  id: string
  title: string
  content: string
}

interface ReportSource {
  name: string
  confidence: number
  url: string
}

interface ReportDetail {
  id: string
  title: string
  type: string
  company: string | null
  created_at: string
  updated_at: string
  status: string
  summary: string
  sections: ReportSection[]
  sources: ReportSource[]
  is_favorite?: boolean
  is_archived?: boolean
}

interface SearchMatch {
  sectionId: string
  sectionTitle: string
  startIndex: number
  endIndex: number
  context: string
}

interface Annotation {
  id: string
  report_id: string
  section_id: string
  selected_text: string
  start_offset: number
  end_offset: number
  comment: string
  created_at: string
  user_id: string
}

interface ReportVersion {
  version: number
  created_at: string
  author: string
  changes: string
  is_current: boolean
}

interface Comment {
  id: string
  report_id: string
  user_id: string
  user_name: string
  user_email: string
  text: string
  created_at: string
  parent_id: string | null
  resolved: boolean
  resolved_by: string | null
  resolved_by_name: string | null
  resolved_at: string | null
}

interface SWOTData {
  strengths: string[]
  weaknesses: string[]
  opportunities: string[]
  threats: string[]
}

// Function to parse SWOT content
function parseSWOTContent(content: string): SWOTData | null {
  const strengths: string[] = []
  const weaknesses: string[] = []
  const opportunities: string[] = []
  const threats: string[] = []

  // Identify which quadrant we're currently parsing
  let currentSection: 'strengths' | 'weaknesses' | 'opportunities' | 'threats' | null = null

  const lines = content.split('\n')

  for (const line of lines) {
    const trimmedLine = line.trim()

    // Detect section headers
    if (trimmedLine.toLowerCase().includes('mocne strony') || trimmedLine.toLowerCase().includes('strengths')) {
      currentSection = 'strengths'
      continue
    } else if (trimmedLine.toLowerCase().includes('słabe strony') || trimmedLine.toLowerCase().includes('weaknesses')) {
      currentSection = 'weaknesses'
      continue
    } else if (trimmedLine.toLowerCase().includes('szanse') || trimmedLine.toLowerCase().includes('opportunities')) {
      currentSection = 'opportunities'
      continue
    } else if (trimmedLine.toLowerCase().includes('zagrożenia') || trimmedLine.toLowerCase().includes('threats')) {
      currentSection = 'threats'
      continue
    }

    // Parse bullet points (starting with -)
    if (trimmedLine.startsWith('-') && currentSection) {
      const item = trimmedLine.substring(1).trim()
      if (item) {
        switch (currentSection) {
          case 'strengths':
            strengths.push(item)
            break
          case 'weaknesses':
            weaknesses.push(item)
            break
          case 'opportunities':
            opportunities.push(item)
            break
          case 'threats':
            threats.push(item)
            break
        }
      }
    }
  }

  // Only return SWOT data if we found at least some items
  if (strengths.length === 0 && weaknesses.length === 0 && opportunities.length === 0 && threats.length === 0) {
    return null
  }

  return { strengths, weaknesses, opportunities, threats }
}

// SWOT Diagram Component
function SWOTDiagram({ data, onItemClick }: { data: SWOTData, onItemClick?: (quadrant: string, item: string) => void }) {
  const [expandedQuadrant, setExpandedQuadrant] = useState<string | null>(null)
  const [hoveredItem, setHoveredItem] = useState<string | null>(null)

  const quadrants = [
    {
      key: 'strengths',
      title: 'Mocne strony',
      subtitle: 'Strengths',
      items: data.strengths,
      bgColor: 'bg-green-50',
      borderColor: 'border-green-300',
      headerBg: 'bg-green-500',
      headerText: 'text-white',
      itemBg: 'bg-green-100',
      itemText: 'text-green-800',
      icon: '💪',
      hoverBg: 'hover:bg-green-200',
    },
    {
      key: 'weaknesses',
      title: 'Słabe strony',
      subtitle: 'Weaknesses',
      items: data.weaknesses,
      bgColor: 'bg-red-50',
      borderColor: 'border-red-300',
      headerBg: 'bg-red-500',
      headerText: 'text-white',
      itemBg: 'bg-red-100',
      itemText: 'text-red-800',
      icon: '⚠️',
      hoverBg: 'hover:bg-red-200',
    },
    {
      key: 'opportunities',
      title: 'Szanse',
      subtitle: 'Opportunities',
      items: data.opportunities,
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-300',
      headerBg: 'bg-blue-500',
      headerText: 'text-white',
      itemBg: 'bg-blue-100',
      itemText: 'text-blue-800',
      icon: '🚀',
      hoverBg: 'hover:bg-blue-200',
    },
    {
      key: 'threats',
      title: 'Zagrożenia',
      subtitle: 'Threats',
      items: data.threats,
      bgColor: 'bg-amber-50',
      borderColor: 'border-amber-300',
      headerBg: 'bg-amber-500',
      headerText: 'text-white',
      itemBg: 'bg-amber-100',
      itemText: 'text-amber-800',
      icon: '⚡',
      hoverBg: 'hover:bg-amber-200',
    },
  ]

  const toggleExpand = (key: string) => {
    setExpandedQuadrant(expandedQuadrant === key ? null : key)
  }

  return (
    <div className="w-full">
      {/* SWOT Grid */}
      <div className="grid grid-cols-2 gap-4">
        {/* Internal Factors Label */}
        <div className="col-span-2 flex items-center justify-center">
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <span className="text-green-500">●</span> Pozytywne
            </span>
            <span className="mx-4 text-gray-300">|</span>
            <span className="flex items-center gap-1">
              <span className="text-red-500">●</span> Negatywne
            </span>
          </div>
        </div>

        {/* Row 1: Internal factors */}
        <div className="col-span-2 text-center text-xs text-gray-400 uppercase tracking-wider mb-1">
          Czynniki wewnętrzne
        </div>

        {/* Strengths */}
        <div
          className={`${quadrants[0].bgColor} ${quadrants[0].borderColor} border-2 rounded-xl overflow-hidden transition-all duration-300 ${expandedQuadrant === 'strengths' ? 'ring-2 ring-green-400 shadow-lg' : ''}`}
        >
          <div
            className={`${quadrants[0].headerBg} ${quadrants[0].headerText} px-4 py-3 flex items-center justify-between cursor-pointer`}
            onClick={() => toggleExpand('strengths')}
          >
            <div className="flex items-center gap-2">
              <span className="text-xl">{quadrants[0].icon}</span>
              <div>
                <div className="font-semibold">{quadrants[0].title}</div>
                <div className="text-xs opacity-80">{quadrants[0].subtitle}</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="bg-white/20 px-2 py-0.5 rounded-full text-sm">{quadrants[0].items.length}</span>
              <svg
                className={`h-5 w-5 transition-transform duration-300 ${expandedQuadrant === 'strengths' ? 'rotate-180' : ''}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
          <div className={`p-4 transition-all duration-300 ${expandedQuadrant === 'strengths' ? 'max-h-96' : 'max-h-48'} overflow-y-auto`}>
            <ul className="space-y-2">
              {quadrants[0].items.map((item, idx) => (
                <li
                  key={idx}
                  className={`${quadrants[0].itemBg} ${quadrants[0].itemText} ${quadrants[0].hoverBg} px-3 py-2 rounded-lg text-sm cursor-pointer transition-colors duration-200`}
                  onClick={() => onItemClick?.('strengths', item)}
                  onMouseEnter={() => setHoveredItem(`strengths-${idx}`)}
                  onMouseLeave={() => setHoveredItem(null)}
                >
                  <span className="mr-2">✓</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Weaknesses */}
        <div
          className={`${quadrants[1].bgColor} ${quadrants[1].borderColor} border-2 rounded-xl overflow-hidden transition-all duration-300 ${expandedQuadrant === 'weaknesses' ? 'ring-2 ring-red-400 shadow-lg' : ''}`}
        >
          <div
            className={`${quadrants[1].headerBg} ${quadrants[1].headerText} px-4 py-3 flex items-center justify-between cursor-pointer`}
            onClick={() => toggleExpand('weaknesses')}
          >
            <div className="flex items-center gap-2">
              <span className="text-xl">{quadrants[1].icon}</span>
              <div>
                <div className="font-semibold">{quadrants[1].title}</div>
                <div className="text-xs opacity-80">{quadrants[1].subtitle}</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="bg-white/20 px-2 py-0.5 rounded-full text-sm">{quadrants[1].items.length}</span>
              <svg
                className={`h-5 w-5 transition-transform duration-300 ${expandedQuadrant === 'weaknesses' ? 'rotate-180' : ''}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
          <div className={`p-4 transition-all duration-300 ${expandedQuadrant === 'weaknesses' ? 'max-h-96' : 'max-h-48'} overflow-y-auto`}>
            <ul className="space-y-2">
              {quadrants[1].items.map((item, idx) => (
                <li
                  key={idx}
                  className={`${quadrants[1].itemBg} ${quadrants[1].itemText} ${quadrants[1].hoverBg} px-3 py-2 rounded-lg text-sm cursor-pointer transition-colors duration-200`}
                  onClick={() => onItemClick?.('weaknesses', item)}
                  onMouseEnter={() => setHoveredItem(`weaknesses-${idx}`)}
                  onMouseLeave={() => setHoveredItem(null)}
                >
                  <span className="mr-2">✗</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Row 2: External factors */}
        <div className="col-span-2 text-center text-xs text-gray-400 uppercase tracking-wider mt-2 mb-1">
          Czynniki zewnętrzne
        </div>

        {/* Opportunities */}
        <div
          className={`${quadrants[2].bgColor} ${quadrants[2].borderColor} border-2 rounded-xl overflow-hidden transition-all duration-300 ${expandedQuadrant === 'opportunities' ? 'ring-2 ring-blue-400 shadow-lg' : ''}`}
        >
          <div
            className={`${quadrants[2].headerBg} ${quadrants[2].headerText} px-4 py-3 flex items-center justify-between cursor-pointer`}
            onClick={() => toggleExpand('opportunities')}
          >
            <div className="flex items-center gap-2">
              <span className="text-xl">{quadrants[2].icon}</span>
              <div>
                <div className="font-semibold">{quadrants[2].title}</div>
                <div className="text-xs opacity-80">{quadrants[2].subtitle}</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="bg-white/20 px-2 py-0.5 rounded-full text-sm">{quadrants[2].items.length}</span>
              <svg
                className={`h-5 w-5 transition-transform duration-300 ${expandedQuadrant === 'opportunities' ? 'rotate-180' : ''}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
          <div className={`p-4 transition-all duration-300 ${expandedQuadrant === 'opportunities' ? 'max-h-96' : 'max-h-48'} overflow-y-auto`}>
            <ul className="space-y-2">
              {quadrants[2].items.map((item, idx) => (
                <li
                  key={idx}
                  className={`${quadrants[2].itemBg} ${quadrants[2].itemText} ${quadrants[2].hoverBg} px-3 py-2 rounded-lg text-sm cursor-pointer transition-colors duration-200`}
                  onClick={() => onItemClick?.('opportunities', item)}
                  onMouseEnter={() => setHoveredItem(`opportunities-${idx}`)}
                  onMouseLeave={() => setHoveredItem(null)}
                >
                  <span className="mr-2">→</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Threats */}
        <div
          className={`${quadrants[3].bgColor} ${quadrants[3].borderColor} border-2 rounded-xl overflow-hidden transition-all duration-300 ${expandedQuadrant === 'threats' ? 'ring-2 ring-amber-400 shadow-lg' : ''}`}
        >
          <div
            className={`${quadrants[3].headerBg} ${quadrants[3].headerText} px-4 py-3 flex items-center justify-between cursor-pointer`}
            onClick={() => toggleExpand('threats')}
          >
            <div className="flex items-center gap-2">
              <span className="text-xl">{quadrants[3].icon}</span>
              <div>
                <div className="font-semibold">{quadrants[3].title}</div>
                <div className="text-xs opacity-80">{quadrants[3].subtitle}</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="bg-white/20 px-2 py-0.5 rounded-full text-sm">{quadrants[3].items.length}</span>
              <svg
                className={`h-5 w-5 transition-transform duration-300 ${expandedQuadrant === 'threats' ? 'rotate-180' : ''}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
          <div className={`p-4 transition-all duration-300 ${expandedQuadrant === 'threats' ? 'max-h-96' : 'max-h-48'} overflow-y-auto`}>
            <ul className="space-y-2">
              {quadrants[3].items.map((item, idx) => (
                <li
                  key={idx}
                  className={`${quadrants[3].itemBg} ${quadrants[3].itemText} ${quadrants[3].hoverBg} px-3 py-2 rounded-lg text-sm cursor-pointer transition-colors duration-200`}
                  onClick={() => onItemClick?.('threats', item)}
                  onMouseEnter={() => setHoveredItem(`threats-${idx}`)}
                  onMouseLeave={() => setHoveredItem(null)}
                >
                  <span className="mr-2">!</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Legend / Summary */}
      <div className="mt-4 flex items-center justify-center gap-6 text-xs text-gray-500">
        <div className="flex items-center gap-1">
          <span className="h-3 w-3 rounded bg-green-500"></span>
          <span>S: {data.strengths.length}</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="h-3 w-3 rounded bg-red-500"></span>
          <span>W: {data.weaknesses.length}</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="h-3 w-3 rounded bg-blue-500"></span>
          <span>O: {data.opportunities.length}</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="h-3 w-3 rounded bg-amber-500"></span>
          <span>T: {data.threats.length}</span>
        </div>
        <span className="text-gray-400">|</span>
        <span>Razem: {data.strengths.length + data.weaknesses.length + data.opportunities.length + data.threats.length} czynników</span>
      </div>

      {/* Tip for interaction */}
      <div className="mt-3 text-center text-xs text-gray-400">
        💡 Kliknij nagłówek sekcji, aby ją rozwinąć
      </div>
    </div>
  )
}

// Helper function to check if section is SWOT
function isSWOTSection(title: string): boolean {
  return title.toLowerCase().includes('swot') ||
         (title.toLowerCase().includes('analiza') &&
          (title.toLowerCase().includes('mocne') || title.toLowerCase().includes('słabe')))
}

// ===== PORTER FIVE FORCES TYPES AND COMPONENT =====

interface PorterForce {
  name: string
  englishName: string
  strength: 'NISKA' | 'ŚREDNIA' | 'WYSOKA'
  strengthValue: number // 1-3 for visualization
  points: string[]
}

interface PorterData {
  supplierPower: PorterForce
  buyerPower: PorterForce
  substitutes: PorterForce
  newEntrants: PorterForce
  industryRivalry: PorterForce
}

// Parse Porter Five Forces content
function parsePorterContent(content: string): PorterData | null {
  const forces: Partial<PorterData> = {}

  // Define patterns for each force
  const forcePatterns = [
    { key: 'supplierPower', patterns: ['siła przetargowa dostawców', 'supplier power'] },
    { key: 'buyerPower', patterns: ['siła przetargowa nabywców', 'buyer power'] },
    { key: 'substitutes', patterns: ['zagrożenie ze strony substytutów', 'threat of substitutes'] },
    { key: 'newEntrants', patterns: ['zagrożenie ze strony nowych', 'threat of new entrants'] },
    { key: 'industryRivalry', patterns: ['rywalizacja wewnątrz', 'industry rivalry', 'rivalry'] }
  ]

  const forceNames: Record<string, { name: string; englishName: string }> = {
    supplierPower: { name: 'Siła dostawców', englishName: 'Supplier Power' },
    buyerPower: { name: 'Siła nabywców', englishName: 'Buyer Power' },
    substitutes: { name: 'Zagrożenie substytutów', englishName: 'Threat of Substitutes' },
    newEntrants: { name: 'Nowi wchodzący', englishName: 'Threat of New Entrants' },
    industryRivalry: { name: 'Rywalizacja', englishName: 'Industry Rivalry' }
  }

  const strengthMap: Record<string, { strength: 'NISKA' | 'ŚREDNIA' | 'WYSOKA'; value: number }> = {
    'niska': { strength: 'NISKA', value: 1 },
    'low': { strength: 'NISKA', value: 1 },
    'średnia': { strength: 'ŚREDNIA', value: 2 },
    'medium': { strength: 'ŚREDNIA', value: 2 },
    'moderate': { strength: 'ŚREDNIA', value: 2 },
    'wysoka': { strength: 'WYSOKA', value: 3 },
    'high': { strength: 'WYSOKA', value: 3 }
  }

  const lines = content.split('\n')
  let currentForce: string | null = null
  let currentPoints: string[] = []

  for (const line of lines) {
    const trimmedLine = line.trim()
    const lowerLine = trimmedLine.toLowerCase()

    // Check if this line starts a new force section
    let foundForce: { key: string; patterns: string[] } | null = null
    for (const force of forcePatterns) {
      if (force.patterns.some(p => lowerLine.includes(p))) {
        foundForce = force
        break
      }
    }

    if (foundForce) {
      // Save previous force if exists
      if (currentForce && currentPoints.length > 0) {
        const forceData = forces[currentForce as keyof PorterData]
        if (forceData) {
          forceData.points = currentPoints
        }
      }

      // Parse strength from the line (e.g., "WYSOKA", "ŚREDNIA", "NISKA")
      let strength: 'NISKA' | 'ŚREDNIA' | 'WYSOKA' = 'ŚREDNIA'
      let strengthValue = 2

      for (const [key, val] of Object.entries(strengthMap)) {
        if (lowerLine.includes(key)) {
          strength = val.strength
          strengthValue = val.value
          break
        }
      }

      forces[foundForce.key as keyof PorterData] = {
        name: forceNames[foundForce.key].name,
        englishName: forceNames[foundForce.key].englishName,
        strength,
        strengthValue,
        points: []
      }

      currentForce = foundForce.key
      currentPoints = []
      continue
    }

    // Parse bullet points for current force
    if (currentForce && trimmedLine.startsWith('-')) {
      const point = trimmedLine.substring(1).trim()
      if (point) {
        currentPoints.push(point)
      }
    }
  }

  // Save last force
  if (currentForce && currentPoints.length > 0) {
    const forceData = forces[currentForce as keyof PorterData]
    if (forceData) {
      forceData.points = currentPoints
    }
  }

  // Check if we have at least 3 forces parsed
  const parsedForces = Object.keys(forces).length
  if (parsedForces < 3) {
    return null
  }

  // Fill in missing forces with defaults
  const defaultForce = (name: string, englishName: string): PorterForce => ({
    name,
    englishName,
    strength: 'ŚREDNIA',
    strengthValue: 2,
    points: ['Dane niedostępne']
  })

  return {
    supplierPower: forces.supplierPower || defaultForce('Siła dostawców', 'Supplier Power'),
    buyerPower: forces.buyerPower || defaultForce('Siła nabywców', 'Buyer Power'),
    substitutes: forces.substitutes || defaultForce('Zagrożenie substytutów', 'Threat of Substitutes'),
    newEntrants: forces.newEntrants || defaultForce('Nowi wchodzący', 'Threat of New Entrants'),
    industryRivalry: forces.industryRivalry || defaultForce('Rywalizacja', 'Industry Rivalry')
  }
}

// Helper function to check if section is Porter Five Forces
function isPorterSection(title: string): boolean {
  const lowerTitle = title.toLowerCase()
  return lowerTitle.includes('porter') ||
         lowerTitle.includes('five forces') ||
         lowerTitle.includes('pięć sił') ||
         (lowerTitle.includes('analiza') && lowerTitle.includes('sił'))
}

// ===== TAM SAM SOM TYPES AND COMPONENT =====

interface MarketSizeData {
  name: string
  englishName: string
  value: number
  valueFormatted: string
  description: string
  color: string
}

interface TAMSAMSOMData {
  tam: MarketSizeData
  sam: MarketSizeData
  som: MarketSizeData
  methodology?: string[]
  growth?: { label: string; value: string }[]
}

// Parse TAM SAM SOM content
function parseTAMSAMSOMContent(content: string): TAMSAMSOMData | null {
  const data: Partial<TAMSAMSOMData> = {}

  // Patterns to detect TAM, SAM, SOM sections
  const patterns = {
    tam: ['tam', 'total addressable market', 'całkowity rynek'],
    sam: ['sam', 'serviceable addressable market', 'rynek docelowy'],
    som: ['som', 'serviceable obtainable market', 'rynek osiągalny']
  }

  const lines = content.split('\n')
  let currentSection: 'tam' | 'sam' | 'som' | 'methodology' | 'growth' | null = null
  let currentValue = 0
  let currentValueFormatted = ''
  let currentDescription = ''
  const methodologyPoints: string[] = []
  const growthPoints: { label: string; value: string }[] = []

  for (const line of lines) {
    const trimmedLine = line.trim()
    const lowerLine = trimmedLine.toLowerCase()

    // Check for TAM section
    if (patterns.tam.some(p => lowerLine.includes(p)) && !data.tam) {
      currentSection = 'tam'
      continue
    }

    // Check for SAM section
    if (patterns.sam.some(p => lowerLine.includes(p)) && !data.sam) {
      // Save previous TAM if we have data
      if (currentSection === 'tam' && currentValue > 0) {
        data.tam = {
          name: 'TAM',
          englishName: 'Total Addressable Market',
          value: currentValue,
          valueFormatted: currentValueFormatted,
          description: currentDescription,
          color: 'blue'
        }
        currentValue = 0
        currentValueFormatted = ''
        currentDescription = ''
      }
      currentSection = 'sam'
      continue
    }

    // Check for SOM section
    if (patterns.som.some(p => lowerLine.includes(p)) && !data.som) {
      // Save previous SAM if we have data
      if (currentSection === 'sam' && currentValue > 0) {
        data.sam = {
          name: 'SAM',
          englishName: 'Serviceable Addressable Market',
          value: currentValue,
          valueFormatted: currentValueFormatted,
          description: currentDescription,
          color: 'green'
        }
        currentValue = 0
        currentValueFormatted = ''
        currentDescription = ''
      }
      currentSection = 'som'
      continue
    }

    // Check for methodology section
    if (lowerLine.includes('metodolog')) {
      // Save previous SOM if we have data
      if (currentSection === 'som' && currentValue > 0) {
        data.som = {
          name: 'SOM',
          englishName: 'Serviceable Obtainable Market',
          value: currentValue,
          valueFormatted: currentValueFormatted,
          description: currentDescription,
          color: 'purple'
        }
        currentValue = 0
        currentValueFormatted = ''
        currentDescription = ''
      }
      currentSection = 'methodology'
      continue
    }

    // Check for growth/prognoza section
    if (lowerLine.includes('prognoz') || lowerLine.includes('wzrost') || lowerLine.includes('cagr')) {
      currentSection = 'growth'
      continue
    }

    // Parse value lines (e.g., "Wartość: 85 mld PLN")
    if (currentSection && ['tam', 'sam', 'som'].includes(currentSection)) {
      const valueMatch = trimmedLine.match(/wartość[:\s]*([0-9,\.]+)\s*(mld|mln|tys\.?)\s*(PLN|EUR|USD)?/i)
      if (valueMatch) {
        const numStr = valueMatch[1].replace(',', '.')
        let num = parseFloat(numStr)
        const unit = valueMatch[2].toLowerCase()

        // Convert to millions for consistent comparison
        if (unit === 'mld') {
          num = num * 1000 // Convert to millions
        } else if (unit.includes('tys')) {
          num = num / 1000 // Convert to millions
        }

        currentValue = num
        currentValueFormatted = `${valueMatch[1]} ${valueMatch[2]} ${valueMatch[3] || 'PLN'}`.trim()
        continue
      }

      // Parse description lines
      if (lowerLine.startsWith('opis:')) {
        currentDescription = trimmedLine.substring(5).trim()
        continue
      }
    }

    // Parse methodology bullet points
    if (currentSection === 'methodology' && trimmedLine.startsWith('-')) {
      methodologyPoints.push(trimmedLine.substring(1).trim())
      continue
    }

    // Parse growth bullet points (e.g., "- TAM: 3,2% rocznie")
    if (currentSection === 'growth' && trimmedLine.startsWith('-')) {
      const growthMatch = trimmedLine.match(/^-\s*(\w+):\s*(.+)$/)
      if (growthMatch) {
        growthPoints.push({ label: growthMatch[1], value: growthMatch[2] })
      }
      continue
    }
  }

  // Save last section (SOM) if not already saved
  if (currentSection === 'som' && currentValue > 0 && !data.som) {
    data.som = {
      name: 'SOM',
      englishName: 'Serviceable Obtainable Market',
      value: currentValue,
      valueFormatted: currentValueFormatted,
      description: currentDescription,
      color: 'purple'
    }
  }

  // Only return if we have at least TAM and SOM
  if (!data.tam || !data.som) {
    return null
  }

  // Fill in SAM if missing (estimate as average)
  if (!data.sam) {
    data.sam = {
      name: 'SAM',
      englishName: 'Serviceable Addressable Market',
      value: (data.tam.value + data.som.value) / 2,
      valueFormatted: 'Szacunkowa',
      description: 'Wartość szacunkowa',
      color: 'green'
    }
  }

  return {
    tam: data.tam,
    sam: data.sam,
    som: data.som,
    methodology: methodologyPoints.length > 0 ? methodologyPoints : undefined,
    growth: growthPoints.length > 0 ? growthPoints : undefined
  }
}

// Helper function to check if section is TAM SAM SOM
function isTAMSAMSOMSection(title: string): boolean {
  const lowerTitle = title.toLowerCase()
  return (lowerTitle.includes('tam') && lowerTitle.includes('sam')) ||
         lowerTitle.includes('tam sam som') ||
         (lowerTitle.includes('wielkość') && lowerTitle.includes('rynku') &&
          (lowerTitle.includes('tam') || lowerTitle.includes('som')))
}

// TAM SAM SOM Diagram Component - Concentric Circles
function TAMSAMSOMDiagram({ data, onSegmentClick }: { data: TAMSAMSOMData; onSegmentClick?: (segment: string) => void }) {
  const [selectedSegment, setSelectedSegment] = useState<string | null>(null)
  const [hoveredSegment, setHoveredSegment] = useState<string | null>(null)

  const handleClick = (segment: string) => {
    setSelectedSegment(selectedSegment === segment ? null : segment)
    onSegmentClick?.(segment)
  }

  // Calculate relative sizes for circles (TAM is largest, SOM is smallest)
  const maxValue = data.tam.value
  const tamSize = 100
  const samSize = (data.sam.value / maxValue) * 100
  const somSize = (data.som.value / maxValue) * 100

  // Minimum size to keep circles visible
  const minSize = 15
  const tamRadius = 45 // percentage
  const samRadius = Math.max(tamRadius * (samSize / 100), minSize)
  const somRadius = Math.max(tamRadius * (somSize / 100), minSize / 2)

  const segments = [
    { key: 'tam', data: data.tam, radius: tamRadius, color: 'bg-blue-500', borderColor: 'border-blue-600', textColor: 'text-blue-700', lightBg: 'bg-blue-100' },
    { key: 'sam', data: data.sam, radius: samRadius, color: 'bg-green-500', borderColor: 'border-green-600', textColor: 'text-green-700', lightBg: 'bg-green-100' },
    { key: 'som', data: data.som, radius: somRadius, color: 'bg-purple-500', borderColor: 'border-purple-600', textColor: 'text-purple-700', lightBg: 'bg-purple-100' }
  ]

  return (
    <div className="w-full">
      {/* Concentric Circles Visualization */}
      <div className="relative mx-auto" style={{ width: '100%', maxWidth: '500px', height: '400px' }}>
        <div className="absolute inset-0 flex items-center justify-center">
          {/* TAM - Outer circle (z-index: 1) */}
          <div
            className={`absolute rounded-full border-4 transition-all duration-300 cursor-pointer flex items-center justify-center z-[1] ${
              selectedSegment === 'tam' || hoveredSegment === 'tam'
                ? 'border-blue-600 bg-blue-100 shadow-lg scale-105'
                : 'border-blue-400 bg-blue-50'
            }`}
            style={{ width: `${tamRadius * 2}%`, height: `${tamRadius * 2}%` }}
            onClick={() => handleClick('tam')}
            onMouseEnter={() => setHoveredSegment('tam')}
            onMouseLeave={() => setHoveredSegment(null)}
          >
            {/* TAM Label - top */}
            <div className="absolute -top-8 left-1/2 -translate-x-1/2 text-center whitespace-nowrap">
              <div className="font-bold text-blue-700">TAM</div>
              <div className="text-sm text-blue-600">{data.tam.valueFormatted}</div>
            </div>
          </div>

          {/* SAM - Middle circle (z-index: 2) */}
          <div
            className={`absolute rounded-full border-4 transition-all duration-300 cursor-pointer flex items-center justify-center z-[2] ${
              selectedSegment === 'sam' || hoveredSegment === 'sam'
                ? 'border-green-600 bg-green-100 shadow-lg scale-105'
                : 'border-green-400 bg-green-50'
            }`}
            style={{ width: `${samRadius * 2}%`, height: `${samRadius * 2}%` }}
            onClick={() => handleClick('sam')}
            onMouseEnter={() => setHoveredSegment('sam')}
            onMouseLeave={() => setHoveredSegment(null)}
          >
            {/* SAM Label - right side */}
            <div className="absolute -right-20 top-1/2 -translate-y-1/2 text-center whitespace-nowrap">
              <div className="font-bold text-green-700">SAM</div>
              <div className="text-sm text-green-600">{data.sam.valueFormatted}</div>
            </div>
          </div>

          {/* SOM - Inner circle (z-index: 3 - highest to be always clickable) */}
          <div
            className={`absolute rounded-full border-4 transition-all duration-300 cursor-pointer flex items-center justify-center z-[3] ${
              selectedSegment === 'som' || hoveredSegment === 'som'
                ? 'border-purple-600 bg-purple-200 shadow-lg scale-110'
                : 'border-purple-400 bg-purple-100'
            }`}
            style={{ width: `${somRadius * 2}%`, height: `${somRadius * 2}%`, minWidth: '80px', minHeight: '80px' }}
            onClick={() => handleClick('som')}
            onMouseEnter={() => setHoveredSegment('som')}
            onMouseLeave={() => setHoveredSegment(null)}
          >
            <div className="text-center">
              <div className="font-bold text-purple-700 text-sm">SOM</div>
              <div className="text-xs text-purple-600">{data.som.valueFormatted}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Selected Segment Details */}
      {selectedSegment && (
        <div className="mt-6 rounded-xl bg-white border-2 border-gray-200 p-6 shadow-md">
          {segments.filter(s => s.key === selectedSegment).map(segment => (
            <div key={segment.key}>
              <div className="flex items-center gap-3 mb-4">
                <div className={`w-12 h-12 rounded-full ${segment.color} flex items-center justify-center`}>
                  <span className="text-white font-bold text-lg">{segment.data.name}</span>
                </div>
                <div>
                  <h3 className="font-bold text-lg text-gray-800">{segment.data.englishName}</h3>
                  <span className={`text-2xl font-bold ${segment.textColor}`}>{segment.data.valueFormatted}</span>
                </div>
              </div>
              {segment.data.description && (
                <p className="text-gray-600">{segment.data.description}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Legend */}
      <div className="mt-6 flex flex-wrap items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <span className="h-4 w-4 rounded-full bg-blue-500"></span>
          <span className="text-gray-700 font-medium">TAM</span>
          <span className="text-gray-500">- Całkowity Rynek</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-4 w-4 rounded-full bg-green-500"></span>
          <span className="text-gray-700 font-medium">SAM</span>
          <span className="text-gray-500">- Rynek Docelowy</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-4 w-4 rounded-full bg-purple-500"></span>
          <span className="text-gray-700 font-medium">SOM</span>
          <span className="text-gray-500">- Rynek Osiągalny</span>
        </div>
      </div>

      {/* Methodology if available */}
      {data.methodology && data.methodology.length > 0 && (
        <div className="mt-6 rounded-lg bg-gray-50 p-4">
          <h4 className="font-semibold text-gray-700 mb-2">📐 Metodologia kalkulacji:</h4>
          <ul className="space-y-1">
            {data.methodology.map((point, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                <span className="text-gray-400">•</span>
                {point}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Growth Projections if available */}
      {data.growth && data.growth.length > 0 && (
        <div className="mt-4 rounded-lg bg-gradient-to-r from-green-50 to-blue-50 p-4">
          <h4 className="font-semibold text-gray-700 mb-2">📈 Prognoza wzrostu:</h4>
          <div className="flex flex-wrap gap-4">
            {data.growth.map((item, idx) => (
              <div key={idx} className="flex items-center gap-2 text-sm">
                <span className={`font-bold ${
                  item.label.toUpperCase() === 'TAM' ? 'text-blue-600' :
                  item.label.toUpperCase() === 'SAM' ? 'text-green-600' :
                  'text-purple-600'
                }`}>{item.label}:</span>
                <span className="text-gray-700">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Summary Stats */}
      <div className="mt-4 text-center text-xs text-gray-500">
        <span className="inline-flex items-center gap-1">
          📊 Model TAM SAM SOM - Analiza wielkości rynku
        </span>
      </div>

      {/* Tip */}
      <div className="mt-3 text-center text-xs text-gray-400">
        💡 Kliknij okrąg, aby zobaczyć szczegóły
      </div>
    </div>
  )
}

// Porter Five Forces Diagram Component
function PorterDiagram({ data, onForceClick }: { data: PorterData; onForceClick?: (force: string) => void }) {
  const [selectedForce, setSelectedForce] = useState<string | null>(null)
  const [hoveredForce, setHoveredForce] = useState<string | null>(null)

  const forces = [
    { key: 'supplierPower', data: data.supplierPower, position: 'top', icon: '🏭', color: 'purple' },
    { key: 'newEntrants', data: data.newEntrants, position: 'top-right', icon: '🚪', color: 'orange' },
    { key: 'buyerPower', data: data.buyerPower, position: 'bottom-right', icon: '🛒', color: 'blue' },
    { key: 'substitutes', data: data.substitutes, position: 'bottom-left', icon: '🔄', color: 'green' },
    { key: 'industryRivalry', data: data.industryRivalry, position: 'center', icon: '⚔️', color: 'red' }
  ]

  const getStrengthColor = (strength: string) => {
    switch (strength) {
      case 'WYSOKA': return { bg: 'bg-red-100', border: 'border-red-400', text: 'text-red-700', fill: 'bg-red-500' }
      case 'ŚREDNIA': return { bg: 'bg-yellow-100', border: 'border-yellow-400', text: 'text-yellow-700', fill: 'bg-yellow-500' }
      case 'NISKA': return { bg: 'bg-green-100', border: 'border-green-400', text: 'text-green-700', fill: 'bg-green-500' }
      default: return { bg: 'bg-gray-100', border: 'border-gray-400', text: 'text-gray-700', fill: 'bg-gray-500' }
    }
  }

  const handleForceClick = (forceKey: string) => {
    setSelectedForce(selectedForce === forceKey ? null : forceKey)
    onForceClick?.(forceKey)
  }

  return (
    <div className="w-full">
      {/* Pentagon Layout */}
      <div className="relative mx-auto" style={{ width: '100%', maxWidth: '700px', height: '500px' }}>
        {/* Center - Industry Rivalry */}
        <div
          className={`absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-48 cursor-pointer transition-all duration-300 ${
            selectedForce === 'industryRivalry' ? 'z-20 scale-110' : hoveredForce === 'industryRivalry' ? 'z-10 scale-105' : ''
          }`}
          onClick={() => handleForceClick('industryRivalry')}
          onMouseEnter={() => setHoveredForce('industryRivalry')}
          onMouseLeave={() => setHoveredForce(null)}
        >
          <div className={`rounded-xl border-2 p-4 shadow-lg ${getStrengthColor(data.industryRivalry.strength).bg} ${getStrengthColor(data.industryRivalry.strength).border}`}>
            <div className="text-center">
              <span className="text-3xl">⚔️</span>
              <div className="font-bold text-gray-800 mt-2">{data.industryRivalry.name}</div>
              <div className="text-xs text-gray-500">{data.industryRivalry.englishName}</div>
              <div className={`mt-2 inline-block px-3 py-1 rounded-full text-xs font-bold ${getStrengthColor(data.industryRivalry.strength).fill} text-white`}>
                {data.industryRivalry.strength}
              </div>
            </div>
          </div>
        </div>

        {/* Top - Supplier Power */}
        <div
          className={`absolute left-1/2 top-4 -translate-x-1/2 w-44 cursor-pointer transition-all duration-300 ${
            selectedForce === 'supplierPower' ? 'z-20 scale-110' : hoveredForce === 'supplierPower' ? 'z-10 scale-105' : ''
          }`}
          onClick={() => handleForceClick('supplierPower')}
          onMouseEnter={() => setHoveredForce('supplierPower')}
          onMouseLeave={() => setHoveredForce(null)}
        >
          <div className={`rounded-xl border-2 p-3 shadow-md ${getStrengthColor(data.supplierPower.strength).bg} ${getStrengthColor(data.supplierPower.strength).border}`}>
            <div className="text-center">
              <span className="text-2xl">🏭</span>
              <div className="font-semibold text-gray-800 text-sm mt-1">{data.supplierPower.name}</div>
              <div className="text-xs text-gray-500">{data.supplierPower.englishName}</div>
              <div className={`mt-2 inline-block px-2 py-0.5 rounded-full text-xs font-bold ${getStrengthColor(data.supplierPower.strength).fill} text-white`}>
                {data.supplierPower.strength}
              </div>
            </div>
          </div>
          {/* Arrow to center */}
          <div className="absolute left-1/2 -translate-x-1/2 top-full h-12 w-0.5 bg-gray-300">
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 rotate-45 w-2 h-2 border-b-2 border-r-2 border-gray-400"></div>
          </div>
        </div>

        {/* Top Right - New Entrants */}
        <div
          className={`absolute right-8 top-20 w-44 cursor-pointer transition-all duration-300 ${
            selectedForce === 'newEntrants' ? 'z-20 scale-110' : hoveredForce === 'newEntrants' ? 'z-10 scale-105' : ''
          }`}
          onClick={() => handleForceClick('newEntrants')}
          onMouseEnter={() => setHoveredForce('newEntrants')}
          onMouseLeave={() => setHoveredForce(null)}
        >
          <div className={`rounded-xl border-2 p-3 shadow-md ${getStrengthColor(data.newEntrants.strength).bg} ${getStrengthColor(data.newEntrants.strength).border}`}>
            <div className="text-center">
              <span className="text-2xl">🚪</span>
              <div className="font-semibold text-gray-800 text-sm mt-1">{data.newEntrants.name}</div>
              <div className="text-xs text-gray-500">{data.newEntrants.englishName}</div>
              <div className={`mt-2 inline-block px-2 py-0.5 rounded-full text-xs font-bold ${getStrengthColor(data.newEntrants.strength).fill} text-white`}>
                {data.newEntrants.strength}
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Right - Buyer Power */}
        <div
          className={`absolute right-8 bottom-24 w-44 cursor-pointer transition-all duration-300 ${
            selectedForce === 'buyerPower' ? 'z-20 scale-110' : hoveredForce === 'buyerPower' ? 'z-10 scale-105' : ''
          }`}
          onClick={() => handleForceClick('buyerPower')}
          onMouseEnter={() => setHoveredForce('buyerPower')}
          onMouseLeave={() => setHoveredForce(null)}
        >
          <div className={`rounded-xl border-2 p-3 shadow-md ${getStrengthColor(data.buyerPower.strength).bg} ${getStrengthColor(data.buyerPower.strength).border}`}>
            <div className="text-center">
              <span className="text-2xl">🛒</span>
              <div className="font-semibold text-gray-800 text-sm mt-1">{data.buyerPower.name}</div>
              <div className="text-xs text-gray-500">{data.buyerPower.englishName}</div>
              <div className={`mt-2 inline-block px-2 py-0.5 rounded-full text-xs font-bold ${getStrengthColor(data.buyerPower.strength).fill} text-white`}>
                {data.buyerPower.strength}
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Left - Substitutes */}
        <div
          className={`absolute left-8 bottom-24 w-44 cursor-pointer transition-all duration-300 ${
            selectedForce === 'substitutes' ? 'z-20 scale-110' : hoveredForce === 'substitutes' ? 'z-10 scale-105' : ''
          }`}
          onClick={() => handleForceClick('substitutes')}
          onMouseEnter={() => setHoveredForce('substitutes')}
          onMouseLeave={() => setHoveredForce(null)}
        >
          <div className={`rounded-xl border-2 p-3 shadow-md ${getStrengthColor(data.substitutes.strength).bg} ${getStrengthColor(data.substitutes.strength).border}`}>
            <div className="text-center">
              <span className="text-2xl">🔄</span>
              <div className="font-semibold text-gray-800 text-sm mt-1">{data.substitutes.name}</div>
              <div className="text-xs text-gray-500">{data.substitutes.englishName}</div>
              <div className={`mt-2 inline-block px-2 py-0.5 rounded-full text-xs font-bold ${getStrengthColor(data.substitutes.strength).fill} text-white`}>
                {data.substitutes.strength}
              </div>
            </div>
          </div>
        </div>

        {/* Connecting lines to center (visual only) */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: -1 }}>
          {/* Lines from each force to center */}
          <line x1="50%" y1="20%" x2="50%" y2="40%" stroke="#d1d5db" strokeWidth="2" strokeDasharray="4" />
          <line x1="80%" y1="30%" x2="60%" y2="45%" stroke="#d1d5db" strokeWidth="2" strokeDasharray="4" />
          <line x1="80%" y1="70%" x2="60%" y2="55%" stroke="#d1d5db" strokeWidth="2" strokeDasharray="4" />
          <line x1="20%" y1="70%" x2="40%" y2="55%" stroke="#d1d5db" strokeWidth="2" strokeDasharray="4" />
          <line x1="20%" y1="30%" x2="40%" y2="45%" stroke="#d1d5db" strokeWidth="2" strokeDasharray="4" />
        </svg>
      </div>

      {/* Selected Force Details */}
      {selectedForce && (
        <div className="mt-6 rounded-xl bg-white border-2 border-gray-200 p-6 shadow-md">
          {forces.filter(f => f.key === selectedForce).map(force => (
            <div key={force.key}>
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">{force.icon}</span>
                <div>
                  <h3 className="font-bold text-lg text-gray-800">{force.data.name}</h3>
                  <span className="text-sm text-gray-500">{force.data.englishName}</span>
                </div>
                <span className={`ml-auto px-3 py-1 rounded-full text-sm font-bold ${getStrengthColor(force.data.strength).fill} text-white`}>
                  {force.data.strength}
                </span>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold text-gray-700 text-sm">Kluczowe czynniki:</h4>
                <ul className="space-y-2">
                  {force.data.points.map((point, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                      <span className={`mt-0.5 h-2 w-2 rounded-full flex-shrink-0 ${getStrengthColor(force.data.strength).fill}`}></span>
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Legend */}
      <div className="mt-6 flex flex-wrap items-center justify-center gap-4 text-sm">
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded bg-green-500"></span>
          <span className="text-gray-600">Niska - korzystne dla firmy</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded bg-yellow-500"></span>
          <span className="text-gray-600">Średnia - neutralne</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded bg-red-500"></span>
          <span className="text-gray-600">Wysoka - wyzwanie</span>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="mt-4 text-center text-xs text-gray-500">
        <span className="inline-flex items-center gap-1">
          📊 Model Portera - 5 sił wpływających na atrakcyjność branży
        </span>
      </div>

      {/* Tip */}
      <div className="mt-3 text-center text-xs text-gray-400">
        💡 Kliknij siłę, aby zobaczyć szczegóły
      </div>
    </div>
  )
}

// ===== TREND TIMELINE TYPES AND COMPONENT =====

interface TrendTimepoint {
  year: number
  description: string
}

interface TrendData {
  name: string
  category: string
  status: string
  period: string
  impact: string
  timepoints: TrendTimepoint[]
}

interface TrendTimelineData {
  trends: TrendData[]
}

// Parse Trend Timeline content
function parseTrendTimelineContent(content: string): TrendTimelineData | null {
  const trends: TrendData[] = []

  // Split by trend sections (each starting with **Trend:)
  const trendBlocks = content.split(/\*\*Trend:/).filter(block => block.trim())

  for (const block of trendBlocks) {
    const lines = block.split('\n')
    let name = ''
    let category = ''
    let status = ''
    let period = ''
    let impact = ''
    const timepoints: TrendTimepoint[] = []
    let inTimepointSection = false

    for (const line of lines) {
      const trimmedLine = line.trim()

      // First line is the trend name
      if (!name && trimmedLine && !trimmedLine.startsWith('Kategoria') && !trimmedLine.startsWith('Status') && !trimmedLine.startsWith('Okres') && !trimmedLine.startsWith('Wpływ') && !trimmedLine.startsWith('Punkty') && !trimmedLine.startsWith('-')) {
        name = trimmedLine.replace(/\*\*/g, '').trim()
        continue
      }

      // Parse metadata
      if (trimmedLine.startsWith('Kategoria:')) {
        category = trimmedLine.replace('Kategoria:', '').trim()
        continue
      }
      if (trimmedLine.startsWith('Status:')) {
        status = trimmedLine.replace('Status:', '').trim()
        continue
      }
      if (trimmedLine.startsWith('Okres:')) {
        period = trimmedLine.replace('Okres:', '').trim()
        continue
      }
      if (trimmedLine.startsWith('Wpływ:')) {
        impact = trimmedLine.replace('Wpływ:', '').trim()
        continue
      }
      if (trimmedLine.startsWith('Punkty czasowe:')) {
        inTimepointSection = true
        continue
      }

      // Parse timepoints
      if (inTimepointSection && trimmedLine.startsWith('-')) {
        const timepointMatch = trimmedLine.match(/^-\s*(\d{4}):\s*(.+)$/)
        if (timepointMatch) {
          timepoints.push({
            year: parseInt(timepointMatch[1]),
            description: timepointMatch[2].trim()
          })
        }
      }
    }

    if (name && timepoints.length > 0) {
      trends.push({ name, category, status, period, impact, timepoints })
    }
  }

  if (trends.length === 0) {
    return null
  }

  return { trends }
}

// Helper function to check if section is Trend Timeline
function isTrendTimelineSection(title: string): boolean {
  const lowerTitle = title.toLowerCase()
  return (lowerTitle.includes('trend') && lowerTitle.includes('timeline')) ||
         (lowerTitle.includes('trendy') && lowerTitle.includes('rynkow')) ||
         (lowerTitle.includes('trend') && (lowerTitle.includes('analiza') || lowerTitle.includes('czasow')))
}

// Trend Timeline Diagram Component
function TrendTimelineDiagram({ data, onTrendClick }: { data: TrendTimelineData; onTrendClick?: (trend: string) => void }) {
  const [selectedTrend, setSelectedTrend] = useState<string | null>(null)
  const [hoveredTimepoint, setHoveredTimepoint] = useState<{ trendIdx: number; pointIdx: number } | null>(null)

  // Calculate year range across all trends
  const allYears = data.trends.flatMap(t => t.timepoints.map(tp => tp.year))
  const minYear = Math.min(...allYears)
  const maxYear = Math.max(...allYears)
  const yearRange = maxYear - minYear

  // Generate year labels
  const yearLabels: number[] = []
  for (let y = minYear; y <= maxYear; y++) {
    yearLabels.push(y)
  }

  const getCategoryStyle = (category: string) => {
    switch (category.toLowerCase()) {
      case 'technologia':
        return { bg: 'bg-blue-500', light: 'bg-blue-100', border: 'border-blue-300', text: 'text-blue-700', icon: '🔬' }
      case 'regulacje':
        return { bg: 'bg-purple-500', light: 'bg-purple-100', border: 'border-purple-300', text: 'text-purple-700', icon: '📜' }
      case 'rynek':
        return { bg: 'bg-green-500', light: 'bg-green-100', border: 'border-green-300', text: 'text-green-700', icon: '📈' }
      case 'społeczne':
        return { bg: 'bg-orange-500', light: 'bg-orange-100', border: 'border-orange-300', text: 'text-orange-700', icon: '👥' }
      default:
        return { bg: 'bg-gray-500', light: 'bg-gray-100', border: 'border-gray-300', text: 'text-gray-700', icon: '📌' }
    }
  }

  const getStatusStyle = (status: string) => {
    switch (status.toLowerCase()) {
      case 'rosnący':
        return { color: 'text-green-600', badge: 'bg-green-100 text-green-800', icon: '📈' }
      case 'dojrzały':
        return { color: 'text-blue-600', badge: 'bg-blue-100 text-blue-800', icon: '✓' }
      case 'stabilny':
        return { color: 'text-gray-600', badge: 'bg-gray-100 text-gray-800', icon: '➡️' }
      case 'malejący':
        return { color: 'text-red-600', badge: 'bg-red-100 text-red-800', icon: '📉' }
      default:
        return { color: 'text-gray-600', badge: 'bg-gray-100 text-gray-800', icon: '•' }
    }
  }

  const getImpactStyle = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'wysoki':
        return { badge: 'bg-red-100 text-red-800 border-red-300' }
      case 'średni':
        return { badge: 'bg-yellow-100 text-yellow-800 border-yellow-300' }
      case 'niski':
        return { badge: 'bg-green-100 text-green-800 border-green-300' }
      default:
        return { badge: 'bg-gray-100 text-gray-800 border-gray-300' }
    }
  }

  const handleTrendClick = (trendName: string) => {
    setSelectedTrend(selectedTrend === trendName ? null : trendName)
    onTrendClick?.(trendName)
  }

  const getTimelinePosition = (year: number): string => {
    const position = ((year - minYear) / yearRange) * 100
    return `${position}%`
  }

  return (
    <div className="w-full">
      {/* Category Legend */}
      <div className="mb-6 flex flex-wrap items-center justify-center gap-4 text-sm">
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded bg-blue-500"></span>
          <span className="text-gray-600">Technologia</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded bg-purple-500"></span>
          <span className="text-gray-600">Regulacje</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded bg-green-500"></span>
          <span className="text-gray-600">Rynek</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded bg-orange-500"></span>
          <span className="text-gray-600">Społeczne</span>
        </div>
      </div>

      {/* Timeline Container */}
      <div className="relative">
        {/* Year axis */}
        <div className="relative h-10 border-b-2 border-gray-300 mb-4">
          <div className="absolute inset-x-8 flex justify-between">
            {yearLabels.map((year) => (
              <div key={year} className="flex flex-col items-center">
                <div className="h-3 w-0.5 bg-gray-400"></div>
                <span className="text-xs text-gray-500 mt-1 font-medium">{year}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Trends */}
        <div className="space-y-6 mt-8">
          {data.trends.map((trend, trendIdx) => {
            const categoryStyle = getCategoryStyle(trend.category)
            const statusStyle = getStatusStyle(trend.status)
            const impactStyle = getImpactStyle(trend.impact)
            const isSelected = selectedTrend === trend.name

            return (
              <div key={trendIdx} className="relative">
                {/* Trend Header */}
                <div
                  className={`mb-3 p-3 rounded-lg cursor-pointer transition-all duration-300 ${
                    isSelected
                      ? `${categoryStyle.light} ${categoryStyle.border} border-2 shadow-md`
                      : 'bg-gray-50 border border-gray-200 hover:border-gray-300 hover:shadow-sm'
                  }`}
                  onClick={() => handleTrendClick(trend.name)}
                >
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">{categoryStyle.icon}</span>
                      <div>
                        <h4 className="font-semibold text-gray-800">{trend.name}</h4>
                        <span className="text-xs text-gray-500">{trend.period}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${categoryStyle.bg} text-white`}>
                        {trend.category}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusStyle.badge}`}>
                        {statusStyle.icon} {trend.status}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${impactStyle.badge}`}>
                        Wpływ: {trend.impact}
                      </span>
                      <svg
                        className={`h-5 w-5 transition-transform duration-300 text-gray-400 ${isSelected ? 'rotate-180' : ''}`}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </div>
                </div>

                {/* Timeline Track */}
                <div className={`relative mx-8 transition-all duration-300 ${isSelected ? 'h-auto opacity-100 mb-4' : 'h-0 opacity-0 overflow-hidden'}`}>
                  {/* Horizontal line */}
                  <div className={`absolute left-0 right-0 top-4 h-1 rounded ${categoryStyle.bg} opacity-30`}></div>

                  {/* Timepoints */}
                  <div className="relative h-32">
                    {trend.timepoints.map((tp, pointIdx) => {
                      const position = getTimelinePosition(tp.year)
                      const isHovered = hoveredTimepoint?.trendIdx === trendIdx && hoveredTimepoint?.pointIdx === pointIdx
                      const isFuture = tp.year > new Date().getFullYear()

                      return (
                        <div
                          key={pointIdx}
                          className="absolute flex flex-col items-center"
                          style={{ left: position, transform: 'translateX(-50%)' }}
                          onMouseEnter={() => setHoveredTimepoint({ trendIdx, pointIdx })}
                          onMouseLeave={() => setHoveredTimepoint(null)}
                        >
                          {/* Point marker */}
                          <div
                            className={`w-4 h-4 rounded-full border-2 ${categoryStyle.bg} border-white shadow-md transition-transform duration-200 ${
                              isHovered ? 'scale-150 z-10' : ''
                            } ${isFuture ? 'opacity-50' : ''}`}
                          />

                          {/* Year label */}
                          <span className={`text-xs font-bold mt-1 ${categoryStyle.text} ${isFuture ? 'opacity-50' : ''}`}>
                            {tp.year}
                          </span>

                          {/* Tooltip on hover */}
                          {isHovered && (
                            <div className={`absolute top-10 z-20 w-56 p-3 rounded-lg shadow-lg ${categoryStyle.light} ${categoryStyle.border} border text-sm`}>
                              <div className="font-semibold text-gray-800 mb-1">{tp.year}</div>
                              <div className={`${categoryStyle.text}`}>{tp.description}</div>
                              {isFuture && (
                                <div className="mt-2 text-xs text-gray-500 italic">📅 Prognoza</div>
                              )}
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Summary Stats */}
      <div className="mt-6 text-center text-xs text-gray-500">
        <span className="inline-flex items-center gap-1">
          📊 Oś czasu trendów - {data.trends.length} trendów z {allYears.length} punktami czasowymi
        </span>
      </div>

      {/* Tip */}
      <div className="mt-3 text-center text-xs text-gray-400">
        💡 Kliknij trend, aby rozwinąć szczegółową oś czasu. Najedź na punkt, aby zobaczyć opis.
      </div>
    </div>
  )
}

// ===== OWNERSHIP TREE TYPES AND COMPONENT =====

interface OwnershipNode {
  id: string
  name: string
  type: 'ROOT' | 'SHAREHOLDER' | 'UBO'
  percentage: number
  details?: {
    entityType?: string
    krs?: string
    country?: string
    role?: string
    description?: string
  }
  children: OwnershipNode[]
}

interface OwnershipData {
  rootCompany: string
  tree: OwnershipNode
  shareholders: {
    name: string
    percentage: number
    type: string
    krs?: string
    country?: string
    role?: string
    description?: string
  }[]
  ubos: {
    name: string
    path: string
    isDirect: boolean
  }[]
}

// Parse ownership content
function parseOwnershipContent(content: string): OwnershipData | null {
  const lines = content.split('\n')

  // Find the tree structure
  const treeLines: string[] = []
  let inTree = false
  let rootCompanyName = ''

  for (const line of lines) {
    if (line.includes('[ROOT]')) {
      inTree = true
      // Extract root company name and percentage
      const rootMatch = line.match(/\[ROOT\]\s*(.+?)\s*\((\d+)%\)/)
      if (rootMatch) {
        rootCompanyName = rootMatch[1].trim()
      }
    }

    if (inTree) {
      if (line.includes('[ROOT]') || line.includes('[SHAREHOLDER]') || line.includes('[UBO]')) {
        treeLines.push(line)
      } else if (line.trim() === '' || line.includes('**Szczegóły')) {
        inTree = false
      }
    }
  }

  if (!rootCompanyName || treeLines.length === 0) {
    return null
  }

  // Parse tree structure
  function parseTreeLevel(lines: string[], startIdx: number, currentIndent: number): { node: OwnershipNode | null; nextIdx: number } {
    if (startIdx >= lines.length) {
      return { node: null, nextIdx: startIdx }
    }

    const line = lines[startIdx]
    const indentMatch = line.match(/^[\s│├└─]*/)
    const indent = indentMatch ? indentMatch[0].length : 0

    // Parse node info
    const nodeMatch = line.match(/\[(ROOT|SHAREHOLDER|UBO)\]\s*(.+?)\s*\((\d+)%\)(?:\s*-\s*(.+))?/)
    if (!nodeMatch) {
      return { node: null, nextIdx: startIdx + 1 }
    }

    const type = nodeMatch[1] as 'ROOT' | 'SHAREHOLDER' | 'UBO'
    const name = nodeMatch[2].trim()
    const percentage = parseInt(nodeMatch[3])
    const role = nodeMatch[4]?.trim()

    const node: OwnershipNode = {
      id: `node_${startIdx}`,
      name,
      type,
      percentage,
      details: role ? { role } : undefined,
      children: []
    }

    // Parse children
    let nextIdx = startIdx + 1
    while (nextIdx < lines.length) {
      const nextLine = lines[nextIdx]
      const nextIndentMatch = nextLine.match(/^[\s│├└─]*/)
      const nextIndent = nextIndentMatch ? nextIndentMatch[0].length : 0

      if (nextIndent > indent) {
        const childResult = parseTreeLevel(lines, nextIdx, nextIndent)
        if (childResult.node) {
          node.children.push(childResult.node)
        }
        nextIdx = childResult.nextIdx
      } else {
        break
      }
    }

    return { node, nextIdx }
  }

  const treeResult = parseTreeLevel(treeLines, 0, 0)

  // Parse shareholders details
  const shareholders: OwnershipData['shareholders'] = []
  let inShareholders = false
  let currentShareholder: OwnershipData['shareholders'][0] | null = null

  for (const line of lines) {
    if (line.includes('**Szczegóły udziałowców:**')) {
      inShareholders = true
      continue
    }
    if (line.includes('**Beneficjenci rzeczywiści')) {
      inShareholders = false
      if (currentShareholder) {
        shareholders.push(currentShareholder)
        currentShareholder = null
      }
      continue
    }

    if (inShareholders) {
      // New shareholder entry
      const shareholderMatch = line.match(/^(.+?)\s*-\s*(\d+)%(?:\s*\((.+)\))?$/)
      if (shareholderMatch) {
        if (currentShareholder) {
          shareholders.push(currentShareholder)
        }
        currentShareholder = {
          name: shareholderMatch[1].trim(),
          percentage: parseInt(shareholderMatch[2]),
          type: '',
          description: ''
        }
        continue
      }

      // Shareholder details
      if (currentShareholder && line.startsWith('Typ:')) {
        currentShareholder.type = line.replace('Typ:', '').trim()
      } else if (currentShareholder && line.startsWith('KRS:')) {
        currentShareholder.krs = line.replace('KRS:', '').trim()
      } else if (currentShareholder && line.startsWith('Kraj:')) {
        currentShareholder.country = line.replace('Kraj:', '').trim()
      } else if (currentShareholder && line.startsWith('Rola:')) {
        currentShareholder.role = line.replace('Rola:', '').trim()
      } else if (currentShareholder && line.startsWith('Opis:')) {
        currentShareholder.description = line.replace('Opis:', '').trim()
      }
    }
  }

  // Parse UBOs
  const ubos: OwnershipData['ubos'] = []
  let inUbos = false

  for (const line of lines) {
    if (line.includes('**Beneficjenci rzeczywiści (UBO):**')) {
      inUbos = true
      continue
    }
    if (line.includes('**Historia zmian')) {
      inUbos = false
      continue
    }

    if (inUbos && line.trim().startsWith('-')) {
      const uboLine = line.replace('-', '').trim()
      const uboMatch = uboLine.match(/^(.+?)\s*\((.+)\)$/)
      if (uboMatch) {
        const isDirect = uboMatch[2].toLowerCase().includes('bezpośrednio')
        ubos.push({
          name: uboMatch[1].trim(),
          path: uboMatch[2].trim(),
          isDirect
        })
      }
    }
  }

  if (!treeResult.node) {
    return null
  }

  return {
    rootCompany: rootCompanyName,
    tree: treeResult.node,
    shareholders,
    ubos
  }
}

// Helper function to check if section is Ownership
function isOwnershipSection(title: string): boolean {
  const lowerTitle = title.toLowerCase()
  return lowerTitle.includes('struktura własno') ||
         lowerTitle.includes('struktura własnośc') ||
         lowerTitle.includes('ownership') ||
         (lowerTitle.includes('udziałowc') && lowerTitle.includes('struktur')) ||
         lowerTitle.includes('beneficjent')
}

// Ownership Tree Diagram Component
function OwnershipTreeDiagram({ data, onNodeClick }: { data: OwnershipData; onNodeClick?: (node: OwnershipNode) => void }) {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set(['node_0']))
  const [selectedNode, setSelectedNode] = useState<OwnershipNode | null>(null)
  const [showShareholderDetails, setShowShareholderDetails] = useState(false)

  const toggleNode = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId)
    } else {
      newExpanded.add(nodeId)
    }
    setExpandedNodes(newExpanded)
  }

  const handleNodeClick = (node: OwnershipNode) => {
    setSelectedNode(selectedNode?.id === node.id ? null : node)
    onNodeClick?.(node)
  }

  const getNodeStyle = (type: 'ROOT' | 'SHAREHOLDER' | 'UBO') => {
    switch (type) {
      case 'ROOT':
        return {
          bg: 'bg-indigo-500',
          border: 'border-indigo-600',
          light: 'bg-indigo-50',
          text: 'text-indigo-800',
          icon: '🏢'
        }
      case 'SHAREHOLDER':
        return {
          bg: 'bg-blue-500',
          border: 'border-blue-600',
          light: 'bg-blue-50',
          text: 'text-blue-800',
          icon: '📊'
        }
      case 'UBO':
        return {
          bg: 'bg-green-500',
          border: 'border-green-600',
          light: 'bg-green-50',
          text: 'text-green-800',
          icon: '👤'
        }
    }
  }

  const renderTreeNode = (node: OwnershipNode, depth: number = 0, isLast: boolean = true): JSX.Element => {
    const style = getNodeStyle(node.type)
    const isExpanded = expandedNodes.has(node.id)
    const hasChildren = node.children.length > 0
    const isSelected = selectedNode?.id === node.id

    return (
      <div key={node.id} className="relative">
        {/* Connection line from parent */}
        {depth > 0 && (
          <div className="absolute left-0 top-0 w-8 h-8">
            <div className="absolute left-0 top-0 bottom-1/2 w-px bg-gray-300"></div>
            <div className="absolute left-0 top-1/2 right-0 h-px bg-gray-300"></div>
          </div>
        )}

        {/* Node */}
        <div
          className={`ml-${depth > 0 ? '8' : '0'} mb-2 relative`}
          style={{ marginLeft: depth > 0 ? '2rem' : '0' }}
        >
          <div
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg cursor-pointer transition-all duration-200 ${
              isSelected
                ? `${style.light} border-2 ${style.border} shadow-md`
                : 'bg-white border border-gray-200 hover:border-gray-300 hover:shadow-sm'
            }`}
            onClick={() => handleNodeClick(node)}
          >
            {/* Expand/collapse button */}
            {hasChildren && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  toggleNode(node.id)
                }}
                className="w-5 h-5 flex items-center justify-center rounded bg-gray-100 hover:bg-gray-200 transition-colors"
              >
                <svg
                  className={`h-3 w-3 text-gray-600 transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            )}

            {/* Node icon */}
            <span className={`w-8 h-8 flex items-center justify-center rounded-full ${style.bg} text-white text-sm`}>
              {style.icon}
            </span>

            {/* Node info */}
            <div className="flex flex-col">
              <span className="font-medium text-gray-800">{node.name}</span>
              <div className="flex items-center gap-2 text-xs">
                <span className={`px-1.5 py-0.5 rounded ${style.light} ${style.text} font-medium`}>
                  {node.percentage}%
                </span>
                <span className="text-gray-500">
                  {node.type === 'ROOT' ? 'Spółka' : node.type === 'SHAREHOLDER' ? 'Udziałowiec' : 'Beneficjent rzeczywisty'}
                </span>
              </div>
            </div>

            {/* Role badge */}
            {node.details?.role && (
              <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600">
                {node.details.role}
              </span>
            )}
          </div>

          {/* Children */}
          {hasChildren && isExpanded && (
            <div className="mt-2 relative">
              {/* Vertical connector line */}
              {node.children.length > 1 && (
                <div
                  className="absolute left-4 top-0 w-px bg-gray-300"
                  style={{ height: 'calc(100% - 1rem)' }}
                ></div>
              )}

              {node.children.map((child, idx) => (
                <div key={child.id} className="relative">
                  {renderTreeNode(child, depth + 1, idx === node.children.length - 1)}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="w-full">
      {/* Legend */}
      <div className="mb-6 flex flex-wrap items-center justify-center gap-4 text-sm">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 flex items-center justify-center rounded-full bg-indigo-500 text-white text-xs">🏢</span>
          <span className="text-gray-600">Spółka główna</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 flex items-center justify-center rounded-full bg-blue-500 text-white text-xs">📊</span>
          <span className="text-gray-600">Udziałowiec</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 flex items-center justify-center rounded-full bg-green-500 text-white text-xs">👤</span>
          <span className="text-gray-600">Beneficjent rzeczywisty (UBO)</span>
        </div>
      </div>

      {/* Tree Visualization */}
      <div className="p-4 bg-gray-50 rounded-xl border border-gray-200 overflow-x-auto">
        {renderTreeNode(data.tree)}
      </div>

      {/* Selected Node Details */}
      {selectedNode && (
        <div className="mt-4 p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold text-gray-800 flex items-center gap-2">
              {getNodeStyle(selectedNode.type).icon}
              {selectedNode.name}
            </h4>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-500">Typ:</span>
              <span className="ml-2 font-medium">
                {selectedNode.type === 'ROOT' ? 'Spółka główna' :
                 selectedNode.type === 'SHAREHOLDER' ? 'Udziałowiec' :
                 'Beneficjent rzeczywisty'}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Udział:</span>
              <span className="ml-2 font-medium">{selectedNode.percentage}%</span>
            </div>
            {selectedNode.details?.role && (
              <div className="col-span-2">
                <span className="text-gray-500">Rola:</span>
                <span className="ml-2 font-medium">{selectedNode.details.role}</span>
              </div>
            )}
          </div>

          {/* Find shareholder details */}
          {data.shareholders.map((sh, idx) => {
            if (sh.name === selectedNode.name) {
              return (
                <div key={idx} className="mt-3 pt-3 border-t border-gray-100">
                  {sh.type && (
                    <div className="text-sm">
                      <span className="text-gray-500">Typ podmiotu:</span>
                      <span className="ml-2">{sh.type}</span>
                    </div>
                  )}
                  {sh.krs && (
                    <div className="text-sm">
                      <span className="text-gray-500">KRS:</span>
                      <span className="ml-2 font-mono">{sh.krs}</span>
                    </div>
                  )}
                  {sh.country && (
                    <div className="text-sm">
                      <span className="text-gray-500">Kraj:</span>
                      <span className="ml-2">{sh.country}</span>
                    </div>
                  )}
                  {sh.description && (
                    <div className="text-sm mt-2">
                      <span className="text-gray-500">Opis:</span>
                      <p className="mt-1 text-gray-700">{sh.description}</p>
                    </div>
                  )}
                </div>
              )
            }
            return null
          })}
        </div>
      )}

      {/* UBO Summary */}
      {data.ubos.length > 0 && (
        <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
          <h4 className="font-semibold text-green-800 mb-3 flex items-center gap-2">
            👤 Beneficjenci rzeczywiści (UBO)
          </h4>
          <div className="space-y-2">
            {data.ubos.map((ubo, idx) => (
              <div key={idx} className="flex items-center justify-between bg-white rounded-lg p-2 border border-green-100">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 flex items-center justify-center rounded-full bg-green-500 text-white text-xs">
                    {ubo.isDirect ? '✓' : '↗'}
                  </span>
                  <span className="font-medium text-gray-800">{ubo.name}</span>
                </div>
                <span className={`text-xs px-2 py-1 rounded ${ubo.isDirect ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
                  {ubo.isDirect ? 'Bezpośrednio' : ubo.path}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Shareholders Summary Table */}
      <div className="mt-4">
        <button
          onClick={() => setShowShareholderDetails(!showShareholderDetails)}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
        >
          <svg
            className={`h-4 w-4 transition-transform duration-200 ${showShareholderDetails ? 'rotate-90' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          {showShareholderDetails ? 'Ukryj tabelę udziałowców' : 'Pokaż tabelę udziałowców'}
        </button>

        {showShareholderDetails && data.shareholders.length > 0 && (
          <div className="mt-3 overflow-hidden rounded-lg border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nazwa</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Udział</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Typ</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rola</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.shareholders.map((sh, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm font-medium text-gray-900">{sh.name}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">
                      <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded font-medium">{sh.percentage}%</span>
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-600">{sh.type || '-'}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">{sh.role || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Summary Stats */}
      <div className="mt-4 flex items-center justify-center gap-6 text-xs text-gray-500">
        <div className="flex items-center gap-1">
          <span className="h-3 w-3 rounded bg-blue-500"></span>
          <span>Udziałowcy: {data.shareholders.length}</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="h-3 w-3 rounded bg-green-500"></span>
          <span>Beneficjenci: {data.ubos.length}</span>
        </div>
      </div>

      {/* Tip */}
      <div className="mt-3 text-center text-xs text-gray-400">
        💡 Kliknij węzeł drzewa, aby zobaczyć szczegóły. Użyj strzałek, aby rozwinąć/zwinąć gałęzie.
      </div>
    </div>
  )
}

// ===== FINANCIAL RATIO RADAR CHART TYPES AND COMPONENT =====

interface FinancialRatio {
  name: string
  shortName: string
  value: number
  benchmark: number
  unit: string
  description: string
  category: string
  isInverted?: boolean // true if lower is better (e.g., debt ratio)
}

interface FinancialRatiosData {
  ratios: FinancialRatio[]
  summary?: string
}

// Parse financial ratios content
function parseFinancialRatiosContent(content: string): FinancialRatiosData | null {
  if (!content.includes('[FINANCIAL_RATIOS_RADAR]') && !content.includes('[RATIO]')) {
    return null
  }

  const ratios: FinancialRatio[] = []
  const lines = content.split('\n')

  let currentCategory = ''
  let i = 0

  while (i < lines.length) {
    const line = lines[i].trim()

    // Detect category headers
    if (line.startsWith('**Wskaźniki rentowności')) {
      currentCategory = 'Rentowność'
    } else if (line.startsWith('**Wskaźniki płynności')) {
      currentCategory = 'Płynność'
    } else if (line.startsWith('**Wskaźniki zadłużenia')) {
      currentCategory = 'Zadłużenie'
    } else if (line.startsWith('**Wskaźniki efektywności')) {
      currentCategory = 'Efektywność'
    }

    // Parse ratio entries
    if (line.startsWith('[RATIO]')) {
      const nameMatch = line.match(/\[RATIO\]\s*(.+)/)
      if (nameMatch) {
        const fullName = nameMatch[1].trim()
        // Extract short name (first part or abbreviation in parentheses)
        const shortNameMatch = fullName.match(/\(([^)]+)\)/)
        const shortName = shortNameMatch ? shortNameMatch[1] : fullName.split(' ')[0]

        // Parse the following lines for value, benchmark, description
        let value = 0
        let benchmark = 0
        let unit = '%'
        let description = ''

        // Look at next lines for value/benchmark/description
        for (let j = i + 1; j < Math.min(i + 5, lines.length); j++) {
          const nextLine = lines[j].trim()

          if (nextLine.startsWith('Wartość:')) {
            const valueMatch = nextLine.match(/Wartość:\s*([\d.,]+)\s*(%|dni)?/)
            if (valueMatch) {
              value = parseFloat(valueMatch[1].replace(',', '.'))
              if (valueMatch[2]) {
                unit = valueMatch[2]
              }
            }
          } else if (nextLine.startsWith('Benchmark')) {
            const benchmarkMatch = nextLine.match(/Benchmark.*?:\s*([\d.,]+)/)
            if (benchmarkMatch) {
              benchmark = parseFloat(benchmarkMatch[1].replace(',', '.'))
            }
          } else if (nextLine.startsWith('Opis:')) {
            description = nextLine.replace('Opis:', '').trim()
          }
        }

        // Determine if this is an inverted metric (lower is better)
        const isInverted = fullName.toLowerCase().includes('zadłużeni') ||
                          fullName.toLowerCase().includes('debt') ||
                          fullName.toLowerCase().includes('dso')

        ratios.push({
          name: fullName,
          shortName,
          value,
          benchmark,
          unit,
          description,
          category: currentCategory,
          isInverted
        })
      }
    }

    i++
  }

  // Parse summary
  let summary = ''
  const summaryMatch = content.match(/\*\*Podsumowanie:\*\*\s*([\s\S]*?)(?:\*\*|$)/)
  if (summaryMatch) {
    summary = summaryMatch[1].trim()
  }

  if (ratios.length === 0) {
    return null
  }

  return { ratios, summary }
}

// Helper function to check if section is Financial Ratios
function isFinancialRatiosSection(title: string): boolean {
  const lowerTitle = title.toLowerCase()
  return (lowerTitle.includes('wskaźnik') && lowerTitle.includes('finans')) ||
         (lowerTitle.includes('wskaźnik') && lowerTitle.includes('radar')) ||
         lowerTitle.includes('financial ratio') ||
         lowerTitle.includes('radar chart')
}

// Financial Ratio Radar Chart Component
function FinancialRatioRadarChart({ data, onRatioClick }: { data: FinancialRatiosData; onRatioClick?: (ratio: FinancialRatio) => void }) {
  const [selectedRatio, setSelectedRatio] = useState<FinancialRatio | null>(null)
  const [hoveredRatio, setHoveredRatio] = useState<string | null>(null)
  const [showBenchmark, setShowBenchmark] = useState(true)

  // Calculate normalized values (0-100 scale) for radar chart
  const normalizeValue = (ratio: FinancialRatio): number => {
    // For percentage values, use them directly (capped at 100)
    if (ratio.unit === '%') {
      if (ratio.isInverted) {
        // For inverted metrics (lower is better), inverse the scale
        return Math.max(0, Math.min(100, 100 - ratio.value))
      }
      return Math.min(100, ratio.value * 3) // Scale up smaller percentages
    }
    // For ratio values (like 2.1), multiply by a factor
    if (ratio.unit === 'dni') {
      // Days - inverse scale (fewer days is better)
      return Math.max(0, Math.min(100, 100 - ratio.value))
    }
    // Generic ratio normalization
    if (ratio.isInverted) {
      return Math.max(0, Math.min(100, 100 - ratio.value * 20))
    }
    return Math.min(100, ratio.value * 20)
  }

  const normalizeBenchmark = (ratio: FinancialRatio): number => {
    if (ratio.unit === '%') {
      if (ratio.isInverted) {
        return Math.max(0, Math.min(100, 100 - ratio.benchmark))
      }
      return Math.min(100, ratio.benchmark * 3)
    }
    if (ratio.unit === 'dni') {
      return Math.max(0, Math.min(100, 100 - ratio.benchmark))
    }
    if (ratio.isInverted) {
      return Math.max(0, Math.min(100, 100 - ratio.benchmark * 20))
    }
    return Math.min(100, ratio.benchmark * 20)
  }

  // SVG radar chart parameters
  const centerX = 200
  const centerY = 200
  const maxRadius = 150
  const numAxes = data.ratios.length
  const angleStep = (2 * Math.PI) / numAxes

  // Generate polygon points for values
  const getPolygonPoints = (getValue: (ratio: FinancialRatio) => number): string => {
    return data.ratios.map((ratio, index) => {
      const angle = index * angleStep - Math.PI / 2 // Start from top
      const normalizedValue = getValue(ratio)
      const radius = (normalizedValue / 100) * maxRadius
      const x = centerX + radius * Math.cos(angle)
      const y = centerY + radius * Math.sin(angle)
      return `${x},${y}`
    }).join(' ')
  }

  // Generate axis lines
  const getAxisEndpoint = (index: number): { x: number; y: number } => {
    const angle = index * angleStep - Math.PI / 2
    return {
      x: centerX + maxRadius * Math.cos(angle),
      y: centerY + maxRadius * Math.sin(angle)
    }
  }

  // Get label position (slightly outside the chart)
  const getLabelPosition = (index: number): { x: number; y: number; anchor: string } => {
    const angle = index * angleStep - Math.PI / 2
    const labelRadius = maxRadius + 35
    const x = centerX + labelRadius * Math.cos(angle)
    const y = centerY + labelRadius * Math.sin(angle)

    let anchor = 'middle'
    if (x < centerX - 20) anchor = 'end'
    else if (x > centerX + 20) anchor = 'start'

    return { x, y, anchor }
  }

  const getCategoryColor = (category: string): string => {
    switch (category) {
      case 'Rentowność': return '#22c55e' // green
      case 'Płynność': return '#3b82f6' // blue
      case 'Zadłużenie': return '#ef4444' // red
      case 'Efektywność': return '#f59e0b' // amber
      default: return '#6b7280' // gray
    }
  }

  const handleRatioClick = (ratio: FinancialRatio) => {
    setSelectedRatio(selectedRatio?.name === ratio.name ? null : ratio)
    onRatioClick?.(ratio)
  }

  // Calculate comparison status
  const getComparisonStatus = (ratio: FinancialRatio): { label: string; color: string; icon: string } => {
    const diff = ratio.isInverted
      ? ratio.benchmark - ratio.value  // For inverted, lower value is better
      : ratio.value - ratio.benchmark

    if (diff > 0) {
      return { label: 'Powyżej benchmarku', color: 'text-green-600', icon: '▲' }
    } else if (diff < 0) {
      return { label: 'Poniżej benchmarku', color: 'text-red-600', icon: '▼' }
    }
    return { label: 'Na poziomie benchmarku', color: 'text-gray-600', icon: '●' }
  }

  return (
    <div className="w-full">
      {/* Toggle benchmark overlay */}
      <div className="flex justify-end mb-4">
        <label className="inline-flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={showBenchmark}
            onChange={(e) => setShowBenchmark(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-600">Pokaż benchmark branżowy</span>
        </label>
      </div>

      {/* Radar Chart SVG */}
      <div className="flex justify-center">
        <svg viewBox="0 0 400 400" className="w-full max-w-lg">
          {/* Background circles (grid) */}
          {[0.25, 0.5, 0.75, 1].map((scale) => (
            <circle
              key={scale}
              cx={centerX}
              cy={centerY}
              r={maxRadius * scale}
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="1"
              strokeDasharray={scale === 1 ? "0" : "4"}
            />
          ))}

          {/* Axis lines */}
          {data.ratios.map((ratio, index) => {
            const endpoint = getAxisEndpoint(index)
            return (
              <line
                key={`axis-${index}`}
                x1={centerX}
                y1={centerY}
                x2={endpoint.x}
                y2={endpoint.y}
                stroke="#d1d5db"
                strokeWidth="1"
              />
            )
          })}

          {/* Benchmark polygon (if enabled) */}
          {showBenchmark && (
            <polygon
              points={getPolygonPoints(normalizeBenchmark)}
              fill="rgba(156, 163, 175, 0.2)"
              stroke="#9ca3af"
              strokeWidth="2"
              strokeDasharray="5,5"
            />
          )}

          {/* Value polygon */}
          <polygon
            points={getPolygonPoints(normalizeValue)}
            fill="rgba(59, 130, 246, 0.3)"
            stroke="#3b82f6"
            strokeWidth="2"
          />

          {/* Data points */}
          {data.ratios.map((ratio, index) => {
            const angle = index * angleStep - Math.PI / 2
            const normalizedValue = normalizeValue(ratio)
            const radius = (normalizedValue / 100) * maxRadius
            const x = centerX + radius * Math.cos(angle)
            const y = centerY + radius * Math.sin(angle)
            const isHovered = hoveredRatio === ratio.name
            const isSelected = selectedRatio?.name === ratio.name

            return (
              <g key={`point-${index}`}>
                <circle
                  cx={x}
                  cy={y}
                  r={isHovered || isSelected ? 8 : 6}
                  fill={getCategoryColor(ratio.category)}
                  stroke="white"
                  strokeWidth="2"
                  className="cursor-pointer transition-all duration-200"
                  onMouseEnter={() => setHoveredRatio(ratio.name)}
                  onMouseLeave={() => setHoveredRatio(null)}
                  onClick={() => handleRatioClick(ratio)}
                />
                {/* Benchmark point */}
                {showBenchmark && (
                  <circle
                    cx={centerX + ((normalizeBenchmark(ratio) / 100) * maxRadius) * Math.cos(angle)}
                    cy={centerY + ((normalizeBenchmark(ratio) / 100) * maxRadius) * Math.sin(angle)}
                    r={4}
                    fill="none"
                    stroke="#9ca3af"
                    strokeWidth="2"
                  />
                )}
              </g>
            )
          })}

          {/* Labels */}
          {data.ratios.map((ratio, index) => {
            const { x, y, anchor } = getLabelPosition(index)
            const isHovered = hoveredRatio === ratio.name
            const isSelected = selectedRatio?.name === ratio.name

            return (
              <text
                key={`label-${index}`}
                x={x}
                y={y}
                textAnchor={anchor}
                className={`text-xs cursor-pointer transition-all duration-200 ${
                  isHovered || isSelected ? 'font-bold' : ''
                }`}
                fill={isHovered || isSelected ? getCategoryColor(ratio.category) : '#4b5563'}
                onMouseEnter={() => setHoveredRatio(ratio.name)}
                onMouseLeave={() => setHoveredRatio(null)}
                onClick={() => handleRatioClick(ratio)}
              >
                {ratio.shortName}
              </text>
            )
          })}

          {/* Center label */}
          <text
            x={centerX}
            y={centerY}
            textAnchor="middle"
            className="text-xs"
            fill="#9ca3af"
          >
            Wskaźniki
          </text>
        </svg>
      </div>

      {/* Legend */}
      <div className="mt-6 flex flex-wrap items-center justify-center gap-4 text-sm">
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded bg-green-500"></span>
          <span className="text-gray-600">Rentowność</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded bg-blue-500"></span>
          <span className="text-gray-600">Płynność</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded bg-red-500"></span>
          <span className="text-gray-600">Zadłużenie</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded bg-amber-500"></span>
          <span className="text-gray-600">Efektywność</span>
        </div>
        {showBenchmark && (
          <>
            <span className="text-gray-300">|</span>
            <div className="flex items-center gap-2">
              <span className="h-0.5 w-4 bg-gray-400" style={{ borderStyle: 'dashed', borderWidth: '2px' }}></span>
              <span className="text-gray-600">Benchmark branżowy</span>
            </div>
          </>
        )}
      </div>

      {/* Ratio Values Table */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
        {data.ratios.map((ratio) => {
          const comparison = getComparisonStatus(ratio)
          const isSelected = selectedRatio?.name === ratio.name

          return (
            <div
              key={ratio.name}
              className={`p-3 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
                isSelected
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
              onClick={() => handleRatioClick(ratio)}
            >
              <div className="text-xs text-gray-500 mb-1">{ratio.shortName}</div>
              <div className="flex items-baseline gap-1">
                <span className="text-lg font-bold text-gray-800">
                  {ratio.value}
                </span>
                <span className="text-sm text-gray-500">{ratio.unit}</span>
              </div>
              <div className={`text-xs ${comparison.color} flex items-center gap-1`}>
                <span>{comparison.icon}</span>
                <span>vs {ratio.benchmark}{ratio.unit}</span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Selected Ratio Details */}
      {selectedRatio && (
        <div className="mt-6 rounded-xl bg-white border-2 border-blue-200 p-6 shadow-md">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="font-bold text-lg text-gray-800">{selectedRatio.name}</h3>
              <span className="text-sm text-gray-500">{selectedRatio.category}</span>
            </div>
            <span
              className="h-4 w-4 rounded"
              style={{ backgroundColor: getCategoryColor(selectedRatio.category) }}
            ></span>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-500">Wartość firmy</div>
              <div className="text-2xl font-bold text-gray-800">
                {selectedRatio.value}{selectedRatio.unit}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-500">Benchmark branżowy</div>
              <div className="text-2xl font-bold text-gray-500">
                {selectedRatio.benchmark}{selectedRatio.unit}
              </div>
            </div>
          </div>

          <div className="mb-4">
            <div className="text-sm font-semibold text-gray-700 mb-2">Porównanie z benchmarkiem:</div>
            <div className={`flex items-center gap-2 ${getComparisonStatus(selectedRatio).color}`}>
              <span className="text-xl">{getComparisonStatus(selectedRatio).icon}</span>
              <span className="font-medium">{getComparisonStatus(selectedRatio).label}</span>
              {!selectedRatio.isInverted ? (
                <span className="text-sm">
                  ({selectedRatio.value > selectedRatio.benchmark ? '+' : ''}
                  {(selectedRatio.value - selectedRatio.benchmark).toFixed(1)}{selectedRatio.unit})
                </span>
              ) : (
                <span className="text-sm">
                  ({selectedRatio.value < selectedRatio.benchmark ? '+' : ''}
                  {(selectedRatio.benchmark - selectedRatio.value).toFixed(1)}{selectedRatio.unit} lepiej)
                </span>
              )}
            </div>
          </div>

          {selectedRatio.description && (
            <div className="text-sm text-gray-600 bg-blue-50 rounded-lg p-3">
              <strong>Opis:</strong> {selectedRatio.description}
            </div>
          )}
        </div>
      )}

      {/* Summary */}
      {data.summary && (
        <div className="mt-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-200">
          <div className="flex items-start gap-3">
            <span className="text-2xl">📊</span>
            <div>
              <div className="font-semibold text-gray-800 mb-1">Podsumowanie analizy</div>
              <div className="text-sm text-gray-600">{data.summary}</div>
            </div>
          </div>
        </div>
      )}

      {/* Stats summary */}
      <div className="mt-6 text-center text-xs text-gray-500">
        <span className="inline-flex items-center gap-1">
          📊 Wykres radarowy - {data.ratios.length} wskaźników finansowych
          {showBenchmark && ' z benchmarkiem branżowym'}
        </span>
      </div>

      {/* Tip */}
      <div className="mt-3 text-center text-xs text-gray-400">
        💡 Kliknij punkt lub kafelek, aby zobaczyć szczegóły wskaźnika
      </div>
    </div>
  )
}

// ===== COMPETITOR POSITIONING MAP TYPES AND COMPONENT =====

interface Competitor {
  name: string
  x: number
  y: number
  revenue: string
  segment: string
  description: string
}

interface PositioningMapData {
  xAxisLabel: string
  yAxisLabel: string
  xMin: number
  xMax: number
  yMin: number
  yMax: number
  competitors: Competitor[]
  legend: { segment: string; color: string; description: string }[]
  quadrantAnalysis: string[]
  conclusions: string[]
}

// Parse Competitor Positioning Map content
function parsePositioningMapContent(content: string): PositioningMapData | null {
  const lines = content.split('\n')

  let xAxisLabel = 'Udział w rynku (%)'
  let yAxisLabel = 'Innowacyjność'
  let xMin = 0, xMax = 15, yMin = 0, yMax = 10
  const competitors: Competitor[] = []
  const legend: { segment: string; color: string; description: string }[] = []
  const quadrantAnalysis: string[] = []
  const conclusions: string[] = []

  let currentCompetitor: Partial<Competitor> | null = null
  let inLegend = false
  let inAnalysis = false
  let inConclusions = false

  for (const line of lines) {
    const trimmedLine = line.trim()

    // Parse axis definitions
    if (trimmedLine.startsWith('Oś X:')) {
      const match = trimmedLine.match(/Oś X:\s*([^|]+)\|\s*min:\s*([\d.]+)\s*\|\s*max:\s*([\d.]+)/)
      if (match) {
        xAxisLabel = match[1].trim()
        xMin = parseFloat(match[2])
        xMax = parseFloat(match[3])
      }
    } else if (trimmedLine.startsWith('Oś Y:')) {
      const match = trimmedLine.match(/Oś Y:\s*([^|]+)\|\s*min:\s*([\d.]+)\s*\|\s*max:\s*([\d.]+)/)
      if (match) {
        yAxisLabel = match[1].trim()
        yMin = parseFloat(match[2])
        yMax = parseFloat(match[3])
      }
    }
    // Parse competitor entry
    else if (trimmedLine.startsWith('[COMPETITOR]')) {
      // Save previous competitor if exists
      if (currentCompetitor && currentCompetitor.name) {
        competitors.push(currentCompetitor as Competitor)
      }
      currentCompetitor = {
        name: trimmedLine.replace('[COMPETITOR]', '').trim(),
        x: 0,
        y: 0,
        revenue: '',
        segment: '',
        description: ''
      }
    }
    else if (currentCompetitor) {
      if (trimmedLine.startsWith('Pozycja:')) {
        const match = trimmedLine.match(/Pozycja:\s*([\d.]+),\s*([\d.]+)/)
        if (match) {
          currentCompetitor.x = parseFloat(match[1])
          currentCompetitor.y = parseFloat(match[2])
        }
      } else if (trimmedLine.startsWith('Przychody:')) {
        currentCompetitor.revenue = trimmedLine.replace('Przychody:', '').trim()
      } else if (trimmedLine.startsWith('Segment:')) {
        currentCompetitor.segment = trimmedLine.replace('Segment:', '').trim()
      } else if (trimmedLine.startsWith('Opis:')) {
        currentCompetitor.description = trimmedLine.replace('Opis:', '').trim()
      }
    }

    // Parse legend
    if (trimmedLine.includes('Legenda segmentów') || trimmedLine.includes('**Legenda')) {
      inLegend = true
      inAnalysis = false
      inConclusions = false
      // Save last competitor before legend
      if (currentCompetitor && currentCompetitor.name) {
        competitors.push(currentCompetitor as Competitor)
        currentCompetitor = null
      }
      continue
    }

    if (inLegend && trimmedLine.match(/^[🟦🟩🟨🟪🟧🟥⬜]/)) {
      const parts = trimmedLine.split(' - ')
      if (parts.length >= 2) {
        const segment = parts[0].replace(/[🟦🟩🟨🟪🟧🟥⬜]\s*/, '').trim()
        const description = parts.slice(1).join(' - ').trim()
        const colorMap: { [key: string]: string } = {
          '🟦': '#3B82F6',
          '🟩': '#22C55E',
          '🟨': '#EAB308',
          '🟪': '#A855F7',
          '🟧': '#F97316',
          '🟥': '#EF4444',
          '⬜': '#6B7280'
        }
        const emoji = trimmedLine.match(/^[🟦🟩🟨🟪🟧🟥⬜]/)?.[0] || '⬜'
        legend.push({ segment, color: colorMap[emoji] || '#6B7280', description })
      }
    }

    // Parse quadrant analysis
    if (trimmedLine.includes('Analiza pozycjonowania') || trimmedLine.includes('**Analiza')) {
      inLegend = false
      inAnalysis = true
      inConclusions = false
      continue
    }

    if (inAnalysis && trimmedLine.startsWith('- Kwadrant')) {
      quadrantAnalysis.push(trimmedLine.substring(2))
    }

    // Parse conclusions
    if (trimmedLine.includes('**Wnioski') || trimmedLine.includes('Wnioski:')) {
      inLegend = false
      inAnalysis = false
      inConclusions = true
      continue
    }

    if (inConclusions && /^\d+\./.test(trimmedLine)) {
      conclusions.push(trimmedLine.replace(/^\d+\.\s*/, ''))
    }
  }

  // Save last competitor if not yet saved
  if (currentCompetitor && currentCompetitor.name) {
    competitors.push(currentCompetitor as Competitor)
  }

  if (competitors.length === 0) {
    return null
  }

  return {
    xAxisLabel,
    yAxisLabel,
    xMin,
    xMax,
    yMin,
    yMax,
    competitors,
    legend,
    quadrantAnalysis,
    conclusions
  }
}

// Helper function to check if section is Competitor Positioning Map
function isPositioningMapSection(title: string): boolean {
  const lowerTitle = title.toLowerCase()
  return (lowerTitle.includes('pozycjonowanie') && lowerTitle.includes('konkurent')) ||
         (lowerTitle.includes('mapa') && lowerTitle.includes('konkurent')) ||
         (lowerTitle.includes('positioning') && lowerTitle.includes('map')) ||
         (lowerTitle.includes('competitor') && lowerTitle.includes('position'))
}

// Competitor Positioning Map Component
function CompetitorPositioningMap({ data, onCompetitorClick }: { data: PositioningMapData; onCompetitorClick?: (competitor: Competitor) => void }) {
  const [selectedCompetitor, setSelectedCompetitor] = useState<Competitor | null>(null)
  const [hoveredCompetitor, setHoveredCompetitor] = useState<Competitor | null>(null)

  // Plot dimensions
  const plotWidth = 600
  const plotHeight = 400
  const padding = { top: 30, right: 30, bottom: 60, left: 60 }
  const innerWidth = plotWidth - padding.left - padding.right
  const innerHeight = plotHeight - padding.top - padding.bottom

  // Scale functions
  const scaleX = (value: number): number => {
    return padding.left + ((value - data.xMin) / (data.xMax - data.xMin)) * innerWidth
  }

  const scaleY = (value: number): number => {
    return plotHeight - padding.bottom - ((value - data.yMin) / (data.yMax - data.yMin)) * innerHeight
  }

  // Get segment color
  const getSegmentColor = (segment: string): string => {
    const found = data.legend.find(l => l.segment.toLowerCase() === segment.toLowerCase())
    if (found) return found.color

    // Default colors based on keywords
    if (segment.toLowerCase().includes('enterprise') || segment.toLowerCase().includes('software')) return '#3B82F6'
    if (segment.toLowerCase().includes('saas')) return '#22C55E'
    if (segment.toLowerCase().includes('gaming') || segment.toLowerCase().includes('gier')) return '#EAB308'
    if (segment.toLowerCase().includes('e-commerce') || segment.toLowerCase().includes('commerce')) return '#A855F7'
    if (segment.toLowerCase().includes('hr')) return '#F97316'
    if (segment.toLowerCase().includes('health')) return '#EF4444'
    return '#6B7280'
  }

  // Calculate bubble size based on revenue
  const getBubbleSize = (revenue: string): number => {
    const match = revenue.match(/([\d,]+)/)?.[1]
    if (!match) return 20
    const value = parseFloat(match.replace(/,/g, ''))
    // Scale: 100 -> 15px, 15000 -> 50px
    const minSize = 15
    const maxSize = 50
    const size = minSize + (Math.log10(value + 1) / Math.log10(20000)) * (maxSize - minSize)
    return Math.max(minSize, Math.min(maxSize, size))
  }

  const handleCompetitorClick = (competitor: Competitor) => {
    setSelectedCompetitor(selectedCompetitor?.name === competitor.name ? null : competitor)
    onCompetitorClick?.(competitor)
  }

  // Grid lines for X axis
  const xGridLines = []
  const xStep = (data.xMax - data.xMin) / 5
  for (let i = 0; i <= 5; i++) {
    const value = data.xMin + i * xStep
    xGridLines.push(value)
  }

  // Grid lines for Y axis
  const yGridLines = []
  const yStep = (data.yMax - data.yMin) / 5
  for (let i = 0; i <= 5; i++) {
    const value = data.yMin + i * yStep
    yGridLines.push(value)
  }

  // Quadrant dividers (middle)
  const midX = (data.xMax + data.xMin) / 2
  const midY = (data.yMax + data.yMin) / 2

  return (
    <div className="w-full">
      {/* Legend */}
      <div className="mb-4 flex flex-wrap items-center justify-center gap-3 text-sm">
        {data.legend.map((item, idx) => (
          <div key={idx} className="flex items-center gap-2">
            <span
              className="h-3 w-3 rounded-full"
              style={{ backgroundColor: item.color }}
            ></span>
            <span className="text-gray-600">{item.segment}</span>
          </div>
        ))}
      </div>

      {/* Scatter Plot SVG */}
      <div className="flex justify-center">
        <svg
          viewBox={`0 0 ${plotWidth} ${plotHeight}`}
          className="w-full max-w-2xl"
          style={{ maxHeight: '450px' }}
        >
          {/* Background */}
          <rect
            x={padding.left}
            y={padding.top}
            width={innerWidth}
            height={innerHeight}
            fill="#F8FAFC"
            stroke="#E2E8F0"
          />

          {/* Grid lines */}
          {xGridLines.map((value, idx) => (
            <line
              key={`x-grid-${idx}`}
              x1={scaleX(value)}
              y1={padding.top}
              x2={scaleX(value)}
              y2={plotHeight - padding.bottom}
              stroke="#E2E8F0"
              strokeDasharray="4,4"
            />
          ))}
          {yGridLines.map((value, idx) => (
            <line
              key={`y-grid-${idx}`}
              x1={padding.left}
              y1={scaleY(value)}
              x2={plotWidth - padding.right}
              y2={scaleY(value)}
              stroke="#E2E8F0"
              strokeDasharray="4,4"
            />
          ))}

          {/* Quadrant dividers */}
          <line
            x1={scaleX(midX)}
            y1={padding.top}
            x2={scaleX(midX)}
            y2={plotHeight - padding.bottom}
            stroke="#94A3B8"
            strokeWidth="1.5"
            strokeDasharray="8,4"
          />
          <line
            x1={padding.left}
            y1={scaleY(midY)}
            x2={plotWidth - padding.right}
            y2={scaleY(midY)}
            stroke="#94A3B8"
            strokeWidth="1.5"
            strokeDasharray="8,4"
          />

          {/* Quadrant labels */}
          <text x={padding.left + 10} y={padding.top + 20} fill="#64748B" fontSize="10" fontWeight="500">
            Innowatorzy
          </text>
          <text x={plotWidth - padding.right - 60} y={padding.top + 20} fill="#64748B" fontSize="10" fontWeight="500">
            Liderzy
          </text>
          <text x={padding.left + 10} y={plotHeight - padding.bottom - 10} fill="#64748B" fontSize="10" fontWeight="500">
            Nisza
          </text>
          <text x={plotWidth - padding.right - 80} y={plotHeight - padding.bottom - 10} fill="#64748B" fontSize="10" fontWeight="500">
            Konsolidatorzy
          </text>

          {/* X Axis */}
          <line
            x1={padding.left}
            y1={plotHeight - padding.bottom}
            x2={plotWidth - padding.right}
            y2={plotHeight - padding.bottom}
            stroke="#334155"
            strokeWidth="2"
          />
          {/* X Axis Label */}
          <text
            x={plotWidth / 2}
            y={plotHeight - 15}
            textAnchor="middle"
            fill="#334155"
            fontSize="12"
            fontWeight="500"
          >
            {data.xAxisLabel}
          </text>
          {/* X Axis Ticks */}
          {xGridLines.map((value, idx) => (
            <g key={`x-tick-${idx}`}>
              <line
                x1={scaleX(value)}
                y1={plotHeight - padding.bottom}
                x2={scaleX(value)}
                y2={plotHeight - padding.bottom + 5}
                stroke="#334155"
              />
              <text
                x={scaleX(value)}
                y={plotHeight - padding.bottom + 18}
                textAnchor="middle"
                fill="#64748B"
                fontSize="10"
              >
                {value.toFixed(1)}
              </text>
            </g>
          ))}

          {/* Y Axis */}
          <line
            x1={padding.left}
            y1={padding.top}
            x2={padding.left}
            y2={plotHeight - padding.bottom}
            stroke="#334155"
            strokeWidth="2"
          />
          {/* Y Axis Label */}
          <text
            x={15}
            y={plotHeight / 2}
            textAnchor="middle"
            fill="#334155"
            fontSize="12"
            fontWeight="500"
            transform={`rotate(-90, 15, ${plotHeight / 2})`}
          >
            {data.yAxisLabel}
          </text>
          {/* Y Axis Ticks */}
          {yGridLines.map((value, idx) => (
            <g key={`y-tick-${idx}`}>
              <line
                x1={padding.left - 5}
                y1={scaleY(value)}
                x2={padding.left}
                y2={scaleY(value)}
                stroke="#334155"
              />
              <text
                x={padding.left - 10}
                y={scaleY(value) + 4}
                textAnchor="end"
                fill="#64748B"
                fontSize="10"
              >
                {value.toFixed(1)}
              </text>
            </g>
          ))}

          {/* Competitor bubbles */}
          {data.competitors.map((competitor, idx) => {
            const cx = scaleX(competitor.x)
            const cy = scaleY(competitor.y)
            const r = getBubbleSize(competitor.revenue)
            const color = getSegmentColor(competitor.segment)
            const isSelected = selectedCompetitor?.name === competitor.name
            const isHovered = hoveredCompetitor?.name === competitor.name

            return (
              <g
                key={idx}
                onClick={() => handleCompetitorClick(competitor)}
                onMouseEnter={() => setHoveredCompetitor(competitor)}
                onMouseLeave={() => setHoveredCompetitor(null)}
                style={{ cursor: 'pointer' }}
              >
                {/* Bubble */}
                <circle
                  cx={cx}
                  cy={cy}
                  r={r}
                  fill={color}
                  fillOpacity={isSelected || isHovered ? 0.9 : 0.7}
                  stroke={isSelected ? '#1E293B' : isHovered ? '#475569' : 'white'}
                  strokeWidth={isSelected ? 3 : isHovered ? 2 : 1.5}
                  className="transition-all duration-200"
                />
                {/* Company name label */}
                <text
                  x={cx}
                  y={cy - r - 5}
                  textAnchor="middle"
                  fill="#1E293B"
                  fontSize="9"
                  fontWeight="500"
                >
                  {competitor.name.split(' ')[0]}
                </text>
              </g>
            )
          })}
        </svg>
      </div>

      {/* Tooltip / Details panel */}
      {(selectedCompetitor || hoveredCompetitor) && (
        <div className="mt-4 rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="flex items-center gap-3 mb-2">
            <span
              className="h-4 w-4 rounded-full"
              style={{ backgroundColor: getSegmentColor((selectedCompetitor || hoveredCompetitor)!.segment) }}
            ></span>
            <span className="font-semibold text-gray-900">
              {(selectedCompetitor || hoveredCompetitor)!.name}
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
              {(selectedCompetitor || hoveredCompetitor)!.segment}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Przychody:</span>{' '}
              <span className="font-medium text-gray-900">{(selectedCompetitor || hoveredCompetitor)!.revenue}</span>
            </div>
            <div>
              <span className="text-gray-500">Pozycja:</span>{' '}
              <span className="font-medium text-gray-900">
                X: {(selectedCompetitor || hoveredCompetitor)!.x.toFixed(1)}, Y: {(selectedCompetitor || hoveredCompetitor)!.y.toFixed(1)}
              </span>
            </div>
          </div>
          <p className="mt-2 text-sm text-gray-600">
            {(selectedCompetitor || hoveredCompetitor)!.description}
          </p>
        </div>
      )}

      {/* Quadrant Analysis */}
      {data.quadrantAnalysis.length > 0 && (
        <div className="mt-4 p-4 rounded-lg bg-slate-50 border border-slate-200">
          <h4 className="font-semibold text-gray-800 mb-2">📊 Analiza kwadrantów</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            {data.quadrantAnalysis.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-indigo-500 mt-1">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Conclusions */}
      {data.conclusions.length > 0 && (
        <div className="mt-4 p-4 rounded-lg bg-blue-50 border border-blue-200">
          <h4 className="font-semibold text-blue-800 mb-2">💡 Wnioski</h4>
          <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
            {data.conclusions.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ol>
        </div>
      )}

      {/* Stats */}
      <div className="mt-4 flex justify-center gap-6 text-sm">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-100 text-indigo-700">
          <span className="font-medium">Konkurenci: {data.competitors.length}</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-purple-100 text-purple-700">
          <span className="font-medium">Segmenty: {data.legend.length}</span>
        </div>
      </div>

      {/* Tip */}
      <div className="mt-3 text-center text-xs text-gray-400">
        💡 Kliknij na bąbelek, aby zobaczyć szczegóły firmy. Rozmiar bąbelka odzwierciedla przychody.
      </div>
    </div>
  )
}

// Helper functions for text formatting
function applyMarkdownFormatting(text: string, textarea: HTMLTextAreaElement, format: string): string {
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = text.substring(start, end)

  if (!selectedText) return text

  let formattedText = ''
  let newText = ''

  switch (format) {
    case 'bold':
      formattedText = `**${selectedText}**`
      break
    case 'italic':
      formattedText = `*${selectedText}*`
      break
    case 'link':
      const url = prompt('Enter URL:')
      if (url) {
        formattedText = `[${selectedText}](${url})`
      } else {
        return text
      }
      break
    default:
      return text
  }

  newText = text.substring(0, start) + formattedText + text.substring(end)

  // Set cursor position after formatted text
  setTimeout(() => {
    textarea.selectionStart = textarea.selectionEnd = start + formattedText.length
    textarea.focus()
  }, 0)

  return newText
}

function insertBulletedList(text: string, textarea: HTMLTextAreaElement): string {
  const start = textarea.selectionStart
  const listItem = '\n- '
  const newText = text.substring(0, start) + listItem + text.substring(start)

  setTimeout(() => {
    textarea.selectionStart = textarea.selectionEnd = start + listItem.length
    textarea.focus()
  }, 0)

  return newText
}

function insertTable(text: string, textarea: HTMLTextAreaElement, rows: number, cols: number): string {
  const start = textarea.selectionStart

  // Generate markdown table
  let table = '\n\n'

  // Header row
  table += '|'
  for (let i = 0; i < cols; i++) {
    table += ` Header ${i + 1} |`
  }
  table += '\n'

  // Separator row
  table += '|'
  for (let i = 0; i < cols; i++) {
    table += ' --- |'
  }
  table += '\n'

  // Data rows
  for (let r = 0; r < rows - 1; r++) {
    table += '|'
    for (let c = 0; c < cols; c++) {
      table += ` Cell ${r + 1}-${c + 1} |`
    }
    table += '\n'
  }

  table += '\n'

  const newText = text.substring(0, start) + table + text.substring(start)

  setTimeout(() => {
    textarea.selectionStart = textarea.selectionEnd = start + table.length
    textarea.focus()
  }, 0)

  return newText
}

// Sortable Section Wrapper Component for Drag & Drop
function SortableSectionWrapper({ section, children }: { section: { id: string }, children: React.ReactNode }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: section.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <div ref={setNodeRef} style={style} className="relative">
      {/* Drag Handle */}
      <div
        {...attributes}
        {...listeners}
        className="absolute -left-8 top-6 cursor-grab active:cursor-grabbing text-gray-400 hover:text-gray-600"
        title="Przeciągnij aby zmienić kolejność"
      >
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M9 3h2v2H9V3zm0 4h2v2H9V7zm0 4h2v2H9v-2zm0 4h2v2H9v-2zm0 4h2v2H9v-2zM13 3h2v2h-2V3zm0 4h2v2h-2V7zm0 4h2v2h-2v-2zm0 4h2v2h-2v-2zm0 4h2v2h-2v-2z"/>
        </svg>
      </div>
      {children}
    </div>
  )
}

export default function ReportViewerPage() {
  const router = useRouter()
  const params = useParams()
  const reportId = params.id as string

  const [report, setReport] = useState<ReportDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  // Search state
  const [searchQuery, setSearchQuery] = useState('')
  const [searchMatches, setSearchMatches] = useState<SearchMatch[]>([])
  const [currentMatchIndex, setCurrentMatchIndex] = useState(0)
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const searchInputRef = useRef<HTMLInputElement>(null)

  // Annotation state
  const [annotations, setAnnotations] = useState<Annotation[]>([])
  const [selectedText, setSelectedText] = useState('')
  const [selectionInfo, setSelectionInfo] = useState<{
    sectionId: string
    startOffset: number
    endOffset: number
    rect: DOMRect | null
  } | null>(null)
  const [annotationComment, setAnnotationComment] = useState('')
  const [showAnnotationModal, setShowAnnotationModal] = useState(false)
  const [isSavingAnnotation, setIsSavingAnnotation] = useState(false)

  // Version history state
  const [versions, setVersions] = useState<ReportVersion[]>([])
  const [showVersionHistory, setShowVersionHistory] = useState(false)
  const [currentVersion, setCurrentVersion] = useState<number | null>(null)
  const [isLoadingVersion, setIsLoadingVersion] = useState(false)

  // Restore version state
  const [showRestoreConfirm, setShowRestoreConfirm] = useState(false)
  const [versionToRestore, setVersionToRestore] = useState<number | null>(null)
  const [isRestoring, setIsRestoring] = useState(false)
  const [restoreMessage, setRestoreMessage] = useState('')

  // Collaboration comments state
  const [comments, setComments] = useState<Comment[]>([])
  const [newCommentText, setNewCommentText] = useState('')
  const [isSubmittingComment, setIsSubmittingComment] = useState(false)
  const [showCommentsPanel, setShowCommentsPanel] = useState(false)
  const [replyingTo, setReplyingTo] = useState<string | null>(null)
  const [showResolvedComments, setShowResolvedComments] = useState(true)
  const [isResolvingComment, setIsResolvingComment] = useState<string | null>(null)

  // Export state
  const [showExportMenu, setShowExportMenu] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [exportError, setExportError] = useState('')
  const [selectedSections, setSelectedSections] = useState<string[]>([]) // IDs of sections to export
  const [preferredFormat, setPreferredFormat] = useState<string>('pdf') // User's preferred export format

  // Share via email state
  const [showShareModal, setShowShareModal] = useState(false)
  const [shareTab, setShareTab] = useState<'email' | 'link' | 'embed'>('link') // Default to link tab
  const [embedCode, setEmbedCode] = useState('')
  const [embedCopied, setEmbedCopied] = useState(false)
  const [shareEmail, setShareEmail] = useState('')
  const [shareMessage, setShareMessage] = useState('')
  const [isSharing, setIsSharing] = useState(false)
  const [shareSuccess, setShareSuccess] = useState(false)
  const [shareError, setShareError] = useState('')

  // Share link state
  const [shareLink, setShareLink] = useState('')
  const [isGeneratingLink, setIsGeneratingLink] = useState(false)
  const [linkCopied, setLinkCopied] = useState(false)
  const [sharePassword, setSharePassword] = useState('')
  const [passwordProtected, setPasswordProtected] = useState(false)

  // Access log state
  const [showAccessLogModal, setShowAccessLogModal] = useState(false)
  const [accessLogData, setAccessLogData] = useState<any>(null)
  const [isLoadingAccessLog, setIsLoadingAccessLog] = useState(false)

  // Edit mode state
  const [isEditing, setIsEditing] = useState(false)
  const [editedSections, setEditedSections] = useState<{[key: string]: string}>({})
  const [editedTitle, setEditedTitle] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [sortedSections, setSortedSections] = useState<ReportSection[]>([])  // For drag & drop reordering
  const [editedSectionTitles, setEditedSectionTitles] = useState<{[key: string]: string}>({})  // For section title editing

  // Auto-save state
  const [lastAutoSave, setLastAutoSave] = useState<Date | null>(null)
  const [isAutoSaving, setIsAutoSaving] = useState(false)
  const editedSectionsRef = useRef<{[key: string]: string}>({})

  // Table insertion state
  const [showTableModal, setShowTableModal] = useState(false)
  const [tableRows, setTableRows] = useState(3)
  const [tableCols, setTableCols] = useState(3)
  const [currentSectionForTable, setCurrentSectionForTable] = useState<string | null>(null)

  // Delete section state
  const [showDeleteConfirmModal, setShowDeleteConfirmModal] = useState(false)
  const [sectionToDelete, setSectionToDelete] = useState<{ id: string, title: string } | null>(null)

  // Collapse/expand sections state
  const [collapsedSections, setCollapsedSections] = useState<Set<string>>(new Set())

  useEffect(() => {
    fetchReport()
    fetchAnnotations()
    fetchVersions()
    fetchComments()
    fetchUserPreferences()
  }, [reportId])

  // Refresh user preferences when export menu is opened
  useEffect(() => {
    if (showExportMenu) {
      fetchUserPreferences()
    }
  }, [showExportMenu])

  // Sync sortedSections with report.sections when report loads
  useEffect(() => {
    if (report && report.sections) {
      setSortedSections([...report.sections])
      // Initialize all sections as selected by default
      setSelectedSections(report.sections.map(s => s.id))
    }
  }, [report])

  // Handle hash navigation for deep linking to sections
  useEffect(() => {
    // Only run after report is loaded
    if (!report) return

    const hash = window.location.hash
    if (hash) {
      // Small delay to ensure DOM is fully rendered
      setTimeout(() => {
        const element = document.querySelector(hash)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }, 300)
    }
  }, [report])

  // Keyboard shortcut for search (Ctrl+F)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault()
        setIsSearchOpen(true)
        setTimeout(() => searchInputRef.current?.focus(), 100)
      }
      if (e.key === 'Escape') {
        setIsSearchOpen(false)
        setSearchQuery('')
        setSearchMatches([])
        setShowAnnotationModal(false)
        setShowRestoreConfirm(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Text selection handler
  useEffect(() => {
    const handleSelectionChange = () => {
      const selection = window.getSelection()
      if (!selection || selection.isCollapsed || !selection.toString().trim()) {
        return
      }

      const text = selection.toString().trim()
      if (text.length < 3) return // Minimum 3 characters

      // Find which section the selection is in
      const anchorNode = selection.anchorNode
      if (!anchorNode) return

      let element: HTMLElement | null = anchorNode.nodeType === Node.TEXT_NODE
        ? anchorNode.parentElement
        : anchorNode as HTMLElement

      while (element && !element.id?.startsWith('section-')) {
        element = element.parentElement
      }

      if (element && element.id) {
        const sectionId = element.id.replace('section-', '')
        const range = selection.getRangeAt(0)
        const rect = range.getBoundingClientRect()

        setSelectedText(text)
        setSelectionInfo({
          sectionId,
          startOffset: range.startOffset,
          endOffset: range.endOffset,
          rect
        })
      }
    }

    document.addEventListener('selectionchange', handleSelectionChange)
    return () => document.removeEventListener('selectionchange', handleSelectionChange)
  }, [])

  // Keep ref in sync with editedSections
  useEffect(() => {
    editedSectionsRef.current = editedSections
  }, [editedSections])

  // Auto-save effect - saves to localStorage every 30 seconds when editing
  useEffect(() => {
    if (!isEditing) return

    // Save immediately when edit mode starts
    const timeoutId = setTimeout(() => {
      autoSaveToLocal()
    }, 1000) // Wait 1 second before first auto-save

    // Then set up interval for periodic saves
    const intervalId = setInterval(() => {
      autoSaveToLocal()
    }, 30000) // Auto-save every 30 seconds

    return () => {
      clearTimeout(timeoutId)
      clearInterval(intervalId)
    }
  }, [isEditing, reportId])

  // Drag & Drop sensors for section reordering
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  // Handle drag end event for section reordering
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event

    if (!over || active.id === over.id) {
      return
    }

    setSortedSections((sections) => {
      const oldIndex = sections.findIndex((s) => s.id === active.id)
      const newIndex = sections.findIndex((s) => s.id === over.id)

      return arrayMove(sections, oldIndex, newIndex)
    })

    // Mark as having unsaved changes
    setIsSaving(false)
  }

  // Handle delete section click - show confirmation modal
  const handleDeleteSectionClick = (sectionId: string, sectionTitle: string) => {
    setSectionToDelete({ id: sectionId, title: sectionTitle })
    setShowDeleteConfirmModal(true)
  }

  // Confirm and delete section
  const confirmDeleteSection = () => {
    if (!sectionToDelete) return

    // Remove section from sortedSections
    setSortedSections((sections) => sections.filter((s) => s.id !== sectionToDelete.id))

    // Remove section content from editedSections
    const newEditedSections = { ...editedSections }
    delete newEditedSections[sectionToDelete.id]
    setEditedSections(newEditedSections)

    // Remove section title from editedSectionTitles
    const newEditedTitles = { ...editedSectionTitles }
    delete newEditedTitles[sectionToDelete.id]
    setEditedSectionTitles(newEditedTitles)

    // Close modal
    setShowDeleteConfirmModal(false)
    setSectionToDelete(null)

    // Mark as having unsaved changes
    setIsSaving(false)
  }

  const fetchReport = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Raport nie został znaleziony. Mógł zostać usunięty.')
        }
        throw new Error('Failed to fetch report')
      }

      const data = await response.json()
      setReport(data)
    } catch (err) {
      if (err instanceof Error && err.message.includes('znaleziony')) {
        setError(err.message)
      } else {
        setError('Nie udalo sie zaladowac raportu')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const fetchAnnotations = async () => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/annotations`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setAnnotations(data.annotations || [])
      }
    } catch (err) {
      console.error('Failed to fetch annotations:', err)
    }
  }

  // Add new section
  const addNewSection = () => {
    const newSection: ReportSection = {
      id: `section_new_${Date.now()}`,
      title: 'Nowa sekcja',
      content: 'Wpisz treść sekcji...'
    }

    setSortedSections([...sortedSections, newSection])
    setEditedSections({ ...editedSections, [newSection.id]: newSection.content })
  }

  const saveReportChanges = async () => {
    const token = getStoredToken()
    if (!token || !report) return

    setIsSaving(true)

    try {
      // Update sections with edited content, titles AND new order from sortedSections
      const updatedSections = sortedSections.map(section => ({
        ...section,
        title: editedSectionTitles[section.id] || section.title,
        content: editedSections[section.id] || section.content
      }))

      // Prepare update payload
      const updatePayload: any = {
        sections: updatedSections,
        last_known_updated_at: report.updated_at  // For conflict detection
      }

      // Include title if it was edited
      if (editedTitle && editedTitle !== report.title) {
        updatePayload.title = editedTitle
      }

      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updatePayload)
        }
      )

      if (response.ok) {
        // Clear auto-save draft since changes are now saved
        clearAutoSaveDraft()
        // Refresh report to get updated content
        await fetchReport()
        setIsEditing(false)
        setEditedSections({})
        setEditedTitle('')
        // Show success toast
        toast.success('Raport zapisany pomyślnie', {
          description: 'Wszystkie zmiany zostały zapisane'
        })
      } else if (response.status === 409) {
        // Edit conflict detected
        const errorData = await response.json()
        const conflictMessage = errorData.detail?.message || 'This report was modified by another user.'
        if (confirm(`${conflictMessage}\n\nClick OK to refresh and see the latest version (your changes will be lost), or Cancel to keep editing.`)) {
          // User chose to refresh - reload the report
          await fetchReport()
          setIsEditing(false)
          setEditedSections({})
          setEditedTitle('')
          clearAutoSaveDraft()
        }
        // If user cancelled, they stay in edit mode with their changes
      } else {
        toast.error('Nie udało się zapisać zmian', {
          description: 'Spróbuj ponownie'
        })
      }
    } catch (err) {
      console.error('Failed to save report:', err)
      toast.error('Nie udało się zapisać zmian', {
        description: 'Wystąpił błąd podczas zapisywania'
      })
    } finally {
      setIsSaving(false)
    }
  }

  // Auto-save to localStorage
  const autoSaveToLocal = () => {
    const currentSections = editedSectionsRef.current
    if (!reportId || Object.keys(currentSections).length === 0) return

    try {
      setIsAutoSaving(true)
      localStorage.setItem(`draft_${reportId}`, JSON.stringify({
        sections: currentSections,
        timestamp: new Date().toISOString()
      }))
      setLastAutoSave(new Date())

      // Clear auto-saving indicator after 1 second
      setTimeout(() => setIsAutoSaving(false), 1000)
    } catch (err) {
      console.error('Failed to auto-save to localStorage:', err)
      setIsAutoSaving(false)
    }
  }

  // Clear auto-save draft from localStorage
  const clearAutoSaveDraft = () => {
    if (!reportId) return
    try {
      localStorage.removeItem(`draft_${reportId}`)
      setLastAutoSave(null)
    } catch (err) {
      console.error('Failed to clear draft:', err)
    }
  }

  const toggleEditMode = () => {
    if (isEditing) {
      // Cancel editing - reset edited sections and clear draft
      setEditedSections({})
      setEditedTitle('')
      clearAutoSaveDraft()
    } else {
      // Enter edit mode - check for auto-saved draft first
      let initialEdited: {[key: string]: string} = {}

      try {
        const draftData = localStorage.getItem(`draft_${reportId}`)
        if (draftData) {
          const draft = JSON.parse(draftData)
          const draftAge = new Date().getTime() - new Date(draft.timestamp).getTime()
          const oneHour = 60 * 60 * 1000

          // Only restore if draft is less than 1 hour old
          if (draftAge < oneHour && confirm('Znaleziono niezapisane zmiany. Czy chcesz je przywrócić?')) {
            initialEdited = draft.sections
            setLastAutoSave(new Date(draft.timestamp))
          } else {
            // Clear old draft
            clearAutoSaveDraft()
          }
        }
      } catch (err) {
        console.error('Failed to restore draft:', err)
      }

      // If no draft restored, initialize with current content
      if (Object.keys(initialEdited).length === 0) {
        report?.sections.forEach(section => {
          initialEdited[section.id] = section.content
        })
      }

      setEditedSections(initialEdited)
      // Initialize title with current report title
      setEditedTitle(report?.title || '')
    }
    setIsEditing(!isEditing)
  }

  const fetchVersions = async () => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/versions`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setVersions(data.versions || [])
        // Set current version
        const current = data.versions?.find((v: ReportVersion) => v.is_current)
        if (current) {
          setCurrentVersion(current.version)
        }
      }
    } catch (err) {
      console.error('Failed to fetch versions:', err)
    }
  }

  const loadVersion = async (version: number) => {
    const token = getStoredToken()
    if (!token) return

    setIsLoadingVersion(true)

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/versions/${version}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setReport(data)
        setCurrentVersion(version)
        setShowVersionHistory(false)
      }
    } catch (err) {
      console.error('Failed to load version:', err)
    } finally {
      setIsLoadingVersion(false)
    }
  }

  const restoreVersion = async () => {
    if (!versionToRestore) return

    const token = getStoredToken()
    if (!token) return

    setIsRestoring(true)
    setRestoreMessage('')

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/versions/restore/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ version: versionToRestore }),
        }
      )

      if (response.ok) {
        const data = await response.json()
        setRestoreMessage(`Przywrócono wersję ${versionToRestore}. Utworzono nową wersję ${data.new_version}.`)
        setShowRestoreConfirm(false)
        // Refresh versions and report
        await fetchVersions()
        await loadVersion(data.new_version)
      } else {
        setRestoreMessage('Nie udało się przywrócić wersji')
      }
    } catch (err) {
      console.error('Failed to restore version:', err)
      setRestoreMessage('Błąd podczas przywracania wersji')
    } finally {
      setIsRestoring(false)
    }
  }

  const handleRestoreClick = (version: number, e: React.MouseEvent) => {
    e.stopPropagation()
    setVersionToRestore(version)
    setShowRestoreConfirm(true)
  }

  const fetchComments = async () => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/comments`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setComments(data.comments || [])
      }
    } catch (err) {
      console.error('Failed to fetch comments:', err)
    }
  }

  const fetchUserPreferences = async () => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(
        `${API_BASE_URL}/users/me/preferences`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        if (data.preferred_format) {
          setPreferredFormat(data.preferred_format)
        }
      }
    } catch (err) {
      console.error('Failed to fetch user preferences:', err)
    }
  }

  const submitComment = async (parentId: string | null = null) => {
    if (!newCommentText.trim()) return

    const token = getStoredToken()
    if (!token) return

    setIsSubmittingComment(true)

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/comments`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ text: newCommentText, parent_id: parentId }),
        }
      )

      if (response.ok) {
        const newComment = await response.json()
        setComments(prev => [...prev, newComment])
        setNewCommentText('')
        setReplyingTo(null)
      }
    } catch (err) {
      console.error('Failed to submit comment:', err)
    } finally {
      setIsSubmittingComment(false)
    }
  }

  const deleteComment = async (commentId: string) => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/comments/${commentId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        setComments(prev => prev.filter(c => c.id !== commentId))
      }
    } catch (err) {
      console.error('Failed to delete comment:', err)
    }
  }

  const resolveComment = async (commentId: string) => {
    const token = getStoredToken()
    if (!token) return

    setIsResolvingComment(commentId)

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/comments/${commentId}/resolve`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        // Update the comment in local state
        setComments(prev => prev.map(c =>
          c.id === commentId ? data.comment : c
        ))
      }
    } catch (err) {
      console.error('Failed to resolve comment:', err)
    } finally {
      setIsResolvingComment(null)
    }
  }

  const saveAnnotation = async () => {
    if (!selectedText || !selectionInfo || !annotationComment.trim()) return

    const token = getStoredToken()
    if (!token) return

    setIsSavingAnnotation(true)

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/annotations`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            section_id: selectionInfo.sectionId,
            selected_text: selectedText,
            start_offset: selectionInfo.startOffset,
            end_offset: selectionInfo.endOffset,
            comment: annotationComment,
          }),
        }
      )

      if (response.ok) {
        const newAnnotation = await response.json()
        setAnnotations(prev => [...prev, newAnnotation])
        setShowAnnotationModal(false)
        setAnnotationComment('')
        setSelectedText('')
        setSelectionInfo(null)
        // Clear selection
        window.getSelection()?.removeAllRanges()
      }
    } catch (err) {
      console.error('Failed to save annotation:', err)
    } finally {
      setIsSavingAnnotation(false)
    }
  }

  const deleteAnnotation = async (annotationId: string) => {
    const token = getStoredToken()
    if (!token) return

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/annotations/${annotationId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        setAnnotations(prev => prev.filter(a => a.id !== annotationId))
      }
    } catch (err) {
      console.error('Failed to delete annotation:', err)
    }
  }

  // Duplicate report
  const duplicateReport = async () => {
    const token = getStoredToken()
    if (!token || !reportId) return

    const csrfToken = await getCsrfToken()

    try {
      const headers: HeadersInit = {
        'Authorization': `Bearer ${token}`,
      }

      if (csrfToken) {
        headers['X-CSRF-Token'] = csrfToken
      }

      const response = await fetch(`${API_BASE_URL}/reports/${reportId}/duplicate`, {
        method: 'POST',
        headers,
      })

      if (response.ok) {
        const data = await response.json()
        // Navigate to the newly created duplicate report
        router.push(`/reports/${data.new_id}`)
      } else {
        console.error('Failed to duplicate report:', await response.text())
        alert('Nie udało się zduplikować raportu')
      }
    } catch (err) {
      console.error('Failed to duplicate report:', err)
      alert('Wystąpił błąd podczas duplikowania raportu')
    }
  }

  // Save as template
  const saveAsTemplate = async () => {
    const token = getStoredToken()
    if (!token || !reportId) return

    const templateName = prompt('Wprowadź nazwę szablonu:')
    if (!templateName || templateName.trim() === '') return

    try {
      // Get CSRF token
      const csrfToken = await getCsrfToken()
      if (!csrfToken) {
        alert('Nie udało się pobrać tokenu CSRF')
        return
      }

      const response = await fetch(`${API_BASE_URL}/reports/${reportId}/save-as-template?template_name=${encodeURIComponent(templateName.trim())}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-CSRF-Token': csrfToken,
        },
      })

      if (response.ok) {
        const data = await response.json()
        alert(`Szablon "${templateName}" został utworzony pomyślnie!`)
      } else {
        console.error('Failed to save template:', await response.text())
        alert('Nie udało się zapisać szablonu')
      }
    } catch (err) {
      console.error('Failed to save template:', err)
      alert('Wystąpił błąd podczas zapisywania szablonu')
    }
  }

  // Toggle favorite status
  const toggleFavorite = async () => {
    const token = getStoredToken()
    if (!token || !report) return

    const isFavorite = report.is_favorite
    const csrfToken = await getCsrfToken()

    try {
      const method = isFavorite ? 'DELETE' : 'POST'
      const headers: HeadersInit = {
        'Authorization': `Bearer ${token}`,
      }

      if (csrfToken) {
        headers['X-CSRF-Token'] = csrfToken
      }

      const response = await fetch(`${API_BASE_URL}/reports/${reportId}/favorite`, {
        method,
        headers,
      })

      if (response.ok) {
        // Update the report in local state
        setReport(prev => prev ? { ...prev, is_favorite: !isFavorite } : null)
      }
    } catch (err) {
      console.error('Failed to toggle favorite:', err)
    }
  }

  const archiveReport = async () => {
    const token = getStoredToken()
    if (!token || !reportId) return

    const csrfToken = await getCsrfToken()

    try {
      const headers: HeadersInit = {
        'Authorization': `Bearer ${token}`,
      }

      if (csrfToken) {
        headers['X-CSRF-Token'] = csrfToken
      }

      const response = await fetch(`${API_BASE_URL}/reports/${reportId}/archive`, {
        method: 'POST',
        headers,
      })

      if (response.ok) {
        // Redirect to reports list after archiving
        router.push('/reports')
      }
    } catch (err) {
      console.error('Failed to archive report:', err)
    }
  }

  const unarchiveReport = async () => {
    const token = getStoredToken()
    if (!token || !reportId) return

    const csrfToken = await getCsrfToken()

    try {
      const headers: HeadersInit = {
        'Authorization': `Bearer ${token}`,
      }

      if (csrfToken) {
        headers['X-CSRF-Token'] = csrfToken
      }

      const response = await fetch(`${API_BASE_URL}/reports/${reportId}/unarchive`, {
        method: 'POST',
        headers,
      })

      if (response.ok) {
        // Redirect to reports list after unarchiving
        router.push('/reports')
      }
    } catch (err) {
      console.error('Failed to unarchive report:', err)
    }
  }

  // Search functionality
  const performSearch = useCallback((query: string) => {
    if (!report || !query.trim()) {
      setSearchMatches([])
      setCurrentMatchIndex(0)
      return
    }

    const matches: SearchMatch[] = []
    const queryLower = query.toLowerCase()

    report.sections.forEach((section) => {
      const contentLower = section.content.toLowerCase()
      let startIndex = 0

      while (true) {
        const index = contentLower.indexOf(queryLower, startIndex)
        if (index === -1) break

        // Get context around the match (50 chars before and after)
        const contextStart = Math.max(0, index - 50)
        const contextEnd = Math.min(section.content.length, index + query.length + 50)
        let context = section.content.substring(contextStart, contextEnd)

        if (contextStart > 0) context = '...' + context
        if (contextEnd < section.content.length) context = context + '...'

        matches.push({
          sectionId: section.id,
          sectionTitle: section.title,
          startIndex: index,
          endIndex: index + query.length,
          context
        })

        startIndex = index + 1
      }
    })

    setSearchMatches(matches)
    setCurrentMatchIndex(0)

    // Scroll to first match
    if (matches.length > 0) {
      scrollToMatch(0, matches)
    }
  }, [report])

  const scrollToMatch = (index: number, matches: SearchMatch[] = searchMatches) => {
    if (matches.length === 0) return

    const match = matches[index]
    const sectionElement = document.getElementById(`section-${match.sectionId}`)
    if (sectionElement) {
      sectionElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value
    setSearchQuery(query)
    performSearch(query)
  }

  const goToNextMatch = () => {
    if (searchMatches.length === 0) return
    const nextIndex = (currentMatchIndex + 1) % searchMatches.length
    setCurrentMatchIndex(nextIndex)
    scrollToMatch(nextIndex)
  }

  const goToPrevMatch = () => {
    if (searchMatches.length === 0) return
    const prevIndex = currentMatchIndex === 0 ? searchMatches.length - 1 : currentMatchIndex - 1
    setCurrentMatchIndex(prevIndex)
    scrollToMatch(prevIndex)
  }

  // Highlight matching text in content (per paragraph)
  const highlightText = (content: string, sectionId: string) => {
    if (!searchQuery.trim()) return content

    const parts: (string | JSX.Element)[] = []
    const queryLower = searchQuery.toLowerCase()
    const contentLower = content.toLowerCase()
    let lastIndex = 0
    let matchIndex = 0

    // Find matches within this specific paragraph
    while (true) {
      const index = contentLower.indexOf(queryLower, lastIndex)
      if (index === -1) break

      // Add text before match
      if (index > lastIndex) {
        parts.push(content.substring(lastIndex, index))
      }

      // Find if this is the current global match
      const sectionMatches = searchMatches.filter(m => m.sectionId === sectionId)
      const globalMatchIndex = searchMatches.findIndex(
        m => m.sectionId === sectionId &&
        content.toLowerCase().indexOf(searchQuery.toLowerCase()) === index
      )

      // Determine if this is highlighted as current
      const isCurrentMatch = sectionMatches.some((m, idx) => {
        const matchInSection = searchMatches.indexOf(m)
        return matchInSection === currentMatchIndex &&
               content.substring(index, index + searchQuery.length).toLowerCase() === queryLower
      })

      // Add highlighted match
      parts.push(
        <mark
          key={`${sectionId}-${index}-${matchIndex}`}
          className={`${isCurrentMatch ? 'bg-orange-400' : 'bg-yellow-200'} px-0.5 rounded`}
        >
          {content.substring(index, index + searchQuery.length)}
        </mark>
      )

      lastIndex = index + searchQuery.length
      matchIndex++
    }

    // Add remaining text
    if (lastIndex < content.length) {
      parts.push(content.substring(lastIndex))
    }

    return parts.length > 0 ? parts : content
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pl-PL', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Get annotations for a specific section
  const getSectionAnnotations = (sectionId: string) => {
    return annotations.filter(a => a.section_id === sectionId)
  }

  // Toggle section selection for export
  const toggleSectionSelection = (sectionId: string) => {
    setSelectedSections(prev => {
      if (prev.includes(sectionId)) {
        return prev.filter(id => id !== sectionId)
      } else {
        return [...prev, sectionId]
      }
    })
  }

  // Select/deselect all sections
  const toggleAllSections = () => {
    if (selectedSections.length === report?.sections.length) {
      setSelectedSections([])
    } else {
      setSelectedSections(report?.sections.map(s => s.id) || [])
    }
  }

  // Toggle section collapse/expand
  const toggleSectionCollapse = (sectionId: string) => {
    setCollapsedSections(prev => {
      const newSet = new Set(prev)
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId)
      } else {
        newSet.add(sectionId)
      }
      return newSet
    })
  }

  // Export functionality
  const handleExport = async (format: 'xlsx' | 'pdf' | 'docx' | 'pptx') => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsExporting(true)
    setExportError('')
    setShowExportMenu(false)

    try {
      const csrfToken = await getCsrfToken()
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/export`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken || '',
          },
          body: JSON.stringify({
            format,
            section_ids: selectedSections.length > 0 ? selectedSections : undefined
          }),
        }
      )

      if (!response.ok) {
        throw new Error('Export failed')
      }

      // Check if response is a file download or JSON
      const contentType = response.headers.get('content-type')

      // Handle file downloads (all Office formats + PDF)
      const isFileDownload = contentType?.includes('application/vnd.openxmlformats-officedocument') ||
                           contentType?.includes('application/pdf')

      if (isFileDownload) {
        // Handle file download
        const blob = await response.blob()
        const contentDisposition = response.headers.get('content-disposition')
        let filename = `report_${reportId}.${format}`

        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="?([^";\n]+)"?/)
          if (filenameMatch) {
            filename = filenameMatch[1]
          }
        }

        // Create download link
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        // Handle JSON response (error or fallback)
        const data = await response.json()
        if (data.message) {
          setExportError(data.message)
        }
      }
    } catch (err) {
      console.error('Export failed:', err)
      setExportError('Nie udało się wyeksportować raportu')
    } finally {
      setIsExporting(false)
    }
  }

  // Print functionality
  const handlePrint = () => {
    window.print()
  }

  // Share via email functionality
  const handleShareEmail = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    // Validate email
    if (!shareEmail || !shareEmail.includes('@')) {
      setShareError('Proszę podać prawidłowy adres email')
      return
    }

    setIsSharing(true)
    setShareError('')
    setShareSuccess(false)

    try {
      // Get CSRF token
      const csrfToken = await getCsrfToken()
      if (!csrfToken) {
        setShareError('Failed to get security token')
        setIsSharing(false)
        return
      }

      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/share/email`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken,
          },
          body: JSON.stringify({
            recipient_email: shareEmail,
            message: shareMessage,
          }),
        }
      )

      if (!response.ok) {
        throw new Error('Failed to share report')
      }

      const data = await response.json()
      setShareSuccess(true)

      // Reset form after 2 seconds
      setTimeout(() => {
        setShowShareModal(false)
        setShareEmail('')
        setShareMessage('')
        setShareSuccess(false)
      }, 2000)
    } catch (err) {
      console.error('Share failed:', err)
      setShareError('Nie udało się udostępnić raportu')
    } finally {
      setIsSharing(false)
    }
  }

  // Generate share link functionality
  const handleGenerateShareLink = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setIsGeneratingLink(true)
    setShareError('')

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/share`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            password: passwordProtected ? sharePassword : null
          })
        }
      )

      if (!response.ok) {
        throw new Error('Failed to generate share link')
      }

      const data = await response.json()
      setShareLink(data.share_url)
    } catch (err) {
      console.error('Generate link failed:', err)
      setShareError('Nie udało się wygenerować linku')
    } finally {
      setIsGeneratingLink(false)
    }
  }

  // Copy share link to clipboard
  const handleCopyShareLink = async () => {
    try {
      await navigator.clipboard.writeText(shareLink)
      setLinkCopied(true)
      setTimeout(() => setLinkCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  // Generate embed code
  const handleGenerateEmbedCode = async () => {
    let linkToUse = shareLink

    // First generate share link if not already generated
    if (!linkToUse) {
      await handleGenerateShareLink()
      // Wait a bit for state to update, then use the shareLink from state
      // In practice, we need to refactor to return the link from handleGenerateShareLink
      // For now, we'll wait and check again
      await new Promise(resolve => setTimeout(resolve, 100))
    }

    // Use the shareLink state (should be populated by now)
    // If still not available, it will be empty and user needs to regenerate
    const iframe = `<iframe src="${shareLink}" width="100%" height="800" frameborder="0" allowfullscreen></iframe>`
    setEmbedCode(iframe)
  }

  // Copy embed code to clipboard
  const handleCopyEmbedCode = async () => {
    try {
      await navigator.clipboard.writeText(embedCode)
      setEmbedCopied(true)
      setTimeout(() => setEmbedCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy embed code:', err)
    }
  }

  // Fetch access log
  const handleViewAccessLog = async () => {
    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    setShowAccessLogModal(true)
    setIsLoadingAccessLog(true)

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/share/access-log`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error('Failed to fetch access log')
      }

      const data = await response.json()
      setAccessLogData(data)
    } catch (err) {
      console.error('Fetch access log failed:', err)
      setAccessLogData({ error: 'Nie udało się pobrać logu dostępu' })
    } finally {
      setIsLoadingAccessLog(false)
    }
  }

  // Revoke share link
  const handleRevokeShareLink = async (shareToken: string) => {
    if (!confirm('Czy na pewno chcesz cofnąć ten link udostępnienia? Link przestanie działać.')) {
      return
    }

    const token = getStoredToken()
    if (!token) {
      router.push('/auth/login')
      return
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/reports/${reportId}/share/${shareToken}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        // Refresh the access log to show updated list
        await handleViewAccessLog()
      } else {
        const errorData = await response.json()
        alert(`Nie udało się cofnąć linku: ${errorData.detail || 'Nieznany błąd'}`)
      }
    } catch (error) {
      console.error('Error revoking share link:', error)
      alert('Wystąpił błąd podczas cofania linku')
    }
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
          <p className="mt-3 text-gray-600">Ladowanie raportu...</p>
        </div>
      </div>
    )
  }

  if (error || !report) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="mb-4 text-6xl">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Nie udało się załadować raportu</h1>
          <p className="text-red-600 mb-4">{error || 'Raport nie został znaleziony'}</p>
          <p className="text-gray-600 mb-6">Sprawdź czy raport istnieje lub spróbuj ponownie później.</p>
          <Link href="/reports" className="inline-block rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700">
            Wróć do listy raportów
          </Link>
        </div>
      </div>
    )
  }

  // Additional safety check for report structure
  if (!report.sections || !Array.isArray(report.sections)) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="mb-4 text-6xl">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Błąd struktury raportu</h1>
          <p className="text-red-600 mb-4">Raport jest nieprawidłowy lub uszkodzony</p>
          <p className="text-gray-600 mb-6">Dane raportu nie zawierają wymaganych sekcji.</p>
          <Link href="/reports" className="inline-block rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700">
            Wróć do listy raportów
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-white px-4 py-3">
        <div className="mx-auto flex max-w-4xl items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/reports" className="text-gray-600 hover:text-gray-900">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </Link>
            <h1 className="text-lg font-semibold text-gray-900 truncate max-w-md">{report.title}</h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowCommentsPanel(!showCommentsPanel)}
              className="relative rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-50"
              title="Komentarze"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              {comments.length > 0 && (
                <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-xs text-white">
                  {comments.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setShowVersionHistory(!showVersionHistory)}
              className="rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-50"
              title="Historia wersji"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
            <button
              onClick={toggleFavorite}
              className="rounded-lg border border-gray-300 p-2 hover:bg-gray-50"
              title={report.is_favorite ? 'Usuń z ulubionych' : 'Dodaj do ulubionych'}
            >
              <svg
                className={`h-5 w-5 ${report.is_favorite ? 'fill-yellow-400 stroke-yellow-500' : 'fill-none stroke-gray-600'}`}
                viewBox="0 0 24 24"
                strokeWidth={1.5}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
              </svg>
            </button>
            <button
              onClick={report?.is_archived ? unarchiveReport : archiveReport}
              className="rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-50"
              title={report?.is_archived ? "Przywróć z archiwum" : "Archiwizuj raport"}
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
              </svg>
            </button>
            <button
              onClick={duplicateReport}
              className="rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-50"
              title="Duplikuj raport"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </button>
            <button
              onClick={saveAsTemplate}
              className="rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-50"
              title="Zapisz jako szablon"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </button>
            {/* Edit/Save buttons */}
            {!isEditing ? (
              <button
                onClick={toggleEditMode}
                className="rounded-lg border border-blue-500 bg-blue-500 p-2 text-white hover:bg-blue-600"
                title="Edit report"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
            ) : (
              <>
                <button
                  onClick={saveReportChanges}
                  disabled={isSaving}
                  className="rounded-lg border border-green-500 bg-green-500 px-3 py-2 text-white hover:bg-green-600 disabled:opacity-50"
                  title="Save changes"
                >
                  {isSaving ? 'Saving...' : 'Save'}
                </button>
                <button
                  onClick={toggleEditMode}
                  disabled={isSaving}
                  className="rounded-lg border border-gray-300 px-3 py-2 text-gray-600 hover:bg-gray-50 disabled:opacity-50"
                  title="Cancel editing"
                >
                  Cancel
                </button>
                {/* Auto-save indicator */}
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  {isAutoSaving ? (
                    <>
                      <div className="h-3 w-3 animate-spin rounded-full border-2 border-gray-400 border-t-transparent"></div>
                      <span>Zapisywanie...</span>
                    </>
                  ) : lastAutoSave ? (
                    <>
                      <svg className="h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span>Auto-zapisano {new Date(lastAutoSave).toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' })}</span>
                    </>
                  ) : null}
                </div>
              </>
            )}
            <button
              onClick={() => {
                setIsSearchOpen(!isSearchOpen)
                if (!isSearchOpen) {
                  setTimeout(() => searchInputRef.current?.focus(), 100)
                }
              }}
              className="no-print rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-50"
              title="Szukaj w raporcie (Ctrl+F)"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
            {/* Share button */}
            <button
              onClick={() => setShowShareModal(true)}
              className="no-print flex items-center gap-2 rounded-lg border border-blue-600 px-4 py-2 text-sm text-blue-600 hover:bg-blue-50"
              title="Udostępnij raport przez email"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
              Udostępnij
            </button>

            {/* View Access Log button */}
            <button
              onClick={handleViewAccessLog}
              className="no-print flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
              title="Zobacz kto otworzył udostępniony raport"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Log dostępu
            </button>

            {/* Print button */}
            <button
              onClick={handlePrint}
              className="no-print flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
              title="Drukuj raport (Ctrl+P)"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              Drukuj
            </button>

            <div className="relative no-print">
              <button
                onClick={() => setShowExportMenu(!showExportMenu)}
                disabled={isExporting}
                className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {isExporting ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                    Eksportowanie...
                  </>
                ) : (
                  <>
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Eksportuj
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </>
                )}
              </button>

              {/* Export dropdown menu */}
              {showExportMenu && (
                <div className="absolute right-0 mt-2 w-80 rounded-lg bg-white shadow-lg ring-1 ring-black ring-opacity-5 z-50">
                  {/* Section selection */}
                  <div className="border-b px-4 py-3">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-medium text-gray-900">Wybierz sekcje</h4>
                      <button
                        onClick={toggleAllSections}
                        className="text-xs text-blue-600 hover:text-blue-800"
                      >
                        {selectedSections.length === report?.sections.length ? 'Odznacz wszystkie' : 'Zaznacz wszystkie'}
                      </button>
                    </div>
                    <div className="max-h-48 overflow-y-auto space-y-1">
                      {report?.sections.map((section, index) => (
                        <label
                          key={section.id}
                          className="flex items-center gap-2 py-1 px-2 rounded hover:bg-gray-50 cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={selectedSections.includes(section.id)}
                            onChange={() => toggleSectionSelection(section.id)}
                            className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                          />
                          <span className="text-sm text-gray-700">
                            {index + 1}. {section.title}
                          </span>
                        </label>
                      ))}
                    </div>
                    {selectedSections.length === 0 && (
                      <p className="text-xs text-red-600 mt-2">Wybierz przynajmniej jedną sekcję</p>
                    )}
                  </div>

                  {/* Export format buttons */}
                  <div className="py-1">
                    <div className="px-4 py-2">
                      <h4 className="text-xs font-medium text-gray-500 uppercase">Format eksportu</h4>
                    </div>
                    <button
                      onClick={() => handleExport('xlsx')}
                      disabled={selectedSections.length === 0}
                      className={`flex w-full items-center gap-3 px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed ${preferredFormat === 'xlsx' ? 'ring-2 ring-blue-500 bg-blue-50' : ''}`}
                    >
                      <div className="flex h-8 w-8 items-center justify-center rounded bg-green-100">
                        <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">Excel (.xlsx)</span>
                          {preferredFormat === 'xlsx' && (
                            <span className="text-xs px-2 py-0.5 bg-blue-600 text-white rounded-full">Domyślny</span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500">Z formułami finansowymi</div>
                      </div>
                    </button>
                    <button
                      onClick={() => handleExport('pdf')}
                      disabled={selectedSections.length === 0}
                      className={`flex w-full items-center gap-3 px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed ${preferredFormat === 'pdf' ? 'ring-2 ring-blue-500 bg-blue-50' : ''}`}
                    >
                      <div className="flex h-8 w-8 items-center justify-center rounded bg-red-100">
                        <svg className="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">PDF</span>
                          {preferredFormat === 'pdf' && (
                            <span className="text-xs px-2 py-0.5 bg-blue-600 text-white rounded-full">Domyślny</span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500">Do wydruku i udostępnienia</div>
                      </div>
                    </button>
                    <button
                      onClick={() => handleExport('docx')}
                      disabled={selectedSections.length === 0}
                      className={`flex w-full items-center gap-3 px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed ${preferredFormat === 'docx' ? 'ring-2 ring-blue-500 bg-blue-50' : ''}`}
                    >
                      <div className="flex h-8 w-8 items-center justify-center rounded bg-blue-100">
                        <svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">Word (.docx)</span>
                          {preferredFormat === 'docx' && (
                            <span className="text-xs px-2 py-0.5 bg-blue-600 text-white rounded-full">Domyślny</span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500">Do edycji dokumentu</div>
                      </div>
                    </button>
                    <button
                      onClick={() => handleExport('pptx')}
                      disabled={selectedSections.length === 0}
                      className={`flex w-full items-center gap-3 px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed ${preferredFormat === 'pptx' ? 'ring-2 ring-blue-500 bg-blue-50' : ''}`}
                    >
                      <div className="flex h-8 w-8 items-center justify-center rounded bg-orange-100">
                        <svg className="h-5 w-5 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                        </svg>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">PowerPoint (.pptx)</span>
                          {preferredFormat === 'pptx' && (
                            <span className="text-xs px-2 py-0.5 bg-blue-600 text-white rounded-full">Domyślny</span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500">Do prezentacji slajdów</div>
                      </div>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Comments Panel */}
      {showCommentsPanel && (
        <div className="fixed inset-0 z-50 flex items-start justify-end bg-black/30">
          <div className="h-full w-full max-w-md bg-white shadow-xl overflow-y-auto flex flex-col">
            <div className="sticky top-0 bg-white border-b px-4 py-3">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-lg font-semibold text-gray-900">Komentarze ({comments.length})</h2>
                <button
                  onClick={() => setShowCommentsPanel(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              {/* Filter toggle for resolved comments */}
              <div className="flex items-center gap-2 text-sm">
                <button
                  onClick={() => setShowResolvedComments(!showResolvedComments)}
                  className={`flex items-center gap-1.5 rounded-full px-3 py-1 transition-colors ${
                    showResolvedComments
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {showResolvedComments ? 'Pokaż rozwiązane' : 'Ukryj rozwiązane'}
                </button>
                <span className="text-gray-500">
                  ({comments.filter(c => c.resolved && !c.parent_id).length} rozwiązanych)
                </span>
              </div>
            </div>
            <div className="flex-1 p-4 space-y-4 overflow-y-auto">
              {comments.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Brak komentarzy. Bądź pierwszą osobą, która doda komentarz!</p>
              ) : (
                // Show only top-level comments (no parent_id), filtered by resolved status
                comments
                  .filter(c => !c.parent_id)
                  .filter(c => showResolvedComments || !c.resolved)
                  .map((comment) => {
                  // Get replies for this comment
                  const replies = comments.filter(c => c.parent_id === comment.id)
                  return (
                    <div key={comment.id} className="space-y-2">
                      <div className={`rounded-lg border p-4 transition-colors ${
                        comment.resolved
                          ? 'border-green-200 bg-green-50'
                          : 'border-gray-200 bg-white'
                      }`}>
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                              comment.resolved ? 'bg-green-200' : 'bg-blue-100'
                            }`}>
                              {comment.resolved ? (
                                <svg className="h-5 w-5 text-green-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                </svg>
                              ) : (
                                <span className="text-blue-700 font-medium text-sm">
                                  {comment.user_name.charAt(0).toUpperCase()}
                                </span>
                              )}
                            </div>
                            <div>
                              <div className={`font-medium text-sm ${comment.resolved ? 'text-green-800' : 'text-gray-900'}`}>
                                {comment.user_name}
                                {comment.resolved && (
                                  <span className="ml-2 text-xs bg-green-200 text-green-800 px-2 py-0.5 rounded-full">
                                    Rozwiązany
                                  </span>
                                )}
                              </div>
                              <div className="text-xs text-gray-500">
                                {new Date(comment.created_at).toLocaleDateString('pl-PL', {
                                  day: 'numeric',
                                  month: 'short',
                                  year: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                                {comment.resolved && comment.resolved_by_name && (
                                  <span className="ml-2 text-green-600">
                                    • Rozwiązał: {comment.resolved_by_name}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {/* Resolve/Unresolve button */}
                            <button
                              onClick={() => resolveComment(comment.id)}
                              disabled={isResolvingComment === comment.id}
                              className={`transition-colors ${
                                comment.resolved
                                  ? 'text-green-600 hover:text-amber-600'
                                  : 'text-gray-400 hover:text-green-500'
                              }`}
                              title={comment.resolved ? 'Oznacz jako nierozwiązany' : 'Rozwiąż'}
                            >
                              {isResolvingComment === comment.id ? (
                                <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
                              ) : (
                                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                </svg>
                              )}
                            </button>
                            <button
                              onClick={() => setReplyingTo(replyingTo === comment.id ? null : comment.id)}
                              className="text-gray-400 hover:text-blue-500"
                              title="Odpowiedz"
                            >
                              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                              </svg>
                            </button>
                            <button
                              onClick={() => deleteComment(comment.id)}
                              className="text-gray-400 hover:text-red-500"
                              title="Usuń komentarz"
                            >
                              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                          </div>
                        </div>
                        <p className={`text-sm ${comment.resolved ? 'text-green-700' : 'text-gray-700'}`}>{comment.text}</p>

                        {/* Reply input for this comment */}
                        {replyingTo === comment.id && (
                          <div className="mt-3 pt-3 border-t border-gray-100">
                            <div className="flex gap-2">
                              <textarea
                                value={newCommentText}
                                onChange={(e) => setNewCommentText(e.target.value)}
                                placeholder={`Odpowiedz na komentarz ${comment.user_name}...`}
                                className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
                                rows={2}
                                autoFocus
                                onKeyDown={(e) => {
                                  if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault()
                                    submitComment(comment.id)
                                  }
                                  if (e.key === 'Escape') {
                                    setReplyingTo(null)
                                    setNewCommentText('')
                                  }
                                }}
                              />
                              <button
                                onClick={() => submitComment(comment.id)}
                                disabled={!newCommentText.trim() || isSubmittingComment}
                                className="rounded-lg bg-blue-600 px-3 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50 self-end"
                              >
                                {isSubmittingComment ? (
                                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                                ) : (
                                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                  </svg>
                                )}
                              </button>
                            </div>
                            <p className="text-xs text-gray-500 mt-1">Esc aby anulować</p>
                          </div>
                        )}
                      </div>

                      {/* Nested replies */}
                      {replies.length > 0 && (
                        <div className="ml-6 space-y-2">
                          {replies.map((reply) => (
                            <div key={reply.id} className="rounded-lg border border-gray-200 p-3 bg-gray-50">
                              <div className="flex items-start justify-between mb-2">
                                <div className="flex items-center gap-2">
                                  <div className="h-6 w-6 rounded-full bg-green-100 flex items-center justify-center">
                                    <span className="text-green-700 font-medium text-xs">
                                      {reply.user_name.charAt(0).toUpperCase()}
                                    </span>
                                  </div>
                                  <div>
                                    <div className="font-medium text-gray-900 text-xs">{reply.user_name}</div>
                                    <div className="text-xs text-gray-500">
                                      {new Date(reply.created_at).toLocaleDateString('pl-PL', {
                                        day: 'numeric',
                                        month: 'short',
                                        hour: '2-digit',
                                        minute: '2-digit'
                                      })}
                                    </div>
                                  </div>
                                </div>
                                <button
                                  onClick={() => deleteComment(reply.id)}
                                  className="text-gray-400 hover:text-red-500"
                                  title="Usuń odpowiedź"
                                >
                                  <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                  </svg>
                                </button>
                              </div>
                              <p className="text-gray-700 text-xs">{reply.text}</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )
                })
              )}
            </div>
            <div className="sticky bottom-0 bg-white border-t p-4">
              <div className="flex gap-2">
                <textarea
                  value={replyingTo ? '' : newCommentText}
                  onChange={(e) => !replyingTo && setNewCommentText(e.target.value)}
                  placeholder={replyingTo ? 'Wpisz odpowiedź powyżej...' : 'Dodaj komentarz...'}
                  className={`flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none ${replyingTo ? 'bg-gray-100 cursor-not-allowed' : ''}`}
                  rows={2}
                  disabled={!!replyingTo}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey && !replyingTo) {
                      e.preventDefault()
                      submitComment(null)
                    }
                  }}
                />
                <button
                  onClick={() => submitComment(null)}
                  disabled={!newCommentText.trim() || isSubmittingComment || !!replyingTo}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50 self-end"
                >
                  {isSubmittingComment ? (
                    <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                  ) : (
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  )}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Naciśnij Enter, aby wysłać. Shift+Enter dla nowej linii.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Version History Panel */}
      {showVersionHistory && (
        <div className="fixed inset-0 z-50 flex items-start justify-end bg-black/30">
          <div className="h-full w-full max-w-md bg-white shadow-xl overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-4 py-3 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Historia wersji</h2>
              <button
                onClick={() => setShowVersionHistory(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-4 space-y-3">
              {versions.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Brak historii wersji</p>
              ) : (
                versions.map((version) => (
                  <div
                    key={version.version}
                    className={`rounded-lg border p-4 cursor-pointer transition-colors ${
                      currentVersion === version.version
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                    }`}
                    onClick={() => loadVersion(version.version)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">
                        Wersja {version.version}
                        {version.is_current && (
                          <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full">
                            Aktualna
                          </span>
                        )}
                      </span>
                      <div className="flex items-center gap-2">
                        {!version.is_current && (
                          <button
                            onClick={(e) => handleRestoreClick(version.version, e)}
                            className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded hover:bg-amber-200 transition-colors"
                            title="Przywróć tę wersję"
                          >
                            Przywróć
                          </button>
                        )}
                        {isLoadingVersion && currentVersion === version.version && (
                          <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"></div>
                        )}
                      </div>
                    </div>
                    <div className="text-sm text-gray-600 mb-1">{version.changes}</div>
                    <div className="text-xs text-gray-500">
                      {version.author} &bull; {new Date(version.created_at).toLocaleDateString('pl-PL', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Restore Confirmation Modal */}
      {showRestoreConfirm && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Przywróć wersję</h3>
            <p className="text-gray-600 mb-4">
              Czy na pewno chcesz przywrócić raport do wersji {versionToRestore}?
            </p>
            <p className="text-sm text-gray-500 mb-6">
              Zostanie utworzona nowa wersja z zawartością wybranej wersji historycznej.
              Obecna wersja nie zostanie utracona.
            </p>
            {restoreMessage && (
              <div className={`mb-4 p-3 rounded-lg text-sm ${
                restoreMessage.includes('Błąd') || restoreMessage.includes('Nie udało')
                  ? 'bg-red-50 text-red-700'
                  : 'bg-green-50 text-green-700'
              }`}>
                {restoreMessage}
              </div>
            )}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowRestoreConfirm(false)
                  setVersionToRestore(null)
                  setRestoreMessage('')
                }}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                disabled={isRestoring}
              >
                Anuluj
              </button>
              <button
                onClick={restoreVersion}
                disabled={isRestoring}
                className="rounded-lg bg-amber-600 px-4 py-2 text-sm text-white hover:bg-amber-700 disabled:opacity-50"
              >
                {isRestoring ? 'Przywracanie...' : 'Przywróć'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Search Bar */}
      {isSearchOpen && (
        <div className="sticky top-[57px] z-40 border-b bg-white px-4 py-3 shadow-sm">
          <div className="mx-auto flex max-w-4xl items-center gap-3">
            <div className="relative flex-1">
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={handleSearchChange}
                placeholder="Szukaj w raporcie..."
                className="w-full rounded-lg border border-gray-300 px-4 py-2 pr-20 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                autoFocus
              />
              {searchMatches.length > 0 && (
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-gray-500">
                  {currentMatchIndex + 1} / {searchMatches.length}
                </span>
              )}
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={goToPrevMatch}
                disabled={searchMatches.length === 0}
                className="rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-50 disabled:opacity-50"
                title="Poprzedni wynik"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                </svg>
              </button>
              <button
                onClick={goToNextMatch}
                disabled={searchMatches.length === 0}
                className="rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-50 disabled:opacity-50"
                title="Nastepny wynik"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            <button
              onClick={() => {
                setIsSearchOpen(false)
                setSearchQuery('')
                setSearchMatches([])
              }}
              className="rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-50"
              title="Zamknij (Esc)"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Annotation Tooltip - shows when text is selected */}
      {selectedText && selectionInfo && selectionInfo.rect && !showAnnotationModal && (
        <div
          className="fixed z-50 bg-gray-900 text-white rounded-lg shadow-lg px-3 py-2 text-sm"
          style={{
            top: selectionInfo.rect.bottom + window.scrollY + 8,
            left: selectionInfo.rect.left + selectionInfo.rect.width / 2,
            transform: 'translateX(-50%)'
          }}
        >
          <button
            onClick={() => setShowAnnotationModal(true)}
            className="flex items-center gap-2 hover:text-blue-300"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
            Dodaj adnotacje
          </button>
        </div>
      )}

      {/* Annotation Modal */}
      {showAnnotationModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Dodaj adnotacje</h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Zaznaczony tekst:
              </label>
              <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-3 text-sm text-gray-700">
                &quot;{selectedText.substring(0, 100)}{selectedText.length > 100 ? '...' : ''}&quot;
              </div>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Komentarz:
              </label>
              <textarea
                value={annotationComment}
                onChange={(e) => setAnnotationComment(e.target.value)}
                placeholder="Wpisz swoj komentarz..."
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                rows={3}
                autoFocus
              />
            </div>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowAnnotationModal(false)
                  setAnnotationComment('')
                }}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
              >
                Anuluj
              </button>
              <button
                onClick={saveAnnotation}
                disabled={!annotationComment.trim() || isSavingAnnotation}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {isSavingAnnotation ? 'Zapisywanie...' : 'Zapisz'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Table Size Modal */}
      {showTableModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Wstaw tabelę</h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Liczba wierszy:
              </label>
              <input
                type="number"
                min="2"
                max="20"
                value={tableRows}
                onChange={(e) => setTableRows(parseInt(e.target.value) || 3)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                autoFocus
              />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Liczba kolumn:
              </label>
              <input
                type="number"
                min="2"
                max="10"
                value={tableCols}
                onChange={(e) => setTableCols(parseInt(e.target.value) || 3)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowTableModal(false)
                  setCurrentSectionForTable(null)
                }}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
              >
                Anuluj
              </button>
              <button
                onClick={() => {
                  if (currentSectionForTable && report) {
                    // Find textarea by section ID in DOM
                    const sectionElement = document.getElementById(`section-${currentSectionForTable}`)
                    const textarea = sectionElement?.querySelector('textarea') as HTMLTextAreaElement
                    if (textarea) {
                      const currentContent = editedSections[currentSectionForTable] || report.sections.find(s => s.id === currentSectionForTable)?.content || ''
                      const newContent = insertTable(currentContent, textarea, tableRows, tableCols)
                      setEditedSections({ ...editedSections, [currentSectionForTable]: newContent })
                    }
                  }
                  setShowTableModal(false)
                  setCurrentSectionForTable(null)
                }}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
              >
                Wstaw
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Section Confirmation Modal */}
      {showDeleteConfirmModal && sectionToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Usuń sekcję?</h3>
                <p className="text-sm text-gray-500 mt-1">Ta operacja jest nieodwracalna</p>
              </div>
            </div>
            <p className="text-gray-700 mb-6">
              Czy na pewno chcesz usunąć sekcję <strong>&quot;{sectionToDelete.title}&quot;</strong>?
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowDeleteConfirmModal(false)
                  setSectionToDelete(null)
                }}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
              >
                Anuluj
              </button>
              <button
                onClick={confirmDeleteSection}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700"
              >
                Usuń sekcję
              </button>
            </div>
          </div>
        </div>
      )}

      <main className="mx-auto max-w-4xl px-4 py-8">
        {/* Report Header */}
        <div className="mb-8 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 p-8 text-white">
          <div className="mb-4 flex items-center gap-3">
            <span className="rounded-full bg-white/20 px-3 py-1 text-sm">
              {report.type === 'company_profile' ? 'Profil firmy' :
               report.type === 'market_analysis' ? 'Analiza rynku' :
               report.type === 'due_diligence' ? 'Due Diligence' : report.type}
            </span>
            {report.company && (
              <span className="text-blue-100">&#x2022; {report.company}</span>
            )}
          </div>
          {isEditing ? (
            <input
              type="text"
              value={editedTitle}
              onChange={(e) => setEditedTitle(e.target.value)}
              className="text-2xl font-bold bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg px-4 py-2 text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/50 w-full"
              placeholder="Tytuł raportu..."
            />
          ) : (
            <h1 className="text-2xl font-bold">{report.title}</h1>
          )}
          <p className="mt-3 text-blue-100">{report.summary}</p>
          <div className="mt-4 flex gap-4 text-sm text-blue-200">
            <span>Utworzono: {formatDate(report.created_at)}</span>
            <span>Aktualizacja: {formatDate(report.updated_at)}</span>
          </div>
        </div>

        {/* Table of Contents */}
        <div className="mb-8 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-4 font-semibold text-gray-900">Spis tresci</h2>
          <nav className="space-y-2">
            {report.sections.map((section, index) => (
              <a
                key={section.id}
                href={`#section-${section.id}`}
                className="block text-gray-600 hover:text-blue-600"
              >
                {index + 1}. {section.title}
              </a>
            ))}
          </nav>
        </div>

        {/* Annotations Summary */}
        {annotations.length > 0 && (
          <div className="mb-8 rounded-xl bg-yellow-50 border border-yellow-200 p-6">
            <h2 className="mb-4 font-semibold text-gray-900 flex items-center gap-2">
              <svg className="h-5 w-5 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
              Adnotacje ({annotations.length})
            </h2>
            <div className="space-y-3">
              {annotations.map((annotation) => (
                <div key={annotation.id} className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="text-sm text-gray-500 mb-1">
                        Zaznaczony tekst:
                      </div>
                      <div className="text-sm text-gray-700 italic mb-2">
                        &quot;{annotation.selected_text.substring(0, 80)}{annotation.selected_text.length > 80 ? '...' : ''}&quot;
                      </div>
                      <div className="text-gray-800">{annotation.comment}</div>
                    </div>
                    <button
                      onClick={() => deleteAnnotation(annotation.id)}
                      className="ml-2 text-gray-400 hover:text-red-500"
                      title="Usun adnotacje"
                    >
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Report Sections */}
        {isEditing ? (
          <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
            <SortableContext items={sortedSections.map(s => s.id)} strategy={verticalListSortingStrategy}>
              <div className="space-y-8 pl-10">
                {sortedSections.map((section, index) => {
                  // Parse section data for special visualizations
                  const swotData = isSWOTSection(section.title) ? parseSWOTContent(section.content) : null
                  const porterData = isPorterSection(section.title) ? parsePorterContent(section.content) : null
                  const tamSamSomData = isTAMSAMSOMSection(section.title) ? parseTAMSAMSOMContent(section.content) : null
                  const trendTimelineData = isTrendTimelineSection(section.title) ? parseTrendTimelineContent(section.content) : null
                  const ownershipData = isOwnershipSection(section.title) ? parseOwnershipContent(section.content) : null
                  const positioningMapData = isPositioningMapSection(section.title) ? parsePositioningMapContent(section.content) : null
                  const financialRatiosData = isFinancialRatiosSection(section.title) ? parseFinancialRatiosContent(section.content) : null

                  return (
                    <SortableSectionWrapper key={section.id} section={section}>
                      <section
                        id={`section-${section.id}`}
                        className="rounded-xl bg-white p-6 shadow-sm"
                      >
                        <div className="mb-4 flex items-center gap-2">
                          <span className="text-xl font-semibold text-gray-600">{index + 1}.</span>
                          <input
                            type="text"
                            value={editedSectionTitles[section.id] || section.title}
                            onChange={(e) => setEditedSectionTitles({ ...editedSectionTitles, [section.id]: e.target.value })}
                            className="flex-1 text-xl font-semibold text-gray-900 border-b-2 border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-2 py-1 rounded transition-colors"
                          />
                          {(swotData || porterData || tamSamSomData || trendTimelineData || ownershipData || positioningMapData || financialRatiosData) && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                              📊 Diagram interaktywny
                            </span>
                          )}
                          {/* Delete Section Button */}
                          <button
                            onClick={() => handleDeleteSectionClick(section.id, editedSectionTitles[section.id] || section.title)}
                            className="ml-auto text-gray-400 hover:text-red-600 transition-colors p-2 rounded-lg hover:bg-red-50"
                            title="Usuń sekcję"
                          >
                            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>

                {/* SWOT Diagram Visualization */}
                {swotData ? (
                  <SWOTDiagram data={swotData} />
                ) : porterData ? (
                  /* Porter Five Forces Visualization */
                  <PorterDiagram data={porterData} />
                ) : tamSamSomData ? (
                  /* TAM SAM SOM Visualization */
                  <TAMSAMSOMDiagram data={tamSamSomData} />
                ) : trendTimelineData ? (
                  /* Trend Timeline Visualization */
                  <TrendTimelineDiagram data={trendTimelineData} />
                ) : ownershipData ? (
                  /* Ownership Tree Visualization */
                  <OwnershipTreeDiagram data={ownershipData} />
                ) : positioningMapData ? (
                  /* Competitor Positioning Map Visualization */
                  <CompetitorPositioningMap data={positioningMapData} />
                ) : financialRatiosData ? (
                  /* Financial Ratio Radar Chart Visualization */
                  <FinancialRatioRadarChart data={financialRatiosData} />
                ) : isEditing ? (
                  /* Edit mode - show textarea with formatting toolbar */
                  <div>
                    {/* Formatting toolbar */}
                    <div className="mb-2 flex gap-2 rounded-t-lg border border-gray-300 bg-gray-50 p-2">
                      <button
                        onClick={(e) => {
                          const textarea = (e.target as HTMLButtonElement).closest('div')?.parentElement?.querySelector('textarea')
                          if (textarea && editedSections[section.id] !== undefined) {
                            const newContent = applyMarkdownFormatting(editedSections[section.id], textarea as HTMLTextAreaElement, 'bold')
                            setEditedSections({ ...editedSections, [section.id]: newContent })
                          }
                        }}
                        className="rounded border border-gray-300 bg-white px-3 py-1 text-sm font-bold hover:bg-gray-100"
                        title="Bold (Ctrl+B)"
                      >
                        <strong>B</strong>
                      </button>
                      <button
                        onClick={(e) => {
                          const textarea = (e.target as HTMLButtonElement).closest('div')?.parentElement?.querySelector('textarea')
                          if (textarea && editedSections[section.id] !== undefined) {
                            const newContent = applyMarkdownFormatting(editedSections[section.id], textarea as HTMLTextAreaElement, 'italic')
                            setEditedSections({ ...editedSections, [section.id]: newContent })
                          }
                        }}
                        className="rounded border border-gray-300 bg-white px-3 py-1 text-sm italic hover:bg-gray-100"
                        title="Italic (Ctrl+I)"
                      >
                        <em>I</em>
                      </button>
                      <button
                        onClick={(e) => {
                          const textarea = (e.target as HTMLButtonElement).closest('div')?.parentElement?.querySelector('textarea')
                          if (textarea && editedSections[section.id] !== undefined) {
                            const newContent = insertBulletedList(editedSections[section.id], textarea as HTMLTextAreaElement)
                            setEditedSections({ ...editedSections, [section.id]: newContent })
                          }
                        }}
                        className="rounded border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100"
                        title="Bulleted list"
                      >
                        • List
                      </button>
                      <button
                        onClick={(e) => {
                          const textarea = (e.target as HTMLButtonElement).closest('div')?.parentElement?.querySelector('textarea')
                          if (textarea && editedSections[section.id] !== undefined) {
                            const newContent = applyMarkdownFormatting(editedSections[section.id], textarea as HTMLTextAreaElement, 'link')
                            setEditedSections({ ...editedSections, [section.id]: newContent })
                          }
                        }}
                        className="rounded border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100"
                        title="Insert link"
                      >
                        🔗 Link
                      </button>
                      <button
                        onClick={() => {
                          // Trigger file input click
                          const fileInput = document.getElementById(`image-upload-${section.id}`) as HTMLInputElement
                          if (fileInput) {
                            fileInput.click()
                          }
                        }}
                        className="rounded border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100"
                        title="Insert image"
                      >
                        🖼️ Image
                      </button>
                      <input
                        id={`image-upload-${section.id}`}
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={async (e) => {
                          const file = e.target.files?.[0]
                          if (!file) return

                          const token = getStoredToken()
                          if (!token) return

                          // Upload image
                          const formData = new FormData()
                          formData.append('file', file)

                          try {
                            const response = await fetch(
                              `${API_BASE_URL}/reports/upload-image`,
                              {
                                method: 'POST',
                                headers: {
                                  'Authorization': `Bearer ${token}`,
                                },
                                body: formData
                              }
                            )

                            if (response.ok) {
                              const data = await response.json()
                              const imageUrl = `http://localhost:8000${data.url}`
                              const altText = file.name.replace(/\.[^/.]+$/, '')

                              // Insert markdown image syntax
                              const textarea = document.querySelector(`textarea[data-section-id="${section.id}"]`) as HTMLTextAreaElement
                              if (textarea) {
                                const start = textarea.selectionStart || 0
                                const currentContent = editedSections[section.id] || section.content
                                const imageMarkdown = `\n![${altText}](${imageUrl})\n`
                                const newContent = currentContent.substring(0, start) + imageMarkdown + currentContent.substring(start)
                                setEditedSections({ ...editedSections, [section.id]: newContent })
                              }
                            } else {
                              alert('Failed to upload image')
                            }
                          } catch (err) {
                            console.error('Image upload error:', err)
                            alert('Failed to upload image')
                          }

                          // Reset input
                          e.target.value = ''
                        }}
                      />
                      <button
                        onClick={() => {
                          // Open table size modal
                          setCurrentSectionForTable(section.id)
                          setShowTableModal(true)
                        }}
                        className="rounded border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100"
                        title="Insert table"
                      >
                        📊 Table
                      </button>
                    </div>
                    <textarea
                      data-section-id={section.id}
                      value={editedSections[section.id] || section.content}
                      onChange={(e) => {
                        setEditedSections({ ...editedSections, [section.id]: e.target.value })
                      }}
                      className="w-full rounded-b-lg border border-gray-300 p-4 font-mono text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows={20}
                    />
                    {/* Preview */}
                    <div className="mt-4 rounded-lg border border-gray-200 bg-gray-50 p-4">
                      <div className="mb-2 text-xs font-semibold uppercase text-gray-500">Preview:</div>
                      <div className="prose prose-gray max-w-none">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          className="text-gray-700"
                          components={{
                            a: ({ node, ...props }) => (
                              <a {...props} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 underline" />
                            ),
                            p: ({ node, children, ...props }) => (
                              <p {...props} className="mb-4">{children}</p>
                            ),
                            ul: ({ node, ...props }) => (
                              <ul {...props} className="list-disc list-inside mb-4 space-y-1" />
                            ),
                            ol: ({ node, ...props }) => (
                              <ol {...props} className="list-decimal list-inside mb-4 space-y-1" />
                            ),
                            strong: ({ node, ...props }) => (
                              <strong {...props} className="font-bold" />
                            ),
                            em: ({ node, ...props }) => (
                              <em {...props} className="italic" />
                            ),
                          }}
                        >
                          {editedSections[section.id] || section.content}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </div>
                ) : (
                  /* View mode - show ReactMarkdown */
                  <div className="prose prose-gray max-w-none">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      className="text-gray-700"
                      components={{
                        // Custom link component to open in new tab
                        a: ({ node, ...props }) => (
                          <a {...props} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 underline" />
                        ),
                        // Custom paragraph to apply highlighting
                        p: ({ node, children, ...props }) => (
                          <p {...props} className="mb-4">
                            {children}
                          </p>
                        ),
                        // Style lists
                        ul: ({ node, ...props }) => (
                          <ul {...props} className="list-disc list-inside mb-4 space-y-1" />
                        ),
                        ol: ({ node, ...props }) => (
                          <ol {...props} className="list-decimal list-inside mb-4 space-y-1" />
                        ),
                        // Style code blocks
                        code: ({ node, inline, ...props }: any) =>
                          inline ? (
                            <code {...props} className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono" />
                          ) : (
                            <code {...props} className="block bg-gray-100 p-3 rounded text-sm font-mono overflow-x-auto" />
                          ),
                        // Style blockquotes
                        blockquote: ({ node, ...props }) => (
                          <blockquote {...props} className="border-l-4 border-gray-300 pl-4 italic my-4" />
                        ),
                        // Style headings
                        h1: ({ node, ...props }) => <h1 {...props} className="text-2xl font-bold mt-6 mb-4" />,
                        h2: ({ node, ...props }) => <h2 {...props} className="text-xl font-bold mt-5 mb-3" />,
                        h3: ({ node, ...props }) => <h3 {...props} className="text-lg font-bold mt-4 mb-2" />,
                      }}
                    >
                      {section.content}
                    </ReactMarkdown>
                  </div>
                )}

                {/* Section Annotations */}
                {getSectionAnnotations(section.id).length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="text-sm font-medium text-yellow-700 mb-2">
                      Adnotacje w tej sekcji:
                    </div>
                    {getSectionAnnotations(section.id).map((annotation) => (
                      <div key={annotation.id} className="bg-yellow-50 rounded-lg p-3 mb-2 text-sm">
                        <div className="text-gray-500 italic mb-1">
                          &quot;{annotation.selected_text.substring(0, 50)}...&quot;
                        </div>
                        <div className="text-gray-700">{annotation.comment}</div>
                      </div>
                    ))}
                  </div>
                        )}
                      </section>
                    </SortableSectionWrapper>
                  )
                })}

                {/* Add Section Button */}
                <div className="mt-6 flex justify-center">
                  <button
                    onClick={addNewSection}
                    className="flex items-center gap-2 rounded-lg border-2 border-dashed border-gray-300 bg-white px-6 py-3 text-sm font-medium text-gray-700 transition-colors hover:border-blue-500 hover:bg-blue-50 hover:text-blue-700"
                  >
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Dodaj sekcję
                  </button>
                </div>
              </div>
            </SortableContext>
          </DndContext>
        ) : (
          <div className="space-y-8">
            {report.sections.map((section, index) => {
              // Check if this is a SWOT section
              const swotData = isSWOTSection(section.title) ? parseSWOTContent(section.content) : null
              // Check if this is a Porter Five Forces section
              const porterData = isPorterSection(section.title) ? parsePorterContent(section.content) : null
              // Check if this is a TAM SAM SOM section
              const tamSamSomData = isTAMSAMSOMSection(section.title) ? parseTAMSAMSOMContent(section.content) : null
              // Check if this is a Trend Timeline section
              const trendTimelineData = isTrendTimelineSection(section.title) ? parseTrendTimelineContent(section.content) : null
              // Check if this is an Ownership section
              const ownershipData = isOwnershipSection(section.title) ? parseOwnershipContent(section.content) : null
              // Check if this is a Competitor Positioning Map section
              const positioningMapData = isPositioningMapSection(section.title) ? parsePositioningMapContent(section.content) : null
              // Check if this is a Financial Ratios Radar section
              const financialRatiosData = isFinancialRatiosSection(section.title) ? parseFinancialRatiosContent(section.content) : null

              return (
                <section
                  key={section.id}
                  id={`section-${section.id}`}
                  className="rounded-xl bg-white p-6 shadow-sm"
                >
                  {/* View mode section content */}
                  <button
                    onClick={() => toggleSectionCollapse(section.id)}
                    className="w-full flex items-center justify-between mb-4 text-left hover:bg-gray-50 rounded-lg p-2 -ml-2 transition-colors"
                  >
                    <h2 className="text-xl font-semibold text-gray-900">
                      {index + 1}. {section.title}
                    </h2>
                    <svg
                      className={`h-5 w-5 text-gray-500 transition-transform flex-shrink-0 ml-2 ${collapsedSections.has(section.id) ? '' : 'rotate-180'}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {/* Conditional rendering based on section type - only if not collapsed */}
                  {!collapsedSections.has(section.id) && (
                    <>
                      {swotData ? (
                        <SWOTDiagram data={swotData} />
                      ) : porterData ? (
                        <PorterDiagram data={porterData} />
                      ) : tamSamSomData ? (
                        <TAMSAMSOMDiagram data={tamSamSomData} />
                      ) : trendTimelineData ? (
                        <TrendTimelineDiagram data={trendTimelineData} />
                      ) : ownershipData ? (
                        <OwnershipTreeDiagram data={ownershipData} />
                      ) : positioningMapData ? (
                        <CompetitorPositioningMap data={positioningMapData} />
                      ) : financialRatiosData ? (
                        <FinancialRatioRadarChart data={financialRatiosData} />
                      ) : (
                        <div className="prose max-w-none">
                          <ReactMarkdown>{section.content}</ReactMarkdown>
                        </div>
                      )}
                    </>
                  )}
                </section>
              )
            })}
          </div>
        )}

        {/* Sources */}
        <div className="mt-8 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-4 font-semibold text-gray-900">Zrodla</h2>
          <div className="space-y-3">
            {report.sources.map((source, idx) => (
              <div key={idx} className="flex items-center justify-between rounded-lg border border-gray-200 p-3">
                <div className="flex items-center gap-3">
                  <span className="text-gray-600">{source.name}</span>
                  <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline">
                    {source.url}
                  </a>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-500">Pewnosc:</span>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    source.confidence >= 0.9 ? 'bg-green-100 text-green-800' :
                    source.confidence >= 0.75 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-orange-100 text-orange-800'
                  }`}>
                    {Math.round(source.confidence * 100)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Annotation Instructions */}
        <div className="mt-8 rounded-xl bg-blue-50 border border-blue-200 p-4 text-sm text-blue-700">
          <div className="font-medium mb-1">Jak dodac adnotacje?</div>
          <p>Zaznacz dowolny tekst w raporcie, a pojawi sie opcja dodania komentarza. Twoje adnotacje zostana zapisane i beda widoczne przy kolejnych wizytach.</p>
        </div>
      </main>

      {/* Share Modal with Tabs */}
      {showShareModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
          <div className="w-full max-w-md rounded-lg bg-white shadow-xl">
            <div className="border-b border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Udostępnij raport</h3>
                <button
                  onClick={() => {
                    setShowShareModal(false)
                    setShareEmail('')
                    setShareMessage('')
                    setShareError('')
                    setShareSuccess(false)
                    setShareLink('')
                    setLinkCopied(false)
                    setEmbedCode('')
                    setEmbedCopied(false)
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-gray-200">
              <button
                onClick={() => setShareTab('link')}
                className={`flex-1 px-4 py-3 text-sm font-medium ${
                  shareTab === 'link'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                🔗 Link
              </button>
              <button
                onClick={() => setShareTab('email')}
                className={`flex-1 px-4 py-3 text-sm font-medium ${
                  shareTab === 'email'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                ✉️ Email
              </button>
              <button
                onClick={() => setShareTab('embed')}
                className={`flex-1 px-4 py-3 text-sm font-medium ${
                  shareTab === 'embed'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                📋 Embed
              </button>
            </div>

            <div className="p-4 space-y-4">
              {/* Link Tab */}
              {shareTab === 'link' && (
                <>
                  {shareError && (
                    <div className="rounded-md bg-red-50 p-4">
                      <p className="text-sm text-red-700">{shareError}</p>
                    </div>
                  )}

                  {!shareLink ? (
                    <div className="text-center py-6">
                      <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                      </svg>
                      <h3 className="mt-2 text-sm font-medium text-gray-900">Wygeneruj link udostępniania</h3>
                      <p className="mt-1 text-sm text-gray-500">Stwórz publiczny link do tego raportu</p>

                      {/* Password protection option */}
                      <div className="mt-4 space-y-3 max-w-sm mx-auto">
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            id="password-protect"
                            checked={passwordProtected}
                            onChange={(e) => {
                              setPasswordProtected(e.target.checked)
                              if (!e.target.checked) {
                                setSharePassword('')
                              }
                            }}
                            className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                          />
                          <label htmlFor="password-protect" className="ml-2 text-sm text-gray-700">
                            Chroń hasłem
                          </label>
                        </div>

                        {passwordProtected && (
                          <div className="text-left">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Hasło
                            </label>
                            <input
                              type="password"
                              value={sharePassword}
                              onChange={(e) => setSharePassword(e.target.value)}
                              placeholder="Wpisz hasło..."
                              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                            />
                          </div>
                        )}
                      </div>

                      <div className="mt-6">
                        <button
                          onClick={handleGenerateShareLink}
                          disabled={isGeneratingLink || (passwordProtected && !sharePassword)}
                          className="inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                        >
                          {isGeneratingLink ? (
                            <>
                              <div className="h-4 w-4 mr-2 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                              Generowanie...
                            </>
                          ) : (
                            <>
                              <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                              </svg>
                              Wygeneruj link
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="rounded-md bg-green-50 p-4">
                        <div className="flex items-start">
                          <svg className="h-5 w-5 text-green-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <div className="flex-1">
                            <p className="text-sm font-medium text-green-800">Link utworzony pomyślnie!</p>
                            <p className="text-xs text-green-700 mt-1">Każdy kto ma ten link może zobaczyć raport</p>
                          </div>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Link do udostępnienia
                        </label>
                        <div className="flex gap-2">
                          <input
                            type="text"
                            value={shareLink}
                            readOnly
                            className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm bg-gray-50"
                          />
                          <button
                            onClick={handleCopyShareLink}
                            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                          >
                            {linkCopied ? (
                              <>
                                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                </svg>
                              </>
                            ) : (
                              'Kopiuj'
                            )}
                          </button>
                        </div>
                      </div>

                      <div className="rounded-md bg-yellow-50 p-3 text-xs text-yellow-800">
                        ⚠️ Link wygasa po 30 dniach. Możesz cofnąć dostęp w dowolnym momencie.
                      </div>
                    </>
                  )}
                </>
              )}

              {/* Email Tab */}
              {shareTab === 'email' && (
                <>
                  {shareSuccess ? (
                    <div className="rounded-md bg-green-50 p-4">
                      <div className="flex items-center">
                        <svg className="h-5 w-5 text-green-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <p className="text-sm text-green-700">Raport został pomyślnie udostępniony!</p>
                      </div>
                    </div>
                  ) : (
                    <>
                      {shareError && (
                        <div className="rounded-md bg-red-50 p-4">
                          <p className="text-sm text-red-700">{shareError}</p>
                        </div>
                      )}

                      <div>
                        <label htmlFor="share-email" className="block text-sm font-medium text-gray-700 mb-1">
                          Adres email odbiorcy *
                        </label>
                        <input
                          id="share-email"
                          type="email"
                          value={shareEmail}
                          onChange={(e) => setShareEmail(e.target.value)}
                          placeholder="email@example.com"
                          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                          required
                        />
                      </div>

                      <div>
                        <label htmlFor="share-message" className="block text-sm font-medium text-gray-700 mb-1">
                          Wiadomość (opcjonalnie)
                        </label>
                        <textarea
                          id="share-message"
                          value={shareMessage}
                          onChange={(e) => setShareMessage(e.target.value)}
                          placeholder="Dodaj krótką wiadomość..."
                          rows={4}
                          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        />
                      </div>

                      <div className="flex gap-3 pt-2">
                        <button
                          onClick={() => {
                            setShowShareModal(false)
                            setShareEmail('')
                            setShareMessage('')
                            setShareError('')
                          }}
                          className="flex-1 rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                          disabled={isSharing}
                        >
                          Anuluj
                        </button>
                        <button
                          onClick={handleShareEmail}
                          disabled={isSharing || !shareEmail}
                          className="flex-1 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {isSharing ? (
                            <span className="flex items-center justify-center">
                              <div className="h-4 w-4 mr-2 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                              Wysyłanie...
                            </span>
                          ) : (
                            'Wyślij'
                          )}
                        </button>
                      </div>
                    </>
                  )}
                </>
              )}

              {/* Embed Tab */}
              {shareTab === 'embed' && (
                <>
                  {!embedCode ? (
                    <div className="text-center py-6">
                      <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                      </svg>
                      <h3 className="mt-2 text-sm font-medium text-gray-900">Wygeneruj kod osadzania</h3>
                      <p className="mt-1 text-sm text-gray-500">Stwórz kod HTML do osadzenia raportu na swojej stronie</p>

                      <div className="mt-6">
                        <button
                          onClick={handleGenerateEmbedCode}
                          className="inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                        >
                          <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                          </svg>
                          Wygeneruj kod
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="rounded-md bg-green-50 p-4">
                        <div className="flex items-start">
                          <svg className="h-5 w-5 text-green-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <div className="flex-1">
                            <p className="text-sm font-medium text-green-800">Kod osadzania wygenerowany!</p>
                            <p className="text-xs text-green-700 mt-1">Skopiuj poniższy kod i wklej na swojej stronie</p>
                          </div>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Kod HTML (iframe)
                        </label>
                        <div className="space-y-2">
                          <textarea
                            value={embedCode}
                            readOnly
                            rows={4}
                            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm bg-gray-50 font-mono"
                          />
                          <button
                            onClick={handleCopyEmbedCode}
                            className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 flex items-center justify-center"
                          >
                            {embedCopied ? (
                              <>
                                <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                </svg>
                                Skopiowano!
                              </>
                            ) : (
                              <>
                                <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                                Kopiuj kod
                              </>
                            )}
                          </button>
                        </div>
                      </div>

                      <div className="rounded-md bg-blue-50 p-3 text-xs text-blue-800">
                        <p className="font-medium mb-1">💡 Jak użyć:</p>
                        <ol className="list-decimal list-inside space-y-1">
                          <li>Skopiuj powyższy kod HTML</li>
                          <li>Wklej go w miejscu gdzie chcesz osadzić raport</li>
                          <li>Raport będzie wyświetlany w iframe o szerokości 100% i wysokości 800px</li>
                        </ol>
                      </div>
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Access Log Modal */}
      {showAccessLogModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
          <div className="w-full max-w-4xl rounded-lg bg-white shadow-xl max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between border-b p-4">
              <h3 className="text-lg font-semibold text-gray-900">Log dostępu do raportu</h3>
              <button
                onClick={() => setShowAccessLogModal(false)}
                className="rounded-lg p-1 hover:bg-gray-100"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="overflow-y-auto p-4">
              {isLoadingAccessLog ? (
                <div className="flex items-center justify-center py-12">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
                </div>
              ) : accessLogData?.error ? (
                <div className="text-center py-12 text-red-600">
                  {accessLogData.error}
                </div>
              ) : accessLogData?.share_links?.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <svg className="h-12 w-12 mx-auto mb-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="font-medium">Brak udostępnień</p>
                  <p className="text-sm mt-1">Ten raport nie był jeszcze udostępniany</p>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="rounded-lg bg-blue-50 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">Podsumowanie</h4>
                        <p className="text-sm text-gray-600 mt-1">
                          Raport został udostępniony {accessLogData?.share_links?.length || 0} razy
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-3xl font-bold text-blue-600">{accessLogData?.total_accesses || 0}</div>
                        <div className="text-sm text-gray-600">Całkowite wyświetlenia</div>
                      </div>
                    </div>
                  </div>

                  {accessLogData?.share_links?.map((shareLink: any, idx: number) => (
                    <div key={idx} className="rounded-lg border border-gray-200 p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h5 className="font-medium text-gray-900">Link udostępnienia #{idx + 1}</h5>
                          <p className="text-sm text-gray-500 mt-1">
                            Utworzono: {new Date(shareLink.created_at).toLocaleString('pl-PL')}
                          </p>
                          <p className="text-sm text-gray-500">
                            Wygasa: {new Date(shareLink.expires_at).toLocaleString('pl-PL')}
                          </p>
                        </div>
                        <div className="flex items-start gap-3">
                          <div className="text-right">
                            <div className="text-2xl font-bold text-gray-900">{shareLink.access_count}</div>
                            <div className="text-xs text-gray-500">wyświetleń</div>
                          </div>
                          <button
                            onClick={() => handleRevokeShareLink(shareLink.share_token)}
                            className="flex items-center gap-1 rounded-lg border border-red-300 bg-white px-3 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                            title="Cofnij udostępnienie - link przestanie działać"
                          >
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                            </svg>
                            Cofnij
                          </button>
                        </div>
                      </div>

                      {shareLink.accesses && shareLink.accesses.length > 0 ? (
                        <div className="mt-4">
                          <h6 className="text-sm font-medium text-gray-700 mb-2">Historia dostępu:</h6>
                          <div className="space-y-2 max-h-60 overflow-y-auto">
                            {shareLink.accesses.map((access: any, accessIdx: number) => (
                              <div key={accessIdx} className="flex items-start gap-3 text-sm bg-gray-50 rounded p-3">
                                <svg className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                </svg>
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2 flex-wrap">
                                    <span className="font-medium text-gray-900">
                                      {new Date(access.timestamp).toLocaleString('pl-PL')}
                                    </span>
                                    <span className="text-gray-400">•</span>
                                    <span className="text-gray-600">{access.ip_address}</span>
                                    {access.country !== 'Unknown' && (
                                      <>
                                        <span className="text-gray-400">•</span>
                                        <span className="text-gray-600">{access.country}</span>
                                      </>
                                    )}
                                    {access.city !== 'Unknown' && (
                                      <>
                                        <span className="text-gray-400">•</span>
                                        <span className="text-gray-600">{access.city}</span>
                                      </>
                                    )}
                                  </div>
                                  <div className="text-xs text-gray-500 mt-1 truncate" title={access.user_agent}>
                                    {access.user_agent}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500 mt-3 text-center py-4">
                          Ten link nie został jeszcze otwarty
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
