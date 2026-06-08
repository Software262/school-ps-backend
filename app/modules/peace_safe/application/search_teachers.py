from sqlmodel import Session

from app.modules.peace_safe.infrastructure.repository import PeaceSafeRepository


class SearchTeachers:
    def __init__(self, session: Session):
        self.repo = PeaceSafeRepository(session)

    async def execute(self, query: str) -> list[dict]:
        teachers = self.repo.search_teachers(query)
        return [
            {
                "id": t.id,
                "nombre": t.nombre,
                "documento": t.documento,
                "asignatura": t.asignatura,
            }
            for t in teachers
        ]
