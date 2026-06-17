"""
Rectoría Module DTO Request Schemas.

This module contains the Pydantic DTO (Data Transfer Object) models representing
incoming request payloads for teacher observations and administrative statuses.

Author: Yessyth Jaimes
Role: Product Owner and developer of the rectoria module
"""

from pydantic import BaseModel, Field


class CreateObservationRequest(BaseModel):
    """
    Schema for creating a new administrative observation.

    Attributes:
        docente_id (int): Unique identifier of the teacher (must be >= 1).
        periodo_id (int | None): Unique identifier of the academic period. If not provided, the active period will be used.
        id_usuario (int): Unique identifier of the user creating the observation (must be >= 1).
        descripcion (str): Detailed text of the observation (length between 3 and 400).
        tipo_observacion (str): Type of observation (length between 3 and 50).
    """

    docente_id: int = Field(ge=1)
    periodo_id: int | None = Field(default=None, ge=1)
    id_usuario: int | None = Field(default=None, ge=1)
    descripcion: str = Field(min_length=3, max_length=400)
    tipo_observacion: str = Field(min_length=3, max_length=50)


class CreateStatusRequest(BaseModel):
    """
    Schema for assigning a new administrative status to a teacher.

    Attributes:
        docente_id (int): Unique identifier of the teacher (must be >= 1).
        periodo_id (int | None): Unique identifier of the academic period. If not provided, the active period will be used.
        id_usuario (int | None): Unique identifier of the user assigning the status. If not provided, an admin user will be auto-resolved.
        motivo_estado (str): Reason or details for the status assignment (length between 3 and 400).
    """

    docente_id: int = Field(ge=1)
    periodo_id: int | None = Field(default=None, ge=1)
    id_usuario: int | None = Field(default=None, ge=1)
    motivo_estado: str = Field(min_length=3, max_length=400)


class UpdateStatusRequest(BaseModel):
    """
    Schema for updating an existing administrative status.

    Attributes:
        id_usuario (int | None): Unique identifier of the user executing the update. If not provided, an admin user will be auto-resolved.
        motivo_estado (str): The updated reason or details (length between 3 and 400).
    """

    id_usuario: int | None = Field(default=None, ge=1)
    motivo_estado: str = Field(min_length=3, max_length=400)
