'use client'

import dynamic from 'next/dynamic'
import { useState, useMemo } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { OBRAS } from '@/lib/mock-data'
import type { MapFilters, RiskLevel } from '@/types'
import MapFiltersPanel from '@/components/map/MapFilters'
import ObraCard from '@/components/map/ObraCard'
import BannerCarousel from '@/components/home/BannerCarousel'

const PeruMap = dynamic(() => import('@/components/map/PeruMap'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full rounded-xl bg-gray-100 flex items-center justify-center text-gray-400 text-sm font-light">
      Cargando mapa…
    </div>
  ),
})

const DEFAULT_FILTERS: MapFilters = { region: '', tipo: '', estado: '', riesgo: '' }
const PAGE_SIZE = 4

function matchRiesgo(score: RiskLevel, riesgo: string): boolean {
  if (!riesgo) return true
  if (riesgo.startsWith('Alto')) return score >= 4
  if (riesgo.startsWith('Medio')) return score === 3
  if (riesgo.startsWith('Bajo')) return score <= 2
  return true
}

export default function HomePage() {
  const [filters, setFilters] = useState<MapFilters>(DEFAULT_FILTERS)
  const [page, setPage] = useState(1)

  const filteredObras = useMemo(() => {
    setPage(1)
    return OBRAS.filter(o => {
      if (filters.region && o.region.toLowerCase() !== filters.region.toLowerCase()) return false
      if (filters.tipo && o.tipo !== filters.tipo) return false
      if (filters.estado && o.estado !== filters.estado) return false
      if (!matchRiesgo(o.score, filters.riesgo)) return false
      return true
    })
  }, [filters])

  const totalPages = Math.ceil(filteredObras.length / PAGE_SIZE)
  const pageObras = filteredObras.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  return (
    <div className="flex flex-col gap-5 p-4 max-w-[1400px] mx-auto w-full">

      {/* Banner row: carousel + vertical gif */}
      <div className="flex gap-4 items-stretch">
        <div className="min-w-0" style={{ flex: '0 0 72%' }}>
          <BannerCarousel />
        </div>
        <div className="hidden md:block" style={{ flex: '0 0 calc(28% - 16px)' }}>
          <img
            src="/assets/bannervertical.gif"
            alt="Banner lateral"
            className="w-full h-full object-cover rounded-2xl shadow-lg"
            style={{ display: 'block' }}
          />
        </div>
      </div>

      {/* Filters */}
      <MapFiltersPanel
        filters={filters}
        onChange={setFilters}
        totalObras={OBRAS.length}
        filteredObras={filteredObras.length}
      />

      {/* Mapa Peru + sidebar */}
      <div className="flex gap-4 flex-col lg:flex-row items-stretch">

        {/* Mapa interactivo del Peru */}
        <div className="flex-1 min-h-[500px] lg:min-h-[580px] bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
          <PeruMap
            onSelectRegion={(region) =>
              setFilters(prev => ({ ...prev, region }))
            }
          />
        </div>

        {/* Sidebar de obras */}
        <div className="lg:w-80 xl:w-96 flex flex-col">

          {/* Header */}
          <p className="text-xs font-light text-gray-400 px-1 mb-3 shrink-0">
            {filters.region ? (
              <>
                <span className="font-semibold text-navy-800">{filteredObras.length}</span>{' '}
                obras en <span className="font-semibold text-teal-600">{filters.region}</span>
              </>
            ) : (
              <>
                <span className="font-semibold text-navy-800">{filteredObras.length}</span> obras —
                haz clic en un departamento para filtrar
              </>
            )}
          </p>

          {/* Cards — flex-1 ocupa todo el espacio restante */}
          <div className="flex-1 flex flex-col gap-3 min-h-0">
            {filteredObras.length === 0 ? (
              <div className="flex-1 flex items-center justify-center text-gray-400 text-sm font-light">
                No hay obras para los filtros seleccionados
              </div>
            ) : (
              pageObras.map(obra => (
                <div key={obra.id} className="flex-1 min-h-0">
                  <ObraCard obra={obra} compact />
                </div>
              ))
            )}
          </div>

          {/* Paginación */}
          {totalPages > 1 && (
            <div className="shrink-0 mt-3 flex items-center justify-between">
              <p className="text-[11px] font-light text-gray-400">
                {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, filteredObras.length)} de {filteredObras.length}
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
                      n === page ? 'bg-navy-800 text-white border-navy-800' : 'border-gray-200 text-gray-500 hover:bg-gray-50'
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
          )}
        </div>
      </div>
    </div>
  )
}
