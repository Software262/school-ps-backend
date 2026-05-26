from pydantic import BaseModel, Field


class FilterPagination(BaseModel):
    page: int = Field(default=1)
    limit: int = Field(default=10)
