from app.modules.tuition.domain.entities import TuitionInstallment, TuitionAccount
from app.modules.tuition.domain.repositories import TuitionRepository
from app.modules.tuition.schemas.request import PaymentCreateRequest


class TuitionService:
    def __init__(self, repository: TuitionRepository):
        self.repository = repository

    def get_student_account(self, student_id: int) -> TuitionAccount | None:
        """
        Obtiene la cuenta de pensión asociada a un estudiante específico.
        Enriquece cada cuota con el total acumulado del mes y el saldo pendiente.
        """
        account = self.repository.get_account_by_student_id(student_id)
        if not account:
            return None

        monthly_value = account.valor_total

        # Calcular el total pagado por mes agrupando todas las cuotas
        totals_by_month: dict[int, int] = {}
        for inst in account.installments:
            totals_by_month[inst.mes] = (
                totals_by_month.get(inst.mes, 0) + inst.valor_pagado
            )

        # Enriquecer cada cuota con los acumulados calculados
        for inst in account.installments:
            inst.total_pagado_mes = totals_by_month.get(inst.mes, 0)
            inst.saldo_pendiente = max(monthly_value - inst.total_pagado_mes, 0)

        return account

    def register_payment(self, request: PaymentCreateRequest) -> TuitionInstallment:
        """
        Registra un nuevo abono a la pensión de un estudiante aplicando validaciones financieras.
        """
        account = self.repository.get_account_by_student_id(request.estudiante_id)
        if not account:
            raise ValueError(
                f"No se encontró cuenta de pensión para el estudiante {request.estudiante_id}"
            )

        if not self.validate_consecutive_months(account, request.mes):
            previous_month = request.mes - 1
            raise ValueError(
                f"No puede pagar el mes {request.mes} porque el mes anterior ({previous_month}) no ha sido pagado en su totalidad."
            )

        previous_installments = self.repository.get_installments_by_month(
            student_id=request.estudiante_id, mes=request.mes
        )

        monthly_total = 0
        if previous_installments:
            monthly_total = previous_installments[0].valor_total
        else:
            monthly_total = account.valor_total

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

        total_paid_so_far = sum(inst.valor_pagado for inst in previous_installments)
        total_pagado_mes = total_paid_so_far + request.valor_pagado
        saldo_pendiente = max(monthly_total - total_pagado_mes, 0)

        new_installment = TuitionInstallment(
            pension_id=account.id or 0,
            estudiante_id=request.estudiante_id,
            mes=request.mes,
            cuota=next_cuota,
            valor_total=monthly_total,
            valor_pagado=request.valor_pagado,
            fecha_pago=request.fecha_pago,
            faltante=faltante,
            total_pagado_mes=total_pagado_mes,
            saldo_pendiente=saldo_pendiente,
        )

        return self.repository.save_installment(new_installment)

    def validate_consecutive_months(
        self, account: TuitionAccount, target_month: int
    ) -> bool:
        """
        Valida que el mes anterior haya sido pagado en su totalidad antes de permitir
        el pago del mes actual, garantizando pagos consecutivos.

        Retorna:
            True si el pago puede proceder (mes 1 o mes anterior saldado).
            False si el mes anterior aún tiene saldo pendiente.
        """
        if target_month <= 1:
            return True

        previous_month = target_month - 1
        prev_month_installments = [
            inst for inst in account.installments if inst.mes == previous_month
        ]

        monthly_total = account.valor_total
        total_paid_prev_month = sum(
            inst.valor_pagado for inst in prev_month_installments
        )

        return total_paid_prev_month >= monthly_total

    def calculate_installment_status(
        self,
        previous_installments: list[TuitionInstallment],
        new_payment_amount: int,
        total_monthly_value: int,
    ) -> bool:
        """
        Calcula si el mes todavía tiene saldo pendiente (faltante == True)
        después de aplicar el nuevo abono.
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
        Valida que un nuevo abono no exceda el total mensual permitido
        y que el mes no se encuentre ya pagado en su totalidad.
        """
        total_paid_so_far = sum(inst.valor_pagado for inst in previous_installments)

        if total_paid_so_far >= total_monthly_value:
            raise ValueError(
                "El estudiante ya se encuentra en paz y salvo en este módulo para el mes seleccionado."
            )

        if total_paid_so_far + new_payment_amount > total_monthly_value:
            faltante = total_monthly_value - total_paid_so_far
            raise ValueError(
                f"El abono supera el saldo permitido. El saldo faltante es de solo {faltante}."
            )

    def get_next_cuota_number(
        self, previous_installments: list[TuitionInstallment]
    ) -> int:
        """
        Calcula el siguiente número de cuota (consecutivo) para el mes.
        """
        if not previous_installments:
            return 1
        return max(inst.cuota for inst in previous_installments) + 1
