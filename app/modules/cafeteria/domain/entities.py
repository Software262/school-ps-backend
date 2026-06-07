"""
Cafeteria Module Domain Entities.
Author: Danilo Castillejo
"""

from pydantic import BaseModel


class CafeteriaEntity(BaseModel):
    id: int
    estudiante_id: int
    estado_cafeteria: bool
    observaciones: str | None


class DebtorEntity(BaseModel):
    id: int
    estudiante_id: int
    nombre: str
    documento: str
    grado: str
    estado_cafeteria: bool
    observaciones: str


class StudentInfoEntity(BaseModel):
    id: int
    nombre: str
    documento: str
    grado: str


class GradeEntity(BaseModel):
    id: int
    nombre: str


class ReportRowEntity(BaseModel):
    """Entidad necesaria para la exportación de reportes"""

    documento: str
    nombre: str
    grado: str
    estado_cafeteria: bool
    observaciones: str
