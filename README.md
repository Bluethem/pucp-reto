# CorruptóMetro

Sistema web de detección de sobreprecios y transparencia en obras públicas del Estado Peruano.

## Problemática y usuario objetivo

**Problemática:** En el Perú, los expedientes técnicos de obras públicas declaran precios por partida (cemento, fierro, mano de obra, etc.) que muchas veces superan ampliamente los precios de referencia oficiales (INEI, Ministerio de Vivienda), sin que exista una herramienta accesible que cruce esta información de forma automática. La data existe (INFOBRAS, SEACE, INEI, JNE, SUNAT) pero está fragmentada y no es legible para el ciudadano promedio.

**Usuario objetivo:** Ciudadanos, periodistas de investigación, y fiscalizadores (regidores de oposición, sociedad civil organizada) que necesitan identificar obras públicas con indicios de sobreprecio sin tener que cruzar manualmente expedientes técnicos contra tablas de precios oficiales.

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | Next.js 14 (App Router) + TypeScript, Leaflet/react-leaflet, Tailwind CSS, shadcn/ui, Recharts |
| Backend | FastAPI (Python) |
| Base de datos | PostgreSQL + PostGIS |
| Jobs / ETL | APScheduler (o Celery + Redis) para sincronización periódica de fuentes |
| Deployment | Vercel (frontend) + Railway/Render o Supabase (backend + DB) |

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

## Modelos y herramientas de IA utilizadas

- **Claude (Anthropic)** — asistencia en diseño de arquitectura, especificación funcional de módulos, definición del motor de scoring y redacción de documentación técnica.
- *(Completar si se usan modelos adicionales: ej. parsing de PDF con IA, clasificación de partidas, etc.)*

## Integrantes y roles

| Nombre | Rol |
|---|---|
| *David Luza Ccorimanya* | *Implementacion - Devops* |
| *Christopher Henrry Albino Soto* | *Diseño UX/UI - Frontend* |
| *Ricco Didier Rashuaman Sapallanay* | *Implementacion - Devops* |

## Documentación adicional

- [Spec general del sistema](./docs/spec.md) *(ajustar ruta según ubicación real)*
- *(Agregar enlaces a: diagramas de arquitectura, ADRs, mockups, etc.)*