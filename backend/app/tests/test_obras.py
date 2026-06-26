"""Tests del módulo Obras."""


def test_listar_obras(client, db_session, crear_obra):
    crear_obra(titulo="Obra A")
    crear_obra(titulo="Obra B")
    resp = client.get("/api/v1/obras")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 2


def test_get_obra_by_id(client, db_session, crear_obra):
    obra = crear_obra(titulo="Obra detalle")
    resp = client.get(f"/api/v1/obras/{obra.id}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["id"] == obra.id
    assert data["titulo"] == "Obra detalle"
    assert "nivel_riesgo" in data
    assert "partidas" in data


def test_get_obra_inexistente(client, db_session):
    resp = client.get("/api/v1/obras/no-existe-123")
    assert resp.status_code == 404


def test_filtros_obras(client, db_session, crear_obra):
    crear_obra(departamento="Lima")
    crear_obra(departamento="Cusco")
    resp = client.get("/api/v1/obras", params={"departamento": "Cusco"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert all(o["departamento"] == "Cusco" for o in data)
    assert len(data) >= 1


def test_resumen_obras(client, db_session, crear_obra):
    crear_obra(score_riesgo=10)
    crear_obra(score_riesgo=75)
    resp = client.get("/api/v1/obras/resumen")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "total" in data
    assert "por_nivel" in data


def test_buscar_obras(client, db_session, crear_obra):
    crear_obra(titulo="Mejoramiento de pista Av. Lima")
    resp = client.get("/api/v1/obras/buscar", params={"q": "Mejoramiento"})
    assert resp.status_code == 200
    assert isinstance(resp.json()["data"], list)


def test_geolocalizadas_obras(client, db_session, crear_obra):
    crear_obra()
    resp = client.get("/api/v1/obras/geolocalizadas")
    assert resp.status_code == 200
    assert isinstance(resp.json()["data"], list)
