from fastapi import status

from app.shared.schemas.filter_pagination import Pagination


class Response:
    def __init__(
        self,
        data: object | list[object] = None,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK,
        details: dict | None = None,
    ):
        self.data = data
        self.status_code = status_code
        self.message = message
        self.details = details

    def filterPagination(self, page: int, limit: int):
        if isinstance(self.data, list):
            self.data = Pagination(items=self.data, current_page=page, page_size=limit)
        return self

    def to_dict(self) -> dict:
        return {
            "statusCode": self.status_code,
            "data": self.data,
            "message": self.message,
            "details": self.details,
        }
