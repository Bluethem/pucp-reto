import { notFound } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, User, AlertTriangle, Building2 } from 'lucide-react'
import { getAutoridadById, getMunicipioById, getObraById } from '@/lib/mock-data'
import RiskBadge from '@/components/shared/RiskBadge'
import Disclaimer from '@/components/shared/Disclaimer'
import SourceTag from '@/components/shared/SourceTag'
import type { RiskLevel } from '@/types'

interface Props {
  params: Promise<{ id: string }>
}

export default async function AutoridadPage({ params }: Props) {
  const { id } = await params
  const autoridad = getAutoridadById(id)
  if (!autoridad) notFound()

  const municipio = getMunicipioById(autoridad.municipioId)
  const obras = autoridad.obrasGestionIds
    .map(id => getObraById(id))
    .filter(Boolean)

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <Link
        href={`/municipio/${autoridad.municipioId}`}
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-navy-800 mb-5 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Volver al municipio
      </Link>

      {/* Profile card */}
      <div className="bg-white border border-gray-200 rounded-2xl p-6 mb-5 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="w-16 h-16 rounded-full bg-navy-100 flex items-center justify-center shrink-0">
            <User className="w-8 h-8 text-navy-600" />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-xl font-bold text-navy-800">{autoridad.nombre}</h1>
            <p className="text-teal-600 font-semibold text-sm mt-0.5">{autoridad.cargo}</p>
            <div className="flex flex-wrap gap-3 mt-2 text-sm text-gray-500">
              <span>{autoridad.partido}</span>
              <span>·</span>
              <span>Período {autoridad.periodo}</span>
              <span>·</span>
              <span>DNI: {autoridad.dni}</span>
            </div>
            {municipio && (
              <Link
                href={`/municipio/${municipio.id}`}
                className="inline-flex items-center gap-1 text-xs text-teal-700 hover:underline mt-2"
              >
                <Building2 className="w-3.5 h-3.5" /> {municipio.nombre}
              </Link>
            )}
          </div>
        </div>

        {autoridad.procesos.length > 0 && (
          <div className="mt-4 flex items-center gap-2 bg-red-50 border border-red-200 rounded-xl px-4 py-2.5">
            <AlertTriangle className="w-4 h-4 text-red-500 shrink-0" />
            <p className="text-sm text-red-700 font-medium">
              {autoridad.procesos.length} proceso(s) / denuncia(s) registrada(s) en fuentes públicas
            </p>
          </div>
        )}
      </div>

      {/* Procesos */}
      {autoridad.procesos.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-5 mb-5">
          <h2 className="text-base font-semibold text-navy-800 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            Procesos / denuncias registradas
          </h2>
          <div className="space-y-4">
            {autoridad.procesos.map(proc => (
              <div
                key={proc.id}
                className="border border-red-100 bg-red-50 rounded-xl px-4 py-3"
              >
                <div className="flex items-center justify-between gap-2 flex-wrap">
                  <span className="text-sm font-semibold text-red-800">{proc.tipo}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded-full font-medium">
                      {proc.estado}
                    </span>
                    <SourceTag source={proc.fuente} date={proc.fecha} />
                  </div>
                </div>
                <p className="text-sm text-red-700 mt-1.5">{proc.descripcion}</p>
              </div>
            ))}
          </div>
          <p className="mt-3 text-xs text-gray-400">
            Fuente: datos públicos del JNE y Poder Judicial. Estado al momento de la consulta.
          </p>
        </div>
      )}

      {/* Obras */}
      <div className="bg-white border border-gray-200 rounded-xl p-5 mb-5">
        <h2 className="text-base font-semibold text-navy-800 mb-4 flex items-center gap-2">
          <Building2 className="w-4 h-4 text-teal-600" />
          Obras bajo su gestión
        </h2>
        {obras.length === 0 ? (
          <p className="text-sm text-gray-400">Sin obras registradas.</p>
        ) : (
          <div className="space-y-3">
            {obras.map(obra => obra && (
              <Link key={obra.id} href={`/obra/${obra.id}`}>
                <div className="flex items-center justify-between gap-3 p-3 bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors cursor-pointer">
                  <p className="text-sm font-medium text-gray-800 line-clamp-1">{obra.titulo}</p>
                  <RiskBadge score={obra.score as RiskLevel} size="sm" showLabel={false} />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      <Disclaimer />
    </div>
  )
}
