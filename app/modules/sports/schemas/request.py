from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

from pydantic import model_validator

from app.modules.inventory.schemas.request import (
    CreateItemRequest,
    FilterPaginationInventory,
    FilterPaginationBorrowings,
    UpdateSingleItemRequest,
    InventoryItemRequest,
)


# ---------- Filtros ----------

class FilterPaginationSports(FilterPaginationInventory):
    item_type: Literal["deporte"] | None = Field(default="deporte")

    @model_validator(mode="after")
    def validate_sport_type(self) -> "FilterPaginationSports":
        if self.item_type != "deporte":
            raise ValueError("Tipo inválido para el módulo de Deportes")
        return self


class FilterPaginationSportsBorrowings(FilterPaginationBorrowings):
    item_type: Literal["deporte"] | None = Field(default="deporte")
    active: bool | None = None

    @model_validator(mode="after")
    def validate_sport_type(self) -> "FilterPaginationSportsBorrowings":
        if self.item_type != "deporte":
            raise ValueError("Tipo inválido para el módulo de Deportes")
        return self


# ---------- Items ----------

class CreateSportItemRequest(CreateItemRequest):
    tipo_inventario_id: int = Field(default=0, exclude=True)


class UpdateCompleteSportItemRequest(UpdateSingleItemRequest):
    tipo_inventario_id: int | None = Field(default=None, exclude=True)


class UpdateSportItemRequest(UpdateSingleItemRequest):
    tipo_inventario_id: int | None = Field(default=None, exclude=True)


class SportItemFileRequest(InventoryItemRequest):
    tipo_inventario_id: int = Field(default=0, exclude=True)


# ---------- Préstamos ----------

class CreateSportBorrowRequest(BaseModel):
    inventario_id: int = Field(ge=1)
    estudiante_id: int = Field(ge=1)
    fecha_salida: datetime = Field(examples=[datetime.now()])
    cantidad: int = Field(ge=1)
    observacion: str | None = Field(default=None)


class ReturnSportBorrowRequest(BaseModel):
    inventario_id: int = Field(ge=1)
    estudiante_id: int = Field(ge=1)
    cantidad: int = Field(ge=1)
    observacion: str = Field(min_length=5, max_length=400)


# ---------- Novedades ----------

class CreateSportNovedadRequest(BaseModel):
    prestamo_id: int = Field(ge=1)
    descripcion: str = Field(min_length=5, max_length=250)


class ResolveSportNovedadRequest(BaseModel):
    descripcion: str = Field(min_length=5, max_length=250)