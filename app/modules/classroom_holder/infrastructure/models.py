from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Observador(SQLModel, table=True):
    __tablename__ = "observador"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # 🌟 CORRECCIÓN: Le decimos explícitamente a SQLModel que son llaves foráneas
    estudiante_id: int = Field(foreign_key="estudiante.id", nullable=False)
    docente_id: int = Field(foreign_key="docente.id", nullable=False)

    tipo_incidencia: str = Field(max_length=50, nullable=False)
    descripcion: str = Field(max_length=400, nullable=False)
    fecha: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    esta_abierta: bool = Field(default=True, nullable=False)
    fecha_cierre: Optional[datetime] = Field(default=None, nullable=True)
