"""Tests del módulo Auth."""


def test_register_exitoso(client, db_session):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "nuevo@test.com", "password": "password123", "alias": "nuevo"},
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert "access_token" in data
    assert data["user"]["email"] == "nuevo@test.com"


def test_register_email_duplicado(client, db_session):
    payload = {"email": "dup@test.com", "password": "password123"}
    client.post("/api/v1/auth/register", json=payload)
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409


def test_register_password_invalida(client, db_session):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "x@test.com", "password": "123"},
    )
    assert resp.status_code == 422


def test_login_exitoso(client, db_session):
    client.post(
        "/api/v1/auth/register",
        json={"email": "login@test.com", "password": "password123"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.com", "password": "password123"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()["data"]


def test_login_credenciales_invalidas(client, db_session):
    client.post(
        "/api/v1/auth/register",
        json={"email": "wrong@test.com", "password": "password123"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@test.com", "password": "incorrecta"},
    )
    assert resp.status_code == 401


def test_get_me_sin_token(client, db_session):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_get_me_con_token(client, db_session, headers_usuario):
    resp = client.get("/api/v1/auth/me", headers=headers_usuario)
    assert resp.status_code == 200
    assert resp.json()["data"]["email"] == "user@test.com"
