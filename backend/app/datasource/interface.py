from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Optional


class PrecioReferencia(ABC):
    insumo: str
    codigo_inei: str
    unidad: str
    precio: Decimal
    departamento: Optional[str]
    mes: int
    anio: int
    fuente: str


class DataSource(ABC):

    @abstractmethod
    def obtener_precio_referencia(
        self,
        codigo_inei: str,
        departamento: Optional[str] = None,
    ) -> Optional[PrecioReferencia]:
        ...

    @abstractmethod
    def obtener_costo_m2(
        self,
        tipo_obra: str,
        departamento: str,
    ) -> Optional[Decimal]:
        ...

    @abstractmethod
    def get_metadata(self) -> dict:
        ...

    @abstractmethod
    def get_last_update(self) -> Optional[datetime]:
        ...
