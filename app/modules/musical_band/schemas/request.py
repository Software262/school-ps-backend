from typing import Literal

from pydantic import Field, model_validator

from app.modules.inventory.schemas.request import (
    CreateBorrowRequest,
    CreateItemRequest,
    FilterPaginationBorrowings,
    FilterPaginationInventory,
    ReturnBorrowRequest,
    UpdateSingleItemRequest,
)


class FilterPaginationMusicalBand(FilterPaginationInventory):
    item_type: Literal["banda", "deporte", "ajedrez"] | None = Field(default="banda")

    @model_validator(mode="after")
    def validate_modification_modes(self) -> "FilterPaginationMusicalBand":
        if self.item_type != "banda":
            raise ValueError("Invalido tipo para obtener los articulos")
        return self


class FilterPaginationBorrowingMusicalBand(FilterPaginationBorrowings):
    item_type: Literal["banda", "deporte", "ajedrez"] | None = Field(default="banda")

    @model_validator(mode="after")
    def validate_modification_modes(self) -> "FilterPaginationBorrowingMusicalBand":
        if self.item_type != "banda":
            raise ValueError("Invalido tipo para obtener los articulos")
        return self


class CreateInstrumentRequest(CreateItemRequest):
    pass


class UpdateItemMusicalBand(UpdateSingleItemRequest):
    pass


class CreateInstrumentBorrowingMusicalBand(CreateBorrowRequest):
    pass


class ReturnInstrumentBorrowingMusicalBand(ReturnBorrowRequest):
    pass
