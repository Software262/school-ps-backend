from pydantic import BaseModel


class CreateTypeInventoryResponse(BaseModel):
    id: int
    nombre: str


class CreateItemInventoryResponse(BaseModel):
    id: int
    nombre: str
    cantidad: int
    estado_objeto: str
    observacion: str | None


class UpdateItemInventoryResponse(BaseModel):
    id: int
    nombre: str
    cantidad: int
    estado_objeto: str
    observacion: str | None


class CreateItemBorrowingResponse(BaseModel):
    id: int
    inventario_id: int
    estudiante_id: int
    cantidad: int
    observacion: str | None
