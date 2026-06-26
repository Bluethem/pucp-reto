"""Tests del módulo Municipios/Entidades."""

import pytest


@pytest.fixture
def crear_entidad(db_session):
    from app.models.entidad import Entidad

    def _crear(**kwargs):
        datos = dict(nombre="Municipalidad Test", tipo="municipalidad_distrital",
                     departamento="Lima", provincia="Lima", distrito="Miraflores")
        datos.update(kwargs)
        entidad = Entidad(**datos)
        db_session.add(entidad)
        db_session.commit()
        db_session.refresh(entidad)
        return entidad

    return _crear


def test_listar_municipios(client, db_session, crear_entidad):
    crear_entidad()
    resp = client.get("/api/v1/municipios")
    assert resp.status_code == 200
    assert isinstance(resp.json()["data"], list)
    assert len(resp.json()["data"]) >= 1


def test_get_municipio_by_id(client, db_session, crear_entidad):
    entidad = crear_entidad()
    resp = client.get(f"/api/v1/municipios/{entidad.id}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["id"] == entidad.id
    assert "autoridades" in data


def test_get_municipio_inexistente(client, db_session):
    resp = client.get("/api/v1/municipios/no-existe")
    assert resp.status_code == 404


def test_municipio_obras(client, db_session, crear_entidad, crear_obra):
    entidad = crear_entidad()
    crear_obra(entidad_id=entidad.id)
    resp = client.get(f"/api/v1/municipios/{entidad.id}/obras")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) >= 1


def test_filtros_municipios(client, db_session, crear_entidad):
    crear_entidad(departamento="Cusco")
    resp = client.get("/api/v1/municipios", params={"departamento": "Cusco"})
    assert resp.status_code == 200
    assert all(e["departamento"] == "Cusco" for e in resp.json()["data"])
