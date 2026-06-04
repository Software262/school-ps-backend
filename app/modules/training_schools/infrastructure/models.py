from datetime import datetime

from sqlmodel import Field

from app.shared.infrastructure.base import Base


class DetalleEscuelaFormacion(Base, table=True):
    # fk to Complementario (the program)
    complementario_id: int = Field(foreign_key="complementario.id")
    # fk to Estudiante
    estudiante_id: int = Field(foreign_key="estudiante.id", index=True)
    # academic period (required; every enrollment belongs to a period)
    periodo_id: int = Field(foreign_key="periodo.id", index=True)
    # last staff member who acted on this record
    usuario_id: int | None = Field(default=None, foreign_key="usuario.id")
    fecha_registro: datetime = Field(default_factory=datetime.now)
    mes: str = Field(max_length=20)
    # true = active enrollment, false = withdrawn
    activo: bool = Field(default=True)
    # true = paz y salvo (no pending debt), false = obligation pending
    estado_escuela: bool = Field(default=True)
    # remaining balance in COP; zero means fully paid
    saldo_pendiente: int = Field(default=0)
    # populated on withdrawal for traceability (ef-rf-05)
    motivo_retiro: str | None = Field(default=None, max_length=400)
    # free-text notes captured at enrollment
    observaciones: str | None = Field(default=None, max_length=400)
    # actual agreed amount (may differ from program base price)
    valor_acordado: int = Field(default=0)
    # physical receipt number delivered to the student
    numero_comprobante: str | None = Field(default=None, max_length=100)
