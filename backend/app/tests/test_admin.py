"""Tests del módulo Admin."""


def test_salud_fuentes_admin(client, db_session, headers_admin):
    resp = client.get("/api/v1/admin/salud-fuentes", headers=headers_admin)
    assert resp.status_code == 200
    assert "fuentes" in resp.json()["data"]


def test_salud_fuentes_sin_admin(client, db_session, headers_usuario):
    resp = client.get("/api/v1/admin/salud-fuentes", headers=headers_usuario)
    assert resp.status_code == 403


def test_salud_fuentes_sin_auth(client, db_session):
    resp = client.get("/api/v1/admin/salud-fuentes")
    assert resp.status_code == 401


def test_listar_usuarios_admin(client, db_session, headers_admin):
    resp = client.get("/api/v1/admin/usuarios", headers=headers_admin)
    assert resp.status_code == 200
    assert isinstance(resp.json()["data"], list)


def test_comentarios_reportados_admin(client, db_session, headers_admin):
    resp = client.get("/api/v1/admin/comentarios-reportados", headers=headers_admin)
    assert resp.status_code == 200
    assert isinstance(resp.json()["data"], list)
