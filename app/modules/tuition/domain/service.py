from typing import List

from app.modules.tuition.domain.entities import TuitionInstallment


class TuitionService:
    @staticmethod
    def calculate_installment_status(
        previous_installments: List[TuitionInstallment],
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

    @staticmethod
    def validate_payment_amount(
        previous_installments: List[TuitionInstallment],
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

    @staticmethod
    def get_next_cuota_number(previous_installments: List[TuitionInstallment]) -> int:
        """
        Calculates the next installment number (cuota).
        """
        if not previous_installments:
            return 1
        return max(inst.cuota for inst in previous_installments) + 1
