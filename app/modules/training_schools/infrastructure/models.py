from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from app.shared.infrastructure.base import Base


class DetalleEscuelaFormacion(Base, table=True):
    __table_args__ = (
        UniqueConstraint(
            "complementario_id",
            "estudiante_id",
            "mes",
            name="uq_detalle_escuela_estudiante_programa_mes",
        ),
    )

    complementario_id: int = Field(foreign_key="complementario.id")
    estudiante_id: int = Field(foreign_key="estudiante.id")
    fecha_registro: datetime = Field()
    mes: str = Field(max_length=20)
    activo: bool = Field()
    estado_escuela: bool = Field()
    motivo_baja: str | None = Field(default=None, max_length=255)
