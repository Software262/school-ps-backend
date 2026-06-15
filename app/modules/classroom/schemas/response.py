from pydantic import BaseModel, Field


class PupitreOutSchema(BaseModel):
    id: int | None
    estudiante_id: int
    estado: str
    observacion: str | None = Field(default=None, max_length=400)


class PupitreStudentOutSchema(BaseModel):
    id: int | None
    estudiante_id: int
    nombre_estudiante: str
    documento: str
    grado: str
    docente_titular: str | None
    estado: str
    observacion: str | None = Field(default=None, max_length=400)


class BulkUpdateResponse(BaseModel):
    total_actualizados: int
    ids_no_encontrados: list[int] = []
