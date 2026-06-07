from tempfile import SpooledTemporaryFile

from fastapi import UploadFile
from pandas import read_csv, read_excel

from app.modules.inventory.schemas.request import InventoryItemRequest

content_types = {
    "text/csv": ".csv",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
}


async def validate_file(file: UploadFile) -> bytes | None:
    if not file.filename:
        return None

    if file.content_type not in content_types.keys():
        return None

    return await file.read()


async def validate_data(
    filename: str | None, data: bytes
) -> list[InventoryItemRequest]:
    if not filename:
        return []

    with SpooledTemporaryFile() as buffer:
        buffer.write(data)
        buffer.seek(0)

        if filename.endswith(
            content_types[
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ]
        ) or filename.endswith(content_types["application/vnd.ms-excel"]):
            df = read_excel(buffer)
        else:
            df = read_csv(buffer)

    new_data = df.drop_duplicates()
    records = new_data.to_dict(orient="records")

    validateItems: list[InventoryItemRequest] = []

    for _, r in enumerate(records):
        try:
            validateItems.append(InventoryItemRequest(**r))
        except Exception:
            return validateItems

    return validateItems
