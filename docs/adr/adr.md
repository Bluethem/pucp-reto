# Actividad: Decisiones de Diseño

## Contexto

El diseño de software es, en esencia, un **proceso de toma de decisiones**. Cada elección —desde el lenguaje de programación hasta la forma en que se sincronizan dos servicios— condiciona los atributos de calidad del sistema, su evolución a futuro y el esfuerzo que demandará al equipo de desarrollo. Sin embargo, estas decisiones suelen perderse en la memoria del equipo: se toman en una reunión, se implementan, y meses (o años) después nadie recuerda **por qué** se eligió una alternativa sobre otra.

Documentar las decisiones de diseño tiene dos propósitos centrales:

1. **Hacer explícito el razonamiento** detrás de cada elección, de modo que el equipo (presente y futuro) pueda entender el contexto, las restricciones y los trade-offs considerados.
2. **Facilitar la evolución del sistema**, ya que cuando aparezcan nuevos requisitos o restricciones, se podrá revisitarla decisión con conocimiento de causa, en lugar de partir de cero.

En esta actividad trabajaremos con dos elementos: las **categorías de decisiones de diseño** que propone Bass et al. en su libro *Software Architecture in Practice* (2021) y la **plantilla de Architecture Decision Record (ADR)** tomando como referencia a Richards y Ford (2020).

---

## Tabla resumen

| ID | Título | Categoría | Estado |
|---|---|---|---|
| ADR-001 | Gemini API para extracción de partidas desde PDFs de expedientes técnicos | Elección de Tecnología | Aceptado |
| ADR-002 | Ingesta programada de fuentes externas mediante ETL batch | Modelo de Coordinación | Aceptado |
| ADR-003 | Stack tecnológico: Next.js + FastAPI + PostgreSQL/PostGIS | Elección de Tecnología | Aceptado |
| ADR-004 | Abstracción de fuentes externas mediante DataSource Interface | Asignación de Responsabilidades | Aceptado |
| ADR-005 | Scores de riesgo precomputados en pipeline ETL vs cálculo en tiempo real | Modelo de Coordinación | Aceptado |
| ADR-006 | PostgreSQL con PostGIS como motor de base de datos | Modelo de Datos | Aceptado |
| ADR-007 | Caché con TTL y degradación elegante para fuentes externas | Gestión de Recursos | Aceptado |
| ADR-008 | Monorepo con frontend y backend en un solo repositorio | Mapeo entre Elementos Arquitectónicos | Aceptado |
| ADR-009 | Configuración y credenciales resueltas en tiempo de ejecución | Tiempo de Enlace | Aceptado |
| ADR-010 | Modelo de usuarios tipo YouTube (acceso público sin login) | Asignación de Responsabilidades | Aceptado |

---

## ADR-001 — Gemini API para extracción de partidas desde PDFs de expedientes técnicos

**Categoría:** Elección de Tecnología

**Contexto:**
El motor de scoring (RF-SCO-01) necesita el desglose de partidas de cada obra —insumo, unidad, cantidad, precio unitario declarado— para compararlo contra los precios de referencia del INEI. Se confirmó mediante el spike técnico que INFOBRAS **no expone esta información en API ni datos estructurados**: los expedientes técnicos solo están disponibles como PDFs subidos por las entidades ejecutoras. Estos PDFs varían drásticamente en formato, calidad y contenido: algunos tienen texto embebido, otros son escaneados (imagen sin texto), y el formato de las tablas de partidas es inconsistente entre municipalidades. El equipo tiene ~11h de desarrollo total y no puede dedicar más de 3-4h a resolver este problema.

**Alternativas:**
1. **pdfplumber (Python).**
   - Biblioteca de código abierto para extraer tablas de PDFs con texto embebido.
   - Gratuito, determinista, bien documentado.
   - **Limitación:** solo funciona en PDFs con texto seleccionable. No puede procesar PDFs escaneados (que son una proporción significativa). Requiere ajuste por cada formato de tabla distinto; la experiencia con proyectos similares muestra que se necesitan 4-6h para lograr una tasa de éxito aceptable (>70%).
2. **Gemini API (Google).**
   - Modelo de IA multimodal que puede leer PDFs (con texto y escaneados) y extraer tablas a JSON estructurado mediante prompting.
   - Maneja formatos inconsistentes y PDFs escaneados. Implementación estimada en 3-4h.
   - **Limitación:** no determinista (mismo PDF puede dar resultados ligeramente distintos); puede alucinar datos; tiene costo por llamada API; requiere conectividad.
