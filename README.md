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
