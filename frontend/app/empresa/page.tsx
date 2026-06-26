export const dynamic = 'force-dynamic'

import Link from 'next/link'
import { Building2, AlertTriangle } from 'lucide-react'
import { api } from '@/lib/api'
import RiskBadge from '@/components/shared/RiskBadge'
import { formatCurrency } from '@/lib/utils'

export default async function EmpresasPage() {
  const empresas = await api.empresas.listar()
  const sorted = [...empresas].sort((a, b) => b.score - a.score)

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-8">
        <p className="text-[11px] font-semibold uppercase tracking-widest text-teal-600 mb-1">
          Base de datos
        </p>
        <h1 className="text-3xl font-extrabold text-navy-800">Empresas contratistas</h1>
        <p className="text-[13px] font-light text-gray-400 mt-1">
          Perfil de confiabilidad basado en historial de adjudicaciones y sobreprecios.
        </p>
      </div>

      <div className="space-y-3">
        {sorted.map(empresa => (
          <Link key={empresa.id} href={`/empresa/${empresa.id}`}>
            <div className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <p className="text-[15px] font-bold text-navy-800">{empresa.razonSocial}</p>
                  <div className="flex flex-wrap gap-3 mt-1.5 text-[12px] font-light text-gray-400">
                    <span>RUC {empresa.ruc}</span>
                    <span>·</span>
                    <span>{empresa.obrasAdjudicadas} obras adjudicadas</span>
                  </div>
                  {empresa.alertas.length > 0 && (
                    <div className="mt-2 flex items-center gap-1.5 text-[11px] font-medium text-amber-600">
                      <AlertTriangle className="w-3 h-3" />
                      {empresa.alertas.length} alerta{empresa.alertas.length > 1 ? 's' : ''} detectada{empresa.alertas.length > 1 ? 's' : ''}
                    </div>
                  )}
                </div>
                <RiskBadge score={empresa.score} size="md" />
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
