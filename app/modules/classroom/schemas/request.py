from pydantic import BaseModel

class PupitreInSchema (BaseModel):
    estado_pupitre : bool
    observacion : str|None


class BulkUpdateRequest (BaseModel):
    estudiantes_ids: list[int]
    estado_pupitre: bool
    observacion: str | None
