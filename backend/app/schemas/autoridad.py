"""Schemas Pydantic del módulo Autoridades (solo datos públicos del JNE)."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class AutoridadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    entidad_id: str | None = None
    nombre: str
    cargo: str | None = None
    partido: str | None = None
    periodo_inicio: date | None = None
    periodo_fin: date | None = None
    foto_url: str | None = None
