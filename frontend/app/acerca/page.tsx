import { Database, Scale, Users } from 'lucide-react'
import Image from 'next/image'
import Disclaimer from '@/components/shared/Disclaimer'

export default function AcercaPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <div className="overflow-hidden rounded-2xl mx-auto mb-5" style={{ width: 64, height: 64 }}>
          <Image
            src="/assets/glass.png"
            alt="glass"
            width={96}
            height={96}
            style={{ width: 96, height: 'auto', transform: 'scale(1.35)', transformOrigin: 'center' }}
          />
        </div>
        <p className="text-[11px] font-semibold uppercase tracking-widest text-teal-600 mb-2">
          Sistema de transparencia
        </p>
        <h1 className="text-4xl font-extrabold text-navy-800 tracking-tight">
          glass
        </h1>
        <p className="text-[14px] font-light text-gray-400 mt-3 max-w-sm mx-auto leading-relaxed">
          Detección de sobreprecios y transparencia en obras públicas del Estado Peruano
        </p>
      </div>

      <div className="space-y-5">
        <div className="bg-white border border-gray-200 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-9 h-9 rounded-xl bg-teal-50 flex items-center justify-center">
              <Database className="w-4 h-4 text-teal-600" />
            </div>
            <h2 className="text-[16px] font-bold text-navy-800">Que hace el sistema</h2>
          </div>
          <p className="text-[13px] font-light text-gray-500 leading-relaxed">
            El sistema cruza automáticamente los precios declarados en expedientes técnicos de
            obras públicas (fuente: INFOBRAS / MEF) contra los precios de referencia oficiales
            (INEI – Índices Unificados de Precios de la Construcción; MVCS – Valores Unitarios
            Oficiales). El resultado es un{' '}
            <span className="font-semibold text-navy-800">score de riesgo 1–5</span> por obra, con
            desglose completo de cada indicador.
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-9 h-9 rounded-xl bg-teal-50 flex items-center justify-center">
              <Scale className="w-4 h-4 text-teal-600" />
            </div>
            <h2 className="text-[16px] font-bold text-navy-800">Motor de scoring</h2>
          </div>
          <ol className="space-y-2.5">
            {[
              'Se ingestán las partidas del expediente (insumo, unidad, cantidad, precio declarado).',
              'Se empareja cada insumo con el precio de referencia INEI correspondiente.',
              'Se calcula el ratio = precio_declarado / precio_referencia por partida.',
              'El score global (1–5) se genera por promedio ponderado de ratios y otros indicadores de riesgo del contrato.',
              'El cálculo es determinista: cada score puede explicarse al detalle.',
            ].map((step, i) => (
              <li key={i} className="flex gap-3 text-[13px] font-light text-gray-500">
                <span className="font-bold text-teal-600 shrink-0 w-5">{i + 1}.</span>
                {step}
              </li>
            ))}
          </ol>
        </div>

        <div className="bg-white border border-gray-200 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-9 h-9 rounded-xl bg-teal-50 flex items-center justify-center">
              <Users className="w-4 h-4 text-teal-600" />
            </div>
            <h2 className="text-[16px] font-bold text-navy-800">Fuentes de datos</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {[
              ['INFOBRAS', 'Obras y presupuesto — MEF'],
              ['SEACE', 'Contratos y licitaciones — OSCE'],
              ['INEI', 'Precios de referencia primaria'],
              ['MVCS', 'Valores unitarios oficiales por departamento'],
              ['JNE', 'Autoridades y procesos electorales'],
              ['SUNAT', 'RUC, estado y representante legal'],
            ].map(([name, desc]) => (
              <div key={name} className="flex gap-2 text-[13px]">
                <span className="font-bold text-teal-600 shrink-0 w-16">{name}</span>
                <span className="font-light text-gray-500">{desc}</span>
              </div>
            ))}
          </div>
        </div>

        <Disclaimer />

        <p className="text-center text-[11px] font-light text-gray-400">
          Proyecto PUCP 2025 &nbsp;·&nbsp; David Luza &nbsp;·&nbsp; Christopher Albino &nbsp;·&nbsp; Ricco Rashuaman
        </p>
      </div>
    </div>
  )
}
