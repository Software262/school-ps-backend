from app.core.db import SessionDep
from app.modules.enrollment.infrastructure.models import Complementario


class UpdateTestComplementary:
    """Actualiza el nombre y valor de un complementario de tipo prueba."""

    def __init__(self, session: SessionDep):
        self.session = session

    def execute(self, comp_id: int, tipo_complementario: str, valor: int) -> int:
        comp = self.session.get(Complementario, comp_id)
        if not comp:
            raise ValueError("Prueba no encontrada")

        comp.tipo_complementario = tipo_complementario
        comp.valor = valor

        self.session.add(comp)
        self.session.commit()
        self.session.refresh(comp)
        return int(comp.id) if comp.id is not None else 0
