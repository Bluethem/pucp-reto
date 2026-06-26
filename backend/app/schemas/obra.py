"""Schemas Pydantic del módulo Obras."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator

from app.core.utils import nivel_riesgo


class PartidaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    insumo: str
    codigo_inei: str | None = None
    unidad: str | None = None
    cantidad: float | None = None
    precio_declarado: float | None = None
    precio_referencia_inei: float | None = None
    ratio: float | None = None


class ObraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    codigo_infobras: str
    titulo: str
    tipo_obra: str | None = None
    estado: str | None = None
    presupuesto_total: float | None = None
    departamento: str | None = None
    provincia: str | None = None
    distrito: str | None = None
    score_riesgo: int | None = None
    modo_analisis: str | None = None
    nivel_riesgo: str | None = None

    @model_validator(mode="after")
    def _set_nivel(self):
        self.nivel_riesgo = nivel_riesgo(self.score_riesgo)
        return self


class ObraDetailResponse(ObraResponse):
    partidas: list[PartidaResponse] = []


class ObraGeoResponse(BaseModel):
    id: str
    titulo: str
    tipo_obra: str | None = None
    estado: str | None = None
    score_riesgo: int | None = None
    nivel_riesgo: str | None = None
    lat: float | None = None
    lon: float | None = None


class ObraExtraerRequest(BaseModel):
    codigo_infobras: str
    titulo: Optional[str] = None
    departamento: Optional[str] = None


class ObraExtraerResponse(BaseModel):
    obra: ObraResponse
    score: dict | None = None
    partidas: list[PartidaResponse] = []


class ObraFilterParams(BaseModel):
    departamento: str | None = None
    tipo_obra: str | None = None
    estado: str | None = None
    nivel: str | None = None
    skip: int = 0
    limit: int = 100
