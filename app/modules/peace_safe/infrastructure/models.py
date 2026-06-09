from datetime import datetime, timezone

from sqlmodel import Field

from app.shared.infrastructure.base import Base


class PazYSalvo(Base, table=True):
    entidad_tipo: str = Field(max_length=20, description="estudiante | docente")
    entidad_id: int = Field(
        description="ID del estudiante o docente segun entidad_tipo"
    )
    periodo_id: int = Field(foreign_key="periodo.id")
    usuario_genera_id: int = Field(
        description="ID del usuario que genero el paz y salvo"
    )
    estado_final: str = Field(max_length=20, description="paz_y_salvo | observado")
    codigo_certificado: str = Field(
        max_length=50, unique=True, description="Codigo unico del certificado"
    )
    fecha_generacion: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    observacion: str | None = Field(max_length=500, default=None)


class DetallePazYSalvo(Base, table=True):
    paz_y_salvo_id: int = Field(foreign_key="pazysalvo.id")
    modulo: str = Field(max_length=50, description="Clave del modulo")
    nombre_modulo: str = Field(max_length=100, description="Nombre para mostrar")
    estado: str = Field(max_length=20, description="ok | error")
    detalle: str = Field(max_length=500, description="Descripcion del resultado")
