"""Schemas Pydantic del módulo Scoring."""

from pydantic import BaseModel


class PartidaScoreResponse(BaseModel):
    insumo: str | None = None
    unidad: str | None = None
    cantidad: float | None = None
    precio_declarado: float | None = None
    precio_referencia: float | None = None
    ratio: float | None = None
    fuente: str | None = None
    departamento: str | None = None
    factor_regional: float | None = None
    es_alerta: bool | None = None
    comparable: bool | None = None


class ScoreResponse(BaseModel):
    obra_id: str
    score: int
    clasificacion: str
    nivel_riesgo: str | None = None
    modo_analisis: str
    total_partidas: int
    partidas_comparables: int
    alertas: int
    partidas: list[PartidaScoreResponse] = []
