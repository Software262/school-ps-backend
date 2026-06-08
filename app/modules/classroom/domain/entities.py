# classroom/domain/entities.py
from pydantic import BaseModel


class PupitreEntity(BaseModel):
    id: int
    estudiante_id: int
    estado_pupitre: bool
    observacion: str | None


class StudentEntity(BaseModel):
    id: int
    nombre: str
    documento: str
    grado_id: int


class GradeEntity(BaseModel):
    id: int
    nombre: str
    docente_titular: str | None
