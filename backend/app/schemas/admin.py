"""Schemas Pydantic del módulo Admin."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FuenteEstado(BaseModel):
    nombre: str
    estado: str  # up | down | desconocido
    ultima_actualizacion: datetime | None = None


class SaludFuentesResponse(BaseModel):
    fuentes: list[FuenteEstado] = []


class ComentarioReportadoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    usuario_id: str
    recurso_tipo: str
    recurso_id: str
    contenido: str
    reportado: bool
    oculto: bool
    created_at: datetime | None = None


class UsuarioAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    alias: str | None = None
    rol: str
