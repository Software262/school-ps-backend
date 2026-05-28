"""
Cafeteria Module DTO Response Schemas.

This module contains the Pydantic models used to structure the data
returned by the API endpoints.

Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from datetime import datetime
from pydantic import BaseModel


class CafeteriaStudentResponse(BaseModel):
    """
    Schema for the list view of students in the cafeteria module.
    Includes basic student info and their current debt status.
    """

    id: int
    estudiante: str
    documento: str
    estado: bool
    observaciones: str | None = None


class CafeteriaRecordResponse(BaseModel):
    """
    Schema for a single cafeteria record, usually returned after
    an individual update or manual block.
    """

    id: int
    estudiante_id: int
    periodo_id: int
    usuario_id: int | None = None
    estado_cafeteria: bool
    observaciones: str | None = None
    updated_at: datetime


class BulkOperationSummaryResponse(BaseModel):
    """
    Schema for the summary of a bulk operation.
    Provides feedback on how many records were processed or skipped.
    """

    total_seleccionados: int
    total_actualizados: int
    total_excluidos: int
