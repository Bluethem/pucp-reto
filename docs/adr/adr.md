# Architecture Decision Records (ADR)

Este archivo registra las decisiones técnicas significativas del proyecto. Cada ADR documenta el contexto, las opciones consideradas y la justificación de la decisión final.

---

## ADR-001: Extracción de partidas de expediente técnico mediante Gemini API

- **Estado:** Aceptado
- **Fecha:** 2026-06-26
- **Decisión:** Extraer las partidas del expediente técnico (insumo, unidad, cantidad, precio declarado) desde PDFs alojados en INFOBRAS usando Gemini API, complementado con fallback a costo/m² (RF-SCO-08).

### Contexto

El motor de scoring necesita el desglose de partidas (insumo, unidad, cantidad, precio unitario) de cada obra para compararlo contra los precios de referencia del INEI. INFOBRAS no expone esta información en API ni datos estructurados — solo como PDFs subidos por las entidades ejecutoras. Estos PDFs varían en formato, calidad y contenido (algunos son escaneados, otros tienen texto embebido, otros tienen tablas inconsistentes).

### Opciones consideradas

| Opción | Descripción | Pros | Contras |
|---|---|---|---|
| **A) pdfplumber** | Extraer tablas de PDFs con texto embebido usando la librería pdfplumber (Python) | Gratuito, determinista | No funciona en PDFs escaneados; frágil ante formatos inconsistentes; requiere ~4-6h de implementación y ajuste por municipio |
| **B) Gemini API** | Enviar PDF a Gemini y recibir JSON estructurado de las partidas | Maneja PDFs escaneados y con texto; entiende contexto; tolera formatos variables; ~3-4h de implementación | No determinista (puede variar entre llamadas); puede alucinar datos; costo por API call; latencia |
| **C) Hardcodear demo** | Preparar manualmente 2-3 obras para la demo y no implementar extracción automatizada | Rápido (~1h), 100% confiable para demo | No escalable; el producto no resuelve el problema real fuera de la demo |
| **D) Solo fallback costo/m²** | Usar solo RF-SCO-08 como scoring, sin extraer partidas | Determinista, implementación rápida (~2h) | Pérdida de granularidad; la propuesta de valor central (comparación por insumo) no se cumple |

### Decisión

Se elige la **Opción B (Gemini API)** como método primario de extracción, con la **Opción D (fallback costo/m²)** como respaldo automático cuando:
- El PDF del expediente técnico no está disponible o no es accesible
- Gemini no puede extraer las partidas de forma confiable
- El consumo de API excede el presupuesto del torneo

### Consecuencias

- **Positivas:** Podemos procesar tanto PDFs con texto como escaneados; el formato variable entre municipalidades no es un problema para Gemini.
- **Negativas:** El pipeline no es determinista — dos ejecuciones sobre el mismo PDF pueden dar resultados ligeramente distintos. Hay que implementar un paso de validación (rangos esperados por insumo) y logging de la respuesta cruda.
- **Costo:** El plan Free de Gemini tiene límites. Para el MVP (~10-20 obras) es suficiente. Para producción se necesitaría plan pago.
- **Trazabilidad:** La respuesta cruda de Gemini se almacena en BD junto con las partidas extraídas y la fecha/hora, para auditoría y reprocesamiento.

### Referencias

- RF-SCO-01, RF-SCO-08
- INFOBRAS (MEF) — Portal de consulta pública
- Documentación Gemini API: https://ai.google.dev/gemini-api/docs

---

## ADR-002: Estrategia de consumo de fuentes (INEI + SEACE + Gemini)

- **Estado:** Aceptado
- **Fecha:** 2026-06-26
- **Decisión:** Usar INEI como fuente única de precios de referencia, SEACE/OCDS como fuente de metadatos de obra y contratista, y Gemini para extracción de partidas de expediente técnico desde PDFs de INFOBRAS.

### Contexto

El sistema cruza tres tipos de datos: precios declarados (expediente), precios de referencia (oficiales) y metadatos de la obra. Cada tipo tiene una fuente óptima diferente.

### Decisiones por fuente

| Fuente | Dato que provee | Formato | Estrategia de ingesta |
|---|---|---|---|
| **INEI** — Índices Unificados de Precios de la Construcción | Precios de referencia por insumo con código estandarizado | .xlsx mensual | ETL programado: descargar → parsear → cargar a PostgreSQL. Actualización mensual. |
| **Ministerio de Vivienda** — Valores Unitarios Oficiales | Ajuste regional de precios de referencia por departamento | .xlsx periódico | Fallback regional para RF-SCO-07. Misma estrategia ETL. |
| **SEACE / OCDS** — Contrataciones Abiertas (OECE) | Metadatos de obra (entidad, contratista, monto total, fechas, ubicación, estado) y perfil del contratista (historial, RUC) | JSON (API REST, estándar OCDS) | Cliente HTTP con caché. Consulta por RUC o por entidad. Cachear respuestas para evitar límites de rate. |
| **INFOBRAS** (vía Gemini) | Partidas del expediente técnico (insumo, unidad, cantidad, precio declarado) | PDF → JSON vía Gemini | Pipeline de extracción: descargar PDF → enviar a Gemini → validar respuesta → almacenar partidas en BD. |
| **JNE** — Infogob | Autoridades (alcaldes, regidores, partido, período) | Web scraping / dataset CSV | Dataset de datos abiertos JNE (actualizado periódicamente) + scraping de refuerzo. |
| **SUNAT** — Consulta RUC | Datos de empresa (RUC, razón social, estado, representante legal) | HTML público / API no oficial | Scraping controlado con caché agresiva. |
| **Poder Judicial / IDEH** | Denuncias y procesos judiciales | Web pública | Scraping exploratorio (Could). |

### Consecuencias

- **Capa de abstracción:** Se implementa `DataSource` interface para que el motor de scoring no dependa directamente de ninguna fuente (RNF-19). Cada fuente implementa: `fetch(url)`, `getMetadata()`, `getLastUpdate()`.
- **Caché:** Todas las fuentes externas pasan por una capa de caché (TTL configurable por fuente) para no agotar créditos y soportar caídas (RNF-05).
- **Modo offline:** Si una fuente falla, la app usa el último dato cacheado e indica la fecha de actualización (RNF-06).

### Referencias

- RNF-05, RNF-06, RNF-19
- SEACE OCDS: https://contratacionesabiertas.oece.gob.pe/
- Datos Abiertos JNE: https://www.datosabiertos.gob.pe/
- Portal MEF Datos Abiertos: https://datosabiertos.mef.gob.pe/
