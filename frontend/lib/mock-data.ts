import type { Obra, Municipio, Empresa, Autoridad } from '@/types'

export const OBRAS: Obra[] = [
  {
    id: 'obra-001',
    titulo: 'Mejoramiento de pistas y veredas en Av. Los Álamos',
    tipo: 'Pavimentación',
    estado: 'En ejecución',
    region: 'Lima',
    departamento: 'Lima',
    lat: -12.0464,
    lng: -77.0428,
    presupuestoTotal: 4_850_000,
    score: 5,
    municipioId: 'mun-001',
    municipioNombre: 'Municipalidad de Los Olivos',
    empresaId: 'emp-001',
    empresaNombre: 'Constructora Andes S.A.C.',
    fechaInicio: '2024-03-01',
    fechaFin: '2025-02-28',
    modoAnalisis: 'partidas',
    infobrasUrl: '#',
    seaceUrl: '#',
    expedientePdfUrl: 'https://cdn.www.gob.pe/uploads/document/file/6495857/5669010-expediente-tecnico-obra-rio-viejo-flores-parte3.pdf?v=1718742062',
    partidas: [
      { id: 'p1',  insumo: 'Cemento Portland Tipo I',        unidad: 'BOL', cantidad: 2400,  precioDeclarado: 38.50, precioReferencia: 24.00, ratio: 1.60, fuente: 'INEI' },
      { id: 'p2',  insumo: 'Fierro corrugado 3/8"',          unidad: 'KG',  cantidad: 18000, precioDeclarado:  5.80, precioReferencia:  3.40, ratio: 1.71, fuente: 'INEI' },
      { id: 'p3',  insumo: 'Arena gruesa',                   unidad: 'M3',  cantidad: 320,   precioDeclarado: 95.00, precioReferencia: 55.00, ratio: 1.73, fuente: 'INEI' },
      { id: 'p4',  insumo: 'Piedra chancada 1/2"',           unidad: 'M3',  cantidad: 280,   precioDeclarado:115.00, precioReferencia: 68.00, ratio: 1.69, fuente: 'INEI' },
      { id: 'p5',  insumo: 'Mano de obra operario',          unidad: 'HH',  cantidad: 9600,  precioDeclarado: 21.00, precioReferencia: 19.50, ratio: 1.08, fuente: 'MVCS' },
      { id: 'p6',  insumo: 'Asfalto RC-250',                 unidad: 'GLN', cantidad: 1800,  precioDeclarado: 18.50, precioReferencia: 11.00, ratio: 1.68, fuente: 'INEI' },
      { id: 'p7',  insumo: 'Agua potable',                   unidad: 'M3',  cantidad: 450,   precioDeclarado:  8.00, precioReferencia:  5.20, ratio: 1.54, fuente: 'INEI' },
      { id: 'p8',  insumo: 'Tubería PVC 4" desagüe',         unidad: 'ML',  cantidad: 620,   precioDeclarado: 32.00, precioReferencia: 20.50, ratio: 1.56, fuente: 'INEI' },
      { id: 'p9',  insumo: 'Madera tornillo (encofrado)',     unidad: 'P2',  cantidad: 3200,  precioDeclarado:  5.20, precioReferencia:  3.80, ratio: 1.37, fuente: 'INEI' },
      { id: 'p10', insumo: 'Mano de obra peón',              unidad: 'HH',  cantidad: 14400, precioDeclarado: 16.50, precioReferencia: 15.80, ratio: 1.04, fuente: 'MVCS' },
      { id: 'p11', insumo: 'Pintura de tráfico amarilla',    unidad: 'GLN', cantidad: 85,    precioDeclarado: 62.00, precioReferencia: 38.00, ratio: 1.63, fuente: 'INEI' },
      { id: 'p12', insumo: 'Clavos para madera 3"',          unidad: 'KG',  cantidad: 210,   precioDeclarado:  6.80, precioReferencia:  4.90, ratio: 1.39, fuente: 'INEI' },
      { id: 'p13', insumo: 'Transporte de materiales',       unidad: 'GLB', cantidad: 1,     precioDeclarado:85000,  precioReferencia: 52000, ratio: 1.63, fuente: 'MVCS' },
    ],
    scoreDetalle: [
      { nombre: 'Ratio promedio de insumos', valor: 3.5, peso: 0.6, descripcion: 'Precio promedio declarado 65% sobre referencia INEI' },
      { nombre: 'Postor único', valor: 5, peso: 0.2, descripcion: 'Solo un postor se presentó a la licitación' },
      { nombre: 'Adicionales de obra', valor: 4, peso: 0.2, descripcion: '2 adicionales aprobados que suman 18% del contrato original' },
    ],
  },
  {
    id: 'obra-002',
    titulo: 'Construcción de local comunal en AA.HH. Villa El Salvador Norte',
    tipo: 'Edificación',
    estado: 'Concluida',
    region: 'Lima',
    departamento: 'Lima',
    lat: -12.2121,
    lng: -76.9361,
    presupuestoTotal: 1_200_000,
    score: 2,
    municipioId: 'mun-002',
    municipioNombre: 'Municipalidad de Villa El Salvador',
    empresaId: 'emp-002',
    empresaNombre: 'Obras Civiles del Sur E.I.R.L.',
    fechaInicio: '2023-06-01',
    fechaFin: '2024-01-15',
    modoAnalisis: 'partidas',
    infobrasUrl: '#',
    seaceUrl: '#',
    partidas: [
      { id: 'p1', insumo: 'Cemento Portland Tipo I', unidad: 'BOL', cantidad: 800, precioDeclarado: 25.5, precioReferencia: 24.0, ratio: 1.06, fuente: 'INEI' },
      { id: 'p2', insumo: 'Fierro corrugado 1/2"', unidad: 'KG', cantidad: 5200, precioDeclarado: 3.55, precioReferencia: 3.40, ratio: 1.04, fuente: 'INEI' },
      { id: 'p3', insumo: 'Ladrillo King Kong', unidad: 'MILL', cantidad: 45, precioDeclarado: 890.0, precioReferencia: 850.0, ratio: 1.05, fuente: 'INEI' },
    ],
    scoreDetalle: [
      { nombre: 'Ratio promedio de insumos', valor: 1, peso: 0.6, descripcion: 'Precios declarados dentro del rango de referencia INEI' },
      { nombre: 'Competencia en licitación', valor: 2, peso: 0.2, descripcion: '3 postores se presentaron' },
      { nombre: 'Adicionales de obra', valor: 1, peso: 0.2, descripcion: 'Sin adicionales registrados' },
    ],
  },
  {
    id: 'obra-003',
    titulo: 'Rehabilitación de carretera Ayacucho–Huanta, tramo III',
    tipo: 'Carretera',
    estado: 'Paralizada',
    region: 'Ayacucho',
    departamento: 'Ayacucho',
    lat: -13.1588,
    lng: -74.2236,
    presupuestoTotal: 12_400_000,
    score: 4,
    municipioId: 'mun-003',
    municipioNombre: 'Gobierno Regional de Ayacucho',
    empresaId: 'emp-001',
    empresaNombre: 'Constructora Andes S.A.C.',
    fechaInicio: '2023-01-10',
    fechaFin: '2025-12-31',
    modoAnalisis: 'fallback_m2',
    infobrasUrl: '#',
    seaceUrl: '#',
    partidas: [
      { id: 'p1', insumo: 'Costo total por km (referencia tipo)', unidad: 'KM', cantidad: 12, precioDeclarado: 1_033_333, precioReferencia: 720_000, ratio: 1.44, fuente: 'MVCS' },
    ],
    scoreDetalle: [
      { nombre: 'Ratio costo/km vs referencia', valor: 4, peso: 0.5, descripcion: 'Costo por km 44% sobre referencia MVCS para carreteras de esta categoría' },
      { nombre: 'Obra paralizada', valor: 5, peso: 0.3, descripcion: 'Ejecución detenida por 8 meses sin justificación registrada' },
      { nombre: 'Empresa con historial de sobreprecios', valor: 3, peso: 0.2, descripcion: 'Misma empresa adjudicataria en otras obras con score alto' },
    ],
  },
  {
    id: 'obra-004',
    titulo: 'Instalación de redes de agua potable y alcantarillado – sector 4',
    tipo: 'Saneamiento',
    estado: 'En ejecución',
    region: 'Arequipa',
    departamento: 'Arequipa',
    lat: -16.4090,
    lng: -71.5375,
    presupuestoTotal: 6_750_000,
    score: 3,
    municipioId: 'mun-004',
    municipioNombre: 'Municipalidad Provincial de Arequipa',
    empresaId: 'emp-003',
    empresaNombre: 'Hidrotecnia S.A.',
    fechaInicio: '2024-01-20',
    fechaFin: '2025-07-30',
    modoAnalisis: 'partidas',
    infobrasUrl: '#',
    seaceUrl: '#',
    partidas: [
      { id: 'p1', insumo: 'Tubería PVC DN 200', unidad: 'ML', cantidad: 4800, precioDeclarado: 85.0, precioReferencia: 62.0, ratio: 1.37, fuente: 'INEI' },
      { id: 'p2', insumo: 'Cemento Portland Tipo IP', unidad: 'BOL', cantidad: 1800, precioDeclarado: 28.0, precioReferencia: 25.5, ratio: 1.10, fuente: 'INEI' },
      { id: 'p3', insumo: 'Excavación en terreno normal', unidad: 'M3', cantidad: 9600, precioDeclarado: 12.5, precioReferencia: 10.0, ratio: 1.25, fuente: 'MVCS' },
    ],
    scoreDetalle: [
      { nombre: 'Ratio promedio de insumos', valor: 3, peso: 0.6, descripcion: 'Precios moderadamente elevados respecto a referencia INEI' },
      { nombre: 'Competencia en licitación', valor: 2, peso: 0.2, descripcion: '2 postores presentados' },
      { nombre: 'Adicionales de obra', valor: 3, peso: 0.2, descripcion: '1 adicional aprobado del 8% del contrato' },
    ],
  },
  {
    id: 'obra-005',
    titulo: 'Construcción de mercado municipal de abastos',
    tipo: 'Edificación',
    estado: 'Por ejecutar',
    region: 'Cusco',
    departamento: 'Cusco',
    lat: -13.5319,
    lng: -71.9675,
    presupuestoTotal: 3_900_000,
    score: 4,
    municipioId: 'mun-005',
    municipioNombre: 'Municipalidad Distrital de San Sebastián',
    empresaId: 'emp-001',
    empresaNombre: 'Constructora Andes S.A.C.',
    fechaInicio: '2025-03-01',
    fechaFin: '2026-02-28',
    modoAnalisis: 'partidas',
    infobrasUrl: '#',
    seaceUrl: '#',
    partidas: [
      { id: 'p1', insumo: 'Acero estructural A36', unidad: 'KG', cantidad: 48000, precioDeclarado: 6.20, precioReferencia: 3.80, ratio: 1.63, fuente: 'INEI' },
      { id: 'p2', insumo: 'Cemento Portland Tipo I', unidad: 'BOL', cantidad: 2200, precioDeclarado: 36.0, precioReferencia: 26.5, ratio: 1.36, fuente: 'INEI' },
    ],
    scoreDetalle: [
      { nombre: 'Ratio promedio de insumos', valor: 4, peso: 0.6, descripcion: 'Precios significativamente por encima de referencia INEI' },
      { nombre: 'Postor único', valor: 5, peso: 0.2, descripcion: 'Un único postor en la licitación' },
      { nombre: 'Empresa con historial', valor: 3, peso: 0.2, descripcion: 'Empresa vinculada a obras con sobreprecios en otras regiones' },
    ],
  },
]

