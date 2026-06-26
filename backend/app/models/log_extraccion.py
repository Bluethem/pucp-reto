import uuid
from sqlalchemy import Column, String, ForeignKey, Enum, JSON, Boolean, SmallInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class LogExtraccion(Base):
    __tablename__ = "log_extraccion"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    obra_id = Column(String(36), ForeignKey("obras.id"), nullable=False)
    fuente = Column(
        Enum("gemini", "inei", "seace", "sunat", "jne", name="fuente_log_enum"),
        nullable=False,
    )
    respuesta_cruda = Column(JSON)
    exitoso = Column(Boolean)
    intentos = Column(SmallInteger, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    obra = relationship("Obra", back_populates="logs")
