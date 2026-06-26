import { Info } from 'lucide-react'

export default function Disclaimer() {
  return (
    <div className="flex gap-3 bg-blue-50 border border-blue-100 rounded-xl px-4 py-3">
      <Info className="w-4 h-4 mt-0.5 shrink-0 text-blue-400" />
      <p className="text-[12px] font-light text-blue-700 leading-relaxed">
        <span className="font-semibold">Nota:</span> Los indicadores mostrados son{' '}
        <span className="font-semibold">señales de riesgo para la vigilancia ciudadana</span> y no
        constituyen determinaciones legales de culpabilidad. Toda la información
        proviene de fuentes públicas oficiales (INFOBRAS, SEACE, INEI, JNE, SUNAT).
      </p>
    </div>
  )
}