export const MUNICIPIOS: Municipio[] = [
  {
    id: 'mun-001',
    nombre: 'Municipalidad de Los Olivos',
    region: 'Lima',
    departamento: 'Lima',
    alcaldeId: 'aut-001',
    regidoresIds: ['aut-002', 'aut-003'],
    obrasIds: ['obra-001'],
    scoreAgregado: 5,
  },
  {
    id: 'mun-002',
    nombre: 'Municipalidad de Villa El Salvador',
    region: 'Lima',
    departamento: 'Lima',
    alcaldeId: 'aut-004',
    regidoresIds: ['aut-005'],
    obrasIds: ['obra-002'],
    scoreAgregado: 2,
  },
  {
    id: 'mun-003',
    nombre: 'Gobierno Regional de Ayacucho',
    region: 'Ayacucho',
    departamento: 'Ayacucho',
    alcaldeId: 'aut-006',
    regidoresIds: [],
    obrasIds: ['obra-003'],
    scoreAgregado: 4,
  },
  {
    id: 'mun-004',
    nombre: 'Municipalidad Provincial de Arequipa',
    region: 'Arequipa',
    departamento: 'Arequipa',
    alcaldeId: 'aut-007',
    regidoresIds: ['aut-008'],
    obrasIds: ['obra-004'],
    scoreAgregado: 3,
  },
  {
    id: 'mun-005',
    nombre: 'Municipalidad Distrital de San Sebastián',
    region: 'Cusco',
    departamento: 'Cusco',
    alcaldeId: 'aut-009',
    regidoresIds: [],
    obrasIds: ['obra-005'],
    scoreAgregado: 4,
  },
]

