from datetime import datetime

from sqlmodel import Field

from app.shared.infrastructure.base import Base


class DetallePazysalvo(Base, table=True):
    estudiante_id: int = Field(foreign_key="estudiante.id")
    prestamo_id: int = Field(foreign_key="prestamo.id")
    cafeteria_id: int = Field(foreign_key="cafeteria.id")
    matricula_id: int = Field(foreign_key="matricula.id")
    pension_id: int = Field(foreign_key="pension.id")
    pupitre_id: int = Field(foreign_key="pupitre.id")
    complemento_id: int = Field(foreign_key="complementario.id")
    estado_escuela: bool


class Pazysalvo(Base, table=True):
    detalle_pazysalvo_id: int = Field(foreign_key="detallepazysalvo.id")
    periodo_id: int = Field(foreign_key="periodo.id")
    estado_final: str = Field(max_length=50)
    fecha: datetime
    observacion: str | None = Field(max_length=400)
