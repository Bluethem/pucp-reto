'use client'

import type { MapFilters } from '@/types'

const REGIONES = ['', 'Lima', 'Arequipa', 'Ayacucho', 'Cusco', 'Piura', 'La Libertad', 'Loreto']
const TIPOS    = ['', 'Pavimentación', 'Edificación', 'Carretera', 'Saneamiento', 'Electrificación']
const ESTADOS  = ['', 'En ejecución', 'Concluida', 'Paralizada', 'Por ejecutar']
const RIESGOS  = ['', 'Alto (4–5)', 'Medio (3)', 'Bajo (1–2)']

interface MapFiltersProps {
  filters: MapFilters
  onChange: (filters: MapFilters) => void
  totalObras: number
  filteredObras: number
}

export default function MapFiltersPanel({
  filters,
  onChange,
  totalObras,
  filteredObras,
}: MapFiltersProps) {
  const set = (key: keyof MapFilters) => (e: React.ChangeEvent<HTMLSelectElement>) =>
    onChange({ ...filters, [key]: e.target.value })

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm px-5 py-4">
      <div className="flex items-baseline gap-3 mb-4">
        <h2 className="text-[13px] font-semibold text-navy-800 uppercase tracking-wider">Filtros</h2>
        <span className="text-[11px] font-light text-gray-400">
          <span className="font-semibold text-teal-600">{filteredObras}</span> de {totalObras} obras
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {[
          { label: 'Tipo de obra', key: 'tipo' as keyof MapFilters, opts: TIPOS },
          { label: 'Estado', key: 'estado' as keyof MapFilters, opts: ESTADOS },
          { label: 'Nivel de riesgo', key: 'riesgo' as keyof MapFilters, opts: RIESGOS },
        ].map(({ label, key, opts }) => (
          <div key={key}>
            <label className="block text-[10px] font-semibold text-gray-400 mb-1.5 uppercase tracking-widest">
              {label}
            </label>
            <select
              value={filters[key]}
              onChange={set(key)}
              className="w-full text-[13px] font-light border border-gray-200 rounded-lg px-3 py-1.5 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-teal-500 text-gray-700"
            >
              <option value="">Todos</option>
              {opts.filter(Boolean).map(o => (
                <option key={o} value={o}>{o}</option>
              ))}
            </select>
          </div>
        ))}
      </div>

      <div className="mt-3 pt-2 border-t border-gray-100">
        <p className="text-[10px] font-light text-gray-400">
          Selecciona un departamento en el mapa para filtrar por región
        </p>
      </div>
    </div>
  )
}