3. **Solo fallback costo/m² (RF-SCO-08).**
   - Usar únicamente la comparación por costo total por metro cuadrado según tipo de obra, sin extraer partidas.
   - Implementación rápida (~2h), determinista.
   - **Limitación:** pérdida total de granularidad; la propuesta de valor central del sistema (comparar precios por insumo) queda incumplida.

**Criterios de Elección:**
- **Capacidad de procesar PDFs escaneados:** crítico, porque muchos expedientes de municipalidades pequeñas son escaneados.
- **Tiempo de implementación:** debe caber en el presupuesto de ~11h del torneo.
- **Tasa de éxito esperada:** la opción debe poder extraer partidas de la mayoría de los PDFs sin ajustes manuales.
- **Determinismo:** deseable, pero secundario frente a la tasa de éxito porque el resultado se cachea.

**Decisión:**
Se adopta **Gemini API** como método primario de extracción, con fallback automático a RF-SCO-08 (costo/m²) cuando el PDF no es procesable.

**Sustento:**
Gemini resuelve el problema central que descarta a pdfplumber: procesa tanto PDFs con texto como escaneados. Su capacidad de entender el contexto semántico de las tablas le permite tolerar los formatos inconsistentes entre municipalidades sin necesidad de ajustes manuales. El tiempo de implementación (~3-4h) cabe en el presupuesto del torneo. El trade-off aceptado es la no-determinismo y el costo por API call, mitigado mediante: (a) una sola extracción por obra con resultado cacheado en BD, (b) un validador que verifica rangos esperados, (c) el fallback costo/m² cuando la extracción falla.

---

## ADR-002 — Ingesta programada de fuentes externas mediante ETL batch

**Categoría:** Modelo de Coordinación

**Contexto:**
El sistema consume datos de múltiples fuentes externas que actualizan su información con frecuencias distintas: INEI publica precios de referencia mensualmente, SEACE/OCDS tiene datos actualizados diariamente, y JNE actualiza sus datasets de autoridades semanalmente. El plan gratuito de Latinfo (posible agregador) permite solo 1,000 consultas mensuales. El sistema debe mostrar datos relativamente frescos sin exceder límites de consumo ni depender de la disponibilidad en tiempo real de cada fuente.

**Alternativas:**
1. **Consultas en tiempo real por cada request.**
   - Cada vez que un usuario ve una obra, el sistema consulta la fuente externa correspondiente.
   - Datos siempre frescos; sin almacenamiento adicional.
   - **Limitaciones:** agota los límites de API rápidamente; la latencia de la fuente impacta al usuario; si la fuente cae, la funcionalidad se pierde.
2. **ETL batch programado.**
   - Un proceso separado descarga, transforma y carga los datos en la BD local según la cadencia que corresponda (mensual/diario/semanal). Las consultas de usuario siempre leen de la BD local.
   - **Limitaciones:** los datos pueden tener hasta N horas/días de desfase respecto a la fuente; requiere infraestructura de jobs.
3. **Modelo híbrido: ETL batch + consulta bajo demanda con caché.**
   - Los datos de referencia (INEI, JNE, SEACE) se sincronizan por batch. Las partidas de obra se extraen bajo demanda (solo cuando un usuario consulta una obra por primera vez) y se cachean.
   - Balance entre frescura y consumo de recursos.

**Criterios de Elección:**
- **Cumplimiento de límites de API** (RNF-05): las consultas en tiempo real excederían el plan gratuito de Latinfo (1,000/mes).
- **Disponibilidad** (RNF-06): el sistema debe funcionar aunque la fuente externa esté caída.
- **Frescura de datos:** aceptable si el desfase es conocido y visible para el usuario (RF-G-04).
- **Simplicidad operativa:** el equipo de 3 personas necesita una solución simple de operar.

**Decisión:**
Se adopta el **modelo híbrido**: ETL batch programado con APScheduler para INEI, SEACE y JNE; extracción bajo demanda para las partidas vía Gemini (con caché posterior); todo almacenado en la BD local desde donde se sirven las consultas.

**Sustento:**
El modelo híbrido respeta los límites del plan gratuito de Latinfo (1,000 consultas/mes se agotarían rápidamente con consultas en tiempo real) y garantiza disponibilidad incluso cuando la fuente externa cae (RNF-06). La cadencia de actualización de cada fuente determina el TTL de su caché: mensual para INEI, diaria para SEACE, semanal para JNE. El desfase temporal es aceptable y se muestra al usuario mediante la fecha de actualización de cada dato (RF-G-04). El trade-off son datos no siempre en vivo a cambio de disponibilidad, performance y costo.

