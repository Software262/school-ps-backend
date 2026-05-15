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
    def get_next_cuota_number(previous_installments: List[TuitionInstallment]) -> int:
        """
        Calculates the next installment number (cuota).
        """
        if not previous_installments:
            return 1
        return max(inst.cuota for inst in previous_installments) + 1
