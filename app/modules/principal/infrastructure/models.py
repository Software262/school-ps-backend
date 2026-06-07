"""
Rectoría Module Infrastructure Models.

This module contains the database schemas and mappings (SQLModel) representing
the infrastructure entities for the Rectoría (Principal) module, including
administrative status, observations, student observer records, and audit logs.

Author: Yessyth Jaimes
Role: Product Owner and developer of the rectoria module
"""

from datetime import datetime

from sqlmodel import Field

from app.shared.infrastructure.base import Base


class RectoriaEstado(Base, table=True):
    """
    Represents the administrative peace and safe (paz y salvo) status of a teacher.

    Attributes:
        docente_id (int): Foreign key identifier of the teacher.
        periodo_id (int): Foreign key identifier of the academic period.
        motivo_estado (str): Reason or details regarding the administrative status.
        fecha_actualizacion (datetime): Timestamp of the last status update.
    """

    docente_id: int = Field(foreign_key="docente.id")
    periodo_id: int = Field(foreign_key="periodo.id")
    motivo_estado: str = Field(max_length=400)
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)


class RectoriaObservaciones(Base, table=True):
    """
    Represents administrative observations registered for a teacher.

    Attributes:
        docente_id (int): Foreign key identifier of the teacher.
        periodo_id (int): Foreign key identifier of the academic period.
        descripcion (str): Detailed text of the administrative observation.
        tipo_observacion (str): Classification type of the observation (e.g. positive, warning).
        fecha (datetime): Timestamp when the observation was registered.
    """

    docente_id: int = Field(foreign_key="docente.id")
    periodo_id: int = Field(foreign_key="periodo.id")
    descripcion: str = Field(max_length=400)
    tipo_observacion: str = Field(max_length=50)
    fecha: datetime


class Auditoria(Base, table=True):
    """
    Represents system audit logs tracking modifications of administrative records.

    Attributes:
        id_usuario (int): Foreign key identifier of the user who made the change.
        tabla_nombre (str): Name of the modified database table.
        registro_id (int): Primary key of the modified table row.
        operacion (str): Operation type executed (e.g., INSERT, UPDATE, DELETE).
        valor_anterior (str): String representation of the record before the modification.
        valor_nuevo (str): String representation of the record after the modification.
    """

    id_usuario: int = Field(foreign_key="usuario.id")
    tabla_nombre: str = Field(max_length=50)
    registro_id: int
    operacion: str = Field(max_length=10)
    valor_anterior: str = Field(default="")
    valor_nuevo: str = Field(default="")
    # TODO: Eliminar este campo cuando se limpie la base de datos de producción.
    # Se mantiene temporalmente como opcional para evitar conflictos de restricción
    # NOT NULL con las bases de datos locales del equipo de desarrollo.
    fecha_accion: datetime | None = Field(default=None)


# Alias para mantener compatibilidad con el resto del módulo actual
PrincipalObservation = RectoriaObservaciones
PrincipalStatus = RectoriaEstado
