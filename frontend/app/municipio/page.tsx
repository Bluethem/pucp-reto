import Link from 'next/link'
import { MapPin } from 'lucide-react'
import { MUNICIPIOS } from '@/lib/mock-data'
import RiskBadge from '@/components/shared/RiskBadge'

export default function MunicipiosPage() {
  const sorted = [...MUNICIPIOS].sort((a, b) => b.scoreAgregado - a.scoreAgregado)

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-8">
        <p className="text-[11px] font-semibold uppercase tracking-widest text-teal-600 mb-1">
          Base de datos
        </p>
        <h1 className="text-3xl font-extrabold text-navy-800">Municipios y entidades</h1>
        <p className="text-[13px] font-light text-gray-400 mt-1">
          Entidades ejecutoras de obras públicas con score de riesgo agregado.
        </p>
      </div>

      <div className="space-y-3">
        {sorted.map(mun => (
          <Link key={mun.id} href={`/municipio/${mun.id}`}>
            <div className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <p className="text-[15px] font-bold text-navy-800">{mun.nombre}</p>
                  <p className="text-[12px] font-light text-gray-400 mt-0.5 flex items-center gap-1.5">
                    <MapPin className="w-3 h-3 text-teal-500" />
                    {mun.region}, {mun.departamento} &nbsp;·&nbsp;
                    <span className="font-medium text-gray-500">{mun.obrasIds.length} obra{mun.obrasIds.length !== 1 ? 's' : ''}</span>
                  </p>
                </div>
                <RiskBadge score={mun.scoreAgregado} size="md" />
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
