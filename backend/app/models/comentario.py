import uuid
from sqlalchemy import Column, String, ForeignKey, Enum, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Comentario(Base):
    __tablename__ = "comentarios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), ForeignKey("usuarios.id"), nullable=False)
    recurso_tipo = Column(
        Enum("obra", "empresa", "municipio", "autoridad", name="recurso_tipo_enum"),
        nullable=False,
    )
    recurso_id = Column(String(36), nullable=False)
    contenido = Column(Text, nullable=False)
    padre_id = Column(String(36), ForeignKey("comentarios.id"))
    reportado = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="comentarios")
    respuestas = relationship("Comentario", backref="padre", remote_side=[id], cascade="all, delete-orphan")
