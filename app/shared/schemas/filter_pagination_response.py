from pydantic import BaseModel


class Pagination(BaseModel):
    items: list[object]
    current_page: int = 1
    page_size: int = 10
