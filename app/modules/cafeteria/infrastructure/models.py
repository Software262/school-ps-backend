from sqlmodel import Field

from app.shared.infrastructure.base import Base


class Cafeteria(Base, table=True):
    estudiante_id: int = Field(foreign_key="estudiante.id")
    periodo_id: int = Field(foreign_key="periodo.id")
    estado_cafeteria: bool = Field()
