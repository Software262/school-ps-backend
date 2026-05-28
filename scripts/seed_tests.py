"""
Script temporal de seed para cargar datos de prueba del módulo Tests.
"""

from datetime import datetime
from sqlmodel import Session, SQLModel, select
from app.core.db import engine
from app.modules.enrollment.infrastructure.models import Estudiante, Complementario
from app.modules.tests.infrastructure.models import DetallePrueba


def seed_tests() -> None:
    # Asegurarse de que las tablas estén creadas
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        existing = session.exec(select(DetallePrueba)).all()
        for e in existing:
            session.delete(e)
        session.commit()

        estudiantes = session.exec(select(Estudiante)).all()
        if not estudiantes:
            print("Error: No hay estudiantes. Ejecuta scripts/seed.py primero.")
            return

        est1 = estudiantes[0]
        est2 = estudiantes[1] if len(estudiantes) > 1 else est1

        # Crear complementarios para pruebas si no existen
        comp_test = session.exec(
            select(Complementario).where(
                Complementario.tipo_complementario == "Simulacro ICFES 2024"
            )
        ).first()

        if not comp_test:
            comp_test = Complementario(
                tipo_complementario="Simulacro ICFES 2024",
                anio=2026,
                valor=50000,
                estado_complemento="Activo",
                uso_matricula=False,
            )
            session.add(comp_test)
            session.commit()
            session.refresh(comp_test)

        comp_test_2 = session.exec(
            select(Complementario).where(
                Complementario.tipo_complementario == "Prueba Saber 10"
            )
        ).first()

        if not comp_test_2:
            comp_test_2 = Complementario(
                tipo_complementario="Prueba Saber 10",
                anio=2026,
                valor=40000,
                estado_complemento="Activo",
                uso_matricula=False,
            )
            session.add(comp_test_2)
            session.commit()
            session.refresh(comp_test_2)

        detalles = [
            DetallePrueba(
                estudiante_id=est1.id,
                complementario_id=comp_test.id,
                tipo_prueba="icfes",
                estado="pagada",
                valor_pagado=50000,
                created_at=datetime.utcnow(),
            ),
            DetallePrueba(
                estudiante_id=est2.id,
                complementario_id=comp_test.id,
                tipo_prueba="icfes",
                estado="pendiente",
                valor_pagado=0,
                created_at=datetime.utcnow(),
            ),
            DetallePrueba(
                estudiante_id=est1.id,
                complementario_id=comp_test_2.id,
                tipo_prueba="saber",
                estado="pago-parcial",
                valor_pagado=20000,
                created_at=datetime.utcnow(),
            ),
        ]

        session.add_all(detalles)
        session.commit()
        print("[OK] Seed de Tests ejecutado exitosamente.")


if __name__ == "__main__":
    seed_tests()
