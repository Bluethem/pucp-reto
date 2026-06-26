"""Entrypoint de la API de Glass (FastAPI, ADR-003).

Inicializa la aplicación, configura CORS para el frontend Next.js y registra
los routers. Por ahora solo expone los endpoints de salud; los routers de
negocio (/obras, /empresas, /municipios, /autoridades, /comentarios, /auth,
/admin, /search) se añadirán a medida que se implementen los módulos.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import health
from app.core.config import settings

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

app.include_router(health.router)


@app.get("/", tags=["root"])
def root() -> dict:
    """Identifica el servicio."""
    return {"service": settings.app_name, "version": __version__, "docs": "/docs"}
