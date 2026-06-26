# Glass

Sistema web de detección de sobreprecios y transparencia en obras públicas del Estado Peruano.

## Problemática y usuario objetivo

**Problemática:** En el Perú, los expedientes técnicos de obras públicas declaran precios por partida (cemento, fierro, mano de obra, etc.) que muchas veces superan ampliamente los precios de referencia oficiales (INEI, Ministerio de Vivienda), sin que exista una herramienta accesible que cruce esta información de forma automática. La data existe (INFOBRAS, SEACE, INEI, JNE, SUNAT) pero está fragmentada y no es legible para el ciudadano promedio.

**Usuario objetivo:** Ciudadanos, periodistas de investigación, y fiscalizadores (regidores de oposición, sociedad civil organizada) que necesitan identificar obras públicas con indicios de sobreprecio sin tener que cruzar manualmente expedientes técnicos contra tablas de precios oficiales.

### 5W — ¿A quién nos dirigimos?

| W | Respuesta |
|---|---|
| **Who** (¿Quién?) | Ciudadanos, periodistas de investigación, regidores de oposición y sociedad civil organizada interesados en la vigilancia de la inversión pública. |
| **What** (¿Qué?) | Un sistema web que cruza automáticamente los precios declarados en expedientes técnicos de obras públicas contra los precios de referencia oficiales del INEI, generando alertas de sobreprecio claras y explicables. |
| **When** (¿Cuándo?) | Durante la ejecución de la obra y al momento de evaluar su cierre o liquidación, cuando los datos ya están registrados en INFOBRAS. |
| **Where** (¿Dónde?) | En todo el Perú. La plataforma cubre obras de municipalidades distritales, provinciales y gobiernos regionales, con datos extraídos de los portales nacionales. |
| **Why** (¿Por qué?) | Porque la información sobre obras públicas está fragmentada en más de cinco portales gubernamentales (INFOBRAS, SEACE, INEI, SUNAT, JNE) y el ciudadano promedio no puede cruzarla manualmente. Sin una herramienta que automatice esta comparación, la fiscalización ciudadana es prácticamente inviable. |

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | Next.js 14 (App Router) + TypeScript, Leaflet/react-leaflet, Tailwind CSS, shadcn/ui, Recharts |
| Backend | FastAPI (Python) |
| Base de datos | PostgreSQL + PostGIS |
| Jobs / ETL | APScheduler (o Celery + Redis) para sincronización periódica de fuentes |
| Deployment | Vercel (frontend) + Railway/Render o Supabase (backend + DB) |

## Estructura del proyecto

```
pucp-reto/
├── backend/                  # API REST (FastAPI + PostgreSQL/PostGIS)
│   └── app/
│       ├── main.py           # Entrypoint FastAPI: CORS y registro de routers
│       ├── core/             # Configuración, conexión a BD, utilidades y formato de respuesta
│       ├── models/           # Modelos ORM (obras, partidas, contratistas, entidades, etc.)
│       ├── schemas/          # Esquemas Pydantic de request/response
│       ├── routers/          # Endpoints REST por módulo (obras, scoring, auth, empresas, ...)
│       ├── services/         # Lógica de negocio: motor de scoring, ETL, autenticación
│       ├── datasource/       # Integraciones: INEI, SEACE/OCDS, Firecrawl, Gemini, MVCS, Mock
│       ├── scripts/          # Scripts de carga e importación de datos
│       ├── api/              # Endpoints de salud (/health)
│       └── tests/            # Pruebas automatizadas (pytest)
├── frontend/                 # Aplicación web (Next.js 14 + TypeScript)
│   ├── app/                  # Rutas: home (mapa), obra, empresa, municipio, autoridad, acerca, api/pdf
│   ├── components/           # Componentes de UI (mapa, tarjetas, filtros, ...)
│   ├── lib/                  # Cliente de la API (lib/api.ts)
│   └── types/                # Tipos del dominio
├── documentacion/            # Documentación funcional y técnica
│   ├── 1/                    # Specs, contexto, requerimientos, casos de uso, atributos de calidad
│   └── 2/                    # Arquitectura, flujo de datos, modelo de datos
├── docs/                     # Decisiones e imágenes de arquitectura
│   ├── adr/                  # Architecture Decision Records (ADR-001 a ADR-010)
│   └── images/               # Diagramas C4 (contexto y contenedores)
└── render.yaml               # Configuración de despliegue (Render)
```

## Instrucciones para correr el proyecto localmente

### Requisitos previos
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+ con extensión PostGIS

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Configurar DATABASE_URL y demás variables
alembic upgrade head       # Aplicar migraciones
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local   # Configurar NEXT_PUBLIC_API_URL
npm run dev
```

La aplicación quedará disponible en `http://localhost:3000`, consumiendo la API en `http://localhost:8000`.

### Base de datos
```bash
# Crear base de datos local con PostGIS habilitado
createdb corruptometro
psql -d corruptometro -c "CREATE EXTENSION postgis;"
```

## Uso de IA en el proyecto

En el proyecto la IA se utilizó de dos formas distintas: como **asistente de desarrollo** durante la construcción, y como **componente del producto** en tiempo de ejecución.

### IA como asistente de desarrollo

Cada integrante trabajó con un asistente de IA sobre el área que le correspondió. El reparto se refleja en el historial de commits.

| Integrante | Herramienta de IA | Aporte principal |
|---|---|---|
| **Ricco Rashuaman** (`ricco_mv`) | **Claude Code** | Documentación del proyecto (contexto, requerimientos, casos de uso, atributos de calidad, arquitectura, flujo de datos y modelo de datos) e inicialización del backend siguiendo la guía de implementación. |
| **David Luza** (`bluethem`) | **OpenCode + DeepSeek** | Implementación y configuración del backend, integraciones con las fuentes (SEACE/OCDS, INEI, expediente vía Firecrawl + Gemini), el endpoint `POST /obras/extraer` que orquesta el pipeline completo, los ADR y el despliegue (Render / Vercel). |
| **Christopher Albino** (`Christopher-Albino`) | **Claude Code** y **Gemini** | Frontend en Next.js: página principal con mapa interactivo, sistema de filtros, tarjetas de obras paginadas, componentes de UI y los modelos de dominio del cliente. |

En todos los casos la IA se usó como apoyo: el equipo revisó, ajustó e integró el código y la documentación generados, y es capaz de explicar cada decisión técnica.

### IA como componente del producto

Más allá del desarrollo, el sistema usa IA generativa como pieza funcional:

- **Gemini API (Google)** — extrae las partidas (insumo, unidad, cantidad y precio declarado) de los PDFs de los expedientes técnicos, que INFOBRAS no publica de forma estructurada. La decisión y sus alternativas están documentadas en [ADR-001](docs/adr/adr.md). El PDF se localiza y descarga con **Firecrawl** antes de pasarlo a Gemini, y la respuesta se valida antes de calcular el score. Cuando el PDF no es procesable, el sistema usa el modo de comparación por costo/m² como respaldo.

## Integrantes y roles

| Nombre | Rol |
|---|---|
| *David Luza Ccorimanya* | *Implementacion - Devops* |
| *Christopher Henrry Albino Soto* | *Diseño UX/UI - Frontend* |
| *Ricco Didier Rashuaman Sapallanay* | *Implementacion - Devops* |
