from datetime import datetime
from sqlmodel import Session, SQLModel, select, text
from app.core.db import engine
from app.modules.enrollment.infrastructure.models import Estudiante, Complementario
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

        assert c1 is not None, "Complementario Prueba ICFES no encontrado"
        assert c2 is not None, "Complementario Simulacro no encontrado"

        detalles = [
            DetallePrueba(
                estudiante_id=int(est1.id) if est1.id is not None else 0,
                complementario_id=int(c1.id),  # type: ignore
                tipo_prueba="icfes",
                estado="pagada",
                valor_pagado=45000,
                created_at=datetime.now(),
            ),
            DetallePrueba(
                estudiante_id=int(est2.id) if est2.id is not None else 0,
                complementario_id=int(c2.id),  # type: ignore
                tipo_prueba="simulacro",
                estado="pendiente",
                valor_pagado=0,
                created_at=datetime.now(),
            ),
            DetallePrueba(
                estudiante_id=int(est1.id) if est1.id is not None else 0,
                complementario_id=int(c2.id),  # type: ignore
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
