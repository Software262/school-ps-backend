# classroom/domain/entities.py
from pydantic import BaseModel


class DetallePupitreEntity(BaseModel):
    id: int
    estudiante_id: int
    estado: str
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


class ComplementarioEntity(BaseModel):
    id: int
    nombre: str
    valor: int
    anio: int
