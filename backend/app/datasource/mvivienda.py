"""DataSource para los Valores Unitarios Oficiales del Ministerio de Vivienda.

Provee:
- Costo por m² por departamento y tipo de edificación (fallback RF-SCO-08)
- Factores de ajuste regional para contexto visual

Los Valores Unitarios Oficiales se publican anualmente vía Resolución Ministerial.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.core.database import SessionLocal
from app.datasource.interface import DataSource
from app.models.precio_referencia import PrecioReferencia


# Factores de ajuste regional estimados basados en Valores Unitarios MVCS
FACTORES_REGIONALES: dict[str, float] = {
    "Lima": 1.00,
    "Callao": 1.02,
    "Arequipa": 1.05,
    "Ica": 1.03,
    "Cusco": 1.12,
    "Junín": 1.08,
    "Piura": 1.06,
    "La Libertad": 1.04,
    "Lambayeque": 1.04,
    "Tumbes": 1.10,
    "Moquegua": 1.05,
    "Tacna": 1.05,
    "Puno": 1.15,
    "Cajamarca": 1.18,
    "Huánuco": 1.18,
    "Pasco": 1.20,
    "Ayacucho": 1.20,
    "San Martín": 1.22,
    "Huancavelica": 1.25,
    "Apurímac": 1.25,
    "Amazonas": 1.28,
    "Ucayali": 1.30,
    "Loreto": 1.35,
    "Madre de Dios": 1.40,
}


class MviviendaDataSource(DataSource):

    def obtener_costo_m2(
        self,
        tipo_obra: str,
        departamento: str,
    ) -> Optional[Decimal]:
        """Retorna el costo por m² del MVCS para un departamento y tipo de obra."""
        db = SessionLocal()
        try:
            resultado = (
                db.query(PrecioReferencia)
                .filter(
                    PrecioReferencia.fuente == "mvivienda",
                    PrecioReferencia.departamento == departamento,
                    PrecioReferencia.insumo.ilike(f"%{tipo_obra}%"),
                )
                .order_by(PrecioReferencia.anio.desc(), PrecioReferencia.mes.desc())
                .first()
            )
            if resultado:
                return resultado.precio
            return None
        finally:
            db.close()

    def obtener_factor_regional(self, departamento: str) -> float:
        """Retorna el factor de ajuste regional para un departamento."""
        return FACTORES_REGIONALES.get(departamento, 1.0)

    def listar_factores_regionales(self) -> dict[str, float]:
        """Retorna todos los factores de ajuste regional."""
        return dict(FACTORES_REGIONALES)

    def obtener_precio_referencia(self, codigo_inei, departamento=None):
        return None

    def get_metadata(self) -> dict:
        return {"source": "mvivienda", "type": "costos_m2"}

    def get_last_update(self) -> Optional[datetime]:
        db = SessionLocal()
        try:
            resultado = (
                db.query(PrecioReferencia)
                .filter(PrecioReferencia.fuente == "mvivienda")
                .order_by(PrecioReferencia.anio.desc(), PrecioReferencia.mes.desc())
                .first()
            )
            if resultado:
                return datetime(resultado.anio, resultado.mes, 1)
            return None
        finally:
            db.close()
