import { notFound } from 'next/navigation'
import Link from 'next/link'
import {
  ArrowLeft, Building2, User, AlertTriangle, MapPin
} from 'lucide-react'
import {
  getMunicipioById,
  getAutoridadesByMunicipio,
  getObrasByMunicipio,
} from '@/lib/mock-data'
import RiskBadge from '@/components/shared/RiskBadge'
import Disclaimer from '@/components/shared/Disclaimer'
import { formatCurrency } from '@/lib/utils'

interface Props {
  params: Promise<{ id: string }>
}

const ESTADO_STYLE: Record<string, string> = {
  'En ejecución': 'bg-blue-100 text-blue-700',
  'Concluida': 'bg-green-100 text-green-700',
  'Paralizada': 'bg-red-100 text-red-700',
  'Por ejecutar': 'bg-gray-100 text-gray-600',
}

export default async function MunicipioPage({ params }: Props) {
  const { id } = await params
  const municipio = getMunicipioById(id)
  if (!municipio) notFound()

  const autoridades = getAutoridadesByMunicipio(municipio.id)
  const obras = getObrasByMunicipio(municipio.id)

  const alcalde = autoridades.find(a => a.cargo === 'Alcalde')
  const regidores = autoridades.filter(a => a.cargo === 'Regidor')
  const totalPpto = obras.reduce((s, o) => s + o.presupuestoTotal, 0)
  const obrasRiesgoAlto = obras.filter(o => o.score >= 4).length

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-navy-800 mb-5 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Volver al mapa
      </Link>

      {/* Header */}
      <div className="bg-white border border-gray-200 rounded-2xl p-6 mb-5 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-xl bg-navy-800 flex items-center justify-center shrink-0">
            <Building2 className="w-7 h-7 text-teal-400" />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-xl md:text-2xl font-bold text-navy-800 leading-tight">
              {municipio.nombre}
            </h1>
            <div className="flex items-center gap-1.5 mt-1 text-sm text-gray-500">
              <MapPin className="w-4 h-4 text-teal-600" />
              {municipio.region}, {municipio.departamento}
            </div>
          </div>
          <div className="shrink-0 text-right">
            <p className="text-xs text-gray-400 mb-1">Score agregado</p>
            <RiskBadge score={municipio.scoreAgregado} size="md" />
          </div>
        </div>

        <div className="mt-5 grid grid-cols-2 md:grid-cols-4 gap-3 pt-5 border-t border-gray-100">
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wide">Total obras</p>
            <p className="text-xl font-bold text-navy-800">{obras.length}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wide">Obras riesgo alto</p>
            <p className={`text-xl font-bold ${obrasRiesgoAlto > 0 ? 'text-red-600' : 'text-green-600'}`}>
              {obrasRiesgoAlto}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wide">Presupuesto total</p>
            <p className="text-base font-bold text-navy-800">{formatCurrency(totalPpto)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wide">Autoridades</p>
            <p className="text-xl font-bold text-navy-800">{autoridades.length}</p>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-5">
        {/* Autoridades */}
        <div>
          <h2 className="text-base font-semibold text-navy-800 mb-3 flex items-center gap-2">
            <User className="w-4 h-4 text-teal-600" /> Autoridades
          </h2>
          <div className="space-y-3">
            {autoridades.length === 0 && (
              <p className="text-sm text-gray-400">Sin datos de autoridades disponibles.</p>
            )}
            {alcalde && (
              <Link href={`/autoridad/${alcalde.id}`}>
                <div className="bg-white border border-teal-200 rounded-xl p-4 hover:shadow-md transition-shadow cursor-pointer">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-navy-100 flex items-center justify-center">
                      <User className="w-5 h-5 text-navy-600" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-navy-800">{alcalde.nombre}</p>
                      <p className="text-xs text-teal-600 font-medium">{alcalde.cargo}</p>
                      <p className="text-xs text-gray-400">{alcalde.partido} · {alcalde.periodo}</p>
                    </div>
                  </div>
                  {alcalde.procesos.length > 0 && (
                    <div className="mt-2 flex items-center gap-1.5 text-xs text-red-600 bg-red-50 rounded-lg px-2.5 py-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                      {alcalde.procesos.length} proceso(s) registrado(s) — JNE / PJ
                    </div>
                  )}
                </div>
              </Link>
            )}
            {regidores.map(r => (
              <Link key={r.id} href={`/autoridad/${r.id}`}>
                <div className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow cursor-pointer">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center">
                      <User className="w-4 h-4 text-gray-500" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-800">{r.nombre}</p>
                      <p className="text-xs text-gray-500">{r.cargo} · {r.partido}</p>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Obras */}
        <div className="md:col-span-2">
          <h2 className="text-base font-semibold text-navy-800 mb-3 flex items-center gap-2">
            <Building2 className="w-4 h-4 text-teal-600" /> Obras bajo esta entidad
          </h2>
          <div className="space-y-3">
            {obras.map(obra => (
              <Link key={obra.id} href={`/obra/${obra.id}`}>
                <div className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow cursor-pointer">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-navy-800 leading-snug">
                        {obra.titulo}
                      </p>
                      <div className="flex flex-wrap gap-1.5 mt-1.5">
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ESTADO_STYLE[obra.estado]}`}>
                          {obra.estado}
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-gray-100 text-gray-600">
                          {obra.tipo}
                        </span>
                      </div>
                    </div>
                    <div className="shrink-0 text-right">
                      <RiskBadge score={obra.score} size="sm" showLabel={false} />
                      <p className="text-xs text-gray-400 mt-1">{formatCurrency(obra.presupuestoTotal)}</p>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-6">
        <Disclaimer />
      </div>
    </div>
  )
}
