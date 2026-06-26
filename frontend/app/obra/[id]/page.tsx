export const dynamic = 'force-dynamic'

import { notFound } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, MapPin, Calendar, Building2, Truck, ExternalLink } from 'lucide-react'
import { api } from '@/lib/api'
import RiskBadge from '@/components/shared/RiskBadge'
import Disclaimer from '@/components/shared/Disclaimer'
import PartidaTable from '@/components/obra/PartidaTable'
import { formatCurrency, riskColor } from '@/lib/utils'

interface Props {
  params: Promise<{ id: string }>
}

export default async function ObraDetailPage({ params }: Props) {
  const { id } = await params
  let obra
  try {
    obra = await api.obras.obtener(id)
  } catch {
    notFound()
  }
  if (!obra) notFound()

  const scoreColor = riskColor(obra.score)

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6">

      {/* Back */}
      <Link href="/"
        className="inline-flex items-center gap-1.5 text-[12px] font-light text-gray-400 hover:text-navy-800 mb-8 transition-colors">
        <ArrowLeft className="w-3.5 h-3.5" /> Volver al mapa
      </Link>

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-5xl font-extrabold text-navy-800 leading-none mb-1">
          {obra.titulo}
        </h1>
        <div className="flex items-center gap-2">
          <span className="text-[13px] font-medium text-teal-600">
            {obra.municipioNombre || obra.municipioId}
          </span>
          <span className="text-gray-300 text-[13px]">·</span>
          <span className="text-[13px] font-light text-gray-400 flex items-center gap-1">
            <MapPin className="w-3 h-3 text-teal-400 shrink-0" />
            {obra.region}, {obra.departamento}
          </span>
        </div>
      </div>

      {/* Características del proyecto */}
      <div className="bg-white border border-gray-200 rounded-2xl p-6 mb-6 shadow-sm">
        <div className="grid grid-cols-3 gap-x-8 gap-y-6">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-1">Presupuesto total</p>
            <p className="text-4xl font-extrabold text-navy-800 leading-none">{formatCurrency(obra.presupuestoTotal)}</p>
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-1">Empresa contratista</p>
            <span className="text-[15px] font-bold text-navy-800 block">
              {obra.empresaNombre || '—'}
            </span>
          </div>
          <div className="flex gap-3 items-start pt-4">
            {obra.infobrasUrl && (
              <a href={obra.infobrasUrl} target="_blank" rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-[11px] font-semibold text-gray-400 hover:text-navy-800 border border-gray-200 rounded-lg px-3 py-1.5 transition-colors">
                <ExternalLink className="w-3 h-3" /> INFOBRAS
              </a>
            )}
            {obra.seaceUrl && (
              <a href={obra.seaceUrl} target="_blank" rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-[11px] font-semibold text-gray-400 hover:text-navy-800 border border-gray-200 rounded-lg px-3 py-1.5 transition-colors">
                <ExternalLink className="w-3 h-3" /> SEACE
              </a>
            )}
          </div>

          <div className="col-span-3 border-t border-gray-100" />

          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-1">Estado</p>
            <p className="text-[13px] font-semibold text-navy-800">{obra.estado}</p>
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-1">Tipo de obra</p>
            <p className="text-[13px] font-medium text-gray-700">{obra.tipo}</p>
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-1">Análisis</p>
            <p className="text-[13px] font-medium text-gray-700 flex items-center gap-1">
              <Calendar className="w-3 h-3 text-teal-500 shrink-0" />
              {obra.modoAnalisis === 'partidas' ? 'Por partida' : 'Costo por m²'}
            </p>
          </div>
        </div>
      </div>

      {/* Score panel */}
      <div className="bg-white border border-gray-200 rounded-2xl p-6 mb-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center gap-6">

          <div className="shrink-0 text-center md:text-left">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-1">
              Puntuación de riesgo
            </p>
            <div className="flex items-end gap-1 justify-center md:justify-start">
              <span className="text-4xl font-extrabold text-navy-800 leading-none">{obra.score}</span>
              <span className="text-xl font-light text-gray-400 mb-1">/100</span>
            </div>
            <div className="mt-2">
              <RiskBadge score={obra.score} size="md" />
            </div>
          </div>

          <div className="flex-1 min-w-0">
            <div className="mb-4">
              <div className="flex justify-between text-[10px] font-light text-gray-400 mb-1">
                <span>0 — Sin riesgo</span>
                <span>100 — Riesgo máximo</span>
              </div>
              <div className="h-3 rounded-full bg-gray-100 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{
                    width: `${obra.score}%`,
                    backgroundColor: scoreColor === 'green' ? '#16a34a' : scoreColor === 'yellow' ? '#ca8a04' : '#dc2626',
                  }}
                />
              </div>
            </div>

            {obra.scoreDetalle.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {obra.scoreDetalle.map(ind => {
                  const color = ind.valor <= 40 ? '#16a34a' : ind.valor <= 60 ? '#ca8a04' : '#dc2626'
                  return (
                    <div key={ind.nombre} className="bg-gray-50 rounded-xl p-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[11px] font-semibold text-navy-800 leading-tight">{ind.nombre}</span>
                        <span className="text-[11px] font-bold ml-2 shrink-0" style={{ color }}>{ind.valor}/100</span>
                      </div>
                      <div className="h-1.5 rounded-full bg-gray-200 overflow-hidden mb-1.5">
                        <div className="h-full rounded-full" style={{ width: `${ind.valor}%`, backgroundColor: color }} />
                      </div>
                      <p className="text-[10px] font-light text-gray-400">{ind.descripcion}</p>
                    </div>
                  )
                })}
              </div>
            )}

          </div>
        </div>
      </div>

      {/* Two-column main body */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 items-stretch">

        {/* LEFT — Expediente técnico PDF */}
        <div className="flex flex-col gap-3">
          <h2 className="text-[15px] font-bold text-navy-800 uppercase tracking-wider">Expediente técnico</h2>

          <div className="flex-1 bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm flex flex-col">
            {obra.expedientePdfUrl ? (
              <>
                <iframe
                  src={`/api/pdf?url=${encodeURIComponent(obra.expedientePdfUrl)}#navpanes=0&view=FitH`}
                  style={{ width: '100%', flex: 1, border: 'none', display: 'block', minHeight: 0 }}
                  title="Expediente técnico"
                />
                <div className="border-t border-gray-100 px-4 py-2.5 flex items-center justify-between bg-gray-50 shrink-0">
                  <span className="text-[11px] font-light text-gray-400">Expediente técnico — PDF</span>
                  <a href={obra.expedientePdfUrl} target="_blank" rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-[11px] font-semibold text-teal-600 hover:underline">
                    <ExternalLink className="w-3 h-3" /> Abrir en nueva pestaña
                  </a>
                </div>
              </>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center gap-3 text-gray-400 p-8">
                <p className="text-sm font-light text-center">Expediente técnico no disponible en formato digital</p>
                {obra.infobrasUrl && (
                  <a href={obra.infobrasUrl} target="_blank" rel="noopener noreferrer"
                    className="text-[12px] font-semibold text-teal-600 hover:underline flex items-center gap-1">
                    <ExternalLink className="w-3 h-3" /> Ver en INFOBRAS
                  </a>
                )}
              </div>
            )}
          </div>
        </div>

        {/* RIGHT — Partidas */}
        <div className="flex flex-col gap-5">
          <h2 className="text-[15px] font-bold text-navy-800 uppercase tracking-wider">Partidas e insumos</h2>

          <PartidaTable partidas={obra.partidas} modoAnalisis={obra.modoAnalisis} />

          <div className="grid grid-cols-2 gap-3 mt-auto">
            <Link href={`/municipio/${obra.municipioId}`}
              className="flex items-center justify-center gap-2 px-4 py-3 bg-navy-800 hover:bg-navy-700 text-white text-[13px] font-semibold rounded-lg transition-colors text-center">
              <Building2 className="w-4 h-4 shrink-0" />
              Municipio y autoridades
            </Link>
            <Link href={`/empresa/${obra.empresaId}`}
              className="flex items-center justify-center gap-2 px-4 py-3 bg-teal-600 hover:bg-teal-700 text-white text-[13px] font-semibold rounded-lg transition-colors text-center">
              <Truck className="w-4 h-4 shrink-0" />
              Perfil de empresa
            </Link>
          </div>
        </div>
      </div>

      <div className="mt-6">
        <Disclaimer />
      </div>
    </div>
  )
}
