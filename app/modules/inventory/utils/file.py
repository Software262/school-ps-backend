from tempfile import SpooledTemporaryFile
from typing import Literal

from fastapi import UploadFile
from pandas import DataFrame, notnull, read_csv, read_excel
from pydantic import ValidationError

from app.modules.inventory.schemas.request import InventoryItemRequest
from app.modules.inventory.schemas.response import ImportRowError

content_types = {
    "text/csv": ".csv",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
}

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
CSV_MEDIA_TYPE = "text/csv"

REQUIRED_COLUMNS = {"tipo_inventario", "nombre", "cantidad_total"}

TEMPLATE_COLUMNS = [
    "tipo_inventario",
    "nombre",
    "cantidad_total",
    "observacion",
    "cantidad_disponible",
    "cantidad_mantenimiento",
]

TEMPLATE_EXAMPLE_ROWS = [
    {
        "tipo_inventario": "banda",
        "nombre": "Trompeta",
        "cantidad_total": 10,
        "observacion": "Opcional",
        "cantidad_disponible": 8,
        "cantidad_mantenimiento": 2,
    },
    {
        "tipo_inventario": "ajedrez",
        "nombre": "Tablero",
        "cantidad_total": 5,
        "observacion": None,
        "cantidad_disponible": None,
        "cantidad_mantenimiento": None,
    },
]

# Ejemplo de una sola fila por tipo, usado en las plantillas de cada módulo
# (banda, deporte). Mantiene la plantilla genérica intacta.
TEMPLATE_TYPE_EXAMPLES = {
    "banda": {
        "nombre": "Trompeta",
        "cantidad_total": 10,
        "observacion": "Opcional",
        "cantidad_disponible": 8,
        "cantidad_mantenimiento": 2,
    },
    "deporte": {
        "nombre": "Balon de futbol",
        "cantidad_total": 15,
        "observacion": "Opcional",
        "cantidad_disponible": 15,
        "cantidad_mantenimiento": 0,
    },
    "ajedrez": {
        "nombre": "Tablero",
        "cantidad_total": 5,
        "observacion": None,
        "cantidad_disponible": None,
        "cantidad_mantenimiento": None,
    },
}


def build_template(
    file_format: Literal["xlsx", "csv"],
    type_name: str | None = None,
) -> tuple[bytes, str, str]:
    rows = TEMPLATE_EXAMPLE_ROWS
    columns = TEMPLATE_COLUMNS
    suffix = ""
    if type_name is not None:
        example = TEMPLATE_TYPE_EXAMPLES.get(
            type_name,
            {
                "tipo_inventario": type_name,
                "nombre": "Ejemplo",
                "cantidad_total": 1,
                "observacion": None,
                "cantidad_disponible": None,
                "cantidad_mantenimiento": None,
            },
        )

        example = {k: v for k, v in example.items() if k != "tipo_inventario"}
        columns = [c for c in TEMPLATE_COLUMNS if c != "tipo_inventario"]
        rows = [example]
        suffix = f"_{type_name}"

    df = DataFrame(rows, columns=columns)

    with SpooledTemporaryFile() as buffer:
        if file_format == "csv":
            df.to_csv(buffer, index=False)
            media_type = CSV_MEDIA_TYPE
            filename = f"plantilla_inventario{suffix}.csv"
        else:
            df.to_excel(buffer, index=False, sheet_name="inventario")
            media_type = XLSX_MEDIA_TYPE
            filename = f"plantilla_inventario{suffix}.xlsx"

        buffer.seek(0)
        content = buffer.read()

    return content, media_type, filename


async def validate_file(file: UploadFile) -> bytes | None:
    if not file.filename:
        return None

    if file.content_type not in content_types.keys():
        return None

    return await file.read()


def _format_validation_error(error: ValidationError) -> str:
    messages: list[str] = []
    for err in error.errors():
        field = ".".join(str(loc) for loc in err["loc"]) or "fila"
        messages.append(f"{field}: {err['msg']}")
    return "; ".join(messages)


def _clean_record(record: dict) -> dict:
    """Convierte NaN a None y los escalares de numpy a tipos nativos de Python."""
    cleaned: dict = {}
    for key, value in record.items():
        if value is None:
            cleaned[key] = None
        elif hasattr(value, "item"):
            cleaned[key] = value.item() if notnull(value) else None
        elif not notnull(value):
            cleaned[key] = None
        else:
            cleaned[key] = value
    return cleaned


async def validate_data(
    filename: str | None, data: bytes, default_type: str | None = None
) -> tuple[list[tuple[int, InventoryItemRequest]], list[ImportRowError]]:
    if not filename:
        return [], [ImportRowError(row=0, error="Archivo sin nombre")]

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

    df = df.drop_duplicates()

    required_columns = REQUIRED_COLUMNS
    if default_type is not None:
        required_columns = REQUIRED_COLUMNS - {"tipo_inventario"}

    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        return [], [
            ImportRowError(
                row=1,
                error=(
                    "Faltan columnas obligatorias: "
                    f"{', '.join(sorted(missing_columns))}"
                ),
            )
        ]

    valid_items: list[tuple[int, InventoryItemRequest]] = []
    errors: list[ImportRowError] = []
    seen_names: set[str] = set()

    for position, (_, row) in enumerate(df.iterrows()):
        row_number = position + 2
        record = _clean_record(row.to_dict())
        if default_type is not None:
            record["tipo_inventario"] = default_type

        try:
            item = InventoryItemRequest(**record)
        except ValidationError as error:
            errors.append(
                ImportRowError(
                    row=row_number,
                    nombre=record.get("nombre"),
                    error=_format_validation_error(error),
                )
            )
            continue

        key = item.nombre.strip().lower()
        if key in seen_names:
            errors.append(
                ImportRowError(
                    row=row_number,
                    nombre=item.nombre,
                    error="Nombre duplicado dentro del archivo",
                )
            )
            continue

        seen_names.add(key)
        valid_items.append((row_number, item))

    return valid_items, errors
