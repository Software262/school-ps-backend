from sqlmodel import select

from app.core.db import SessionDep
from app.modules.chess.infrastructure.models import (
    ChessBorrowingExtension,
    ChessNoveltyExtension,
)
from app.modules.inventory.infrastructure.models import Novedad, Prestamo


class ChessRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def create_borrowing_extension(
        self, prestamo_id: int, grado_id: int | None = None
    ) -> ChessBorrowingExtension:
        extension = ChessBorrowingExtension(prestamo_id=prestamo_id, grado_id=grado_id)
        self.session.add(extension)
        self.session.commit()
        self.session.refresh(extension)
        return extension

    def create_novelty_extension(self, novedad_id: int) -> ChessNoveltyExtension:
        extension = ChessNoveltyExtension(novedad_id=novedad_id)
        self.session.add(extension)
        self.session.commit()
        self.session.refresh(extension)
        return extension

    def get_novelty_extension(self, novedad_id: int) -> ChessNoveltyExtension | None:
        query = select(ChessNoveltyExtension).where(
            ChessNoveltyExtension.novedad_id == novedad_id
        )
        result = self.session.exec(query).first()
        return result

    def get_open_novelties_by_student(self, estudiante_id: int) -> list[Novedad]:
        query = (
            select(Novedad)
            .join(Prestamo)
            .where(Prestamo.id == Novedad.prestamo_id)
            .where(Prestamo.estudiante_id == estudiante_id)
        )
        return [n for n in self.session.exec(query).all() if not n.resuelta]

    def get_novedad_by_id(self, novedad_id: int) -> Novedad | None:
        return self.session.get(Novedad, novedad_id)

    def resolve_novedad_and_extension(
        self, novedad: Novedad, resuelta_por_id: int, notas_resolucion: str
    ) -> None:
        novedad.resuelta = True
        self.session.add(novedad)

        if novedad.id is None:
            raise ValueError("La novedad no tiene un ID válido")
        extension = self.session.exec(
            select(ChessNoveltyExtension).where(
                ChessNoveltyExtension.novedad_id == novedad.id
            )
        ).first()
        if not extension:
            extension = ChessNoveltyExtension(novedad_id=novedad.id)
        extension.resuelta_por_id = resuelta_por_id
        extension.notas_resolucion = notas_resolucion
        self.session.add(extension)
        self.session.commit()
        self.session.refresh(novedad)
        self.session.refresh(extension)
