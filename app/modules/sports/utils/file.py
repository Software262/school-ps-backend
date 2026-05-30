from tempfile import SpooledTemporaryFile

from fastapi import UploadFile
from pandas import read_csv, read_excel

from app.modules.sports.schemas.request import SportItemFileRequest

content_types = {
    "text/csv": ".csv",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
}


async def validate_sport_file(file: UploadFile) -> bytes | None:
    if not file.filename:
        return None
    if file.content_type not in content_types:
        return None
    return await file.read()


async def validate_sport_file_data(
    filename: str | None, data: bytes
) -> list[SportItemFileRequest]:
    """
    Parsea el archivo y valida cada fila como SportItemFileRequest.
    Las columnas esperadas son: nombre, cantidad, estado_objeto, observacion (opcional).
    tipo_inventario_id NO debe estar en el archivo; se inyecta internamente.
    """
    if not filename:
        return []

    with SpooledTemporaryFile() as buffer:
        buffer.write(data)
        buffer.seek(0)

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            df = read_excel(buffer)
        else:
            df = read_csv(buffer)

    # Eliminar columna tipo_inventario_id si alguien la incluyó por error
    df = df.drop(columns=["tipo_inventario_id"], errors="ignore")

    new_data = df.drop_duplicates()
    records = new_data.to_dict(orient="records")

    validated: list[SportItemFileRequest] = []
    for r in records:
        try:
            validated.append(SportItemFileRequest(**r))
        except Exception:
            # Detiene en la primera fila inválida, igual que en inventario
            return validated

    return validated
