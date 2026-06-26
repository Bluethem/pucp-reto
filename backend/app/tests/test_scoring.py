"""Tests del motor de scoring (determinista y trazable)."""

from decimal import Decimal

from app.models.partida import PartidaObra
from app.models.precio_referencia import PrecioReferencia
from app.services.scoring_service import ScoringService


def _seed_precio(db, codigo, precio, departamento=None, fuente="inei", insumo="Insumo", mes=6, anio=2026):
    db.add(
        PrecioReferencia(
            codigo_inei=codigo, insumo=insumo, unidad="u",
            precio=Decimal(str(precio)), departamento=departamento,
            mes=mes, anio=anio, fuente=fuente,
        )
    )
    db.commit()


def _add_partida(db, obra_id, codigo, precio_declarado, cantidad=100, insumo="Cemento"):
    db.add(
        PartidaObra(
            obra_id=obra_id, insumo=insumo, codigo_inei=codigo, unidad="bolsa",
            cantidad=Decimal(str(cantidad)), precio_declarado=Decimal(str(precio_declarado)),
        )
    )
    db.commit()


def test_scoring_con_partidas_validas(db_session, crear_obra):
    _seed_precio(db_session, "CEM-001", 28, departamento=None)
    obra = crear_obra(departamento="Lima")
    _add_partida(db_session, obra.id, "CEM-001", precio_declarado=40)

    resultado = ScoringService(db_session).calcular_score(obra.id)
    assert resultado.modo_analisis == "partidas"
    assert resultado.score > 0  # 40/28 ≈ 1.43 → sobreprecio
    assert resultado.clasificacion in ("verde", "amarillo", "rojo")


def test_scoring_fallback_m2(db_session, crear_obra):
    _seed_precio(db_session, "M2-EDIF", 2800, departamento="Lima",
                 fuente="mvivienda", insumo="edificacion")
    obra = crear_obra(departamento="Lima", metrado_total=300, presupuesto_total=1000000)
    # Sin partidas → fallback costo/m²

    resultado = ScoringService(db_session).calcular_score(obra.id)
    assert resultado.modo_analisis == "fallback_m2"
    assert resultado.score >= 0


def test_scoring_insumo_sin_referencia(db_session, crear_obra):
    obra = crear_obra(departamento="Lima")
    _add_partida(db_session, obra.id, "NO-EXISTE", precio_declarado=40)

    resultado = ScoringService(db_session).calcular_score(obra.id)
    partida = resultado.partidas[0]
    assert partida.comparable is False
    assert partida.fuente == "no_disponible"


def test_scoring_determinista(db_session, crear_obra):
    _seed_precio(db_session, "CEM-001", 28, departamento=None)
    obra = crear_obra(departamento="Lima")
    _add_partida(db_session, obra.id, "CEM-001", precio_declarado=40)

    score1 = ScoringService(db_session).calcular_score(obra.id).score
    score2 = ScoringService(db_session).calcular_score(obra.id).score
    assert score1 == score2


def test_scoring_explicacion_trazable(db_session, crear_obra):
    _seed_precio(db_session, "CEM-001", 28, departamento=None)
    obra = crear_obra(departamento="Lima")
    _add_partida(db_session, obra.id, "CEM-001", precio_declarado=40)

    d = ScoringService(db_session).calcular_score(obra.id).to_dict()
    assert "partidas" in d and len(d["partidas"]) == 1
    assert "ratio" in d["partidas"][0]
    assert "total_partidas" in d


def test_score_endpoint(client, db_session, crear_obra):
    _seed_precio(db_session, "CEM-001", 28, departamento=None)
    obra = crear_obra(departamento="Lima")
    _add_partida(db_session, obra.id, "CEM-001", precio_declarado=40)

    resp = client.get(f"/api/v1/obras/{obra.id}/score")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["obra_id"] == obra.id
    assert "score" in data and "partidas" in data


def test_recalcular_requiere_admin(client, db_session, crear_obra):
    obra = crear_obra()
    resp = client.post(f"/api/v1/obras/{obra.id}/recalcular")
    assert resp.status_code == 401
