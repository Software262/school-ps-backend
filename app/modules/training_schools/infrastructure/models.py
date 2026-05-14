from datetime import datetime

from sqlmodel import Field

from app.shared.infrastructure.base import Base


class DetalleEscuelaFormacion(Base, table=True):
    complementario_id: int = Field(foreign_key="complementario.id")
    estudiante_id: int = Field(foreign_key="estudiante.id")
    fecha_registro: datetime = Field()
    mes: str = Field(max_length=20)
    activo: bool = Field()
    estado_escuela: bool = Field()
