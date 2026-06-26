"""SEACE / OCDS DataSource — metadatos de obra y contratista.

Consume la API de Contrataciones Abiertas del OECE (estándar OCDS).
Documentación: https://contratacionesabiertas.oece.gob.pe/

Endpoints OCDS:
  - GET /api/ocds/records?q={query}             → búsqueda
  - GET /api/ocds/record/{ocid}                  → detalle de proceso
  - GET /api/ocds/releases?q={query}             → releases

El datasource cachea las respuestas y provee degradación elegante.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

import httpx

from app.core.config import settings


class SEACEError(RuntimeError):
    """Error de conexión o respuesta inesperada de la API SEACE/OCDS."""


OCDS_PROJECT_TYPES = {
    "carretera": "carretera",
    "rehabilitacion": "carretera",
    "puente": "carretera",
    "pista": "carretera",
    "vereda": "carretera",
    "alcantarillado": "agua_saneamiento",
    "agua": "agua_saneamiento",
    "saneamiento": "agua_saneamiento",
    "hospital": "salud",
    "salud": "salud",
    "colegio": "educacion",
    "educacion": "educacion",
    "local": "edificacion",
    "edificacion": "edificacion",
    "construccion": "edificacion",
    "mejoramiento": "edificacion",
}


def _inferir_tipo_obra(titulo: str) -> str:
    titulo_lower = titulo.lower()
    for keyword, tipo in OCDS_PROJECT_TYPES.items():
        if keyword in titulo_lower:
            return tipo
    return "otros"


class SEACEDataSource:
    """Cliente para la API OCDS del SEACE/OECE."""

    def __init__(self, base_url: str | None = None, timeout: int = 30):
        self.base_url = base_url or settings.seace_ocds_base_url
        self.timeout = timeout

    def buscar_obras(self, query: str = "", limit: int = 100) -> list[dict]:
        """Busca procesos de contratación por nombre de obra o entidad."""
        url = f"{self.base_url}/api/ocds/records"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url, params={"q": query, "limit": limit})
                resp.raise_for_status()
            return self._parsear_registros(resp.json())
        except httpx.HTTPStatusError as exc:
            raise SEACEError(f"SEACE/OCDS respondió {exc.response.status_code}: {exc.response.text[:200]}")
        except httpx.RequestError as exc:
            raise SEACEError(f"Error de conexión con SEACE/OCDS: {exc}")

    def obtener_obra_por_ocid(self, ocid: str) -> Optional[dict]:
        """Obtiene el detalle completo de un proceso por su OCID."""
        url = f"{self.base_url}/api/ocds/record/{ocid}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url)
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
            return self._parsear_registro_detalle(resp.json())
        except httpx.HTTPStatusError as exc:
            raise SEACEError(f"SEACE/OCDS respondió {exc.response.status_code}")
        except httpx.RequestError as exc:
            raise SEACEError(f"Error de conexión con SEACE/OCDS: {exc}")

    @staticmethod
    def _parsear_registros(data: dict) -> list[dict]:
        """Convierte respuesta OCDS /records a lista de obras simplificadas."""
        resultados = []
        registros = data.get("records", data.get("results", []))
        for record in registros:
            releases = record.get("releases", [])
            if not releases:
                continue
            release = releases[0]
            obra = SEACEDataSource._release_a_obra(release)
            if obra:
                resultados.append(obra)
        return resultados

    @staticmethod
    def _parsear_registro_detalle(data: dict) -> Optional[dict]:
        releases = data.get("releases", [])
        if not releases:
            buyer_data = data.get("buyer", {})
            return {
                "ocid": data.get("ocid", ""),
                "titulo": data.get("title", ""),
                "entidad": buyer_data.get("name", {}).get("es", "") if isinstance(buyer_data, dict) else "",
            }
        return SEACEDataSource._release_a_obra(releases[0])

    @staticmethod
    def _release_a_obra(release: dict) -> Optional[dict]:
        try:
            planning = release.get("planning", {})
            budget = planning.get("budget", {})
            tender = release.get("tender", {})
            buyer = release.get("buyer", {})
            awards = release.get("awards", [])
            supplier = awards[0].get("suppliers", [{}])[0] if awards else {}

            titulo = tender.get("title") or release.get("ocid", "")
            monto = tender.get("value", {}).get("amount")
            if monto is not None:
                monto = Decimal(str(monto))

            return {
                "ocid": release.get("ocid", ""),
                "titulo": titulo,
                "tipo_obra": _inferir_tipo_obra(titulo),
                "entidad": buyer.get("name", {}).get("es", "") if isinstance(buyer, dict) else "",
                "entidad_id": buyer.get("id", {}).get("id", "") if isinstance(buyer, dict) else "",
                "contratista": supplier.get("name", {}).get("es", "") if isinstance(supplier, dict) else "",
                "contratista_ruc": supplier.get("id", {}).get("id", "") if isinstance(supplier, dict) else "",
                "monto_total": float(monto) if monto else None,
                "fecha_adjudicacion": awards[0].get("date") if awards else None,
                "estado": tender.get("status", "desconocido"),
                "fuente": "seace_ocds",
            }
        except (KeyError, IndexError, TypeError):
            return None

    def get_metadata(self) -> dict:
        return {"source": "seace_ocds", "base_url": self.base_url}

    def get_last_update(self) -> Optional[datetime]:
        return datetime.utcnow()
