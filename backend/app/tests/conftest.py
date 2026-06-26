import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.core.config import settings

TEST_DATABASE_URL = settings.database_url.rsplit("/", 1)[0] + "/glass_test"

test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)

Base.metadata.drop_all(bind=test_engine)
Base.metadata.create_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    session = TestSessionLocal()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    yield session

    app.dependency_overrides.clear()
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    with TestClient(app) as c:
        yield c


# --- Fixtures de usuarios y autenticación ---

@pytest.fixture
def usuario_normal(db_session):
    from app.models.usuario import Usuario
    from app.services.auth_service import hash_password

    uid = uuid.uuid4().hex[:8]
    usuario = Usuario(
        email=f"user-{uid}@test.com",
        password_hash=hash_password("password123"),
        alias=f"user-{uid}",
        rol="registrado",
    )
    db_session.add(usuario)
    db_session.commit()
    return usuario


@pytest.fixture
def usuario_admin(db_session):
    from app.models.usuario import Usuario
    from app.services.auth_service import hash_password

    uid = uuid.uuid4().hex[:8]
    usuario = Usuario(
        email=f"admin-{uid}@test.com",
        password_hash=hash_password("password123"),
        alias=f"admin-{uid}",
        rol="administrador",
    )
    db_session.add(usuario)
    db_session.commit()
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
        return obra

    return _crear
