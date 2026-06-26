export type RiskLevel = number // 0–100

export type RiskColor = 'green' | 'yellow' | 'red'

export interface Partida {
  id: string
  insumo: string
  unidad: string
  cantidad: number
  precioDeclarado: number
  precioReferencia: number | null
  ratio: number | null
  fuente: string
}

export interface Obra {
  id: string
  titulo: string
  tipo: string
  estado: string
  region: string
  departamento: string
  lat: number
  lng: number
  presupuestoTotal: number
  score: RiskLevel
  municipioId: string
  municipioNombre: string
  empresaId: string
  empresaNombre: string
  partidas: Partida[]
  scoreDetalle: ScoreIndicador[]
  fechaInicio: string
  fechaFin: string
  infobrasUrl?: string
  seaceUrl?: string
  expedientePdfUrl?: string
  modoAnalisis: 'partidas' | 'fallback_m2'
}

export interface ScoreIndicador {
  nombre: string
  valor: number
  peso: number
  descripcion: string
}

export interface Autoridad {
  id: string
  nombre: string
  cargo: 'Alcalde' | 'Regidor'
  partido: string
  periodo: string
  foto?: string
  dni: string
  municipioId: string
  procesos: Proceso[]
  obrasGestionIds: string[]
}

export interface Proceso {
  id: string
  tipo: string
  estado: string
  fecha: string
  fuente: string
  descripcion: string
}

export interface Municipio {
  id: string
  nombre: string
  region: string
  departamento: string
  alcaldeId?: string
  regidoresIds?: string[]
  obrasIds?: string[]
  scoreAgregado: RiskLevel
}

export interface Empresa {
  id: string
  razonSocial: string
  ruc: string
  representanteLegal: string
  estadoSunat: string
  score: RiskLevel
  scoreDetalle: ScoreIndicador[]
  obrasAdjudicadas: number
  obrasCompletadas: number
  montoTotalAdjudicado: number
  municipiosConContrato: string[]
  alertas: string[]
  obrasIds: string[]
}

export interface MapFilters {
  region: string
  tipo: string
  estado: string
  riesgo: string
}