---

## ADR-003 — Stack tecnológico: Next.js + FastAPI + PostgreSQL/PostGIS

**Categoría:** Elección de Tecnología

**Contexto:**
El equipo de 3 personas necesita construir una aplicación web con mapa interactivo de obras públicas (georreferenciación), SSR para indexación SEO, consumo de APIs externas (asíncrono para no bloquear requests), y despliegue rápido en plataformas gratuitas (Vercel + Railway/Render). Ningún integrante tiene experiencia previa en todos los stacks posibles, por lo que la curva de aprendizaje debe ser manejable en el tiempo del torneo (~11h de desarrollo).

**Alternativas:**
1. **Next.js (App Router) + FastAPI + PostgreSQL/PostGIS.**
   - Next.js: SSR nativo para SEO (RNF-12), Leaflet para mapas, ecosistema React maduro.
   - FastAPI: asíncrono nativo (ideal para múltiples llamadas a APIs externas sin bloquear), generación automática de OpenAPI, tipado con Pydantic.
   - PostgreSQL + PostGIS: consultas geoespaciales nativas, clustering de marcadores por viewport.
   - **Limitación:** dos lenguajes (TypeScript + Python) aumentan el costo cognitivo.
2. **Django + PostgreSQL/PostGIS + Vue.js (o vanilla JS).**
   - Django: ORM maduro, admin integrado, ecosistema completo.
   - **Limitaciones:** Django es síncrono por defecto; para llamadas asíncronas a APIs externas se necesita Celery o similar, aumentando la complejidad. SSR en Vue requiere Nuxt.js, otro framework más.
3. **Node.js + Express + MongoDB + React.**
   - Un solo lenguaje (JavaScript/TypeScript) en frontend y backend.
   - **Limitaciones:** MongoDB no soporta consultas geoespaciales nativas tan potentes como PostGIS (necesita capa adicional). Express no es asíncrono nativo. Sin SSR fácil (Next.js sería mejor).
4. **Next.js + Supabase (PostgreSQL + PostGIS + Auth).**
   - Supabase ofrece PostgreSQL administrado, autenticación, API REST automática.
   - **Limitación:** el backend quedaría limitado a las capacidades de Supabase; la lógica de negocio compleja (scoring, matching de partidas) requeriría edge functions o un backend externo.

**Criterios de Elección:**
- **SEO/indexabilidad** (RNF-12): el frontend debe poder renderizarse en servidor.
- **Geoespacial:** el mapa con clustering y filtros por ubicación requiere consultas espaciales eficientes.
- **Asincronía:** el backend consume múltiples APIs externas (Gemini, SEACE, INEI) que no deben bloquear el event loop.
- **Velocidad de desarrollo:** el equipo tiene ~11h y debe priorizar un stack con buena DX y tooling.
- **Despliegue gratuito:** Vercel (frontend) y Railway/Render (backend) ofrecen capas gratuitas viables.

**Decisión:**
Se adopta **Next.js 14 (App Router) + FastAPI + PostgreSQL 15 con PostGIS**.

**Sustento:**
Next.js resuelve SSR de forma nativa (RNF-12), elimina la necesidad de un framework Vue/Nuxt extra, y tiene el ecosistema más maduro para mapas (Leaflet/react-leaflet). FastAPI es la opción más liviana y rápida para un backend asíncrono en Python —su tipado con Pydantic reduce errores y su generación automática de OpenAPI acelera el desarrollo del frontend. PostgreSQL con PostGIS es el estándar de facto para datos geoespaciales; no hay alternativa gratuita que ofrezca consultas espaciales nativas con su nivel de madurez. El trade-off principal es manejar dos lenguajes (TypeScript + Python), mitigado porque el equipo tiene experiencia en ambos y la interfaz entre ellos es una API REST bien definida por OpenAPI.

---

## ADR-004 — Abstracción de fuentes externas mediante DataSource Interface

**Categoría:** Asignación de Responsabilidades

**Contexto:**
El sistema consume datos de 5+ fuentes externas (INEI, SEACE/OCDS, INFOBRAS vía Gemini, JNE, SUNAT) con interfaces radicalmente distintas: unas son archivos Excel descargables, otras son APIs REST, otras requieren scraping HTML, y una (Gemini) es un modelo de IA. Además, el equipo necesita probar el motor de scoring sin depender de la red ni gastar créditos de API (RNF-21). El contexto del torneo sugiere que la fuente de datos podría cambiar (por ejemplo, de fuentes directas a Latinfo como agregador).