export const EMPRESAS: Empresa[] = [
  {
    id: 'emp-001',
    razonSocial: 'Constructora Andes S.A.C.',
    ruc: '20512345678',
    representanteLegal: 'Marco Antonio Fuentes Quispe',
    estadoSunat: 'ACTIVO',
    score: 5,
    obrasAdjudicadas: 14,
    obrasCompletadas: 7,
    montoTotalAdjudicado: 38_500_000,
    municipiosConContrato: ['mun-001', 'mun-003', 'mun-005'],
    alertas: [
      'RUC con menos de 3 años al momento de primera adjudicación grande',
      'Adjudica en 3 regiones distintas con el mismo representante legal',
      'Múltiples obras con score de riesgo 4–5',
    ],
    scoreDetalle: [
      { nombre: 'Ratio de sobreprecios histórico', valor: 5, peso: 0.5, descripcion: 'Promedio de ratio de precios en sus obras: 1.62' },
      { nombre: 'Concentración municipal', valor: 4, peso: 0.3, descripcion: 'Reiteradas adjudicaciones con los mismos municipios' },
      { nombre: 'Obras abandonadas', valor: 4, peso: 0.2, descripcion: '3 obras paralizadas sin resolución de contrato' },
    ],
    obrasIds: ['obra-001', 'obra-003', 'obra-005'],
  },
  {
    id: 'emp-002',
    razonSocial: 'Obras Civiles del Sur E.I.R.L.',
    ruc: '20601234567',
    representanteLegal: 'Rosa Elena Mamani Condori',
    estadoSunat: 'ACTIVO',
    score: 1,
    obrasAdjudicadas: 5,
    obrasCompletadas: 5,
    montoTotalAdjudicado: 4_200_000,
    municipiosConContrato: ['mun-002'],
    alertas: [],
    scoreDetalle: [
      { nombre: 'Ratio de sobreprecios histórico', valor: 1, peso: 0.5, descripcion: 'Precios dentro de rangos de referencia en todas sus obras' },
      { nombre: 'Competencia en licitación', valor: 1, peso: 0.3, descripcion: 'Compite habitualmente contra 3+ postores' },
      { nombre: 'Tasa de completado', valor: 1, peso: 0.2, descripcion: '100% de obras concluidas dentro del plazo' },
    ],
    obrasIds: ['obra-002'],
  },
  {
    id: 'emp-003',
    razonSocial: 'Hidrotecnia S.A.',
    ruc: '20400987654',
    representanteLegal: 'Carlos Alberto Vargas Díaz',
    estadoSunat: 'ACTIVO',
    score: 3,
    obrasAdjudicadas: 9,
    obrasCompletadas: 7,
    montoTotalAdjudicado: 22_100_000,
    municipiosConContrato: ['mun-004'],
    alertas: [
      'Un adicional de obra aprobado por encima del 5% en 4 proyectos',
    ],
    scoreDetalle: [
      { nombre: 'Ratio de sobreprecios histórico', valor: 3, peso: 0.5, descripcion: 'Ratio promedio moderado: 1.24' },
      { nombre: 'Adicionales de obra', valor: 3, peso: 0.3, descripcion: 'Patrón recurrente de adicionales del 5–10%' },
      { nombre: 'Tasa de completado', valor: 2, peso: 0.2, descripcion: '78% de obras concluidas' },
    ],
    obrasIds: ['obra-004'],
  },
]

