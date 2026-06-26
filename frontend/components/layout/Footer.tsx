import Link from 'next/link'
import Image from 'next/image'

export default function Footer() {
  return (
    <footer className="bg-navy-800 text-white mt-auto">
      <div className="h-[3px] bg-gradient-to-r from-navy-800 via-teal-500 to-teal-400" />

      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">

          {/* Brand */}
          <div>
            <div className="mb-4 overflow-hidden" style={{ width: 48, height: 48 }}>
              <Image
                src="/assets/glass.png"
                alt="glass"
                width={72}
                height={72}
                style={{ width: 72, height: 'auto', transform: 'scale(1.35)', transformOrigin: 'center' }}
              />
            </div>
            <p className="text-[13px] font-light text-gray-400 leading-relaxed">
              Sistema de transparencia y detección de señales de riesgo en obras
              públicas del Estado Peruano. Herramienta de vigilancia ciudadana.
            </p>
          </div>

          {/* Fuentes */}
          <div>
            <h4 className="text-[10px] font-semibold uppercase tracking-widest text-teal-400 mb-4">
              Fuentes de datos
            </h4>
            <ul className="space-y-2 text-[13px] font-light text-gray-400">
              {[
                'INFOBRAS — MEF',
                'SEACE — OSCE',
                'Índices de precios — INEI',
                'Valores Unitarios — MVCS',
                'Autoridades — JNE',
                'RUC — SUNAT',
              ].map(f => <li key={f}>{f}</li>)}
            </ul>
          </div>

          {/* Descargo */}
          <div>
            <h4 className="text-[10px] font-semibold uppercase tracking-widest text-teal-400 mb-4">
              Descargo de responsabilidad
            </h4>
            <p className="text-[12px] font-light text-gray-400 leading-relaxed">
              Los indicadores mostrados son{' '}
              <span className="font-semibold text-gray-300">señales de riesgo</span>{' '}
              para la vigilancia ciudadana y no constituyen determinaciones legales
              de culpabilidad. Toda la información proviene de fuentes públicas oficiales.
            </p>
            <p className="text-[11px] font-light text-gray-600 mt-3">
              Proyecto universitario — PUCP 2025
            </p>
          </div>
        </div>

        <div className="border-t border-navy-700 mt-10 pt-6 flex flex-col md:flex-row items-center justify-between gap-3">
          <span className="text-[11px] font-light text-gray-500">
            © 2025 glass — Vigilancia ciudadana de obras públicas
          </span>
          <div className="flex gap-5 text-[11px] font-light text-gray-500">
            <Link href="/acerca" className="hover:text-teal-400 transition-colors">Acerca del sistema</Link>
            <span>Datos públicos bajo licencia abierta</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
