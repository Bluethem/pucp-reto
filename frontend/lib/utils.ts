import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import type { RiskLevel, RiskColor } from '@/types'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function riskColor(score: RiskLevel): RiskColor {
  if (score <= 2) return 'green'
  if (score === 3) return 'yellow'
  return 'red'
}

export function riskLabel(score: RiskLevel): string {
  if (score <= 2) return 'Bajo'
  if (score === 3) return 'Medio'
  return 'Alto'
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('es-PE', {
    style: 'currency',
    currency: 'PEN',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('es-PE').format(value)
}

export function riskColorClass(score: RiskLevel): string {
  if (score <= 2) return 'text-green-600 bg-green-50 border-green-200'
  if (score === 3) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
  return 'text-red-600 bg-red-50 border-red-200'
}

export function riskBulletColor(score: RiskLevel): string {
  if (score <= 2) return '#16a34a'
  if (score === 3) return '#ca8a04'
  return '#dc2626'
}

export function ratioColorClass(ratio: number): string {
  if (ratio <= 1.1) return 'text-green-600'
  if (ratio <= 1.3) return 'text-yellow-600'
  return 'text-red-600'
}
