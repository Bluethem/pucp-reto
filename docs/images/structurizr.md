# Arquitectura C4

```
workspace "Glass" "Sistema web de detección de sobreprecios y transparencia en obras públicas del Estado Peruano." {

    model {

        // =====================================================================
        // ACTORES / PERSONAS
        // =====================================================================

        visitante = person "Visitante anónimo" "Ciudadano, periodista u OSC. Consulta todo el contenido sin cuenta." "External"
        usuarioRegistrado = person "Usuario registrado" "Visitante autenticado. Comenta, se suscribe y recibe notificaciones." "External"
        administrador = person "Administrador" "Equipo del proyecto. Modera, gestiona usuarios y supervisa la ingesta de datos." "External"

        // =====================================================================
        // SISTEMAS EXTERNOS
        // =====================================================================

        infobras = softwareSystem "INFOBRAS (MEF)" "Portal de obras públicas. Fuente de PDFs de expedientes técnicos." "External"
        seace = softwareSystem "SEACE / OCDS (OSCE)" "Contrataciones abiertas. Metadatos de obra, contratista y contrato vía API OCDS." "External"
        inei = softwareSystem "INEI" "Índices Unificados de Precios de la Construcción. Archivo .xlsx mensual." "External"
        mivivienda = softwareSystem "Ministerio de Vivienda" "Valores Unitarios Oficiales de Edificación por departamento. Ajuste regional." "External"
        jne = softwareSystem "JNE — Infogob" "Datos abiertos de autoridades: alcaldes, regidores, partido, período." "External"
        sunat = softwareSystem "SUNAT" "Consulta pública de RUC: razón social, representante legal, estado." "External"
        gemini = softwareSystem "Gemini API (Google)" "Extracción de partidas estructuradas desde PDFs de expedientes técnicos." "External"

        // =====================================================================
        // SISTEMA PRINCIPAL
        // =====================================================================

        glass = softwareSystem "Glass" "Plataforma de detección de sobreprecios y transparencia en obras públicas del Estado Peruano." {

            // -----------------------------------------------------------------
            // CONTENEDORES — Nivel 2
            // -----------------------------------------------------------------

            webApp = container "Web App (Next.js)" "Interfaz pública del sistema. SSR/SSG para indexación. Mapa interactivo, detalle de obra, perfiles y participación ciudadana." "Next.js 14 + TypeScript + Tailwind CSS + Leaflet + shadcn/ui" "Web Browser" {

                // Componentes — Nivel 3
                mapaGeneral = component "Módulo Mapa General" "Renderiza marcadores georreferenciados con semáforo de riesgo. Filtros por región, tipo y estado. Clustering." "React + react-leaflet"
                detalleObra = component "Módulo Detalle de Obra" "Muestra identidad, presupuesto, score 0-100, desglose de partidas y alertas de sobreprecio por partida." "React + Recharts"
                desgloseScore = component "Componente Desglose de Score" "Explica indicadores que componen el score y su aporte individual. Motor determinista, sin caja negra." "React"
                perfilEmpresa = component "Módulo Perfil de Empresa" "Datos SUNAT, score de confiabilidad, historial de obras, alertas de colusión y sobrevaluación." "React"
                municipioAutoridades = component "Módulo Municipio y Autoridades" "Entidad ejecutora, alcalde y regidores del período, resumen de obras con riesgo agregado." "React"
                perfilAutoridad = component "Módulo Perfil de Autoridad" "Datos públicos JNE: cargo, partido, período, foto y obras bajo gestión. Sin DNI ni denuncias." "React"
                comentarios = component "Módulo Comentarios" "Lectura pública. Publicación, edición y reporte para usuarios registrados." "React"
                notificaciones = component "Centro de Notificaciones" "Campana de notificaciones. Suscripciones a obras, empresas, municipios y autoridades." "React"
                buscador = component "Buscador Global" "Búsqueda por nombre de obra, municipio, empresa (RUC/razón social) y autoridad." "React"
                authUI = component "Auth UI" "Registro, login, logout y recuperación de contraseña. Integración con proveedor externo (Google)." "React + NextAuth"
                adminPanel = component "Panel de Administración" "Backoffice restringido. Moderación de comentarios, gestión de usuarios y tablero de estado del sistema." "React (solo rol admin)"
            }

            api = container "API Backend (FastAPI)" "API REST. Lógica de negocio, autenticación, scoring, comentarios y orquestación de fuentes de datos." "Python + FastAPI + SQLAlchemy" "API" {

                // Componentes — Nivel 3
                obrasRouter = component "Router /obras" "Endpoints de mapa (marcadores + filtros), detalle de obra y score. Sirve datos precomputados." "FastAPI Router"
                scoringEngine = component "Motor de Scoring" "Calcula score 0-100 por promedio ponderado de ratios precio_declarado/precio_referencia. Determinista y trazable. Implementa fallback costo/m²." "Python (puro, sin IA)"
                empresasRouter = component "Router /empresas" "Perfil de empresa, score de confiabilidad, historial y alertas de colusión." "FastAPI Router"
                municipiosRouter = component "Router /municipios" "Entidad ejecutora, autoridades del período y resumen de obras." "FastAPI Router"
                autoridadesRouter = component "Router /autoridades" "Perfil de autoridad con datos públicos JNE y obras de gestión." "FastAPI Router"
                comentariosRouter = component "Router /comentarios" "CRUD de comentarios, reacciones y reportes. Requiere auth para escritura." "FastAPI Router"
                notificacionesRouter = component "Router /notificaciones" "Suscripciones y entrega de notificaciones. Centro de campana." "FastAPI Router"
                authRouter = component "Router /auth" "Registro, login, logout, recuperación de contraseña. JWT + control de roles." "FastAPI Router + JWT"
                adminRouter = component "Router /admin" "Backoffice: moderación, gestión de usuarios, estado del sistema. Rol admin requerido." "FastAPI Router"
                buscadorRouter = component "Router /search" "Búsqueda full-text por obra, empresa, municipio y autoridad." "FastAPI Router + PostgreSQL FTS"
                dataSourceInterface = component "DataSource Interface" "Abstracción sobre todas las fuentes externas. Cada origen implementa fetch(), getMetadata() y getLastUpdate(). Permite mock para tests." "Python ABC"
                cacheLayer = component "Capa de Caché" "TTL configurable por fuente. Degradación elegante: sirve último dato cacheado si la fuente falla. Registra fecha de última actualización." "Redis + Python"
            }

            etlJobs = container "ETL / Jobs (APScheduler)" "Procesos automáticos de ingesta, extracción de partidas y cálculo de scores. Orquesta fuentes externas y alimenta la BD." "Python + APScheduler" "Background Worker" {

                // Componentes — Nivel 3
                ingestorINEI = component "Ingestor INEI" "Descarga mensual del .xlsx de Índices Unificados de Precios. Parsea y hace upsert en precios_referencia. Registra versión/fecha." "Python + openpyxl"
                ingestorSEACE = component "Ingestor SEACE/OCDS" "Consulta API OCDS por rango de fechas o entidad. Extrae obra, contratista y contrato. Geocodifica coordenadas." "Python + httpx"
                ingestorJNE = component "Ingestor JNE" "Descarga dataset de autoridades de Datos Abiertos JNE. Parsea CSV y hace upsert en autoridades." "Python + pandas"
                ingestorSUNAT = component "Ingestor SUNAT" "Scraping controlado de consulta RUC público. Caché agresiva para no exceder rate limits." "Python + httpx + BeautifulSoup"
                geminiExtractor = component "Extractor Gemini" "Descarga PDF de INFOBRAS, lo envía a Gemini API con prompt estructurado y recibe JSON de partidas. Valida rangos. Almacena respuesta cruda en log_extraccion. Una sola extracción por obra (cacheada en BD)." "Python + google-generativeai"
                scoreCalculator = component "Calculador de Scores" "Orquesta el motor de scoring para obras y empresas. Dispara recálculo cuando llegan nuevos datos. Precomputa y persiste scores en BD." "Python"
                fallbackCalculator = component "Calculador Fallback costo/m²" "Comparación de presupuesto total vs. costo de referencia por tipo de obra y metrado cuando el PDF no es parseable." "Python"
            }

            database = container "Base de Datos (PostgreSQL + PostGIS)" "Almacén principal. Obras, partidas, precios de referencia, scores precomputados, contratistas, autoridades, usuarios, comentarios y logs de extracción." "PostgreSQL 15 + PostGIS" "Database" {

                // Esquemas lógicos como componentes
                obras_table = component "obras" "Metadatos de obra: título, tipo, estado, coordenadas (PostGIS), presupuesto, score precomputado, modo de análisis, fecha de actualización."
                partidas_table = component "partidas_obra" "Partidas extraídas por Gemini: insumo, unidad, cantidad, precio_declarado, precio_referencia, ratio, comparable."
                precios_ref_table = component "precios_referencia" "Tabla de precios INEI por insumo con código estandarizado. Versión y fecha de publicación."
                scores_table = component "scores_obras" "Score 0-100 precomputado por obra, desglose de indicadores y aportes individuales. Semáforo."
                contratos_table = component "contratos" "Contratos SEACE: RUC, razón social, monto, fechas, estado, tipo de proceso."
                contratistas_table = component "contratistas" "Perfil del contratista: RUC, razón social, representante, estado SUNAT, score de confiabilidad, historial."
                autoridades_table = component "autoridades" "Alcaldes y regidores: nombre, cargo, partido, período, municipio, foto URL."
                usuarios_table = component "usuarios" "Cuentas registradas: alias, email (hash), contraseña (hash), rol, suscripciones."
                comentarios_table = component "comentarios" "Comentarios por recurso (obra/empresa/municipio/autoridad): autor, fecha, contenido, estado."
                log_extraccion_table = component "log_extraccion" "Respuesta cruda de Gemini por PDF, estado de extracción, fecha, modo (partidas/fallback)."
            }

            cache = container "Caché (Redis)" "Almacén en memoria para respuestas de fuentes externas, sesiones y rate limiting. TTL configurable por fuente." "Redis 7" "Cache"
        }

        // =====================================================================
        // RELACIONES — Nivel 1 (Contexto)
        // =====================================================================

        visitante -> glass "Consulta mapa, obras, empresas, municipios y autoridades" "HTTPS"
        usuarioRegistrado -> glass "Consulta + comenta, suscribe y recibe notificaciones" "HTTPS"
        administrador -> glass "Modera, gestiona usuarios y supervisa ingesta" "HTTPS"

        glass -> infobras "Descarga PDFs de expedientes técnicos" "HTTPS"
        glass -> seace "Consume metadatos de obras y contratos" "HTTPS / API OCDS"
        glass -> inei "Descarga .xlsx mensual de precios de referencia" "HTTPS"
        glass -> mivivienda "Descarga Valores Unitarios Oficiales para ajuste regional" "HTTPS"
        glass -> jne "Consume dataset de autoridades" "HTTPS / CSV"
        glass -> sunat "Scraping de consulta RUC pública" "HTTPS"
        glass -> gemini "Envía PDFs y recibe JSON de partidas" "HTTPS / API REST"

        // =====================================================================
        // RELACIONES — Nivel 2 (Contenedores)
        // =====================================================================

        visitante -> webApp "Navega mapa, obras, perfiles" "HTTPS / Browser"
        usuarioRegistrado -> webApp "Navega + comenta y gestiona notificaciones" "HTTPS / Browser"
        administrador -> webApp "Accede al panel de administración" "HTTPS / Browser"

        webApp -> api "Consume datos y acciones" "HTTPS / JSON REST"
        api -> database "Lee y escribe datos" "TCP / SQL"
        api -> cache "Caché de sesiones y respuestas de fuentes" "TCP / Redis Protocol"

        etlJobs -> database "Persiste datos ingestados y scores precomputados" "TCP / SQL"
        etlJobs -> cache "Cachea respuestas de fuentes externas (TTL)" "TCP / Redis Protocol"
        etlJobs -> infobras "Descarga PDFs de expedientes" "HTTPS"
        etlJobs -> seace "Consulta API OCDS" "HTTPS / API OCDS"
        etlJobs -> inei "Descarga .xlsx de precios" "HTTPS"
        etlJobs -> mivivienda "Descarga Valores Unitarios Oficiales" "HTTPS"
        etlJobs -> jne "Descarga dataset de autoridades" "HTTPS / CSV"
        etlJobs -> sunat "Scraping de RUC" "HTTPS"
        etlJobs -> gemini "Extracción de partidas desde PDF" "HTTPS / API REST"

        api -> etlJobs "Dispara extracción bajo demanda (primera consulta de obra)" "Internal / Python call"

        // =====================================================================
        // RELACIONES — Nivel 3 (Componentes dentro de webApp)
        // =====================================================================

        mapaGeneral -> api "GET /obras?filtros" "HTTPS / JSON"
        detalleObra -> api "GET /obras/{id}" "HTTPS / JSON"
        desgloseScore -> api "GET /obras/{id}/score" "HTTPS / JSON"
        perfilEmpresa -> api "GET /empresas/{ruc}" "HTTPS / JSON"
        municipioAutoridades -> api "GET /municipios/{id}" "HTTPS / JSON"
        perfilAutoridad -> api "GET /autoridades/{id}" "HTTPS / JSON"
        comentarios -> api "GET|POST|PUT|DELETE /comentarios" "HTTPS / JSON"
        notificaciones -> api "GET /notificaciones, POST /suscripciones" "HTTPS / JSON"
        buscador -> api "GET /search?q=" "HTTPS / JSON"
        authUI -> api "POST /auth/register|login|logout" "HTTPS / JSON"
        adminPanel -> api "GET|POST /admin/*" "HTTPS / JSON"

        // =====================================================================
        // RELACIONES — Nivel 3 (Componentes dentro de api)
        // =====================================================================

        obrasRouter -> scoringEngine "Delega cálculo si score no está precomputado"
        obrasRouter -> dataSourceInterface "Consulta caché de datos de obras"
        scoringEngine -> dataSourceInterface "Obtiene partidas y precios de referencia"
        scoringEngine -> fallbackCalculator "Activa si PDF no parseable (modo fallback)"
        dataSourceInterface -> cacheLayer "Lee/escribe caché por fuente"
        cacheLayer -> cache "Persiste entradas de caché" "Redis Protocol"

        empresasRouter -> dataSourceInterface "Obtiene datos SEACE + SUNAT"
        municipiosRouter -> dataSourceInterface "Obtiene datos de entidad y autoridades"
        autoridadesRouter -> dataSourceInterface "Obtiene datos JNE"
        comentariosRouter -> database "Lee/escribe comentarios" "SQL"
        notificacionesRouter -> database "Lee/escribe suscripciones y notificaciones" "SQL"
        authRouter -> database "Lee/escribe usuarios y sesiones" "SQL"
        authRouter -> cache "Almacena sesiones JWT" "Redis"
        adminRouter -> database "Modera y gestiona datos" "SQL"
        buscadorRouter -> database "Full-text search" "SQL / tsvector"

        // =====================================================================
        // RELACIONES — Nivel 3 (Componentes dentro de etlJobs)
        // =====================================================================

        ingestorINEI -> inei "Descarga .xlsx mensual" "HTTPS"
        ingestorINEI -> precios_ref_table "Upsert de precios de referencia" "SQL"

        ingestorSEACE -> seace "Consulta API OCDS" "HTTPS"
        ingestorSEACE -> obras_table "Upsert de metadatos de obra" "SQL"
        ingestorSEACE -> contratos_table "Upsert de contratos" "SQL"
        ingestorSEACE -> contratistas_table "Upsert de contratistas" "SQL"

        ingestorJNE -> jne "Descarga dataset CSV" "HTTPS"
        ingestorJNE -> autoridades_table "Upsert de autoridades" "SQL"

        ingestorSUNAT -> sunat "Scraping de RUC" "HTTPS"
        ingestorSUNAT -> contratistas_table "Actualiza datos de empresa" "SQL"

        geminiExtractor -> infobras "Descarga PDF del expediente" "HTTPS"
        geminiExtractor -> gemini "Envía PDF, recibe JSON de partidas" "HTTPS / API REST"
        geminiExtractor -> partidas_table "Inserta partidas validadas" "SQL"
        geminiExtractor -> log_extraccion_table "Registra respuesta cruda y estado" "SQL"
        geminiExtractor -> fallbackCalculator "Activa fallback si PDF no parseable"

        scoreCalculator -> scoringEngine "Ejecuta motor de scoring"
        scoreCalculator -> obras_table "Lee partidas y precios" "SQL"
        scoreCalculator -> scores_table "Persiste scores precomputados" "SQL"
        scoreCalculator -> contratistas_table "Persiste score de confiabilidad" "SQL"

        fallbackCalculator -> obras_table "Lee tipo, metrado y presupuesto total" "SQL"
        fallbackCalculator -> precios_ref_table "Lee costo/m² de referencia" "SQL"

    }

    // =========================================================================
    // VISTAS
    // =========================================================================

    views {

        // ----- Nivel 1: Contexto del sistema -----
        systemContext glass "C1_Contexto" {
            include *
            autoLayout lr
            title "C1 — Contexto del sistema Glass"
            description "Glass y sus actores externos: personas y sistemas de información gubernamentales."
        }

        // ----- Nivel 2: Contenedores -----
        container glass "C2_Contenedores" {
            include *
            autoLayout lr
            title "C2 — Contenedores de Glass"
            description "Web App (Next.js), API Backend (FastAPI), Jobs ETL (APScheduler), Base de Datos (PostgreSQL+PostGIS) y Caché (Redis)."
        }

        // ----- Nivel 3: Componentes de la Web App -----
        component webApp "C3_WebApp" {
            include *
            autoLayout tb
            title "C3 — Componentes de la Web App (Next.js)"
            description "Módulos de UI: Mapa, Detalle de Obra, Desglose de Score, Empresa, Municipio, Autoridad, Comentarios, Notificaciones, Buscador, Auth y Admin."
        }

        // ----- Nivel 3: Componentes del API Backend -----
        component api "C3_API" {
            include *
            autoLayout tb
            title "C3 — Componentes del API Backend (FastAPI)"
            description "Routers REST, Motor de Scoring, DataSource Interface y Capa de Caché."
        }

        // ----- Nivel 3: Componentes del ETL -----
        component etlJobs "C3_ETL" {
            include *
            autoLayout tb
            title "C3 — Componentes del ETL / Jobs (APScheduler)"
            description "Ingestores por fuente (INEI, SEACE, JNE, SUNAT), Extractor Gemini y Calculadores de Score."
        }

        // ----- Nivel 3: Esquema de la Base de Datos -----
        component database "C3_Database" {
            include *
            autoLayout tb
            title "C3 — Esquema lógico de la Base de Datos (PostgreSQL + PostGIS)"
            description "Tablas principales: obras, partidas_obra, precios_referencia, scores_obras, contratos, contratistas, autoridades, usuarios, comentarios y log_extraccion."
        }

        // ----- Estilos -----
        styles {

            element "Person" {
                shape Person
                background "#1168BD"
                color "#ffffff"
                fontSize 14
            }

            element "External" {
                background "#999999"
                color "#ffffff"
                shape RoundedBox
            }

            element "Software System" {
                background "#1168BD"
                color "#ffffff"
                shape RoundedBox
            }

            element "Web Browser" {
                shape WebBrowser
                background "#438DD5"
                color "#ffffff"
            }

            element "API" {
                shape Hexagon
                background "#2E7D32"
                color "#ffffff"
            }

            element "Background Worker" {
                shape Pipe
                background "#E65100"
                color "#ffffff"
            }

            element "Database" {
                shape Cylinder
                background "#6A1B9A"
                color "#ffffff"
            }

            element "Cache" {
                shape Cylinder
                background "#B71C1C"
                color "#ffffff"
            }

            element "Component" {
                background "#85BBF0"
                color "#000000"
                shape Component
            }

            relationship "Relationship" {
                thickness 2
                color "#707070"
                style dashed
            }
        }
    }
}
```
