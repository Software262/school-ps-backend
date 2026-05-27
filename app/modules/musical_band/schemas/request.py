from typing import Literal

from pydantic import Field, model_validator

from app.modules.inventory.schemas.request import (
    CreateItemRequest,
    FilterPaginationInventory,
)


class FilterPaginationMusicalBand(FilterPaginationInventory):
    item_type: Literal["banda", "deporte", "ajedrez"] | None = Field(default="banda")

    @model_validator(mode="after")
    def validate_modification_modes(self) -> "FilterPaginationMusicalBand":
        if self.item_type != "banda":
            raise ValueError("Invalido tipo para obtener los articulos")
        return self


class CreateInstrumentRequest(CreateItemRequest):
    pass
