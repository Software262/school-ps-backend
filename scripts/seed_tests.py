from datetime import datetime
from sqlmodel import Session, SQLModel, select, text, col
from app.core.db import engine
from app.modules.enrollment.infrastructure.models import (
    Estudiante,
    Complementario,
    Periodo,
)
from app.modules.tests.infrastructure.models import DetallePrueba


def seed_tests() -> None:
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Limpiar detalleprueba
        session.execute(text("TRUNCATE TABLE detalleprueba CASCADE"))
        session.commit()

        estudiantes = session.exec(select(Estudiante)).all()
        if not estudiantes:
            print("Error: No hay estudiantes.")
            return

        # Seleccionar las dos pruebas solicitadas
        c1 = session.exec(
            select(Complementario).where(
                Complementario.tipo_complementario == "Prueba Saber 10"
            )
        ).first()
        c2 = session.exec(
            select(Complementario).where(
                Complementario.tipo_complementario == "Simulacro ICFES 2024"
            )
        ).first()

        est1 = estudiantes[0]
        est2 = estudiantes[1] if len(estudiantes) > 1 else est1

        assert c1 is not None, "Complementario Prueba Saber 10 no encontrado"
        assert c2 is not None, "Complementario Simulacro ICFES 2024 no encontrado"

        periodo = session.exec(
            select(Periodo).where(col(Periodo.estado).is_(True))
        ).first()
        assert periodo is not None, "Periodo activo no encontrado"

        detalles = [
            DetallePrueba(
                estudiante_id=int(est1.id) if est1.id is not None else 0,
                complementario_id=int(c1.id) if c1.id is not None else 0,
                tipo_prueba="icfes",
                estado="pagada",
                valor_pagado=40000,
                periodo_id=int(periodo.id) if periodo.id is not None else 0,
                created_at=datetime.now(),
            ),
            DetallePrueba(
                estudiante_id=int(est2.id) if est2.id is not None else 0,
                complementario_id=int(c2.id) if c2.id is not None else 0,
                tipo_prueba="simulacro",
                estado="pendiente",
                valor_pagado=0,
                periodo_id=int(periodo.id) if periodo.id is not None else 0,
                created_at=datetime.now(),
            ),
            DetallePrueba(
                estudiante_id=int(est1.id) if est1.id is not None else 0,
                complementario_id=int(c2.id) if c2.id is not None else 0,
                tipo_prueba="simulacro",
                estado="pago-parcial",
                valor_pagado=10000,
                periodo_id=int(periodo.id) if periodo.id is not None else 0,
                created_at=datetime.now(),
            ),
        ]

        session.add_all(detalles)
        session.commit()
        print(
            "[OK] Asignaciones de prueba creadas: Estudiantes Juan y Maria con Prueba ICFES y Simulacro."
        )


if __name__ == "__main__":
    seed_tests()
