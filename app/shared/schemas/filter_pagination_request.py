from pydantic import BaseModel


class FilterPagination(BaseModel):
    page: int = 1
    limit: int = 10
