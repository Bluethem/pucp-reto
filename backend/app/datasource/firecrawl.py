"""FirecrawlDataSource — descarga automática de PDFs desde INFOBRAS.

Usa Firecrawl para navegar INFOBRAS, encontrar el expediente técnico
de una obra y descargar el PDF. Luego pasa los bytes a Gemini API
para extraer las partidas estructuradas.

Flujo completo:
  1. Dado un código INFOBRAS de obra
  2. Firecrawl busca la página de la obra
  3. Extrae la URL del PDF del expediente técnico
  4. Firecrawl descarga el PDF (raw)
  5. Gemini extrae las partidas → JSON
  6. Retorna lista de partidas
"""

import re
from datetime import datetime
from typing import Optional

from firecrawl import FirecrawlApp as _FirecrawlApp

from app.core.config import settings


class FirecrawlError(RuntimeError):
    """Error durante la descarga o extracción con Firecrawl."""


class FirecrawlDataSource:
    """Descarga PDFs de expedientes desde INFOBRAS usando Firecrawl."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key if api_key is not None else settings.firecrawl_api_key

    def disponible(self) -> bool:
        return bool(self.api_key)

    def buscar_url_pdf(self, codigo_infobras: str) -> Optional[str]:
        """Busca la URL del PDF del expediente técnico en INFOBRAS.

        Dado un código INFOBRAS, usa Firecrawl para scrapear la página
        de la obra y encontrar el enlace al expediente técnico.
        """
        if not self.disponible():
            raise FirecrawlError("FIRECRAWL_API_KEY no configurada")

        try:
            app = _FirecrawlApp(api_key=self.api_key)
            url_busqueda = f"{settings.infobras_base_url}/ficha/{codigo_infobras}"

            pagina = app.scrape_url(url_busqueda, {"formats": ["html"]})
            contenido = pagina.get("html", "") if isinstance(pagina, dict) else str(pagina)

            pdf_urls = re.findall(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', contenido, re.I)
            if not pdf_urls:
                raise FirecrawlError(f"No se encontró PDF para obra {codigo_infobras}")

            # Retorna la primera URL absoluta de PDF
            pdf_url = pdf_urls[0]
            if pdf_url.startswith("/"):
                pdf_url = f"{settings.infobras_base_url}{pdf_url}"
            return pdf_url

        except Exception as exc:
            if isinstance(exc, FirecrawlError):
                raise
            raise FirecrawlError(f"Error buscando PDF en INFOBRAS: {exc}") from exc

    def descargar_pdf(self, url_pdf: str) -> bytes:
        """Descarga un PDF desde una URL usando Firecrawl."""
        if not self.disponible():
            raise FirecrawlError("FIRECRAWL_API_KEY no configurada")

        try:
            app = _FirecrawlApp(api_key=self.api_key)
            resultado = app.scrape_url(url_pdf, {"formats": ["raw"]})
            if isinstance(resultado, dict) and "raw" in resultado:
                return resultado["raw"]
            if isinstance(resultado, bytes):
                return resultado
            raise FirecrawlError(f"No se pudo descargar PDF: {str(resultado)[:200]}")
        except Exception as exc:
            if isinstance(exc, FirecrawlError):
                raise
            raise FirecrawlError(f"Error descargando PDF: {exc}") from exc

    def extraer_partidas_de_obra(self, codigo_infobras: str) -> list[dict]:
        """Pipeline completo: descarga PDF desde INFOBRAS y extrae partidas con Gemini.

        Args:
            codigo_infobras: Código único de la obra en INFOBRAS.

        Returns:
            Lista de partidas: [{insumo, unidad, cantidad, precio_unitario}, ...]

        Raises:
            FirecrawlError: Si no se puede descargar el PDF o extraer partidas.
        """
        if not settings.gemini_api_key:
            raise FirecrawlError("GEMINI_API_KEY no configurada")

        from app.datasource.gemini import GeminiDataSource

        url_pdf = self.buscar_url_pdf(codigo_infobras)
        pdf_bytes = self.descargar_pdf(url_pdf)

        gemini = GeminiDataSource(api_key=settings.gemini_api_key)
        return gemini.extraer_partidas(pdf_bytes)

    def get_metadata(self) -> dict:
        return {
            "source": "firecrawl",
            "disponible": self.disponible(),
            "gemini_configurado": bool(settings.gemini_api_key),
        }

    def get_last_update(self) -> Optional[datetime]:
        return datetime.utcnow()
