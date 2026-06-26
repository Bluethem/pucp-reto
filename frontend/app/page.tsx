'use client'

import dynamic from 'next/dynamic'
import { useState, useMemo, useEffect, useCallback } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { api } from '@/lib/api'
import type { MapFilters, RiskLevel, Obra } from '@/types'
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
  if (riesgo.startsWith('Alto')) return score >= 61
  if (riesgo.startsWith('Medio')) return score >= 41 && score <= 60
  if (riesgo.startsWith('Bajo')) return score <= 40
  return true
}

export default function HomePage() {
  const [obras, setObras] = useState<Obra[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<MapFilters>(DEFAULT_FILTERS)
  const [page, setPage] = useState(1)

  useEffect(() => {
    setLoading(true)
    setError(null)
    api.obras.listar().then(data => {
      setObras(data)
      setLoading(false)
    }).catch(err => {
      setError(err?.message || 'Error al cargar obras')
      setLoading(false)
    })
  }, [])

  // Reset page when filters change
  useEffect(() => {
    setPage(1)
  }, [filters])

  const filteredObras = useMemo(() => {
    return obras.filter(o => {
      if (filters.region && (o.departamento || '').toLowerCase() !== filters.region.toLowerCase()) return false
      if (filters.tipo && o.tipo !== filters.tipo) return false
      if (filters.estado && o.estado !== filters.estado) return false
      if (!matchRiesgo(o.score, filters.riesgo)) return false
      return true
    })
  }, [filters, obras])

  const totalPages = Math.ceil(filteredObras.length / PAGE_SIZE)
  const pageObras = filteredObras.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const handleSelectRegion = useCallback((region: string) => {
    setFilters(prev => ({ ...prev, region: prev.region === region ? '' : region }))
  }, [])

  return (
    <div className="flex flex-col gap-5 p-4 max-w-[1400px] mx-auto w-full">

      {/* Banner row */}
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
        totalObras={obras.length}
        filteredObras={filteredObras.length}
      />

      {/* Mapa + sidebar */}
      <div className="flex gap-4 flex-col lg:flex-row items-stretch">

        {/* Mapa */}
        <div className="flex-1 min-h-[500px] lg:min-h-[580px] bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
          <PeruMap onSelectRegion={handleSelectRegion} />
        </div>

        {/* Sidebar */}
        <div className="lg:w-80 xl:w-96 flex flex-col">

          <p className="text-xs font-light text-gray-400 px-1 mb-3 shrink-0">
            {loading ? (
              'Cargando obras…'
            ) : filters.region ? (
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

          <div className="flex-1 flex flex-col gap-3 min-h-0">
            {loading ? (
              <div className="flex-1 flex items-center justify-center text-gray-400 text-sm font-light">Cargando…</div>
            ) : error ? (
              <div className="flex-1 flex items-center justify-center text-red-400 text-sm font-light">{error}</div>
            ) : filteredObras.length === 0 ? (
              <div className="flex-1 flex items-center justify-center text-gray-400 text-sm font-light">
                {filters.region ? `No hay obras en ${filters.region}` : 'No hay obras disponibles'}
              </div>
            ) : (
              pageObras.map(obra => (
                <div key={obra.id} className="flex-1 min-h-0">
                  <ObraCard obra={obra} compact />
                </div>
              ))
            )}
          </div>

          {totalPages > 1 && (
            <div className="shrink-0 mt-3 flex items-center justify-between">
              <p className="text-[11px] font-light text-gray-400">
                {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, filteredObras.length)} de {filteredObras.length}
              </p>
              <div className="flex items-center gap-1">
                <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                  className="w-7 h-7 flex items-center justify-center rounded border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
                  <ChevronLeft className="w-4 h-4" />
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(n => (
                  <button key={n} onClick={() => setPage(n)}
                    className={`w-7 h-7 flex items-center justify-center rounded text-[11px] font-semibold border transition-colors ${n === page ? 'bg-navy-800 text-white border-navy-800' : 'border-gray-200 text-gray-500 hover:bg-gray-50'}`}>
                    {n}
                  </button>
                ))}
                <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}
                  className="w-7 h-7 flex items-center justify-center rounded border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
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