**Alternativas:**
1. **Llamadas directas desde el servicio de negocio.**
   - Cada servicio (ObraService, ScoringService) contiene la lógica de conexión a su fuente.
   - Rápido de implementar inicialmente.
   - **Limitaciones:** acoplamiento fuerte; cambiar de fuente requiere modificar el servicio de negocio; imposible testear el scoring sin conexión real.
2. **DataSource Interface con implementaciones intercambiables.**
   - Una interfaz `DataSource` define métodos comunes (`fetchData`, `getMetadata`, `getLastUpdate`). Cada fuente implementa la interfaz. El servicio de negocio depende de la interfaz, no de la implementación concreta. Existe una implementación `MockDataSource` para tests.
   - **Limitaciones:** mayor número de clases/interfaces; requiere un patrón Factory o inyección de dependencias para seleccionar la implementación.

**Criterios de Elección:**
- **Testabilidad** (RNF-21): el motor de scoring debe poder ejecutarse sin conexión a internet.
- **Flexibilidad ante cambios de fuente** (RNF-19): el contexto del torneo sugiere que la fuente podría cambiar a Latinfo.
- **Mantenibilidad:** cada fuente tiene una interfaz distinta; aislar esa complejidad evita que se propague al resto del sistema.
- **Velocidad inicial:** el patrón agrega algo de código base, pero es marginal frente al beneficio.

**Decisión:**
Se implementa una **interfaz `DataSource`** con una implementación concreta por cada fuente externa y una implementación `MockDataSource` para pruebas.

**Sustento:**
La interfaz `DataSource` desacopla la obtención de datos de su consumo, lo que permite (a) testear el motor de scoring contra `MockDataSource` sin red ni consumo de API (RNF-21), (b) cambiar la fuente primaria (ej. de INEI directo a Latinfo) sin modificar el ScoringService, cumpliendo RNF-19, y (c) añadir nuevas fuentes sin alterar la lógica existente. El trade-off es una capa adicional de indirección, que en un sistema con 5+ fuentes heterogéneas no es costo adicional sino aislamiento necesario de la complejidad.

---

## ADR-005 — Scores de riesgo precomputados en pipeline ETL vs cálculo en tiempo real

**Categoría:** Modelo de Coordinación

**Contexto:**
El motor de scoring calcula un score de riesgo (0-100) para cada obra basado en el cruce de partidas del expediente vs. precios de referencia INEI. Este cálculo puede involucrar decenas de partidas por obra, cada una con su matching y ratio. Si se calcula en cada request, la latencia sería alta (especialmente si el cálculo requiere acceso a la BD) y el resultado podría variar si los datos de referencia cambian entre requests. Por otro lado, precomputar implica que el score puede quedar desactualizado hasta el próximo ciclo de ingesta.

**Alternativas:**
1. **Cálculo en tiempo real por request.**
   - Cada vez que un usuario ve una obra, el sistema lee las partidas, hace matching con INEI, calcula ratios y genera el score.
   - Datos siempre frescos.
   - **Limitaciones:** latencia alta (decenas de partidas * matching); inconsistencia potencial (el score puede diferir entre dos requests si los datos de referencia cambiaron); difícil de cachear porque cada request puede dar un resultado distinto.
2. **Precomputación durante la ingesta (ETL).**
   - Cuando se ingieren los datos de una obra (partidas, precios INEI), el pipeline ejecuta el scoring y almacena el resultado en un campo `score_riesgo` de la tabla `obras`.
   - **Limitaciones:** el score se desactualiza hasta la próxima ingesta; si se corrigen datos de referencia, hay que reprocesar.
3. **Híbrido: precomputación + recálculo bajo demanda.**
   - Se precomputa el score en la ingesta, pero se ofrece un botón "Recalcular score" que fuerza un nuevo cálculo si el usuario sospecha que los datos cambiaron.

**Criterios de Elección:**
- **Rendimiento** (RNF-03): los scores deben servirse rápido, sin procesamiento costoso en cada request.
- **Consistencia** (RF-G-03): el score de una obra debe ser el mismo para todos los usuarios que la vean en un mismo instante.
- **Simplicidad:** el equipo tiene ~11h de desarrollo; la solución más simple que cumpla los criterios es preferible.
- **Frescura:** aceptable si el desfase es de horas (para SEACE) o días (para INEI).

