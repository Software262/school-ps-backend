from datetime import datetime

from sqlmodel import Field

from app.shared.infrastructure.base import Base


class Observador(Base, table=True):
    estudiante_id: int = Field(foreign_key="estudiante.id", nullable=False)
    docente_id: int = Field(foreign_key="docente.id", nullable=False)

    tipo_incidencia: str = Field(max_length=50, nullable=False)
    descripcion: str = Field(max_length=400, nullable=False)
    fecha: datetime = Field(default_factory=datetime.now, nullable=False)

    esta_abierta: bool = Field(default=True, nullable=False)
    fecha_cierre: datetime | None = Field(default=None, nullable=True)
