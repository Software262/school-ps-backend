from pydantic import BaseModel

class BulkUpdateResponse (BaseModel):
    total_actualizados: int
    mensaje: str