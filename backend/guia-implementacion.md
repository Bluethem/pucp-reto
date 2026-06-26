# Guía de Implementación — Glass Backend

> **Objetivo:** dividir la implementación del backend en módulos independientes para que 2 personas trabajen en paralelo, cada una con su IA generando código y tests.

---

## Convenciones generales

- **Lenguaje:** Python 3.11+
- **Framework:** FastAPI + SQLAlchemy (síncrono) + PostgreSQL/PostGIS
- **Tests:** pytest + `TestClient` de FastAPI
- **Documentación API:** Swagger en `/docs` (generado automáticamente)
- **Mock Data:** `MockDataSource` para tests sin depender de fuentes externas
- **Formato de respuestas:** JSON con `{ "data": ..., "error": ... }`
- **IDs:** UUID v4 como strings

### Estructura de archivos por módulo

Cada módulo sigue este patrón:

```
app/
├── routers/<modulo>.py       # Endpoints FastAPI
├── schemas/<modulo>.py       # Pydantic request/response
├── services/<modulo>.py      # Lógica de negocio
└── tests/test_<modulo>.py    # Tests (mínimo 4-5)
```

### Plantilla de router

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter(prefix="/api/v1/<recurso>", tags=["<TagOpenAPI>"])

@router.get("")
def listar(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ...
```

### Tests mínimos por módulo (4-5)

| Test | Qué verifica |
|---|---|
| `test_listar_xxx` | GET 200 + estructura JSON (lista) |
| `test_get_xxx_by_id` | GET 200 + campos esperados / GET 404 |
| `test_crear_xxx` | POST 201 + datos creados / POST 422 (validación) |
| `test_xxx_sin_auth` | 401/403 si el endpoint requiere auth |
| `test_filtros_xxx` | GET con query params + resultados filtrados |

---

## Módulo 1 — Base (ya implementado)

**Responsable:** *Ya está listo*

Archivos existentes:
- `docker-compose.yml` — PostgreSQL + API
- `Dockerfile` — imagen Python 3.11
- `app/main.py` — FastAPI con CORS + health
- `app/core/config.py` — Settings vía env vars
- `app/core/database.py` — SQLAlchemy engine + session
- `app/models/*.py` — 9 modelos ORM (Obra, PartidaObra, PrecioReferencia, Contratista, Entidad, Autoridad, Usuario, Comentario, Suscripcion, LogExtraccion)
- `alembic.ini` + `alembic/env.py` — migraciones
- `app/tests/conftest.py` + `test_base.py` — tests base
- `requirements.txt` — todas las dependencias

### Para arrancar

```bash
# 1. Iniciar servicios
cd backend
docker compose up -d

# 2. Ejecutar migraciones
alembic upgrade head

# 3. Correr tests
pytest -v

# 4. Ver API
open http://localhost:8000/docs
```

---

## Módulo 2 — Obras (Responsable A)

**Depende de:** Módulo 1 (Base)

### Archivos a crear

| Archivo | Contenido |
|---|---|
| `app/schemas/obra.py` | `ObraResponse`, `ObraListResponse`, `ObraFilterParams` |
| `app/routers/obras.py` | Endpoints CRUD + geo + scoring |
| `app/services/obra_service.py` | Lógica de obras (filtros, geo queries) |
| `app/tests/test_obras.py` | Tests del módulo |

### Endpoints

| Método | Ruta | Descripción | Auth | Status |
|---|---|---|---|---|
| GET | `/api/v1/obras` | Listar obras con filtros (departamento, tipo, estado, riesgo, skip, limit) | No | 200 |
| GET | `/api/v1/obras/{id}` | Detalle de obra con partidas y score | No | 200, 404 |
| GET | `/api/v1/obras/geolocalizadas` | Obras en viewport (bounds NE/SW) para el mapa | No | 200 |
| GET | `/api/v1/obras/resumen` | Conteo por nivel de riesgo y filtros activos | No | 200 |
| GET | `/api/v1/obras/buscar` | Búsqueda global por nombre, código, municipio | No | 200 |

### Mock Data para tests

```python
def crear_obra_mock(db):
    obra = Obra(
        codigo_infobras="TEST-001",
        titulo="Puente Test",
        tipo_obra="edificacion",
        estado="ejecucion",
        presupuesto_total=1000000,
        departamento="Lima",
        score_riesgo=25,
        modo_analisis="fallback_m2",
    )
    db.add(obra)
    db.commit()
    return obra
```

---

## Módulo 3 — Scoring (Responsable A)

**Depende de:** Módulo 1 + Módulo 2

### Archivos a crear

| Archivo | Contenido |
|---|---|
| `app/schemas/scoring.py` | `ScoreResponse`, `PartidaScoreResponse` |
| `app/routers/scoring.py` | Endpoints de score |
| `app/services/scoring_service.py` | Motor de scoring (determinista, trazable) |
| `app/datasource/interface.py` | `DataSource` abstract base class |
| `app/datasource/mock.py` | `MockDataSource` para tests |
| `app/datasource/inei.py` | `INEIDataSource` (parser .xlsx) |
| `app/datasource/gemini.py` | `GeminiDataSource` (PDF extraction) |
| `app/tests/test_scoring.py` | Tests del motor |

### Endpoints

| Método | Ruta | Descripción | Auth | Status |
|---|---|---|---|---|
| GET | `/api/v1/obras/{id}/score` | Score detallado con desglose por partida | No | 200, 404 |
| POST | `/api/v1/obras/{id}/recalcular` | Forzar recálculo del score | Admin | 200 |

### Lógica del ScoringService

```python
class ScoringService:
    def __init__(self, datasource: DataSource):
        self.datasource = datasource

    def calcular_score(self, obra_id: str) -> dict:
        # 1. Obtener partidas (de BD o datasource)
        # 2. Obtener precios de referencia INEI
        # 3. Matching por código
        # 4. Calcular ratio por partida
        # 5. Score global 0-100
        # 6. Clasificar: verde(0-40) / amarillo(41-60) / rojo(61-100)
        # 7. Guardar en BD
        # 8. Retornar desglose explicativo
```

### Tests del scoring

```python
def test_scoring_con_partidas_validas(db_session):
    """MockDataSource con datos conocidos → score esperado"""
    ...

def test_scoring_fallback_m2(db_session):
    """Sin partidas → fallback costo/m²"""
    ...

def test_scoring_insumo_sin_referencia(db_session):
    """Insumo sin precio INEI → marcado 'no comparable'"""
    ...

def test_scoring_determinista(db_session):
    """Mismo input → mismo score (2 ejecuciones)"""
    ...

def test_scoring_explicacion_trazable(db_session):
    """Score tiene desglose con indicadores y aportes"""
    ...
```

---

## Módulo 4 — Auth (Responsable B)

**Depende de:** Módulo 1

### Archivos a crear

| Archivo | Contenido |
|---|---|
| `app/schemas/auth.py` | `RegisterRequest`, `LoginRequest`, `TokenResponse`, `UserResponse` |
| `app/routers/auth.py` | Endpoints de autenticación |
| `app/services/auth_service.py` | Hash + JWT + validación |
| `app/tests/test_auth.py` | Tests de auth |

### Endpoints

| Método | Ruta | Descripción | Auth | Status |
|---|---|---|---|---|
| POST | `/api/v1/auth/register` | Registrar nuevo usuario | No | 201, 409 |
| POST | `/api/v1/auth/login` | Iniciar sesión (devuelve JWT) | No | 200, 401 |
| GET | `/api/v1/auth/me` | Perfil del usuario actual | JWT | 200, 401 |
| POST | `/api/v1/auth/logout` | Cerrar sesión | JWT | 200 |

### Tests

```python
def test_register_exitoso(client):
    """POST /auth/register → 201 + token"""
    ...

def test_register_email_duplicado(client):
    """POST /auth/register con email existente → 409"""
    ...

def test_login_exitoso(client):
    """POST /auth/login → 200 + JWT"""
    ...

def test_login_credenciales_invalidas(client):
    """POST /auth/login con contraseña incorrecta → 401"""
    ...

def test_get_me_sin_token(client):
    """GET /auth/me sin header → 401"""
    ...
```

---

## Módulo 5 — Municipios y Autoridades (Responsable B)

**Depende de:** Módulo 1 + Módulo 2

### Archivos a crear

| Archivo | Contenido |
|---|---|
| `app/schemas/municipio.py` | `EntidadResponse`, `EntidadDetailResponse` |
| `app/schemas/autoridad.py` | `AutoridadResponse` |
| `app/routers/municipios.py` | Endpoints de entidades |
| `app/routers/autoridades.py` | Endpoints de autoridades |
| `app/services/entidad_service.py` | Lógica de entidades |
| `app/tests/test_municipios.py` | Tests de municipios |
| `app/tests/test_autoridades.py` | Tests de autoridades |

### Endpoints

| Método | Ruta | Descripción | Auth | Status |
|---|---|---|---|---|
| GET | `/api/v1/municipios` | Listar entidades con filtros | No | 200 |
| GET | `/api/v1/municipios/{id}` | Detalle de entidad | No | 200, 404 |
| GET | `/api/v1/municipios/{id}/obras` | Obras de la entidad con scores | No | 200 |
| GET | `/api/v1/autoridades` | Listar autoridades | No | 200 |
| GET | `/api/v1/autoridades/{id}` | Detalle de autoridad + obras a su cargo | No | 200, 404 |

---

## Módulo 6 — Empresas (Responsable B)

**Depende de:** Módulo 1 + Módulo 2

### Archivos a crear

| Archivo | Contenido |
|---|---|
| `app/schemas/empresa.py` | `ContratistaResponse`, `ContratistaDetailResponse` |
| `app/routers/empresas.py` | Endpoints de contratistas |
| `app/services/contratista_service.py` | Lógica de contratistas |
| `app/tests/test_empresas.py` | Tests de empresas |

### Endpoints

| Método | Ruta | Descripción | Auth | Status |
|---|---|---|---|---|
| GET | `/api/v1/empresas` | Listar contratistas (filtro por RUC, razón social) | No | 200 |
| GET | `/api/v1/empresas/{id}` | Detalle de contratista con score de confiabilidad | No | 200, 404 |
| GET | `/api/v1/empresas/{id}/obras` | Obras adjudicadas a la empresa | No | 200 |
| GET | `/api/v1/empresas?ruc=` | Búsqueda por RUC exacto | No | 200, 404 |

---

## Módulo 7 — Comentarios y Suscripciones (Responsable B)

**Depende de:** Módulo 1 + Módulo 4 (Auth)

### Archivos a crear

| Archivo | Contenido |
|---|---|
| `app/schemas/comentario.py` | `ComentarioRequest`, `ComentarioResponse` |
| `app/schemas/suscripcion.py` | `SuscripcionRequest`, `SuscripcionResponse` |
| `app/routers/comentarios.py` | Endpoints de comentarios |
| `app/routers/suscripciones.py` | Endpoints de suscripciones |
| `app/services/comentario_service.py` | Lógica de comentarios |
| `app/services/suscripcion_service.py` | Lógica de suscripciones |
| `app/tests/test_comentarios.py` | Tests de comentarios |
| `app/tests/test_suscripciones.py` | Tests de suscripciones |

### Endpoints

| Método | Ruta | Descripción | Auth | Status |
|---|---|---|---|---|
| GET | `/api/v1/comentarios` | Listar comentarios (filtro por `recurso_tipo` + `recurso_id`) | No | 200 |
| POST | `/api/v1/comentarios` | Crear comentario | JWT | 201, 422 |
| DELETE | `/api/v1/comentarios/{id}` | Eliminar propio comentario | JWT | 204, 403, 404 |
| POST | `/api/v1/comentarios/{id}/reportar` | Reportar comentario inapropiado | JWT | 200 |
| GET | `/api/v1/suscripciones` | Listar suscripciones del usuario | JWT | 200 |
| POST | `/api/v1/suscripciones` | Suscribirse a un recurso | JWT | 201, 409 |
| DELETE | `/api/v1/suscripciones/{id}` | Cancelar suscripción | JWT | 204, 404 |

---

## Módulo 8 — Admin (Responsable B)

**Depende de:** Módulo 1 + Módulo 4 + Módulo 7

### Archivos a crear

| Archivo | Contenido |
|---|---|
| `app/schemas/admin.py` | `SaludFuentesResponse`, `ComentarioReportadoResponse` |
| `app/routers/admin.py` | Endpoints de backoffice |
| `app/services/admin_service.py` | Lógica de administración |
| `app/tests/test_admin.py` | Tests de admin |

### Endpoints

| Método | Ruta | Descripción | Auth | Status |
|---|---|---|---|---|
| GET | `/api/v1/admin/salud-fuentes` | Estado de cada fuente externa | Admin | 200 |
| GET | `/api/v1/admin/comentarios-reportados` | Lista de comentarios reportados | Admin | 200 |
| POST | `/api/v1/admin/comentarios/{id}/moderar` | Ocultar/restaurar comentario | Admin | 200, 404 |
| GET | `/api/v1/admin/usuarios` | Listar usuarios | Admin | 200 |

---

## Cronograma sugerido

| Fase | Módulos | Tiempo | Quién |
|---|---|---|---|
| **Fase 1** (ya) | Base (Docker + models + tests) | — | Ambos |
| **Fase 2** | Obras + Auth | 2h | A: Obras · B: Auth |
| **Fase 3** | Scoring + Municipios/Autoridades | 2h | A: Scoring · B: Municipios |
| **Fase 4** | Empresas + Comentarios/Suscripciones | 2h | A: — · B: Ambos |
| **Fase 5** | Admin + Integración + Deploy | 1h | B: Admin · A: Integración |
| **Total** | 8 módulos | ~7h | 2 personas |

---

## Integración

1. Cada uno desarrolla su módulo en una branch separada (`feat/obras`, `feat/auth`, etc.)
2. Al terminar, crear PR a `main`
3. Correr `pytest -v` antes de mergear (todos los tests deben pasar)
4. Después del merge, verificar Swagger en `/docs`

## Deploy

- **Opción A (Docker):** `docker compose up -d` en el servidor
- **Opción B (Render):** conectar repo, usar `uvicorn app.main:app` como start command
