'use client'

import { useState } from 'react'
import type { Partida } from '@/types'
import { formatCurrency, ratioColorClass } from '@/lib/utils'
import SourceTag from '@/components/shared/SourceTag'
import { AlertTriangle, ChevronLeft, ChevronRight } from 'lucide-react'

const PAGE_SIZE = 5

interface PartidaTableProps {
  partidas: Partida[]
  modoAnalisis: 'partidas' | 'fallback_m2'
}

export default function PartidaTable({ partidas, modoAnalisis }: PartidaTableProps) {
  const [page, setPage] = useState(1)
  const totalPages = Math.ceil(partidas.length / PAGE_SIZE)
  const slice = partidas.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  return (
    <div>
      {modoAnalisis === 'fallback_m2' && (
        <div className="mb-3 flex items-start gap-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
          <AlertTriangle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
          <span>
            Análisis por <strong>fallback de costo global</strong>: el expediente técnico no contiene
            partidas estructuradas. Se compara el costo total por unidad de medida (km, m²)
            contra la referencia MVCS.
          </span>
        </div>
      )}

      <div className="overflow-x-auto rounded-xl border border-gray-200">
        <table className="w-full text-sm table-fixed">
          <colgroup>
            <col style={{ width: '30%' }} />
            <col style={{ width: '8%' }} />
            <col style={{ width: '10%' }} />
            <col style={{ width: '15%' }} />
            <col style={{ width: '15%' }} />
            <col style={{ width: '10%' }} />
            <col style={{ width: '12%' }} />
          </colgroup>
          <thead>
            <tr className="bg-navy-800 text-white text-xs uppercase tracking-wider">
              <th className="text-left px-3 py-2.5 font-semibold">Insumo / Partida</th>
              <th className="text-right px-3 py-2.5 font-semibold">Unid.</th>
              <th className="text-right px-3 py-2.5 font-semibold">Cant.</th>
              <th className="text-right px-3 py-2.5 font-semibold">Precio declarado</th>
              <th className="text-right px-3 py-2.5 font-semibold">Precio referencia</th>
              <th className="text-right px-3 py-2.5 font-semibold">Ratio</th>
              <th className="text-center px-3 py-2.5 font-semibold">Fuente</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {slice.map(p => {
              const hasAlert = p.ratio > 1.3
              return (
                <tr key={p.id} className={hasAlert ? 'bg-red-50' : 'bg-white hover:bg-gray-50'} style={{ height: 56 }}>
                  <td className="px-3 py-2.5 max-w-0">
                    <div className="flex items-center gap-1.5 overflow-hidden">
                      {hasAlert && <AlertTriangle className="w-3.5 h-3.5 text-red-500 shrink-0" />}
                      <span
                        className={`font-medium truncate ${hasAlert ? 'text-red-800' : 'text-gray-800'}`}
                        title={p.insumo}
                      >
                        {p.insumo}
                      </span>
                    </div>
                  </td>
                  <td className="px-3 py-2.5 text-right text-gray-500">{p.unidad}</td>
                  <td className="px-3 py-2.5 text-right text-gray-600">{p.cantidad.toLocaleString('es-PE')}</td>
                  <td className="px-3 py-2.5 text-right font-medium text-gray-800">S/ {p.precioDeclarado.toFixed(2)}</td>
                  <td className="px-3 py-2.5 text-right text-gray-500">S/ {p.precioReferencia.toFixed(2)}</td>
                  <td className={`px-3 py-2.5 text-right font-bold ${ratioColorClass(p.ratio)}`}>
                    {p.ratio.toFixed(2)}×
                  </td>
                  <td className="px-3 py-2.5 text-center">
                    <SourceTag source={p.fuente} />
                  </td>
                </tr>
              )
            })}
            {/* Filas vacías para mantener altura fija */}
            {Array.from({ length: PAGE_SIZE - slice.length }).map((_, i) => (
              <tr key={`empty-${i}`} className="bg-white" style={{ height: 56 }}>
                <td colSpan={7} />
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Paginación */}
      <div className="mt-3 flex items-center justify-between">
        <p className="text-[11px] font-light text-gray-400">
          Mostrando {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, partidas.length)} de {partidas.length} partidas
        </p>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="w-7 h-7 flex items-center justify-center rounded border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map(n => (
            <button
              key={n}
              onClick={() => setPage(n)}
              className={`w-7 h-7 flex items-center justify-center rounded text-[11px] font-semibold border transition-colors ${
                n === page
                  ? 'bg-navy-800 text-white border-navy-800'
                  : 'border-gray-200 text-gray-500 hover:bg-gray-50'
              }`}
            >
              {n}
            </button>
          ))}
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="w-7 h-7 flex items-center justify-center rounded border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      <p className="mt-1 text-xs text-gray-400">
        Ratio = precio declarado / precio de referencia. Valores &gt;1.30 se marcan como alertas.
      </p>
    </div>
  )
}
