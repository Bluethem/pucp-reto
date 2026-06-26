import type { ScoreIndicador, RiskLevel } from '@/types'
import RiskMeter from '@/components/shared/RiskMeter'

interface ScoreExplainerProps {
  score: RiskLevel
  indicadores: ScoreIndicador[]
}

const SEG_COLOR: Record<number, string> = {
  1: '#16a34a', 2: '#4ade80', 3: '#ca8a04', 4: '#f97316', 5: '#dc2626',
}

export default function ScoreExplainer({ score, indicadores }: ScoreExplainerProps) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
      <h3 className="text-sm font-semibold text-navy-800 mb-3">
        Desglose del score de riesgo
      </h3>

      <RiskMeter score={score} size="md" />

      <div className="mt-4 space-y-3">
        {indicadores.map(ind => (
          <div key={ind.nombre} className="flex gap-3 items-start">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold shrink-0"
              style={{ backgroundColor: SEG_COLOR[ind.valor] ?? '#6b7280' }}
            >
              {ind.valor}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-baseline gap-2">
                <span className="text-sm font-medium text-gray-800">{ind.nombre}</span>
                <span className="text-xs text-gray-400">peso {(ind.peso * 100).toFixed(0)}%</span>
              </div>
              <p className="text-xs text-gray-500 mt-0.5">{ind.descripcion}</p>
            </div>
          </div>
        ))}
      </div>

      <p className="mt-3 text-xs text-gray-400">
        Score global = promedio ponderado de indicadores. Motor determinista y trazable.
      </p>
    </div>
  )
}
