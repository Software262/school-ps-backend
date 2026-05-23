from sqlmodel import select

from app.core.db import SessionDep
from app.modules.tuition.domain.entities import TuitionAccount, TuitionInstallment
from app.modules.tuition.domain.repositories import TuitionRepository
from app.modules.tuition.infrastructure.models import Pension, DetallePension


class SQLModelTuitionRepository(TuitionRepository):
    def __init__(self, session: SessionDep):
        self.session = session

    def get_account_by_student_id(self, student_id: int) -> TuitionAccount | None:
        statement = select(Pension).where(Pension.estudiante_id == student_id)
        pension_model = self.session.exec(statement).first()
        if not pension_model:
            return None

        inst_statement = select(DetallePension).where(
            DetallePension.pension_id == pension_model.id
        )
        installments_models = self.session.exec(inst_statement).all()

        installments = [
            TuitionInstallment(
                id=inst.id,
                pension_id=inst.pension_id,
                estudiante_id=inst.estudiante_id,
                mes=inst.mes,
                cuota=inst.cuota,
                valor_total=inst.valor_total,
                valor_pagado=inst.valor_pagado,
                fecha_pago=inst.fecha_pago,
                faltante=inst.faltante,
            )
            for inst in installments_models
        ]

        return TuitionAccount(
            id=pension_model.id,
            para_pension_id=pension_model.para_pension_id,
            estudiante_id=pension_model.estudiante_id,
            grado_id=pension_model.grado_id,
            valor_total=pension_model.valor_total,
            fecha_registro=pension_model.fecha_registro,
            estado_pension=pension_model.estado_pension,
            installments=installments,
        )

    def save_account(self, account: TuitionAccount) -> TuitionAccount:
        raise NotImplementedError

    def get_installments_by_month(
        self, student_id: int, mes: int
    ) -> list[TuitionInstallment]:
        statement = select(DetallePension).where(
            DetallePension.estudiante_id == student_id, DetallePension.mes == mes
        )
        models = self.session.exec(statement).all()
        return [
            TuitionInstallment(
                id=m.id,
                pension_id=m.pension_id,
                estudiante_id=m.estudiante_id,
                mes=m.mes,
                cuota=m.cuota,
                valor_total=m.valor_total,
                valor_pagado=m.valor_pagado,
                fecha_pago=m.fecha_pago,
                faltante=m.faltante,
            )
            for m in models
        ]

    def save_installment(self, installment: TuitionInstallment) -> TuitionInstallment:
        model = DetallePension(
            pension_id=installment.pension_id,
            estudiante_id=installment.estudiante_id,
            mes=installment.mes,
            cuota=installment.cuota,
            valor_total=installment.valor_total,
            valor_pagado=installment.valor_pagado,
            fecha_pago=installment.fecha_pago,
            faltante=installment.faltante,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        installment.id = model.id
        return installment
