from sqlmodel import Session

from app.modules.peace_safe.infrastructure.repository import PeaceSafeRepository


class SearchStudents:
    def __init__(self, session: Session):
        self.repo = PeaceSafeRepository(session)

    async def execute(self, query: str) -> list[dict]:
        students = self.repo.search_students(query)
        return [
            {
                "id": s.id,
                "nombre": s.nombre,
                "documento": s.documento,
            }
            for s in students
        ]
