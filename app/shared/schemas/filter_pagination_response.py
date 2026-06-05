from pydantic import BaseModel, Field


class Pagination(BaseModel):
    items: list[object]
    current_page: int = Field(default=1)
    page_size: int = Field(default=10)
    total: int = Field(default=0, ge=0)
    total_pages: int = Field(default=0, ge=0)
    previous: bool = Field(default=False)
    next: bool = Field(default=False)