**Decisión:**
Se precomputan los scores durante el pipeline de ingesta y se almacenan en la tabla `obras`, con la opción de reprocesamiento manual desde el panel de administración (RF-ADM-05).

**Sustento:**
La precomputación garantiza respuestas rápidas en la API (< 3s para el mapa, RNF-01) y consistencia total: todos los usuarios ven el mismo score para una obra. El coste de reprocesamiento es acotado porque el pipeline corre con la cadencia de actualización de las fuentes (diaria para SEACE, mensual para INEI) y solo para obras nuevas o modificadas. La opción de reprocesamiento manual (RF-ADM-05) cubre el caso de emergencia (datos de referencia corregidos) sin necesidad de recalcular en cada request. El trade-off de frescura (horas/días de desfase) es aceptable y transparente para el usuario porque la fecha de actualización del score se muestra junto al valor (RF-G-04).

---

## ADR-006 — PostgreSQL con PostGIS como motor de base de datos

**Categoría:** Modelo de Datos

**Contexto:**
El sistema maneja datos relacionales complejos (obras, contratistas, municipios, autoridades, usuarios, comentarios) con un componente geoespacial central (el mapa del Perú con marcadores por obra). Se requiere hacer consultas espaciales como "obras dentro de este viewport" y clustering de marcadores por coordenadas. Además, los datos de usuarios y suscripciones requieren consistencia transaccional (ACID). El equipo necesita una solución que se pueda desplegar en un servicio gratuito o de bajo costo (Supabase, Railway, Render).

**Alternativas:**
1. **PostgreSQL 15 con extensión PostGIS.**
   - Motor relacional maduro con extensión geoespacial nativa.
   - ACID completo, tipos geoespaciales (Point, Polygon), funciones espaciales (ST_DWithin, ST_ClusterWithin), índices espaciales (GIST).
   - Amplia oferta de hosting gratuito (Supabase, Railway, Render, Neon).
   - **Limitación:** escalabilidad vertical (no horizontal nativa); pero para el volumen de un MVP es más que suficiente.
2. **MongoDB con $nearSphere / 2dsphere index.**
   - Soporta consultas geoespaciales básicas y escalabilidad horizontal.
   - **Limitaciones:** no tiene ACID entre documentos; el modelo de datos relacional (obra → partidas → contratista → municipio) es más difícil de modelar en documentos sin duplicar datos o usar $lookup (menos eficiente que JOINs en PostGIS). El equipo no tiene experiencia con MongoDB.
3. **MySQL 8 con Spatial Extensions.**
   - Soporta tipos espaciales (Point, Polygon) e índices espaciales.
   - **Limitaciones:** las funciones espaciales de MySQL son menos maduras que PostGIS (falta `ST_ClusterWithin`, `ST_MakeValid`, etc.); el rendimiento en consultas espaciales complejas es inferior.
4. **Supabase como plataforma (PostgreSQL administrado + PostGIS + Auth + Storage).**
   - Ofrece PostgreSQL con PostGIS preinstalado, más autenticación y almacenamiento de archivos.
   - **Limitación:** vendor lock-in leve (auth, storage están atados a Supabase); el tier gratuito tiene límites (500 MB, 2 proyectos).

**Criterios de Elección:**
- **Soporte geoespacial nativo:** crítico para el mapa con clustering y filtros por ubicación (RF-MAP-01, RF-MAP-06).
- **Consistencia ACID:** necesario para datos transaccionales (usuarios, suscripciones).
- **Modelo relacional:** los datos tienen relaciones claras (obra pertenece a municipio, contratista tiene N obras, obra tiene N partidas) que el modelo relacional refleja naturalmente.
- **Costo:** debe existir un tier gratuito viable para el torneo.
- **Experiencia del equipo:** al menos un integrante conoce PostgreSQL.

**Decisión:**
Se adopta **PostgreSQL 15 con extensión PostGIS** como motor de base de datos, desplegado preferentemente sobre Supabase (que ofrece PostGIS preinstalado) o standalone en Railway/Render.

