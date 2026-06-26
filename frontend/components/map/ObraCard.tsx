'use client'

import Link from 'next/link'
import { ArrowRight, MapPin, Building2 } from 'lucide-react'
import type { Obra } from '@/types'
import RiskBadge from '@/components/shared/RiskBadge'
import { formatCurrency } from '@/lib/utils'

interface ObraCardProps {
  obra: Obra
  compact?: boolean
}

const ESTADO_LABEL: Record<string, string> = {
  ejecucion: 'En ejecución',
  concluido: 'Concluida',
  paralizado: 'Paralizada',
  planeado: 'Por ejecutar',
  'En ejecución': 'En ejecución',
  Concluida: 'Concluida',
  Paralizada: 'Paralizada',
  'Por ejecutar': 'Por ejecutar',
}

const ESTADO_COLOR: Record<string, string> = {
  ejecucion: 'bg-blue-100 text-blue-700',
  concluido: 'bg-green-100 text-green-700',
  paralizado: 'bg-red-100 text-red-700',
  planeado: 'bg-gray-100 text-gray-500',
  'En ejecución': 'bg-blue-100 text-blue-700',
  Concluida: 'bg-green-100 text-green-700',
  Paralizada: 'bg-red-100 text-red-700',
  'Por ejecutar': 'bg-gray-100 text-gray-500',
}

export default function ObraCard({ obra, compact = false }: ObraCardProps) {
  const estadoLabel = ESTADO_LABEL[obra.estado] || obra.estado || '—'
  const estadoColor = ESTADO_COLOR[obra.estado] || 'bg-gray-100 text-gray-500'

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow h-full flex flex-col">
      <div className="flex items-start justify-between gap-2 mb-2">
        <h3 className="text-[13px] font-semibold text-navy-800 leading-snug line-clamp-2 flex-1">
          {obra.titulo}
        </h3>
        {obra.score > 0 && <RiskBadge score={obra.score} size="sm" showLabel={false} />}
      </div>

      <div className="flex flex-wrap gap-1.5 mb-3">
        <span className={`text-[11px] px-2 py-0.5 rounded-full font-medium ${estadoColor}`}>
          {estadoLabel}
        </span>
        <span className="text-[11px] px-2 py-0.5 rounded-full font-medium bg-gray-100 text-gray-500">
          {obra.tipo || '—'}
        </span>
      </div>

      {!compact && (
        <>
          <div className="mt-3 space-y-1.5">
            <div className="flex items-center gap-1.5 text-[12px] text-gray-400 font-light">
              <MapPin className="w-3 h-3 shrink-0 text-teal-500" />
              <span>{obra.departamento || obra.region || 'Ubicación no disponible'}</span>
            </div>
            <div className="flex items-center gap-1.5 text-[12px] text-gray-400 font-light">
              <Building2 className="w-3 h-3 shrink-0 text-teal-500" />
              <span className="truncate">{obra.municipioNombre || '—'}</span>
            </div>
          </div>
          {obra.presupuestoTotal > 0 && (
            <div className="mt-3 flex items-center justify-between">
              <span className="text-[11px] font-light text-gray-400">Presupuesto total</span>
              <span className="text-[13px] font-bold text-navy-800">{formatCurrency(obra.presupuestoTotal)}</span>
            </div>
          )}
        </>
      )}

      <Link
        href={`/obra/${obra.id}`}
        className="mt-auto pt-3 flex items-center justify-center gap-1.5 w-full py-2 text-[12px] font-semibold text-teal-700 bg-teal-50 hover:bg-teal-100 rounded-lg transition-colors"
      >
        Ver detalle <ArrowRight className="w-3.5 h-3.5" />
      </Link>
    </div>
  )
}
