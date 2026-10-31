from app.core.db import SessionDep
from app.modules.peace_safe.domain.service import PeaceSafeService
from app.modules.peace_safe.infrastructure.repository import PeaceSafeRepository


class GetDashboardStats:
    """
    Use case to retrieve aggregated student statistics for the institutional dashboard.
    """

    def __init__(self, session: SessionDep):
        self.service = PeaceSafeService(PeaceSafeRepository(session))

    async def execute(self) -> dict:
        """
        Returns the counts used by the dashboard:
          - total_estudiantes: total active students
          - paz_y_salvo: students who have generated a paz_y_salvo in the active period
          - pendientes: active students without a paz_y_salvo yet
          - alertas: open classroom incidents (Observador records still open)
        """
        return self.service.get_dashboard_stats()
