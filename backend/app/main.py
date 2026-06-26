"""Entrypoint de la API de Glass (FastAPI, ADR-003).

Inicializa la aplicación, configura CORS para el frontend Next.js y registra
los routers. Por ahora solo expone los endpoints de salud; los routers de
negocio (/obras, /empresas, /municipios, /autoridades, /comentarios, /auth,
/admin, /search) se añadirán a medida que se implementen los módulos.
"""

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import __version__
from app.api import health
from app.core.config import settings
from app.core.response import envelope
from app.routers import (
    admin,
    autoridades,
    auth,
    comentarios,
    empresas,
    municipios,
    obras,
    scoring,
    suscripciones,
)

app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "Plataforma de detección de sobreprecios y transparencia en obras "
        "públicas del Estado Peruano."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Manejadores de error: formato uniforme {"data": null, "error": {...}} ---

@app.exception_handler(StarletteHTTPException)
async def _http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=envelope(error={"status": exc.status_code, "message": exc.detail}),
    )


@app.exception_handler(RequestValidationError)
async def _validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=envelope(
            error={"status": 422, "message": "validation_error", "detail": jsonable_encoder(exc.errors())}
        ),
    )


# --- Routers ---

app.include_router(health.router)
app.include_router(obras.router)
app.include_router(scoring.router)
app.include_router(auth.router)
app.include_router(municipios.router)
app.include_router(autoridades.router)
app.include_router(empresas.router)
app.include_router(comentarios.router)
app.include_router(suscripciones.router)
app.include_router(admin.router)


@app.get("/", tags=["root"])
def root() -> dict:
    """Identifica el servicio."""
    return {"service": settings.app_name, "version": __version__, "docs": "/docs"}
