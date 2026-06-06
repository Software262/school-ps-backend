from sqlmodel import select, col
from app.core.db import SessionDep
from app.modules.cafeteria.infrastructure.models import Cafeteria
from app.modules.cafeteria.domain.repositories import CafeteriaRepositoryInterface


class CafeteriaRepository(CafeteriaRepositoryInterface):
    def __init__(self, session: SessionDep):
        self.session = session

    async def get_all_debtors(self, periodo_id: int) -> list[Cafeteria]:
        statement = select(Cafeteria).where(
            col(Cafeteria.periodo_id) == periodo_id,
            col(Cafeteria.estado_cafeteria).is_(False),
        )
        return list(self.session.exec(statement).all())

    async def get_by_id(self, registro_id: int) -> Cafeteria | None:
        return self.session.get(Cafeteria, registro_id)

    async def get_by_student_and_period(
        self, estudiante_id: int, periodo_id: int
    ) -> Cafeteria | None:
        statement = select(Cafeteria).where(
            col(Cafeteria.estudiante_id) == estudiante_id,
            col(Cafeteria.periodo_id) == periodo_id,
        )
        return self.session.exec(statement).first()

    async def save(self, record: Cafeteria) -> Cafeteria:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    async def get_multiple_by_ids(self, registro_ids: list[int]) -> list[Cafeteria]:
        statement = select(Cafeteria).where(col(Cafeteria.id).in_(registro_ids))
        return list(self.session.exec(statement).all())
