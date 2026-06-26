"""Schemas Pydantic del módulo Suscripciones."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

RecursoTipo = Literal["obra", "empresa", "municipio", "autoridad"]


class SuscripcionRequest(BaseModel):
    recurso_tipo: RecursoTipo
    recurso_id: str


class SuscripcionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    usuario_id: str
    recurso_tipo: str
    recurso_id: str
    created_at: datetime | None = None
