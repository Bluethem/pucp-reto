"""Tests del módulo Comentarios."""

RECURSO = {"recurso_tipo": "obra", "recurso_id": "obra-123"}


def test_listar_comentarios_publico(client, db_session):
    resp = client.get("/api/v1/comentarios", params=RECURSO)
    assert resp.status_code == 200
    assert isinstance(resp.json()["data"], list)


def test_crear_comentario(client, db_session, headers_usuario):
    resp = client.post(
        "/api/v1/comentarios",
        json={**RECURSO, "contenido": "Esta obra parece tener sobreprecios."},
        headers=headers_usuario,
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["contenido"].startswith("Esta obra")


def test_crear_comentario_sin_auth(client, db_session):
    resp = client.post("/api/v1/comentarios", json={**RECURSO, "contenido": "Hola"})
    assert resp.status_code == 401


def test_eliminar_propio_comentario(client, db_session, headers_usuario):
    creado = client.post(
        "/api/v1/comentarios",
        json={**RECURSO, "contenido": "Comentario a borrar"},
        headers=headers_usuario,
    ).json()["data"]
    resp = client.delete(f"/api/v1/comentarios/{creado['id']}", headers=headers_usuario)
    assert resp.status_code == 204


def test_reportar_comentario(client, db_session, headers_usuario):
    creado = client.post(
        "/api/v1/comentarios",
        json={**RECURSO, "contenido": "Comentario a reportar"},
        headers=headers_usuario,
    ).json()["data"]
    resp = client.post(f"/api/v1/comentarios/{creado['id']}/reportar", headers=headers_usuario)
    assert resp.status_code == 200
    assert resp.json()["data"]["reportado"] is True
