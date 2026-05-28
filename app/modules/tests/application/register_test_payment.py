from app.core.db import SessionDep
from app.modules.tests.infrastructure.repository import InternalTestRepository
from app.modules.tests.schemas.request import PaymentRequest
from app.modules.enrollment.infrastructure.models import Complementario


class RegisterTestPayment:
    def __init__(self, session: SessionDep):
        self.repository = InternalTestRepository(session)

    async def execute(self, test_id: int, request: PaymentRequest):
        test = await self.repository.get_test_by_id(test_id)
        if not test:
            raise ValueError("Test not found")

        comp = self.repository.session.get(Complementario, test.complementario_id)
        if not comp:
            raise ValueError("Complementary not found")

        # Sumar el nuevo monto al valor ya pagado
        test.valor_pagado = (test.valor_pagado or 0) + request.monto

        # Actualizar estado según el saldo
        if test.valor_pagado >= comp.valor:
            test.estado = "pagada"
        else:
            test.estado = "pago-parcial"

        self.repository.session.add(test)
        self.repository.session.commit()
        self.repository.session.refresh(test)
        return test
