from sqlmodel import Field

from app.shared.infrastructure.base import Base


class Pupitre(Base, table=True):
    estudiante_id: int = Field(foreign_key="estudiante.id")
    estado_pupitre: bool = Field()
    observacion: str | None = Field(max_length=400)