**Sustento:**
PostGIS es la extensión geoespacial más madura del ecosistema open source —ninguna alternativa gratuita iguala su soporte de funciones espaciales, tipos nativos e índices GIST para consultas de cercanía y clustering. Al mismo tiempo, PostgreSQL cumple con los requisitos ACID para los datos transaccionales de usuarios y suscripciones. El modelo relacional se alinea naturalmente con el dominio (obra → partidas, obra → contratista, municipio → autoridades). El trade-off (escalabilidad vertical vs. horizontal) es irrelevante en el volumen esperado para un MVP (cientos de obras, miles de usuarios), y Supabase ofrece una plataforma gratuita que integra PostgreSQL, PostGIS y autenticación en un solo servicio.

---

## ADR-007 — Caché con TTL y degradación elegante para fuentes externas

**Categoría:** Gestión de Recursos

**Contexto:**
Las fuentes externas del sistema imponen restricciones de consumo: el plan gratuito de Latinfo permite 1,000 consultas mensuales, Gemini API tiene costos por token, y las APIs gubernamentales (SEACE, JNE, SUNAT) pueden estar caídas o ser lentas. Si el sistema consulta las fuentes en cada request de usuario, agotará rápidamente los límites del plan gratuito y la aplicación quedará inoperativa. Además, si una fuente externa está caída, el sistema debe seguir funcionando con los datos que ya tiene (RNF-06).

**Alternativas:**
1. **Sin caché (consulta directa siempre).**
   - Simplicidad máxima.
   - **Limitaciones:** agota cuotas de API en minutos; el sistema cae si la fuente está caída; latencia alta para el usuario.
2. **Caché con TTL fijo (todo se cachea, expira según cadencia fija).**
   - Reduce drásticamente las consultas a fuentes externas.
   - **Limitaciones:** TTL fijo puede ser demasiado corto (desperdicia consultas) o demasiado largo (datos obsoletos).
3. **Caché con TTL por fuente + degradación elegante.**
   - Cada fuente tiene un TTL que refleja su cadencia de actualización real (INEI: 30 días, SEACE: 24h, JNE: 7 días). Si una fuente no responde, se sirve el último dato en caché y se muestra la fecha de última actualización. Se dispara una alerta al administrador.
   - **Limitaciones:** requiere lógica adicional para manejar expiración y fallos.

**Criterios de Elección:**
- **Costo** (RNF-05): no se debe exceder el plan gratuito de Latinfo (1,000 consultas/mes) ni el presupuesto de Gemini.
- **Disponibilidad** (RNF-06): el sistema debe funcionar aunque la fuente externa esté caída.
- **Frescura de datos:** cada fuente tiene una cadencia distinta; el TTL debe respetarla.
- **Transparencia:** el usuario debe saber qué tan actualizados están los datos (RF-G-04).

**Decisión:**
Se implementa un **sistema de caché con TTL configurable por fuente** y degradación elegante: cuando una fuente no responde, se sirve el último dato cacheado con indicación visual de la fecha de actualización, y se registra el error para el administrador.

**Sustento:**
El TTL por fuente optimiza el uso de los recursos limitados: INEI se actualiza mensualmente, por lo que 1 consulta cada 30 días es suficiente; SEACE cambia a diario, por lo que su TTL es de 24h; JNE es semanal, TTL de 7 días. Esto reduce las consultas a las fuentes externas a ~40-50 por mes (frente a potencialmente miles sin caché), manteniendo el plan gratuito de Latinfo viable. La degradación elegante (RNF-06) garantiza que la aplicación nunca se queda en blanco: si la fuente falla, el usuario ve la última versión cacheada con la fecha visible (RF-G-04). El trade-off es una implementación ligeramente más compleja (manejo de expiración, actualización asíncrona, indicadores de frescura) que se justifica plenamente por la disponibilidad y el costo.

---

## ADR-008 — Monorepo con frontend y backend en un solo repositorio

**Categoría:** Mapeo entre Elementos Arquitectónicos

**Contexto:**
El equipo está compuesto por 3 personas que trabajan en frontend y backend simultáneamente. El frontend (Next.js, TypeScript) y el backend (FastAPI, Python) comparten tipos de datos (DTOs de obras, contratistas, scores) y necesitan coordinación constante en los cambios de API. El proyecto se despliega en dos plataformas distintas (Vercel para frontend, Railway/Render para backend). Se busca minimizar la fricción en el control de versiones y la integración continua.

**Alternativas:**
1. **Polyrepo (repositorios separados para frontend y backend).**
   - Cada equipo puede trabajar y hacer deploy de forma independiente.
   - **Limitaciones:** el equipo es pequeño y las mismas personas trabajan en ambas capas; los cambios en el contrato API requieren commits sincronizados en dos repos; la visibilidad del proyecto completo se pierde; más complejidad de CI/CD (dos pipelines separados).
