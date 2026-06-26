'use client'

import dynamic from 'next/dynamic'
import { useState, useMemo } from 'react'
import { OBRAS } from '@/lib/mock-data'
import type { MapFilters, RiskLevel } from '@/types'
import MapFiltersPanel from '@/components/map/MapFilters'
import ObraCard from '@/components/map/ObraCard'
import Disclaimer from '@/components/shared/Disclaimer'
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

function matchRiesgo(score: RiskLevel, riesgo: string): boolean {
  if (!riesgo) return true
  if (riesgo.startsWith('Alto')) return score >= 4
  if (riesgo.startsWith('Medio')) return score === 3
  if (riesgo.startsWith('Bajo')) return score <= 2
  return true
}

export default function HomePage() {
  const [filters, setFilters] = useState<MapFilters>(DEFAULT_FILTERS)

  const filteredObras = useMemo(() => {
    return OBRAS.filter(o => {
      if (filters.region && o.region.toLowerCase() !== filters.region.toLowerCase()) return false
      if (filters.tipo && o.tipo !== filters.tipo) return false
      if (filters.estado && o.estado !== filters.estado) return false
      if (!matchRiesgo(o.score, filters.riesgo)) return false
      return true
    })
  }, [filters])

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
      <div className="flex gap-4 flex-col lg:flex-row">

        {/* Mapa interactivo del Peru */}
        <div className="flex-1 min-h-[500px] lg:min-h-[580px] bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
          <PeruMap
            onSelectRegion={(region) =>
              setFilters(prev => ({ ...prev, region }))
            }
          />
        </div>

        {/* Sidebar de obras */}
        <div className="lg:w-80 xl:w-96 flex flex-col gap-3 overflow-y-auto max-h-[580px]">
          {filters.region ? (
            <p className="text-xs font-light text-gray-400 px-1">
              <span className="font-semibold text-navy-800">{filteredObras.length}</span>{' '}
              obras en{' '}
              <span className="font-semibold text-teal-600">{filters.region}</span>
            </p>
          ) : (
            <p className="text-xs font-light text-gray-400 px-1">
              <span className="font-semibold text-navy-800">{filteredObras.length}</span> obras —
              haz clic en un departamento para filtrar
            </p>
          )}
          {filteredObras.map(obra => (
            <ObraCard key={obra.id} obra={obra} compact />
          ))}
          {filteredObras.length === 0 && (
            <div className="text-center py-12 text-gray-400 text-sm font-light">
              No hay obras para los filtros seleccionados
            </div>
          )}
        </div>
      </div>

      <Disclaimer />
    </div>
  )
}
