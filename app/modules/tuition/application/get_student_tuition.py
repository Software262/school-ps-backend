from app.core.db import SessionDep
from app.modules.tuition.infrastructure.repositories import SQLModelTuitionRepository
from app.modules.tuition.domain.service import TuitionService
from app.modules.tuition.domain.entities import TuitionAccount
from app.modules.tuition.schemas.response import TuitionAccountResponse, TuitionInstallmentResponse


class GetStudentTuitionUseCase:
    def __init__(self, session: SessionDep):
        repo = SQLModelTuitionRepository(session)
        self.service = TuitionService(repo)

    def execute(self, student_id: int) -> TuitionAccountResponse | None:
        account = self.service.get_student_account(student_id)
        if not account:
            return None
        return self._build_account_response(account)

    def _build_account_response(self, account: TuitionAccount) -> TuitionAccountResponse:
        """Helper: construye TuitionAccountResponse con las 12 cuotas mensuales."""
        TOTAL_MONTHS = 12  # TODO: leer desde ParametrizarPension.num_meses cuando el Tech Lead agregue la columna
        monthly_value = account.valor_total  # El valor guardado es el costo mensual

        totals_by_month: dict[int, int] = {}
        for inst in account.installments:
            totals_by_month[inst.mes] = totals_by_month.get(inst.mes, 0) + inst.valor_pagado

        installments_response = []
        for mes in range(1, TOTAL_MONTHS + 1):
            mes_trans = [i for i in account.installments if i.mes == mes]
            total_pagado = totals_by_month.get(mes, 0)
            saldo_pendiente = max(monthly_value - total_pagado, 0)

            if mes_trans:
                last_inst = mes_trans[-1]
                installments_response.append(
                    TuitionInstallmentResponse(
                        id=last_inst.id or 0,
                        mes=mes,
                        cuota=last_inst.cuota,
                        valor_total=monthly_value,
                        valor_pagado=last_inst.valor_pagado,
                        total_pagado_mes=total_pagado,
                        saldo_pendiente=saldo_pendiente,
                        fecha_pago=last_inst.fecha_pago,
                        faltante=saldo_pendiente > 0,
                    )
                )
            else:
                installments_response.append(
                    TuitionInstallmentResponse(
                        id=-mes,
                        mes=mes,
                        cuota=mes,
                        valor_total=monthly_value,
                        valor_pagado=0,
                        total_pagado_mes=0,
                        saldo_pendiente=monthly_value,
                        fecha_pago=None,
                        faltante=True,
                    )
                )

        return TuitionAccountResponse(
            estudiante_id=account.estudiante_id,
            valor_total_anual=account.valor_total,
            estado_pension_general=account.estado_pension,
            installments=installments_response,
        )
