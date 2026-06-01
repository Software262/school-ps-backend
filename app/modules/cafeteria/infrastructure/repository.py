from sqlmodel import select, col, or_
from app.core.db import SessionDep
from app.modules.cafeteria.infrastructure.models import Cafeteria
from app.modules.cafeteria.domain.repositories import CafeteriaRepositoryInterface
from app.modules.enrollment.infrastructure.models import Estudiante, Grado


class CafeteriaRepository(CafeteriaRepositoryInterface):
    def __init__(self, session: SessionDep):
        self.session = session

    async def get_all_debtors(self, periodo_id: int) -> list:
        """Trae deudores con info de estudiante y grado."""
        statement = (
            select(Cafeteria, Estudiante, Grado)
            .join(Estudiante, col(Cafeteria.estudiante_id) == col(Estudiante.id))
            .join(Grado, col(Estudiante.grado_id) == col(Grado.id))
            .where(col(Cafeteria.periodo_id) == periodo_id)
            # USAR .is_(False) para que funcione en SQL y pase el Linter
            .where(col(Cafeteria.estado_cafeteria).is_(False))
        )
        return list(self.session.exec(statement).all())

    async def search_general_students(
        self, query: str = "", grado_id: int | None = None
    ) -> list:
        """Búsqueda insensible a mayúsculas por nombre/doc."""
        statement = (
            select(Estudiante, Grado)
            .join(Grado, col(Estudiante.grado_id) == col(Grado.id))
            .where(col(Estudiante.activo))
        )

        if query:
            pattern = f"%{query}%"
            statement = statement.where(
                or_(
                    col(Estudiante.nombre).ilike(pattern),
                    col(Estudiante.documento).ilike(pattern),
                )
            )

        if grado_id:
            statement = statement.where(col(Estudiante.grado_id) == grado_id)

        if not query and not grado_id:
            statement = statement.limit(15)

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

    async def get_report_data(self, periodo_id: int) -> list:
        statement = (
            select(Cafeteria, Estudiante, Grado)
            .join(Estudiante, col(Cafeteria.estudiante_id) == col(Estudiante.id))
            .join(Grado, col(Estudiante.grado_id) == col(Grado.id))
            .where(col(Cafeteria.periodo_id) == periodo_id)
        )
        return list(self.session.exec(statement).all())

    async def get_all_grades(self) -> list:
        return list(self.session.exec(select(Grado)).all())
