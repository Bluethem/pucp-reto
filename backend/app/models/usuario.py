import uuid
from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    alias = Column(String(100))
    rol = Column(
        Enum("anonimo", "registrado", "administrador", name="rol_usuario_enum"),
        nullable=False,
        default="registrado",
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    comentarios = relationship("Comentario", back_populates="usuario", cascade="all, delete-orphan")
    suscripciones = relationship("Suscripcion", back_populates="usuario", cascade="all, delete-orphan")
