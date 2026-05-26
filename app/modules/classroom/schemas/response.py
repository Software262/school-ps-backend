from pydantic import BaseModel,Field

class PupitreOutSchema (BaseModel):
    id: int | None
    estudiante_id: int
    estado_pupitre: bool
    observacion: str | None = Field(default=None, max_length=400)



class BulkUpdateResponse (BaseModel):
    total_actualizados: int
