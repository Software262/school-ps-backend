from sqlmodel import select, Session

from app.modules.chess.infrastructure.models import ChessBorrowingExtension, ChessNoveltyExtension
from app.modules.inventory.infrastructure.models import Novedad, Prestamo


class ChessRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_borrowing_extension(self, prestamo_id: int, grado_id: int | None = None) -> ChessBorrowingExtension:
        extension = ChessBorrowingExtension(prestamo_id=prestamo_id, grado_id=grado_id)
        self.session.add(extension)
        self.session.flush()
        return extension

    def create_novelty_extension(self, novedad_id: int) -> ChessNoveltyExtension:
        extension = ChessNoveltyExtension(novedad_id=novedad_id)
        self.session.add(extension)
        self.session.flush()
        return extension

    def get_novelty_extension(self, novedad_id: int) -> ChessNoveltyExtension | None:
        query = select(ChessNoveltyExtension).where(ChessNoveltyExtension.novedad_id == novedad_id)
        result = self.session.exec(query).first()
        return result

    def get_open_novelties_by_student(self, estudiante_id: int) -> list[Novedad]:
        query = (
            select(Novedad)
            .join(Prestamo)
            .where(Prestamo.id == Novedad.prestamo_id)
            .where(Prestamo.estudiante_id == estudiante_id)
            .where(Novedad.resuelta == False)
        )
        return list(self.session.exec(query).all())
