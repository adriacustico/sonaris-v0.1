"""SQLAlchemy model for persisted acoustic calculations."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Calculation(Base):
    """Stored acoustic calculation result."""

    __tablename__ = "calculations"
    __table_args__ = (
        Index("idx_proyecto_id", "proyecto_id"),
        Index("idx_timestamp", "timestamp"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    proyecto_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    entrada_json: Mapped[str] = mapped_column(Text, nullable=False)
    resultado_json: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow, nullable=True)
    eliminado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    proyecto: Mapped["Project"] = relationship("Project", back_populates="calculations")

    @property
    def entrada(self) -> dict[str, Any]:
        """Deserialize the request JSON payload."""
        return json.loads(self.entrada_json)

    @property
    def resultado(self) -> dict[str, Any]:
        """Deserialize the calculation result JSON payload."""
        return json.loads(self.resultado_json)

    def __repr__(self) -> str:
        """Return a compact representation with the weighted index when present."""
        rw = self.resultado.get("Rw", "?")
        return f"Calculation({self.nombre}, Rw={rw} dB)"

    def to_dict(self) -> dict[str, Any]:
        """Serialize all model fields into a dictionary."""
        return {
            "id": self.id,
            "proyecto_id": self.proyecto_id,
            "nombre": self.nombre,
            "entrada": self.entrada,
            "resultado": self.resultado,
            "timestamp": self.timestamp,
            "actualizado_en": self.actualizado_en,
            "eliminado": self.eliminado,
        }
