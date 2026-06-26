import { notFound } from 'next/navigation'
import Link from 'next/link'
import {
  ArrowLeft, Building2, AlertTriangle, TrendingUp, CheckCircle2, XCircle
} from 'lucide-react'
import { getEmpresaById, getObrasByEmpresa } from '@/lib/mock-data'
import RiskBadge from '@/components/shared/RiskBadge'
import ScoreExplainer from '@/components/obra/ScoreExplainer'
import Disclaimer from '@/components/shared/Disclaimer'
import SourceTag from '@/components/shared/SourceTag'
import { formatCurrency } from '@/lib/utils'
import type { RiskLevel } from '@/types'

interface Props {
  params: Promise<{ id: string }>
}

export default async function EmpresaPage({ params }: Props) {
  const { id } = await params
  const empresa = getEmpresaById(id)
  if (!empresa) notFound()

  const obras = getObrasByEmpresa(empresa.id)
  const tasaCompletado = empresa.obrasAdjudicadas > 0
    ? Math.round((empresa.obrasCompletadas / empresa.obrasAdjudicadas) * 100)
    : 0

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
          <div className="w-14 h-14 rounded-xl bg-teal-50 border border-teal-200 flex items-center justify-center shrink-0">
            <Building2 className="w-7 h-7 text-teal-600" />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-xl md:text-2xl font-bold text-navy-800 leading-tight">
              {empresa.razonSocial}
            </h1>
            <div className="flex flex-wrap gap-3 mt-1.5 text-sm text-gray-500">
              <span>RUC: <strong className="text-gray-700">{empresa.ruc}</strong></span>
              <span>·</span>
              <span>Rep. legal: <strong className="text-gray-700">{empresa.representanteLegal}</strong></span>
            </div>
            <div className="mt-2 flex items-center gap-2">
              <span
                className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  empresa.estadoSunat === 'ACTIVO'
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-700'
                }`}
              >
                SUNAT: {empresa.estadoSunat}
              </span>
              <SourceTag source="SUNAT" />
            </div>
          </div>
          <div className="shrink-0 text-right">
            <p className="text-xs text-gray-400 mb-1">Score de confiabilidad</p>
            <RiskBadge score={empresa.score} size="md" />
          </div>
        </div>

        {/* KPI grid */}
        <div className="mt-5 grid grid-cols-2 md:grid-cols-4 gap-3 pt-5 border-t border-gray-100">
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wide">Obras adjudicadas</p>
            <p className="text-xl font-bold text-navy-800">{empresa.obrasAdjudicadas}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wide">Tasa completado</p>
            <p className={`text-xl font-bold ${tasaCompletado >= 80 ? 'text-green-600' : 'text-red-600'}`}>
              {tasaCompletado}%
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wide">Monto total adjudicado</p>
            <p className="text-base font-bold text-navy-800">{formatCurrency(empresa.montoTotalAdjudicado)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wide">Municipios con contrato</p>
            <p className="text-xl font-bold text-navy-800">{empresa.municipiosConContrato.length}</p>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {empresa.alertas.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-5">
          <h2 className="text-sm font-semibold text-amber-800 flex items-center gap-2 mb-3">
            <AlertTriangle className="w-4 h-4" /> Alertas detectadas
          </h2>
          <ul className="space-y-2">
            {empresa.alertas.map((alerta, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-amber-700">
                <AlertTriangle className="w-3.5 h-3.5 mt-0.5 shrink-0 text-amber-500" />
                {alerta}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid md:grid-cols-3 gap-5">
        {/* Obras contratadas */}
        <div className="md:col-span-2">
          <h2 className="text-base font-semibold text-navy-800 mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-teal-600" />
            Obras adjudicadas en el sistema
          </h2>
          <div className="space-y-3">
            {obras.length === 0 && (
              <p className="text-sm text-gray-400">Sin obras en el sistema actual.</p>
            )}
            {obras.map(obra => (
              <Link key={obra.id} href={`/obra/${obra.id}`}>
                <div className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow cursor-pointer">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-navy-800 line-clamp-2 leading-snug">
                        {obra.titulo}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {obra.region} · {obra.tipo} · {obra.estado}
                      </p>
                    </div>
                    <div className="shrink-0 text-right">
                      <RiskBadge score={obra.score as RiskLevel} size="sm" showLabel={false} />
                      <p className="text-xs text-gray-400 mt-1">{formatCurrency(obra.presupuestoTotal)}</p>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* Completado bar */}
          <div className="mt-4 bg-white border border-gray-200 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-navy-800 mb-3 flex items-center gap-2">
              Ejecución de obras
            </h3>
            <div className="flex items-center gap-3 mb-2">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <div className="flex-1">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Completadas</span>
                  <span>{empresa.obrasCompletadas} / {empresa.obrasAdjudicadas}</span>
                </div>
                <div className="h-2 rounded-full bg-gray-100 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-green-500 transition-all"
                    style={{ width: `${tasaCompletado}%` }}
                  />
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <XCircle className="w-4 h-4 text-red-400" />
              <div className="flex-1">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Incompletas / paralizadas</span>
                  <span>{empresa.obrasAdjudicadas - empresa.obrasCompletadas}</span>
                </div>
                <div className="h-2 rounded-full bg-gray-100 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-red-400 transition-all"
                    style={{ width: `${100 - tasaCompletado}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Score explainer */}
        <div>
          <h2 className="text-base font-semibold text-navy-800 mb-3 flex items-center gap-2">
            <Building2 className="w-4 h-4 text-teal-600" />
            Score explicado
          </h2>
          <ScoreExplainer score={empresa.score} indicadores={empresa.scoreDetalle} />
        </div>
      </div>

      <div className="mt-6">
        <Disclaimer />
      </div>
    </div>
  )
}
