const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  const json = await res.json()
  if (!res.ok) throw new ApiError(res.status, json?.error?.message || `Error ${res.status}`)
  return json.data as T
}

function mapObra(b: any): import('@/types').Obra {
  return {
    id: b.id,
    titulo: b.titulo,
    tipo: b.tipo_obra,
    estado: b.estado,
    region: b.departamento,
    departamento: b.departamento,
    lat: 0, lng: 0,
    presupuestoTotal: b.presupuesto_total,
    score: b.score_riesgo ?? 0,
    municipioId: b.entidad_id ?? '',
    municipioNombre: '',
    empresaId: b.contratista_id ?? '',
    empresaNombre: '',
    partidas: [],
    scoreDetalle: [],
    fechaInicio: '',
    fechaFin: '',
    modoAnalisis: b.modo_analisis ?? 'fallback_m2',
  }
}

function mapObraDetalle(b: any, scoreData?: any): import('@/types').Obra {
  const obra = mapObra(b)
  if (scoreData) {
    obra.score = scoreData.score ?? obra.score
    obra.partidas = (scoreData.partidas ?? []).map((p: any) => ({
      id: '',
      insumo: p.insumo,
      unidad: p.unidad,
      cantidad: p.cantidad,
      precioDeclarado: p.precio_declarado,
      precioReferencia: p.precio_referencia,
      ratio: p.ratio,
      fuente: p.fuente,
    }))
    obra.scoreDetalle = []
    if (scoreData.alertas !== undefined) {
      obra.scoreDetalle.push({
        nombre: 'Alertas detectadas',
        valor: scoreData.alertas,
        peso: 1,
        descripcion: `Partidas con ratio ≥ 1.3: ${scoreData.alertas} de ${scoreData.total_partidas}`,
      })
    }
    obra.modoAnalisis = scoreData.modo_analisis ?? obra.modoAnalisis
  }
  return obra
}

function mapEntidad(b: any): import('@/types').Municipio {
  return {
    id: b.id,
    nombre: b.nombre,
    region: b.departamento ?? '',
    departamento: b.departamento ?? '',
    scoreAgregado: 0,
  }
}

function mapContratista(b: any): import('@/types').Empresa {
  return {
    id: b.id,
    razonSocial: b.razon_social,
    ruc: b.ruc,
    representanteLegal: b.representante_legal ?? '',
    estadoSunat: b.estado_sunat ?? '',
    score: b.score_confiabilidad ?? 0,
    obrasAdjudicadas: b.total_obras ?? 0,
    obrasCompletadas: 0,
    montoTotalAdjudicado: 0,
    municipiosConContrato: [],
    alertas: [],
    scoreDetalle: [],
    obrasIds: [],
  }
}

function mapAutoridad(b: any): import('@/types').Autoridad {
  return {
    id: b.id,
    nombre: b.nombre,
    cargo: (b.cargo ?? 'otro') as 'Alcalde' | 'Regidor',
    partido: b.partido ?? '',
    periodo: `${b.periodo_inicio ?? ''}–${b.periodo_fin ?? ''}`,
    dni: '',
    municipioId: b.entidad_id ?? '',
    procesos: [],
    obrasGestionIds: [],
  }
}

export const api = {
  obras: {
    listar: async (params?: Record<string, string>) => {
      const qs = params ? '?' + new URLSearchParams(params).toString() : ''
      const data = await request<any[]>(`/obras${qs}`)
      return data.map(mapObra)
    },
    obtener: async (id: string) => {
      const obra = await request<any>(`/obras/${id}`)
      let score
      try { score = await request<any>(`/obras/${id}/score`) } catch {}
      return mapObraDetalle(obra, score)
    },
    score: async (id: string) => {
      const data = await request<any>(`/obras/${id}/score`)
      return {
        score: data.score,
        clasificacion: data.clasificacion,
        partidas: (data.partidas ?? []).map((p: any) => ({
          id: '', insumo: p.insumo, unidad: p.unidad,
          cantidad: p.cantidad, precioDeclarado: p.precio_declarado,
          precioReferencia: p.precio_referencia, ratio: p.ratio, fuente: p.fuente,
        })),
      }
    },
  },
  municipios: {
    listar: async () => {
      const data = await request<any[]>('/municipios')
      return data.map(mapEntidad)
    },
    obtener: async (id: string) => {
      const data = await request<any>(`/municipios/${id}`)
      const municipio = mapEntidad(data)
      return municipio
    },
    obras: async (id: string) => {
      const data = await request<any[]>(`/municipios/${id}/obras`)
      return data.map(mapObra)
    },
  },
  empresas: {
    listar: async () => {
      const data = await request<any[]>('/empresas')
      return data.map(mapContratista)
    },
    obtener: async (id: string) => {
      const data = await request<any>(`/empresas/${id}`)
      return mapContratista(data)
    },
    obras: async (id: string) => {
      const data = await request<any[]>(`/empresas/${id}/obras`)
      return data.map(mapObra)
    },
  },
  autoridades: {
    listar: async () => {
      const data = await request<any[]>('/autoridades')
      return data.map(mapAutoridad)
    },
    obtener: async (id: string) => {
      const data = await request<any>(`/autoridades/${id}`)
      return mapAutoridad(data)
    },
  },
}
