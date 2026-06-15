from sqlmodel import Field

from app.shared.infrastructure.base import Base


class DetallePupitre(Base, table=True):
    estudiante_id: int = Field(foreign_key="estudiante.id", unique=True)
    complementario_id: int = Field(foreign_key="complementario.id")
    estado: str = Field(default="pendiente", max_length=20)
    observacion: str | None = Field(max_length=400)
