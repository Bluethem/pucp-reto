"""Schemas Pydantic del módulo Municipios/Entidades."""

from pydantic import BaseModel, ConfigDict

from app.schemas.autoridad import AutoridadResponse


class EntidadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nombre: str
    tipo: str | None = None
    departamento: str | None = None
    provincia: str | None = None
    distrito: str | None = None
    ubigeo: str | None = None


class EntidadDetailResponse(EntidadResponse):
    autoridades: list[AutoridadResponse] = []
