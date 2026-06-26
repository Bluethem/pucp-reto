"""Tests del módulo Suscripciones."""

RECURSO = {"recurso_tipo": "obra", "recurso_id": "obra-abc"}


def test_crear_suscripcion(client, db_session, headers_usuario):
    resp = client.post("/api/v1/suscripciones", json=RECURSO, headers=headers_usuario)
    assert resp.status_code == 201
    assert resp.json()["data"]["recurso_id"] == "obra-abc"


def test_listar_suscripciones(client, db_session, headers_usuario):
    client.post("/api/v1/suscripciones", json=RECURSO, headers=headers_usuario)
    resp = client.get("/api/v1/suscripciones", headers=headers_usuario)
    assert resp.status_code == 200
    assert len(resp.json()["data"]) >= 1


def test_suscripcion_duplicada(client, db_session, headers_usuario):
    client.post("/api/v1/suscripciones", json=RECURSO, headers=headers_usuario)
    resp = client.post("/api/v1/suscripciones", json=RECURSO, headers=headers_usuario)
    assert resp.status_code == 409


def test_suscripcion_sin_auth(client, db_session):
    resp = client.post("/api/v1/suscripciones", json=RECURSO)
    assert resp.status_code == 401


def test_eliminar_suscripcion(client, db_session, headers_usuario):
    creada = client.post(
        "/api/v1/suscripciones", json=RECURSO, headers=headers_usuario
    ).json()["data"]
    resp = client.delete(f"/api/v1/suscripciones/{creada['id']}", headers=headers_usuario)
    assert resp.status_code == 204
