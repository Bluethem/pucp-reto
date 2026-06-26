"""MockDataSource para pruebas del motor de scoring.

Proporciona datos ficticios para testear sin depender de fuentes externas.
Implementa la interfaz DataSource (RNF-19, ADR-004).
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional


class PrecioReferenciaMock:
    def __init__(self, codigo_inei, insumo, unidad, precio, departamento=None,
                 mes=6, anio=2026, fuente="inei"):
        self.codigo_inei = codigo_inei
        self.insumo = insumo
        self.unidad = unidad
        self.precio = precio
        self.departamento = departamento
        self.mes = mes
        self.anio = anio
        self.fuente = fuente


PRECIOS_MOCK = {
    "CEM-001": PrecioReferenciaMock("CEM-001", "Cemento Portland Tipo I", "bolsa", Decimal("28.00")),
    "ACR-001": PrecioReferenciaMock("ACR-001", "Acero corrugado 1/2", "kg", Decimal("4.50")),
    "AGR-001": PrecioReferenciaMock("AGR-001", "Agregado grueso (piedra)", "m3", Decimal("55.00")),
    "AGR-002": PrecioReferenciaMock("AGR-002", "Agregado fino (arena)", "m3", Decimal("45.00")),
    "MAD-001": PrecioReferenciaMock("MAD-001", "Madera tornillo", "p2", Decimal("8.50")),
    "MAN-001": PrecioReferenciaMock("MAN-001", "Mano de obra albañil", "hh", Decimal("22.50")),
}

COSTO_M2_MOCK: dict[str, dict[str, Decimal]] = {
    "edificacion": {
        "Lima": Decimal("2800"),
        "Loreto": Decimal("3500"),
        "Cusco": Decimal("3200"),
        "Huancavelica": Decimal("3400"),
    },
    "carretera": {
        "Lima": Decimal("1200"),
        "Loreto": Decimal("1800"),
    },
}

FACTORES_REGIONALES_MOCK: dict[str, float] = {
    "Lima": 1.00,
    "Loreto": 1.35,
    "Cusco": 1.12,
    "Huancavelica": 1.25,
}


class MockDataSource:

    def obtener_precio_referencia(self, codigo_inei, departamento=None):
        precio = PRECIOS_MOCK.get(codigo_inei)
        if precio and departamento and precio.departamento is None:
            return PrecioReferenciaMock(
                precio.codigo_inei, precio.insumo, precio.unidad,
                precio.precio, departamento=departamento,
                mes=precio.mes, anio=precio.anio, fuente=precio.fuente,
            )
        return precio

    def obtener_costo_m2(self, tipo_obra, departamento):
        return COSTO_M2_MOCK.get(tipo_obra, {}).get(departamento)

    def obtener_factor_regional(self, departamento):
        return FACTORES_REGIONALES_MOCK.get(departamento, 1.0)

    def listar_factores_regionales(self):
        return dict(FACTORES_REGIONALES_MOCK)

    def get_metadata(self):
        return {"source": "mock", "version": "0.1.0"}

    def get_last_update(self):
        return datetime.now()
