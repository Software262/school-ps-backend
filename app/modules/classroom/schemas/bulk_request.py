from pydantic import BaseModel

class BulkUpdateRequest (BaseModel):
    estudiantes_ids: list[int]
    estado_pupitre: bool
    observacion: str | None