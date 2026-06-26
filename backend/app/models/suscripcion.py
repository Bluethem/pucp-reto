import uuid
from sqlalchemy import Column, String, ForeignKey, Enum, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Suscripcion(Base):
    __tablename__ = "suscripciones"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), ForeignKey("usuarios.id"), nullable=False)
    recurso_tipo = Column(
        Enum("obra", "empresa", "municipio", "autoridad", name="suscripcion_recurso_tipo_enum"),
        nullable=False,
    )
    recurso_id = Column(String(36), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("usuario_id", "recurso_tipo", "recurso_id", name="uq_suscripcion"),
    )

    usuario = relationship("Usuario", back_populates="suscripciones")