export const AUTORIDADES: Autoridad[] = [
  {
    id: 'aut-001',
    nombre: 'José Luis Ramírez Torres',
    cargo: 'Alcalde',
    partido: 'Fuerza Popular',
    periodo: '2023–2026',
    dni: '08123456',
    municipioId: 'mun-001',
    procesos: [
      {
        id: 'proc-001',
        tipo: 'Proceso penal',
        estado: 'Investigación preliminar',
        fecha: '2024-05-10',
        fuente: 'Poder Judicial',
        descripcion: 'Investigación por presunta colusión en licitación de obras viales',
      },
    ],
    obrasGestionIds: ['obra-001'],
  },
  {
    id: 'aut-004',
    nombre: 'María Fernanda Ccallo Apaza',
    cargo: 'Alcalde',
    partido: 'Juntos por el Perú',
    periodo: '2023–2026',
    dni: '09876543',
    municipioId: 'mun-002',
    procesos: [],
    obrasGestionIds: ['obra-002'],
  },
]

export function getObraById(id: string): Obra | undefined {
  return OBRAS.find(o => o.id === id)
}

export function getMunicipioById(id: string): Municipio | undefined {
  return MUNICIPIOS.find(m => m.id === id)
}

export function getEmpresaById(id: string): Empresa | undefined {
  return EMPRESAS.find(e => e.id === id)
}

export function getAutoridadById(id: string): Autoridad | undefined {
  return AUTORIDADES.find(a => a.id === id)
}

export function getAutoridadesByMunicipio(municipioId: string): Autoridad[] {
  return AUTORIDADES.filter(a => a.municipioId === municipioId)
}

export function getObrasByMunicipio(municipioId: string): Obra[] {
  return OBRAS.filter(o => o.municipioId === municipioId)
}

export function getObrasByEmpresa(empresaId: string): Obra[] {
  return OBRAS.filter(o => o.empresaId === empresaId)
}
