from fastapi import status
from fastapi.encoders import jsonable_encoder

from app.shared.schemas.filter_pagination_response import Pagination


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
            self.data = Pagination(
                items=self.data,
                current_page=page,
                page_size=limit,
            )
        return self

    def to_dict(self) -> dict:
        def serialize_item(item):
            if hasattr(item, "model_dump") and callable(getattr(item, "model_dump")):
                try:
                    return item.model_dump()
                except Exception:
                    pass

            if hasattr(item, "dict") and callable(getattr(item, "dict")):
                try:
                    return item.dict()
                except Exception:
                    pass

            return item

        if isinstance(self.data, list):
            data_to_encode = [serialize_item(x) for x in self.data]
        else:
            data_to_encode = serialize_item(self.data)

        encoded = (
            jsonable_encoder(data_to_encode) if data_to_encode is not None else None
        )

        return {
            "statusCode": self.status_code,
            "data": encoded,
            "message": self.message,
            "details": self.details,
        }