2. **Monorepo (frontend y backend en un solo repositorio, carpetas separadas).**
   - Un solo repositorio con `/frontend` y `/backend`.
   - Cambios de API se ven en un solo commit; CI/CD unificado (o dos pipelines en el mismo repo); visibilidad total del proyecto.
   - **Limitaciones:** el tamaño del repo crece más rápido; los despliegues son independientes pero comparten el mismo historial.

**Criterios de Elección:**
- **Tamaño del equipo** (3 personas que tocan ambas capas): la coordinación entre repos es una carga innecesaria.
- **Velocidad de desarrollo** (~11h): la sincronización de cambios es más rápida en monorepo.
- **Deploys independientes:** aunque el repo es único, frontend y backend se despliegan por separado (Vercel vs Railway/Render).
- **Simplicidad:** el equipo no necesita herramientas de monorepo complejas (Nx, Turborepo, etc.); la estructura de carpetas basta.

**Decisión:**
Se adopta una **estructura monorepo** con los directorios `/frontend` (Next.js) y `/backend` (FastAPI) en la raíz, sin herramientas de monorepo complejas.

**Sustento:**
Para un equipo de 3 personas donde todos intervienen en ambas capas, el polyrepo introduce fricción innecesaria: cada cambio en el contrato API requiere commits sincronizados en dos repos, y la visibilidad del proyecto completo se pierde. El monorepo permite ver el impacto completo de un cambio en un solo commit y simplifica la CI/CD (un solo pipeline que corre tests de frontend y backend, aunque los deploys sean independientes). No se necesitan herramientas como Nx o Turborepo porque el proyecto es pequeño; la separación en carpetas es suficiente. El trade-off (el repositorio crece más rápido) es irrelevante en el volumen del proyecto (~11h de código).

---

## ADR-009 — Configuración y credenciales resueltas en tiempo de ejecución

**Categoría:** Tiempo de Enlace

**Contexto:**
El sistema requiere claves de API para Gemini, credenciales de base de datos (PostgreSQL), URLs de los servicios externos (SEACE, Latinfo), y posiblemente claves de autenticación OAuth para Google Login. Estas credenciales son distintas en cada entorno (desarrollo local, staging, producción). El equipo debe asegurar que las credenciales nunca se expongan en el repositorio, especialmente porque el proyecto es open source y está en GitHub.

**Alternativas:**
1. **Credenciales compiladas o hardcodeadas.**
   - Se escriben en el código fuente y se compilan.
   - **Limitaciones:** violación de seguridad; cualquier persona con acceso al repo o al binario puede leerlas; imposible tener configuraciones distintas por entorno.
2. **Variables de entorno en tiempo de ejecución (12-factor app).**
   - Las credenciales se leen de `os.environ` (Python) o `process.env` (Node) en el momento en que la aplicación se inicia.
   - Nunca están en el código fuente.
   - **Limitaciones:** requiere configuración manual de las variables en cada entorno.
3. **Secret manager externo (ej. Google Secret Manager, AWS Secrets Manager, Vercel Environment Variables).**
   - Las credenciales se almacenan en un servicio externo y se obtienen en tiempo de ejecución.
   - No están en el código ni en variables de entorno del sistema operativo.
   - **Limitaciones:** dependencia de un servicio externo; complejidad adicional para un proyecto pequeño.

**Criterios de Elección:**
- **Seguridad** (RNF-08, RNF-11): las credenciales no deben estar en el repositorio ni en el código.
- **Simplicidad:** el equipo tiene ~11h y no puede dedicar tiempo a configurar un secret manager.
- **Entornos múltiples:** desarrollo local, staging (si aplica), producción.
- **Estándar de la industria:** el patrón 12-factor app es ampliamente aceptado y conocido.

**Decisión:**
Se utilizan **variables de entorno** (`.env` local, variables de entorno de la plataforma de deploy) resueltas en tiempo de ejecución, siguiendo el patrón 12-factor app.

**Sustento:**
Las variables de entorno cumplen con el requisito de seguridad (RNF-11) porque las credenciales nunca se almacenan en el repositorio —el archivo `.env` está en `.gitignore` y las variables en producción se configuran en la consola de Vercel/Railway/Render. La resolución en tiempo de ejecución permite que el mismo código se ejecute en desarrollo y producción sin modificaciones (solo cambia el valor de las variables). Un secret manager externo agregaría complejidad innecesaria para un proyecto de este tamaño: las variables de entorno de las plataformas de deploy (Vercel Environment Variables, Railway Secrets) ofrecen un nivel de seguridad suficiente sin costo adicional. El trade-off aceptado es que las credenciales viajan en texto plano dentro de la infraestructura del proveedor —riesgo estándar y aceptado en aplicaciones SaaS.

