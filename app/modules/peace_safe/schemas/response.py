from pydantic import BaseModel


class ModuloStatus(BaseModel):
    clave: str
    nombre: str
    estado: str
    detalle: str


class EstudianteInfo(BaseModel):
    id: int
    nombre: str
    documento: str
    grado: str = ""


class DocenteInfo(BaseModel):
    id: int
    nombre: str
    documento: str
    asignatura: str


class StatusResponse(BaseModel):
    entidad: EstudianteInfo | DocenteInfo
    modulos: list[ModuloStatus]
    total_modulos: int
    modulos_ok: int
    modulos_error: int
    paz_y_salvo: bool


class GenerateResponse(BaseModel):
    id: int
    codigo: str
    estado_final: str
    fecha: str
    entidad: dict
    periodo: dict
    detalles: list[dict]


class PazYSalvoDetailResponse(BaseModel):
    id: int
    codigo: str
    entidad_tipo: str
    estado_final: str
    fecha_generacion: str
    entidad: dict
    detalles: list[dict]
