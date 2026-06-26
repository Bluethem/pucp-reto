"""Router del módulo Auth."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import envelope
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    usuario = auth_service.registrar_usuario(db, payload.email, payload.password, payload.alias)
    token = auth_service.create_access_token(usuario.id, usuario.rol)
    data = TokenResponse(access_token=token, user=UserResponse.model_validate(usuario))
    return envelope(data.model_dump())


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    usuario = auth_service.autenticar_usuario(db, payload.email, payload.password)
    token = auth_service.create_access_token(usuario.id, usuario.rol)
    data = TokenResponse(access_token=token, user=UserResponse.model_validate(usuario))
    return envelope(data.model_dump())


@router.get("/me")
def me(usuario: Usuario = Depends(auth_service.get_current_user)):
    return envelope(UserResponse.model_validate(usuario).model_dump())


@router.post("/logout")
def logout(_usuario: Usuario = Depends(auth_service.get_current_user)):
    # JWT stateless: el cliente descarta el token.
    return envelope({"mensaje": "Sesión cerrada"})
