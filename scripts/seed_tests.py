from datetime import datetime
from sqlmodel import Session, SQLModel, select, text
from app.core.db import engine
from app.modules.enrollment.infrastructure.models import Estudiante, Complementario
from app.modules.tests.infrastructure.models import DetallePrueba


def seed_tests() -> None:
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Limpiar detalleprueba
        session.exec(text("TRUNCATE TABLE detalleprueba CASCADE"))
        session.commit()

        estudiantes = session.exec(select(Estudiante)).all()
        if not estudiantes:
            print("Error: No hay estudiantes.")
            return

        # Seleccionar las dos pruebas solicitadas
        c1 = session.exec(
            select(Complementario).where(
                Complementario.tipo_complementario == "Prueba ICFES"
            )
        ).first()
        c2 = session.exec(
            select(Complementario).where(
                Complementario.tipo_complementario == "Simulacro"
            )
        ).first()

        est1 = estudiantes[0]
        est2 = estudiantes[1] if len(estudiantes) > 1 else est1

        detalles = [
            DetallePrueba(
                estudiante_id=est1.id,
                complementario_id=c1.id,
                tipo_prueba="icfes",
                estado="pagada",
                valor_pagado=45000,
                created_at=datetime.now(),
            ),
            DetallePrueba(
                estudiante_id=est2.id,
                complementario_id=c2.id,
                tipo_prueba="simulacro",
                estado="pendiente",
                valor_pagado=0,
                created_at=datetime.now(),
            ),
            DetallePrueba(
                estudiante_id=est1.id,
                complementario_id=c2.id,
                tipo_prueba="simulacro",
                estado="pago-parcial",
                valor_pagado=10000,
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
