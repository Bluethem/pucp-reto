import { cn, riskColor, riskLabel } from '@/lib/utils'
import type { RiskLevel } from '@/types'

interface RiskBadgeProps {
  score: RiskLevel
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

const COLORS = {
  green: { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200', dot: 'bg-green-500' },
  yellow: { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200', dot: 'bg-yellow-500' },
  red: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', dot: 'bg-red-500' },
}

export default function RiskBadge({ score, size = 'md', showLabel = true }: RiskBadgeProps) {
  const color = riskColor(score)
  const cfg = COLORS[color]

  const sizeClass = {
    sm: 'text-[11px] px-2 py-0.5 gap-1',
    md: 'text-[12px] px-2.5 py-1 gap-1.5',
    lg: 'text-[13px] px-3 py-1.5 gap-2',
  }[size]

  const dotSize = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
    lg: 'w-2.5 h-2.5',
  }[size]

  return (
    <span
      className={cn(
        'inline-flex items-center font-semibold rounded-full border whitespace-nowrap',
        cfg.bg, cfg.text, cfg.border, sizeClass
      )}
    >
      <span className={cn('rounded-full shrink-0', dotSize, cfg.dot)} />
      {showLabel ? (
        <span>{riskLabel(score)}</span>
      ) : (
        <span>{score}/100</span>
      )}
    </span>
  )
}
