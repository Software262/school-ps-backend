from app.modules.tuition.domain.entities import TuitionInstallment, TuitionAccount
from app.modules.tuition.domain.repositories import TuitionRepository
from app.modules.tuition.schemas.request import PaymentCreateRequest


class TuitionService:
    def __init__(self, repository: TuitionRepository):
        self.repository = repository

    def get_student_account(self, student_id: int) -> TuitionAccount | None:
        return self.repository.get_account_by_student_id(student_id)

    def register_payment(self, request: PaymentCreateRequest) -> TuitionInstallment:
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

        self.validate_payment_amount(
            previous_installments=previous_installments,
            new_payment_amount=request.valor_pagado,
            total_monthly_value=monthly_total,
        )

        faltante = self.calculate_installment_status(
            previous_installments=previous_installments,
            new_payment_amount=request.valor_pagado,
            total_monthly_value=monthly_total,
        )

        next_cuota = self.get_next_cuota_number(previous_installments)

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

        return self.repository.save_installment(new_installment)

    def calculate_installment_status(
        self,
        previous_installments: list[TuitionInstallment],
        new_payment_amount: int,
        total_monthly_value: int,
    ) -> bool:
        """
        Calculates if the month is still missing payments (faltante == True)
        after the new payment is applied.
        """
        total_paid_so_far = sum(inst.valor_pagado for inst in previous_installments)
        new_total_paid = total_paid_so_far + new_payment_amount

        return new_total_paid < total_monthly_value

    def validate_payment_amount(
        self,
        previous_installments: list[TuitionInstallment],
        new_payment_amount: int,
        total_monthly_value: int,
    ) -> None:
        """
        Validates that a new payment does not exceed the monthly total
        and that the month isn't already fully paid.
        """
        total_paid_so_far = sum(inst.valor_pagado for inst in previous_installments)

        if total_paid_so_far >= total_monthly_value:
            raise ValueError(
                "El mes ya se encuentra pagado en su totalidad. No se requieren más abonos."
            )

        if total_paid_so_far + new_payment_amount > total_monthly_value:
            faltante = total_monthly_value - total_paid_so_far
            raise ValueError(
                f"El abono excede el valor pendiente del mes. El saldo faltante es de solo {faltante}."
            )

    def get_next_cuota_number(
        self, previous_installments: list[TuitionInstallment]
    ) -> int:
        """
        Calculates the next installment number (cuota).
        """
        if not previous_installments:
            return 1
        return max(inst.cuota for inst in previous_installments) + 1