---

## ADR-010 — Modelo de usuarios tipo YouTube (acceso público sin login)

**Categoría:** Asignación de Responsabilidades

**Contexto:**
La misión del sistema es la **transparencia y la fiscalización ciudadana**: todo el contenido (mapa, obras, scores, perfiles de contratistas y autoridades) debe ser accesible para cualquier ciudadano sin barreras. Al mismo tiempo, el sistema necesita permitir participación de la comunidad (comentarios, reacciones, suscripciones) y moderación de contenido. El equipo debe decidir qué funcionalidades requieren registro y cuáles son públicas (RF-G-01). Además, la indexabilidad por buscadores (RNF-12) es crítica para que la plataforma sea encontrable.

**Alternativas:**
1. **Todo público sin registro (como Wikipedia).**
   - Sin cuentas de usuario; comentarios asociados a un alias editable.
   - **Limitaciones:** difícil moderar contenido inapropiado; sin notificaciones personalizadas; sin trazabilidad de quién comentó.
2. **Login requerido para todo (como redes sociales).**
   - Para ver cualquier obra, score o perfil, el usuario debe registrarse e iniciar sesión.
   - **Limitaciones:** contradice la misión de transparencia; penaliza el SEO (los buscadores no pueden indexar el contenido); frota la adopción ciudadana.
3. **Modelo tipo YouTube: consulta pública, participación registrada.**
   - Ver contenido: sin login. Comentar, reaccionar, suscribirse: requiere cuenta.
   - Combina transparencia (acceso universal) con comunidad (usuarios registrados).
   - **Limitaciones:** requiere implementar registro/login y moderación.

**Criterios de Elección:**
- **Misión del proyecto:** la transparencia exige que el contenido sea accesible sin barreras (RF-G-01).
- **SEO** (RNF-12): las páginas deben ser indexables; el login bloquea a los crawlers.
- **Participación ciudadana:** los comentarios y alertas requieren cierta responsabilidad del autor (una cuenta).
- **Tiempo de implementación:** la autenticación agrega complejidad, pero es necesaria para comentarios.

**Decisión:**
Se adopta el **modelo tipo YouTube**: todo el contenido de consulta (mapa, obras, scores, perfiles) es accesible sin login. El registro solo se exige para comentar, reaccionar y suscribirse.

**Sustento:**
El modelo tipo YouTube es el que mejor equilibra la misión de transparencia con la necesidad de participación responsable. Permite que cualquier ciudadano acceda al mapa, los scores y los perfiles sin fricción (RF-G-01), lo que es coherente con el propósito del sistema. Al mismo tiempo, el registro para comentar y suscribirse (RF-USR-01, RF-USR-03) proporciona trazabilidad para la moderación (RF-ADM-02) y permite notificaciones personalizadas. El SEO se beneficia porque las páginas de contenido son accesibles para los crawlers sin necesidad de login (RNF-12). La implementación de autenticación se simplifica usando proveedores externos (Google OAuth) y Supabase Auth, que están integrados en el stack elegido. El trade-off (desarrollar registro/login y moderación) es menor que el beneficio de tener una plataforma abierta y encontrable.

---

## Referencias

- Bass, L., Clements, P., & Kazman, R. (2021). *Software Architecture in Practice* (4th ed.). Addison-Wesley.
- Richards, M., & Ford, N. (2020). *Fundamentals of Software Architecture*. O'Reilly Media.
- Especificaciones generales: [`../../documentacion/1/0.specs-generales.md`](../../documentacion/1/0.specs-generales.md)
- Requerimientos: [`../../documentacion/1/2.requerimientos.md`](../../documentacion/1/2.requerimientos.md)
- Casos de uso: [`../../documentacion/1/3.casos-de-uso.md`](../../documentacion/1/3.casos-de-uso.md)
- Atributos de calidad: [`../../documentacion/1/4.atributos-calidad.md`](../../documentacion/1/4.atributos-calidad.md)
- Arquitectura técnica: [`../../documentacion/2/1.arquitectura.md`](../../documentacion/2/1.arquitectura.md)
