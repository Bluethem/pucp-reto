export const dynamic = 'force-dynamic'

import { notFound } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Building2, User, AlertTriangle, MapPin } from 'lucide-react'
import { api } from '@/lib/api'
import { getObraById } from '@/lib/mock-data'
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
  let municipio
  try {
    municipio = await api.municipios.obtener(id)
  } catch {
    notFound()
  }
  if (!municipio) notFound()

  let obras: any[] = []
  try { obras = await api.municipios.obras(id) } catch {}

  const totalPpto = obras.reduce((s: number, o: any) => s + (o.presupuestoTotal || 0), 0)
  const obrasRiesgoAlto = obras.filter((o: any) => o.score >= 61).length

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <Link href="/" className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-navy-800 mb-5 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Volver al mapa
      </Link>

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
            <p className="text-xl font-bold text-navy-800">—</p>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-5">
        <div className="md:col-span-3">
          <h2 className="text-base font-semibold text-navy-800 mb-3 flex items-center gap-2">
            <Building2 className="w-4 h-4 text-teal-600" /> Obras bajo esta entidad
          </h2>
          <div className="space-y-3">
            {obras.length === 0 && (
              <p className="text-sm text-gray-400">Sin obras registradas en el sistema.</p>
            )}
            {obras.map((obra: any) => (
              <Link key={obra.id} href={`/obra/${obra.id}`}>
                <div className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow cursor-pointer">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-navy-800 leading-snug">{obra.titulo}</p>
                      <div className="flex flex-wrap gap-1.5 mt-1.5">
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ESTADO_STYLE[obra.estado] || 'bg-gray-100 text-gray-600'}`}>
                          {obra.estado}
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-gray-100 text-gray-600">
                          {obra.tipo}
                        </span>
                      </div>
                    </div>
                    <div className="shrink-0 text-right">
                      <RiskBadge score={obra.score} size="sm" showLabel={false} />
                      <p className="text-xs text-gray-400 mt-1">{obra.presupuestoTotal ? formatCurrency(obra.presupuestoTotal) : '—'}</p>
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
