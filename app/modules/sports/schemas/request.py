from typing import Literal

from pydantic import Field, model_validator

from app.modules.inventory.schemas.request import (
    CreateItemRequest,
    CreateBorrowRequest,
    FilterPaginationBorrowings,
    FilterPaginationInventory,
    UpdateCompleteItemRequest,
    UpdateSingleItemRequest,
    ReturnBorrowRequest,
)


class FilterPaginationDeportes(FilterPaginationInventory):
    item_type: Literal["banda", "deporte", "ajedrez"] | None = Field(default="deporte")

    @model_validator(mode="after")
    def validate_modification_modes(self) -> "FilterPaginationDeportes":
        if self.item_type != "deporte":
            raise ValueError("Invalido tipo para obtener los articulos")
        return self


class FilterPaginationBorrowingDeportes(FilterPaginationBorrowings):
    item_type: Literal["deporte"] | None = Field(default="deporte")
    active: bool | None = None


class CreateSportItemRequest(CreateItemRequest):
    pass


class UpdateItemDeportesSingle(UpdateSingleItemRequest):
    pass


class UpdateItemDeportesComplete(UpdateCompleteItemRequest):
    pass


class ReturnSportBorrowRequest(ReturnBorrowRequest):
    pass


class CreateSportBorrowRequest(CreateBorrowRequest):
    pass
