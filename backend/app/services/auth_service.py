"""Servicio de autenticación: hashing de contraseñas, JWT y dependencias de rol.

RNF-08 (contraseñas hasheadas, control de acceso por rol) y modelo de usuarios
tipo YouTube (ADR-010): el login solo se exige para participar.
"""

from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.usuario import Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


# --- Hashing ---

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plano: str, hashed: str) -> bool:
    return pwd_context.verify(plano, hashed)


# --- JWT ---

def create_access_token(sub: str, rol: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": sub, "rol": rol, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


# --- Lógica de negocio ---

def registrar_usuario(db: Session, email: str, password: str, alias: str | None) -> Usuario:
    if db.query(Usuario).filter(Usuario.email == email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "El email ya está registrado")
    usuario = Usuario(
        email=email,
        password_hash=hash_password(password),
        alias=alias or email.split("@")[0],
        rol="registrado",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar_usuario(db: Session, email: str, password: str) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not verify_password(password, usuario.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas")
    return usuario


# --- Dependencias de FastAPI ---

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No autenticado")
    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido o expirado")
    usuario = db.query(Usuario).filter(Usuario.id == payload.get("sub")).first()
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario no encontrado")
    return usuario


def get_current_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.rol != "administrador":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Requiere rol de administrador")
    return usuario
