from sqlmodel import Field

from app.shared.infrastructure.base import Base


class ChessBorrowingExtension(Base, table=True):
    prestamo_id: int = Field(foreign_key="prestamo.id", unique=True, index=True)
    grado_id: int | None = Field(default=None, foreign_key="grado.id")


class ChessNoveltyExtension(Base, table=True):
    novedad_id: int = Field(foreign_key="novedad.id", unique=True, index=True)
    resuelta_por_id: int | None = Field(
        default=None
    )  # Id of the admin/user who resolved it
    notas_resolucion: str | None = Field(default=None, max_length=500)
