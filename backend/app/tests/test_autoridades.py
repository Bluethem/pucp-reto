"""Tests del módulo Autoridades."""

import pytest


@pytest.fixture
def crear_autoridad(db_session):
    from app.models.autoridad import Autoridad
    from app.models.entidad import Entidad

    def _crear(**kwargs):
        entidad = Entidad(nombre="Muni Test", tipo="municipalidad_distrital", departamento="Lima")
        db_session.add(entidad)
        db_session.commit()
        datos = dict(entidad_id=entidad.id, nombre="Juan Pérez", cargo="alcalde", partido="Partido X")
        datos.update(kwargs)
        autoridad = Autoridad(**datos)
        db_session.add(autoridad)
        db_session.commit()
        db_session.refresh(autoridad)
        return autoridad

    return _crear


def test_listar_autoridades(client, db_session, crear_autoridad):
    crear_autoridad()
    resp = client.get("/api/v1/autoridades")
    assert resp.status_code == 200
    assert isinstance(resp.json()["data"], list)
    assert len(resp.json()["data"]) >= 1


def test_get_autoridad_by_id(client, db_session, crear_autoridad):
    autoridad = crear_autoridad()
    resp = client.get(f"/api/v1/autoridades/{autoridad.id}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["id"] == autoridad.id
    assert "obras" in data
    assert "descargo" in data  # no acusa: descargo siempre presente


def test_get_autoridad_inexistente(client, db_session):
    resp = client.get("/api/v1/autoridades/no-existe")
    assert resp.status_code == 404


def test_filtros_autoridades(client, db_session, crear_autoridad):
    autoridad = crear_autoridad()
    resp = client.get("/api/v1/autoridades", params={"entidad_id": autoridad.entidad_id})
    assert resp.status_code == 200
    assert all(a["entidad_id"] == autoridad.entidad_id for a in resp.json()["data"])
