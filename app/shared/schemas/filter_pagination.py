from typing import Literal

from pydantic import BaseModel


class Pagination(BaseModel):
    items: list[object]
    current_page: int = 1
    page_size: int = 10


class FilterPagination(BaseModel):
    page: int = 1
    limit: int = 10
    item_type: Literal["banda", "deporte", "ajedrez"] | None = None
