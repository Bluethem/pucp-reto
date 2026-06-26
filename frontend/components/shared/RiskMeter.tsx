'use client'

import type { RiskLevel } from '@/types'

interface RiskMeterProps {
  score: RiskLevel
  size?: 'sm' | 'md' | 'lg'
}

const SEGMENTS = [
  { value: 1, color: '#16a34a', label: '1' },
  { value: 2, color: '#4ade80', label: '2' },
  { value: 3, color: '#ca8a04', label: '3' },
  { value: 4, color: '#f97316', label: '4' },
  { value: 5, color: '#dc2626', label: '5' },
]

export default function RiskMeter({ score, size = 'md' }: RiskMeterProps) {
  const barH = { sm: 'h-2', md: 'h-3', lg: 'h-4' }[size]
  const labelSize = { sm: 'text-xs', md: 'text-sm', lg: 'text-base' }[size]

  return (
    <div className="w-full">
      <div className={`flex rounded-full overflow-hidden gap-0.5 ${barH}`}>
        {SEGMENTS.map(seg => (
          <div
            key={seg.value}
            className="flex-1 transition-opacity"
            style={{
              backgroundColor: seg.color,
              opacity: seg.value <= score ? 1 : 0.18,
            }}
          />
        ))}
      </div>
      <div className={`flex justify-between mt-1 ${labelSize}`}>
        {SEGMENTS.map(seg => (
          <span
            key={seg.value}
            className="font-medium"
            style={{ color: seg.value <= score ? seg.color : '#d1d5db' }}
          >
            {seg.label}
          </span>
        ))}
      </div>
    </div>
  )
}
