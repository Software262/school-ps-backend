from pydantic import BaseModel

class PupitreOutSchema (BaseModel):
    id: int
    estado_pupitre: bool
    observacion: str|None
    mensaje: str


class BulkUpdateResponse (BaseModel):
    total_actualizados: int
    mensaje: str