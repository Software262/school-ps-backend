import math

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.shared.schemas.filter_pagination_response import Pagination


class Response:
    def __init__(
        self,
        data: object | list[object] = None,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK,
        details: dict | None = None,
        success: bool = True,
    ):
        self.data = data
        self.status_code = status_code
        self.message = message
        self.details = details
        self.success = success

    def filterPagination(self, page: int, limit: int, total: int = 0):
        total_pages = math.ceil(total / limit)

        if isinstance(self.data, list):
            self.data = Pagination(
                items=self.data,
                current_page=page,
                page_size=limit,
                total=total,
                total_pages=total_pages,
                previous=page > 1,
                next=page < total_pages,
            )
        return self

    def _serialize_item(self, item):
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

    def to_dict(self):
        if isinstance(self.data, list):
            data_to_encode = [self._serialize_item(x) for x in self.data]
        else:
            data_to_encode = self._serialize_item(self.data)

        encoded = (
            jsonable_encoder(data_to_encode) if data_to_encode is not None else None
        )

        content = {
            "statusCode": self.status_code,
            "success": self.success,
            "data": encoded,
            "message": self.message,
            "details": self.details,
        }

        return JSONResponse(status_code=self.status_code, content=content)
