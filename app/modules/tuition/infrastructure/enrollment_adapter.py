from datetime import datetime
from sqlmodel import select
from app.core.db import SessionDep
from app.modules.enrollment.application.contracts import TuitionServiceContract
from app.modules.tuition.infrastructure.models import ParametrizarPension, Pension

class TuitionEnrollmentAdapter(TuitionServiceContract):
    def __init__(self, session: SessionDep):
        self.session = session

    def create_pension_account(self, student_id: int, grade_id: int, year: int) -> None:
        pension_param_stmt = select(ParametrizarPension).where(
            ParametrizarPension.grado_id == grade_id, ParametrizarPension.anio == year
        )
        para_pension = self.session.exec(pension_param_stmt).first()
        if para_pension is None:
            para_pension = ParametrizarPension(grado_id=grade_id, anio=year, valor=0)
            self.session.add(para_pension)
            self.session.flush()

        assert para_pension.id is not None

        pension_stmt = select(Pension).where(
            Pension.estudiante_id == student_id,
            Pension.para_pension_id == para_pension.id,
        )
        existing_pension = self.session.exec(pension_stmt).first()
        if not existing_pension:
            pension_record = Pension(
                para_pension_id=para_pension.id,
                estudiante_id=student_id,
                grado_id=grade_id,
                valor_total=para_pension.valor,
                fecha_registro=datetime.now(),
                estado_pension=False,
            )
            self.session.add(pension_record)
            self.session.flush()
