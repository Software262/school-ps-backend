from app.modules.tuition.domain.repositories import TuitionRepository
from app.modules.tuition.domain.service import TuitionService
from app.modules.tuition.domain.entities import TuitionInstallment
from app.modules.tuition.schemas.request import PaymentCreateRequest


class RegisterTuitionPaymentUseCase:
    def __init__(self, repository: TuitionRepository):
        self.repository = repository

    def execute(self, request: PaymentCreateRequest) -> TuitionInstallment:
        account = self.repository.get_account_by_student_id(request.estudiante_id)
        if not account:
            raise ValueError(
                f"No pension account found for student {request.estudiante_id}"
            )

        previous_installments = self.repository.get_installments_by_month(
            student_id=request.estudiante_id, mes=request.mes
        )

        monthly_total = 0
        if previous_installments:
            monthly_total = previous_installments[0].valor_total
        else:
            monthly_total = account.valor_total // 10

        TuitionService.validate_payment_amount(
            previous_installments=previous_installments,
            new_payment_amount=request.valor_pagado,
            total_monthly_value=monthly_total,
        )

        faltante = TuitionService.calculate_installment_status(
            previous_installments=previous_installments,
            new_payment_amount=request.valor_pagado,
            total_monthly_value=monthly_total,
        )

        next_cuota = TuitionService.get_next_cuota_number(previous_installments)

        new_installment = TuitionInstallment(
            pension_id=account.id or 0,
            estudiante_id=request.estudiante_id,
            mes=request.mes,
            cuota=next_cuota,
            valor_total=monthly_total,
            valor_pagado=request.valor_pagado,
            fecha_pago=request.fecha_pago,
            faltante=faltante,
        )

        saved_installment = self.repository.save_installment(new_installment)
        return saved_installment
