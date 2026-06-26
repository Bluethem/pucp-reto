import type { Partida } from '@/types'
import { formatCurrency, ratioColorClass } from '@/lib/utils'
import SourceTag from '@/components/shared/SourceTag'
import { AlertTriangle } from 'lucide-react'

interface PartidaTableProps {
  partidas: Partida[]
  modoAnalisis: 'partidas' | 'fallback_m2'
}

export default function PartidaTable({ partidas, modoAnalisis }: PartidaTableProps) {
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
        <table className="w-full text-sm">
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
            {partidas.map(p => {
              const hasAlert = p.ratio > 1.3
              return (
                <tr
                  key={p.id}
                  className={hasAlert ? 'bg-red-50' : 'bg-white hover:bg-gray-50'}
                >
                  <td className="px-3 py-2.5">
                    <div className="flex items-center gap-1.5">
                      {hasAlert && (
                        <AlertTriangle className="w-3.5 h-3.5 text-red-500 shrink-0" />
                      )}
                      <span className={`font-medium ${hasAlert ? 'text-red-800' : 'text-gray-800'}`}>
                        {p.insumo}
                      </span>
                    </div>
                  </td>
                  <td className="px-3 py-2.5 text-right text-gray-500">{p.unidad}</td>
                  <td className="px-3 py-2.5 text-right text-gray-600">
                    {p.cantidad.toLocaleString('es-PE')}
                  </td>
                  <td className="px-3 py-2.5 text-right font-medium text-gray-800">
                    S/ {p.precioDeclarado.toFixed(2)}
                  </td>
                  <td className="px-3 py-2.5 text-right text-gray-500">
                    S/ {p.precioReferencia.toFixed(2)}
                  </td>
                  <td className={`px-3 py-2.5 text-right font-bold ${ratioColorClass(p.ratio)}`}>
                    {p.ratio.toFixed(2)}×
                  </td>
                  <td className="px-3 py-2.5 text-center">
                    <SourceTag source={p.fuente} />
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <p className="mt-2 text-xs text-gray-400">
        Ratio = precio declarado / precio de referencia.
        Valores &gt;1.30 se marcan como alertas de sobreprecio.
      </p>
    </div>
  )
}
