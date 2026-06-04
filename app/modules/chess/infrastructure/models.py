from sqlmodel import Field
from app.shared.infrastructure.base import Base


class ChessBorrowingExtension(Base, table=True):
    __tablename__ = "chess_borrowing_extension"  # type: ignore

    prestamo_id: int = Field(foreign_key="prestamo.id", unique=True, index=True)
    grado_id: int | None = Field(default=None, foreign_key="grado.id")


class ChessNoveltyExtension(Base, table=True):
    __tablename__ = "chess_novelty_extension"  # type: ignore

    novedad_id: int = Field(foreign_key="novedad.id", unique=True, index=True)
    resuelta_por_id: int | None = Field(default=None) # Id of the admin/user who resolved it
    notas_resolucion: str | None = Field(default=None, max_length=500)
