import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, engine, SessionLocal


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c


# --- Fixtures de usuarios y autenticación ---

@pytest.fixture
def usuario_normal(db_session):
    from app.models.usuario import Usuario
    from app.services.auth_service import hash_password

    usuario = Usuario(
        email="user@test.com",
        password_hash=hash_password("password123"),
        alias="user",
        rol="registrado",
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture
def usuario_admin(db_session):
    from app.models.usuario import Usuario
    from app.services.auth_service import hash_password

    usuario = Usuario(
        email="admin@test.com",
        password_hash=hash_password("password123"),
        alias="admin",
        rol="administrador",
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture
def headers_usuario(usuario_normal):
    from app.services.auth_service import create_access_token

    token = create_access_token(usuario_normal.id, usuario_normal.rol)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def headers_admin(usuario_admin):
    from app.services.auth_service import create_access_token

    token = create_access_token(usuario_admin.id, usuario_admin.rol)
    return {"Authorization": f"Bearer {token}"}


# --- Factory de datos de dominio ---

@pytest.fixture
def crear_obra(db_session):
    from app.models.obra import Obra

    def _crear(**kwargs):
        datos = dict(
            codigo_infobras=f"TEST-{uuid.uuid4().hex[:8]}",
            titulo="Obra Test",
            tipo_obra="edificacion",
            estado="ejecucion",
            presupuesto_total=1000000,
            departamento="Lima",
            score_riesgo=25,
            modo_analisis="fallback_m2",
        )
        datos.update(kwargs)
        obra = Obra(**datos)
        db_session.add(obra)
        db_session.commit()
        db_session.refresh(obra)
        return obra

    return _crear
