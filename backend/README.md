# Glass — Backend (FastAPI)

API REST de Glass: logica de negocio, scoring, autenticacion y orquestacion de
fuentes de datos. Stack segun [ADR-003](../docs/adr/adr.md): **FastAPI + SQLAlchemy +
PostgreSQL/PostGIS + APScheduler**.

> Estado: **implementacion completa**. 10 routers, 10 modelos ORM, 9 servicios,
> 7 adaptadores de fuentes, 15 archivos de tests, 1 script de seed, 1 pipeline ETL.

## Estructura

```
backend/
├── app/
│   ├── main.py                # Entrypoint FastAPI + CORS + 10 routers
│   ├── core/
│   │   ├── config.py          # Configuracion por variables de entorno (ADR-009)
│   │   ├── database.py        # Engine + sesion SQLAlchemy (ADR-006)
│   │   ├── response.py        # Envelope uniforme {data, error}
│   │   └── utils.py           # Helpers: uuid, clasificacion de riesgo
│   ├── api/
│   │   └── health.py          # /health y /health/db
│   ├── models/                # 10 modelos ORM (SQLAlchemy)
│   ├── schemas/               # 9 modulos Pydantic (request/response)
│   ├── routers/               # 9 routers FastAPI (+ health = 10 endpoints)
│   ├── services/              # 9 servicios con logica de negocio + ETL
│   ├── datasource/            # 7 fuentes (INEI, Gemini, Mock, Mvivienda, etc.)
│   ├── scripts/
│   │   └── seed_infobras.py   # Seed de datos de prueba
│   └── tests/                 # 15 archivos de tests (pytest)
├── alembic/                   # Migraciones de base de datos
├── entrypoint.sh              # Script de entrada para produccion (Render/Docker)
├── docker-compose.yml         # PostgreSQL + API (desarrollo local)
├── Dockerfile                 # Imagen para produccion
├── requirements.txt
├── .env.example
└── .gitignore
```

## Requisitos

- Python 3.11+
- PostgreSQL 15 con PostGIS — requerido para datos geoespaciales y consultas espaciales

## Puesta en marcha (local)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env        # luego completa los valores

uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Documentacion interactiva (OpenAPI): http://localhost:8000/docs
- Salud: http://localhost:8000/health · BD: http://localhost:8000/health/db

### Con Docker Compose

```bash
docker compose up -d
alembic upgrade head
python app/scripts/seed_infobras.py
```

## Produccion (Render + Supabase)

### Supabase

1. Crear proyecto en [supabase.com](https://supabase.com)
2. En **SQL Editor**, ejecutar `CREATE EXTENSION IF NOT EXISTS postgis;`
3. En **Project Settings → Database → Connection string → URI**, copiar la URL
4. Modificar para SQLAlchemy:
   ```
   postgresql+psycopg2://postgres:password@db.xxx.supabase.co:5432/postgres?sslmode=require
   ```

### Render

1. Conectar el repositorio a Render
2. Configurar variables de entorno en el dashboard:
   - `DATABASE_URL` — URL de Supabase (con `+psycopg2` y `?sslmode=require`)
   - `ENVIRONMENT=production`
   - `GEMINI_API_KEY`
   - `FIRECRAWL_API_KEY`
   - `JWT_SECRET_KEY`
3. Render usa el `Dockerfile` en `backend/` — el `entrypoint.sh` ejecuta automaticamente:
   1. `alembic upgrade head` — migraciones
   2. `python app/scripts/seed_infobras.py` — seed si la BD esta vacia
   3. `uvicorn app.main:app` — servidor en el puerto asignado

## Notas

- **Redis**: declarado en config (`redis_url`) pero aun no implementado. Se usara en futura fase para cache de fuentes externas (ADR-007).
- **ETL**: el servicio `etl_service.py` esta definido con APScheduler pero no se inicia automaticamente en `main.py`. Pendiente de conexion para ingesta programada de fuentes (INEI, SEACE, JNE).
