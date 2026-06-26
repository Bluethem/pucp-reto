# Glass — Backend (FastAPI)

API REST de Glass: lógica de negocio, scoring, autenticación y orquestación de
fuentes de datos. Stack según [ADR-003](../docs/adr/adr.md): **FastAPI + SQLAlchemy +
PostgreSQL/PostGIS + Redis + APScheduler**.

> Estado: **implementación completa**. 8 módulos funcionando: Obras, Scoring, Auth,
> Municipios, Autoridades, Empresas, Comentarios, Suscripciones, Admin.

## Estructura

```
backend/
├── app/
│   ├── main.py              # Entrypoint FastAPI + CORS + 10 routers
│   ├── core/
│   │   ├── config.py        # Configuración por variables de entorno (ADR-009)
│   │   ├── database.py      # Engine + sesión SQLAlchemy (ADR-006)
│   │   ├── response.py      # Envelope uniforme {data, error}
│   │   └── utils.py         # Helpers: uuid, clasificación de riesgo
│   ├── api/
│   │   └── health.py        # /health y /health/db
│   ├── models/              # 10 modelos ORM (SQLAlchemy)
│   ├── schemas/             # 9 módulos Pydantic (request/response)
│   ├── routers/             # 10 routers FastAPI
│   ├── services/            # 8 servicios con lógica de negocio
│   ├── datasource/          # 5 fuentes (INEI, Gemini, Mock, Mvivienda)
│   └── tests/               # 55 tests (pytest)
├── alembic/                 # Migraciones de base de datos
├── docker-compose.yml       # PostgreSQL + API
├── Dockerfile
├── requirements.txt
├── .env.example
└── .gitignore
```

## Requisitos

- Python 3.11+
- PostgreSQL 15 con PostGIS (ADR-006) — opcional para `/health`, requerido para `/health/db`
- Redis 7 (ADR-007) — para caché/sesiones (aún no usado en esta fase)

## Puesta en marcha (local)

```bash
cd backend
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/Mac:
# source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env        # luego completa los valores

uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Documentación interactiva (OpenAPI): http://localhost:8000/docs
- Salud: http://localhost:8000/health · BD: http://localhost:8000/health/db
