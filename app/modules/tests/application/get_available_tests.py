from app.core.db import SessionDep
from sqlmodel import select
from app.modules.enrollment.infrastructure.models import Complementario


class GetAvailableTests:
    def __init__(self, session: SessionDep):
        self.session = session

    async def execute(self):
        return self.session.exec(
            select(Complementario)
            .where(Complementario.estado_complemento == "Activo")
            .where(~Complementario.uso_matricula)
        ).all()
