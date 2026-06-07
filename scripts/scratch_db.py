from sqlmodel import Session, col, select

from app.core.db import engine
from app.modules.enrollment.infrastructure.models import Estudiante, Matricula, Pago

with Session(engine) as session:
    for mid in [38, 41]:
        mat_stmt = (
            select(Matricula, Estudiante)
            .join(Estudiante, col(Matricula.estudiante_id) == col(Estudiante.id))
            .where(Matricula.id == mid)
        )
        res = session.exec(mat_stmt).first()
        if res:
            mat, est = res
            pago_stmt = select(Pago).where(Pago.matricula_id == mid)
            pagos = session.exec(pago_stmt).all()
            print(
                f"Estudiante: {est.nombre} (ID: {est.id}), Matricula ID: {mid}, Estado actual en DB: {mat.estado_matricula}"
            )
            print(f"  Pagos registrados en DB: {len(pagos)}")
            for p in pagos:
                print(
                    f"    Pago ID: {p.id}, Monto: {p.monto_total}, Fecha: {p.fecha_pago}"
                )
