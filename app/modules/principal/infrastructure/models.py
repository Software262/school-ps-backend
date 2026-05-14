from datetime import datetime

from sqlmodel import Field

from app.shared.infrastructure.base import Base


class RectoriaEstado(Base, table=True):
    docente_id: int = Field(foreign_key="docente.id")
    periodo_id: int = Field(foreign_key="periodo.id")
    motivo_estado: str
    fecha_actualizacion: datetime


class RectoriaObservaciones(Base, table=True):
    docente_id: int = Field(foreign_key="docente.id")
    periodo_id: int = Field(foreign_key="periodo.id")
    descripcion: str = Field(max_length=400)
    tipo_observacion: str = Field(max_length=50)
    fecha: datetime


class Observador(Base, table=True):
    estudiante_id: int = Field(foreign_key="estudiante.id")
    tipo_incidencia: str = Field(max_length=50)
    descripcion: str = Field(max_length=400)
    fecha: datetime


class Auditoria(Base, table=True):
    id_usuario: int = Field(foreign_key="usuario.id")
    tabla_nombre: str = Field(max_length=50)
    registro_id: int
    operacion: str = Field(max_length=10)
    valor_anterior: str
    valor_nuevo: str
    fecha_accion: datetime
