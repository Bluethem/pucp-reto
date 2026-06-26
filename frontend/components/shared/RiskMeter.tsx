'use client'

import type { RiskLevel } from '@/types'

interface RiskMeterProps {
  score: RiskLevel
  size?: 'sm' | 'md' | 'lg'
}

export default function RiskMeter({ score, size = 'md' }: RiskMeterProps) {
  const clamped = Math.min(100, Math.max(0, score))
  const barH = { sm: 'h-2', md: 'h-3', lg: 'h-4' }[size]
  const labelSize = { sm: 'text-xs', md: 'text-sm', lg: 'text-base' }[size]

  const green = Math.min(clamped, 40) / 40 * 100
  const yellow = clamped > 40 ? Math.min(clamped - 40, 20) / 20 * 100 : 0
  const red = clamped > 60 ? (clamped - 60) / 40 * 100 : 0

  return (
    <div className="w-full">
      <div className={`flex ${barH} rounded-full overflow-hidden bg-gray-200`}>
        <div className="h-full transition-all duration-500 bg-green-500" style={{ width: `${green}%` }} />
        <div className="h-full transition-all duration-500 bg-yellow-500" style={{ width: `${yellow}%` }} />
        <div className="h-full transition-all duration-500 bg-red-500" style={{ width: `${red}%` }} />
      </div>
      <div className={`flex justify-between mt-1 ${labelSize} text-gray-400`}>
        <span>0</span>
        <span className="text-green-600 font-medium">40</span>
        <span className="text-yellow-600 font-medium">60</span>
        <span>100</span>
      </div>
    </div>
  )
}
