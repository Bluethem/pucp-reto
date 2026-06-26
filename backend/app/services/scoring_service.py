"""Motor de scoring determinista y trazable.

Compara los precios declarados en las partidas del expediente técnico
contra los precios de referencia INEI (nacional) con contexto regional
del Ministerio de Vivienda.

Flujo:
  1. Obtener partidas de la obra
  2. Para cada partida:
     a. Buscar precio de referencia INEI (primero regional, luego nacional)
     b. Si no hay precio → marcar "no comparable" (RF-SCO-10)
     c. Calcular ratio = precio_declarado / precio_referencia
  3. Score global 0-100 = promedio ponderado de ratios
  4. Clasificar: verde(0-40) / amarillo(41-60) / rojo(61-100)
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models.obra import Obra
from app.models.partida import PartidaObra
from app.models.precio_referencia import PrecioReferencia


CLASIFICACION = [
    ("verde", 0, 40),
    ("amarillo", 41, 60),
    ("rojo", 61, 100),
]

UMBRAL_ALERTA = Decimal("1.3")


class ResultadoPartida:
    def __init__(self, insumo: str, unidad: str, cantidad: Decimal,
                 precio_declarado: Decimal, precio_referencia: Optional[Decimal],
                 ratio: Optional[Decimal], fuente: str, departamento: Optional[str],
                 factor_regional: float):
        self.insumo = insumo
        self.unidad = unidad
        self.cantidad = cantidad
        self.precio_declarado = precio_declarado
        self.precio_referencia = precio_referencia
        self.ratio = ratio
        self.fuente = fuente
        self.departamento = departamento
        self.factor_regional = factor_regional

    def to_dict(self) -> dict:
        return {
            "insumo": self.insumo,
            "unidad": self.unidad,
            "cantidad": float(self.cantidad) if self.cantidad else None,
            "precio_declarado": float(self.precio_declarado) if self.precio_declarado else None,
            "precio_referencia": float(self.precio_referencia) if self.precio_referencia else None,
            "ratio": float(self.ratio) if self.ratio else None,
            "fuente": self.fuente,
            "departamento": self.departamento,
            "factor_regional": self.factor_regional,
            "es_alerta": bool(self.ratio and self.ratio >= UMBRAL_ALERTA),
            "comparable": self.precio_referencia is not None,
        }


class ResultadoScore:
    def __init__(self, score: int, clasificacion: str, partidas: list[ResultadoPartida],
                 modo_analisis: str, factores_regionales: dict[str, float]):
        self.score = score
        self.clasificacion = clasificacion
        self.partidas = partidas
        self.modo_analisis = modo_analisis
        self.factores_regionales = factores_regionales

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "clasificacion": self.clasificacion,
            "modo_analisis": self.modo_analisis,
            "partidas": [p.to_dict() for p in self.partidas],
            "factores_regionales": self.factores_regionales,
            "total_partidas": len(self.partidas),
            "partidas_comparables": sum(1 for p in self.partidas if p.comparable),
            "alertas": sum(1 for p in self.partidas if p.es_alerta),
        }


def _clasificar(score: int) -> str:
    for nombre, minimo, maximo in CLASIFICACION:
        if minimo <= score <= maximo:
            return nombre
    return "verde"


class ScoringService:

    def __init__(self, db: Session):
        self.db = db

    def obtener_precio_referencia(
        self, codigo_inei: str, departamento: Optional[str] = None
    ) -> tuple[Optional[Decimal], str, Optional[str]]:
        """Busca precio de referencia: primero regional, luego nacional.

        Returns:
            (precio, fuente, departamento_usado)
        """
        if departamento:
            regional = (
                self.db.query(PrecioReferencia)
                .filter(
                    PrecioReferencia.codigo_inei == codigo_inei,
                    PrecioReferencia.departamento == departamento,
                )
                .order_by(PrecioReferencia.anio.desc(), PrecioReferencia.mes.desc())
                .first()
            )
            if regional:
                return regional.precio, "inei_regional", departamento

        nacional = (
            self.db.query(PrecioReferencia)
            .filter(
                PrecioReferencia.codigo_inei == codigo_inei,
                PrecioReferencia.departamento.is_(None),
            )
            .order_by(PrecioReferencia.anio.desc(), PrecioReferencia.mes.desc())
            .first()
        )
        if nacional:
            return nacional.precio, "inei_nacional", None

        return None, "no_disponible", None

    def calcular_score(self, obra_id: str) -> ResultadoScore:
        obra = self.db.query(Obra).filter(Obra.id == obra_id).first()
        if not obra:
            raise ValueError(f"Obra {obra_id} no encontrada")

        partidas = self.db.query(PartidaObra).filter(PartidaObra.obra_id == obra_id).all()

        if not partidas or not any(p.codigo_inei for p in partidas):
            return self._score_fallback(obra)

        return self._score_por_partidas(partidas, obra.departamento)

    def _score_por_partidas(
        self, partidas: list[PartidaObra], departamento: Optional[str]
    ) -> ResultadoScore:
        resultados: list[ResultadoPartida] = []
        total_ponderado = Decimal("0")
        peso_total = Decimal("0")

        # Factores regionales para contexto visual
        from app.datasource.mvivienda import FACTORES_REGIONALES

        for partida in partidas:
            precio_ref, fuente, dpto_usado = self.obtener_precio_referencia(
                partida.codigo_inei, departamento if partida.codigo_inei else None,
            )

            dpto_efectivo = dpto_usado or departamento
            factor = FACTORES_REGIONALES.get(dpto_efectivo or "", 1.0)

            ratio = None
            if precio_ref and partida.precio_declarado and precio_ref > 0:
                ratio = partida.precio_declarado / precio_ref

            resultados.append(ResultadoPartida(
                insumo=partida.insumo,
                unidad=partida.unidad,
                cantidad=partida.cantidad,
                precio_declarado=partida.precio_declarado,
                precio_referencia=precio_ref,
                ratio=ratio,
                fuente=fuente,
                departamento=dpto_efectivo,
                factor_regional=factor,
            ))

            if ratio is not None and partida.cantidad:
                total_ponderado += ratio * partida.cantidad
                peso_total += partida.cantidad

        score = 0
        if peso_total > 0:
            score = min(int((total_ponderado / peso_total - 1) * 100), 100)
            score = max(score, 0)

        clasificacion = _clasificar(score)

        return ResultadoScore(
            score=score,
            clasificacion=clasificacion,
            partidas=resultados,
            modo_analisis="partidas",
            factores_regionales=dict(FACTORES_REGIONALES),
        )

    def _score_fallback(self, obra: Obra) -> ResultadoScore:
        """Fallback RF-SCO-08: comparación por costo/m²."""
        from app.datasource.mvivienda import MviviendaDataSource, FACTORES_REGIONALES

        mvivienda = MviviendaDataSource()
        costo_m2_referencia = mvivienda.obtener_costo_m2(
            obra.tipo_obra, obra.departamento or "Lima",
        )

        resultado_partida = ResultadoPartida(
            insumo=f"Costo total por m² ({obra.tipo_obra})",
            unidad="m²",
            cantidad=obra.metrado_total,
            precio_declarado=(
                obra.presupuesto_total / obra.metrado_total
                if obra.metrado_total and obra.metrado_total > 0
                else None
            ),
            precio_referencia=costo_m2_referencia,
            ratio=(
                (obra.presupuesto_total / obra.metrado_total) / costo_m2_referencia
                if obra.metrado_total and obra.metrado_total > 0 and costo_m2_referencia
                else None
            ),
            fuente="mvivienda" if costo_m2_referencia else "no_disponible",
            departamento=obra.departamento,
            factor_regional=FACTORES_REGIONALES.get(obra.departamento or "", 1.0),
        )

        # Score basado en el ratio único
        ratio = resultado_partida.ratio
        score = 0
        if ratio:
            score = min(int((ratio - 1) * 100), 100)
            score = max(score, 0)

        return ResultadoScore(
            score=score,
            clasificacion=_clasificar(score),
            partidas=[resultado_partida],
            modo_analisis="fallback_m2",
            factores_regionales=dict(FACTORES_REGIONALES),
        )
