"""Schemas Pydantic del módulo Comentarios."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RecursoTipo = Literal["obra", "empresa", "municipio", "autoridad"]


class ComentarioRequest(BaseModel):
    recurso_tipo: RecursoTipo
    recurso_id: str
    contenido: str = Field(min_length=1, max_length=2000)
    padre_id: str | None = None


class ComentarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    usuario_id: str
    recurso_tipo: str
    recurso_id: str
    contenido: str
    padre_id: str | None = None
    reportado: bool = False
    created_at: datetime | None = None
