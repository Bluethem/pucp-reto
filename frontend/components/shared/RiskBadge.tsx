import { cn } from '@/lib/utils'
import type { RiskLevel } from '@/types'

interface RiskBadgeProps {
  score: RiskLevel
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

const SCORE_CONFIG: Record<
  RiskLevel,
  { label: string; bg: string; text: string; border: string; dot: string }
> = {
  1: { label: 'Riesgo Bajo', bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200', dot: 'bg-green-500' },
  2: { label: 'Riesgo Bajo', bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200', dot: 'bg-green-500' },
  3: { label: 'Riesgo Medio', bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200', dot: 'bg-yellow-500' },
  4: { label: 'Riesgo Alto', bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', dot: 'bg-red-500' },
  5: { label: 'Riesgo Alto', bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', dot: 'bg-red-500' },
}

export default function RiskBadge({ score, size = 'md', showLabel = true }: RiskBadgeProps) {
  const cfg = SCORE_CONFIG[score]

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
        <span>{cfg.label}</span>
      ) : (
        <span>{score * 20}/100</span>
      )}
    </span>
  )
}
