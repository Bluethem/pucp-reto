import { notFound } from 'next/navigation'
import Link from 'next/link'
import {
  ArrowLeft, MapPin, Calendar, Building2, Truck,
  ExternalLink, Layers, AlertTriangle
} from 'lucide-react'
import { getObraById } from '@/lib/mock-data'
import RiskBadge from '@/components/shared/RiskBadge'
import Disclaimer from '@/components/shared/Disclaimer'
import PartidaTable from '@/components/obra/PartidaTable'
import ScoreExplainer from '@/components/obra/ScoreExplainer'
import { formatCurrency } from '@/lib/utils'

interface Props {
  params: Promise<{ id: string }>
}

const ESTADO_STYLE: Record<string, string> = {
  'En ejecución': 'bg-blue-100 text-blue-700',
  'Concluida':    'bg-green-100 text-green-700',
  'Paralizada':   'bg-red-100 text-red-700',
  'Por ejecutar': 'bg-gray-100 text-gray-500',
}

export default async function ObraDetailPage({ params }: Props) {
  const { id } = await params
  const obra = getObraById(id)
  if (!obra) notFound()

  const alertaPartidas = obra.partidas.filter(p => p.ratio > 1.3)

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">

      {/* Back */}
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-[12px] font-light text-gray-400 hover:text-navy-800 mb-6 transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Volver al mapa
      </Link>

      {/* Header card */}
      <div className="bg-white border border-gray-200 rounded-2xl p-6 mb-5 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-start gap-5 justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap gap-2 mb-3">
              <span className={`text-[11px] px-2.5 py-1 rounded-full font-semibold ${ESTADO_STYLE[obra.estado]}`}>
                {obra.estado}
              </span>
              <span className="text-[11px] px-2.5 py-1 rounded-full font-medium bg-gray-100 text-gray-500">
                {obra.tipo}
              </span>
            </div>
            <h1 className="text-2xl font-bold text-navy-800 leading-snug mb-4">
              {obra.titulo}
            </h1>
            <div className="flex flex-wrap gap-5 text-[13px] font-light text-gray-400">
              <span className="flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-teal-500" />
                {obra.region}, {obra.departamento}
              </span>
              <span className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-teal-500" />
                {obra.fechaInicio} — {obra.fechaFin}
              </span>
            </div>
          </div>

          {/* Score box */}
          <div className="shrink-0 bg-gray-50 border border-gray-200 rounded-2xl p-5 text-center min-w-[148px]">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-2">
              Score de riesgo
            </p>
            <div className="text-5xl font-extrabold text-navy-800 leading-none mb-1">
              {obra.score}
              <span className="text-lg font-light text-gray-400">/5</span>
            </div>
            <div className="mt-2">
              <RiskBadge score={obra.score} size="sm" />
            </div>
          </div>
        </div>

        {/* Meta grid */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 pt-5 border-t border-gray-100">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-1">
              Presupuesto total
            </p>
            <p className="text-[15px] font-bold text-navy-800">{formatCurrency(obra.presupuestoTotal)}</p>
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-1">
              Municipio / Entidad
            </p>
            <Link href={`/municipio/${obra.municipioId}`}
              className="text-[13px] font-semibold text-teal-600 hover:underline block">
              {obra.municipioNombre}
            </Link>
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-1">
              Empresa contratista
            </p>
            <Link href={`/empresa/${obra.empresaId}`}
              className="text-[13px] font-semibold text-teal-600 hover:underline block">
              {obra.empresaNombre}
            </Link>
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-1">
              Modo de análisis
            </p>
            <p className="text-[13px] font-medium text-gray-700">
              {obra.modoAnalisis === 'partidas' ? 'Por partidas' : 'Fallback por m²'}
            </p>
          </div>
        </div>

        {/* External links */}
        <div className="mt-4 flex gap-4">
          {obra.infobrasUrl && (
            <a href={obra.infobrasUrl} target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-[11px] font-medium text-gray-400 hover:text-navy-800 transition-colors">
              <ExternalLink className="w-3 h-3" /> INFOBRAS
            </a>
          )}
          {obra.seaceUrl && (
            <a href={obra.seaceUrl} target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-[11px] font-medium text-gray-400 hover:text-navy-800 transition-colors">
              <ExternalLink className="w-3 h-3" /> SEACE
            </a>
          )}
        </div>
      </div>

      {/* Alert banner */}
      {alertaPartidas.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-5 flex gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-[13px] font-bold text-red-800">
              {alertaPartidas.length} partida{alertaPartidas.length > 1 ? 's' : ''} con sobreprecio detectada{alertaPartidas.length > 1 ? 's' : ''}
            </p>
            <p className="text-[12px] font-light text-red-600 mt-0.5">
              {alertaPartidas.map(p => p.insumo).join(', ')}
            </p>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-3 gap-5">
        {/* Partidas */}
        <div className="md:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <Layers className="w-4 h-4 text-teal-600" />
            <h2 className="text-[15px] font-bold text-navy-800">Partidas e insumos</h2>
          </div>
          <PartidaTable partidas={obra.partidas} modoAnalisis={obra.modoAnalisis} />
        </div>

        {/* Score + links */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Building2 className="w-4 h-4 text-teal-600" />
            <h2 className="text-[15px] font-bold text-navy-800">Score explicado</h2>
          </div>
          <ScoreExplainer score={obra.score} indicadores={obra.scoreDetalle} />

          <div className="mt-4 space-y-2">
            <Link href={`/municipio/${obra.municipioId}`}
              className="flex items-center gap-2 w-full px-4 py-3 bg-navy-800 hover:bg-navy-700 text-white text-[13px] font-semibold rounded-xl transition-colors">
              <Building2 className="w-4 h-4" />
              Municipio y autoridades
            </Link>
            <Link href={`/empresa/${obra.empresaId}`}
              className="flex items-center gap-2 w-full px-4 py-3 bg-teal-600 hover:bg-teal-700 text-white text-[13px] font-semibold rounded-xl transition-colors">
              <Truck className="w-4 h-4" />
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
