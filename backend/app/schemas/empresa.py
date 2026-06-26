"""Schemas Pydantic del módulo Empresas/Contratistas."""

from pydantic import BaseModel, ConfigDict, model_validator

from app.core.utils import nivel_riesgo


class ContratistaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ruc: str
    razon_social: str
    representante_legal: str | None = None
    estado_sunat: str | None = None
    score_confiabilidad: int | None = None
    nivel_confiabilidad: str | None = None

    @model_validator(mode="after")
    def _set_nivel(self):
        self.nivel_confiabilidad = nivel_riesgo(self.score_confiabilidad)
        return self


class ContratistaDetailResponse(ContratistaResponse):
    total_obras: int = 0
