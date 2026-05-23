from abc import ABC, abstractmethod

from app.modules.tuition.domain.entities import TuitionAccount, TuitionInstallment


class TuitionRepository(ABC):
    @abstractmethod
    def get_account_by_student_id(self, student_id: int) -> TuitionAccount | None:
        pass

    @abstractmethod
    def save_account(self, account: TuitionAccount) -> TuitionAccount:
        pass

    @abstractmethod
    def get_installments_by_month(
        self, student_id: int, mes: int
    ) -> list[TuitionInstallment]:
        pass

    @abstractmethod
    def save_installment(self, installment: TuitionInstallment) -> TuitionInstallment:
        pass
