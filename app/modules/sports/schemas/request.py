from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.shared.schemas.filter_pagination_request import FilterPagination

# Tipo fijo para todos los items de este módulo
TIPO_DEPORTE = "deporte"


class FilterPaginationSports(FilterPagination):
    """Paginación con filtro de tipo bloqueado a 'deporte'."""
    item_type: Literal["deporte"] = "deporte"


class FilterPaginationSportsBorrowings(FilterPaginationSports):
    active: bool | None = None


# ---------- Items ----------

class CreateSportItemRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=100, description="Nombre del implemento deportivo")
    cantidad: int = Field(ge=1, description="Cantidad disponible")
    estado_objeto: str = Field(min_length=2, max_length=100, description="Estado del implemento")
    observacion: str | None = Field(None, max_length=400, description="Observación opcional")

    # tipo_inventario_id se inyecta internamente desde el servicio; no lo expone el cliente


class UpdateSportItemRequest(BaseModel):
    """PATCH parcial — todos los campos opcionales."""
    nombre: str | None = Field(None, min_length=2, max_length=100)
    cantidad: int | None = Field(None, ge=0)
    estado_objeto: str | None = Field(None, min_length=2, max_length=100)
    observacion: str | None = Field(None, max_length=400)


class UpdateCompleteSportItemRequest(BaseModel):
    """PUT completo."""
    nombre: str = Field(min_length=2, max_length=100)
    cantidad: int = Field(ge=0)
    estado_objeto: str = Field(min_length=2, max_length=100)
    observacion: str | None = Field(None, max_length=400)


# ---------- Préstamos ----------

class CreateSportBorrowRequest(BaseModel):
    inventario_id: int = Field(ge=1, description="ID del implemento a prestar")
    estudiante_id: int = Field(ge=1, description="ID del estudiante que recibe el préstamo")
    fecha_salida: datetime = Field(description="Fecha de préstamo", examples=[datetime.now()])
    cantidad: int = Field(ge=1, description="Cantidad a prestar")
    observacion: str | None = Field(None, max_length=400, description="Observación del préstamo")


class ReturnSportBorrowRequest(BaseModel):
    inventario_id: int = Field(ge=1, description="ID del implemento a devolver")
    estudiante_id: int = Field(ge=1, description="ID del estudiante que devuelve")
    cantidad: int = Field(ge=1, description="Cantidad devuelta")
    observacion: str = Field(
        min_length=5,
        max_length=400,
        description="Observación obligatoria de la devolución (estado en que regresa el implemento)",
    )


# ---------- Novedades ----------

class CreateSportNovedadRequest(BaseModel):
    prestamo_id: int = Field(ge=1, description="ID del préstamo con novedad")
    descripcion: str = Field(
        min_length=5,
        max_length=250,
        description="Descripción de la novedad (daño, pérdida, etc.)",
    )


class ResolveSportNovedadRequest(BaseModel):
    descripcion: str = Field(
        min_length=5,
        max_length=250,
        description="Descripción de cómo se resolvió la novedad (reposición, autorización, etc.)",
    )


# ---------- Carga masiva ----------

class SportItemFileRequest(BaseModel):
    """Fila del archivo CSV/Excel — sin tipo_inventario_id (se inyecta internamente)."""
    nombre: str = Field(min_length=2)
    cantidad: int = Field(gt=0)
    estado_objeto: str = Field(min_length=2)
    observacion: str | None = Field(default=None)
