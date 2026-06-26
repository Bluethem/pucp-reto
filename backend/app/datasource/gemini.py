"""GeminiDataSource — extracción de partidas desde PDFs de expedientes (ADR-001).

Envía el PDF a Gemini con un prompt estructurado y recibe un JSON con las
partidas (insumo, unidad, cantidad, precio_unitario). Si no hay API key
configurada, lanza un error controlado para que el pipeline use el fallback
costo/m² (RF-SCO-08).
"""

import json
from datetime import datetime
from typing import Optional

from app.core.config import settings

PROMPT_EXTRACCION = (
    "Extrae la tabla de partidas del siguiente expediente técnico. "
    "Devuelve EXCLUSIVAMENTE un array JSON de objetos con las claves exactas: "
    '"insumo", "unidad", "cantidad", "precio_unitario". '
    "No incluyas texto adicional ni explicaciones."
)


class GeminiExtractionError(RuntimeError):
    """La extracción con Gemini no fue posible (sin API key, error de red, etc.)."""


class GeminiDataSource:
    """Extractor de partidas basado en Gemini API."""

    def __init__(self, api_key: str | None = None, modelo: str = "gemini-1.5-flash"):
        self.api_key = api_key if api_key is not None else settings.gemini_api_key
        self.modelo = modelo

    def disponible(self) -> bool:
        return bool(self.api_key)

    def extraer_partidas(self, pdf_bytes: bytes) -> list[dict]:
        """Extrae partidas de un PDF. Lanza GeminiExtractionError si no es posible."""
        if not self.disponible():
            raise GeminiExtractionError("GEMINI_API_KEY no configurada")

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.modelo)
            respuesta = model.generate_content(
                [PROMPT_EXTRACCION, {"mime_type": "application/pdf", "data": pdf_bytes}]
            )
            return self._parsear_respuesta(respuesta.text)
        except GeminiExtractionError:
            raise
        except Exception as exc:  # noqa: BLE001 — el pipeline cae a fallback
            raise GeminiExtractionError(str(exc)) from exc

    @staticmethod
    def _parsear_respuesta(texto: str) -> list[dict]:
        texto = texto.strip()
        if texto.startswith("```"):
            texto = texto.strip("`")
            texto = texto[texto.find("[") :] if "[" in texto else texto
        try:
            datos = json.loads(texto)
        except json.JSONDecodeError as exc:
            raise GeminiExtractionError(f"Error parseando JSON de Gemini: {exc}") from exc
        if not isinstance(datos, list):
            raise GeminiExtractionError("Respuesta de Gemini no es una lista de partidas")
        return datos

    def get_metadata(self) -> dict:
        return {"source": "gemini", "modelo": self.modelo, "disponible": self.disponible()}

    def get_last_update(self) -> Optional[datetime]:
        return datetime.utcnow()
