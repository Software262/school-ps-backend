from typing import Protocol

from fastapi import UploadFile, status

from app.modules.inventory.schemas.request import InventoryItemRequest
from app.modules.inventory.schemas.response import ImportItemsResponse, ImportRowError
from app.modules.inventory.utils.file import validate_data, validate_file
from app.shared.utils.response import Response


class ItemsFileImporter(Protocol):
    """Cualquier caso de uso capaz de procesar las filas validadas del archivo."""

    # Tipo de inventario fijo del modulo (banda, deporte). ``None`` en el
    # importador generico de inventario, donde el tipo viaja en el archivo.
    allowed_type: str | None

    async def execute(
        self,
        valid_items: list[tuple[int, InventoryItemRequest]],
        parse_errors: list[ImportRowError],
    ) -> ImportItemsResponse: ...


async def import_items_from_upload(file: UploadFile, importer: ItemsFileImporter):
    """Valida el archivo subido y delega el procesamiento en ``importer``.

    Centraliza la validación de archivo, el parseo de filas y la construcción de
    la respuesta para que cada módulo (inventario, banda, deporte) solo aporte su
    caso de uso con la restricción de tipo correspondiente.
    """
    data = await validate_file(file=file)

    if data is None:
        return Response(
            data=None,
            message="Archivo invalido solamente se aceptan csv o excel",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={},
        ).to_dict()

    valid_items, parse_errors = await validate_data(
        filename=file.filename, data=data, default_type=importer.allowed_type
    )

    if not valid_items and not parse_errors:
        return Response(
            data=None,
            message="El archivo no contiene filas para procesar",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"message": "El archivo no contiene filas para procesar"},
        ).to_dict()

    res = await importer.execute(valid_items=valid_items, parse_errors=parse_errors)

    success = res.failed == 0
    if success:
        message = (
            f"Archivo procesado: {res.created} creados, {res.updated} actualizados"
        )
    else:
        message = (
            f"Archivo procesado con errores: {res.created} creados, "
            f"{res.updated} actualizados, {res.failed} con error"
        )

    return Response(
        data=res,
        message=message,
        success=success,
        status_code=status.HTTP_200_OK,
        details={"message": message},
    ).to_dict()
