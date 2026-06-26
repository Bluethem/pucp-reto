"""Tests del módulo Empresas/Contratistas."""

import pytest


@pytest.fixture
def crear_contratista(db_session):
    from app.models.contratista import Contratista
    import uuid

    def _crear(**kwargs):
        datos = dict(ruc=f"20{uuid.uuid4().hex[:9].upper()}", razon_social="Constructora Test SAC",
                     representante_legal="Ana Gómez", estado_sunat="ACTIVO",
                     score_confiabilidad=70)
        datos.update(kwargs)
        contratista = Contratista(**datos)
        db_session.add(contratista)
        db_session.commit()
        db_session.refresh(contratista)
        return contratista

    return _crear


def test_listar_empresas(client, db_session, crear_contratista):
    crear_contratista()
    resp = client.get("/api/v1/empresas")
    assert resp.status_code == 200
    assert isinstance(resp.json()["data"], list)
    assert len(resp.json()["data"]) >= 1


def test_get_empresa_by_id(client, db_session, crear_contratista):
    contratista = crear_contratista()
    resp = client.get(f"/api/v1/empresas/{contratista.id}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["ruc"] == contratista.ruc
    assert "total_obras" in data
    assert "nivel_confiabilidad" in data


def test_get_empresa_inexistente(client, db_session):
    resp = client.get("/api/v1/empresas/no-existe")
    assert resp.status_code == 404


def test_empresa_obras(client, db_session, crear_contratista, crear_obra):
    contratista = crear_contratista()
    crear_obra(contratista_id=contratista.id)
    resp = client.get(f"/api/v1/empresas/{contratista.id}/obras")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) >= 1


def test_filtro_ruc(client, db_session, crear_contratista):
    crear_contratista(ruc="20999999999")
    resp = client.get("/api/v1/empresas", params={"ruc": "20999999999"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["ruc"] == "20999999999"
