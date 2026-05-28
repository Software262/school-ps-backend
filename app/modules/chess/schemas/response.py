from pydantic import BaseModel


class ReturnChessResponse(BaseModel):
    id: int
    estado_prestamo: bool
    novedad_creada: bool
    mensaje: str
