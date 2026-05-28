from datetime import datetime
from sqlmodel import Session, SQLModel, select
from app.core.db import engine
from app.modules.enrollment.infrastructure.models import (
    Grado,
    Acudiente,
    Estudiante,
    Periodo,
)


def seed_grados():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # 1. Crear Acudiente genérico si no existe
        acudiente = session.exec(
            select(Acudiente).where(Acudiente.nombre == "Acudiente Prueba")
        ).first()
        if not acudiente:
            acudiente = Acudiente(
                nombre="Acudiente Prueba",
                parentesco="Padre/Madre",
                telefono="3000000000",
                correo="acudiente@prueba.com",
            )
            session.add(acudiente)
            session.commit()
            session.refresh(acudiente)

        # 2. Crear Grados 10 y 11
        grado_10 = session.exec(select(Grado).where(Grado.nombre == "Grado 10")).first()
        if not grado_10:
            grado_10 = Grado(nombre="Grado 10")
            session.add(grado_10)

        grado_11 = session.exec(select(Grado).where(Grado.nombre == "Grado 11")).first()
        if not grado_11:
            grado_11 = Grado(nombre="Grado 11")
            session.add(grado_11)

        session.commit()
        session.refresh(grado_10)
        session.refresh(grado_11)

        # 3. Crear 5 estudiantes para Grado 10
        for i in range(1, 6):
            doc = f"100000010{i}"
            est = session.exec(
                select(Estudiante).where(Estudiante.documento == doc)
            ).first()
            if not est:
                session.add(
                    Estudiante(
                        grado_id=grado_10.id,
                        acudiente_id=acudiente.id,
                        nombre=f"Estudiante Décimo {i}",
                        documento=doc,
                        activo=True,
                        fecha_activo=datetime.utcnow(),
                    )
                )

        # 4. Crear 10 estudiantes para Grado 11
        for i in range(1, 11):
            doc = f"110000011{i}"
            est = session.exec(
                select(Estudiante).where(Estudiante.documento == doc)
            ).first()
            if not est:
                session.add(
                    Estudiante(
                        grado_id=grado_11.id,
                        acudiente_id=acudiente.id,
                        nombre=f"Estudiante Once {i}",
                        documento=doc,
                        activo=True,
                        fecha_activo=datetime.utcnow(),
                    )
                )

        # 5. Crear Periodos 2026-1 y 2026-2
        # Periodo model: periodo_electivo (datetime), estado (bool), fecha (datetime)
        p1 = session.exec(
            select(Periodo).where(Periodo.periodo_electivo == datetime(2026, 1, 1))
        ).first()
        if not p1:
            session.add(
                Periodo(
                    periodo_electivo=datetime(2026, 1, 1),
                    estado=True,
                    fecha=datetime.utcnow(),
                )
            )

        p2 = session.exec(
            select(Periodo).where(Periodo.periodo_electivo == datetime(2026, 7, 1))
        ).first()
        if not p2:
            session.add(
                Periodo(
                    periodo_electivo=datetime(2026, 7, 1),
                    estado=True,
                    fecha=datetime.utcnow(),
                )
            )

        session.commit()
        print(
            "[OK] Grados 10 y 11 con estudiantes, y periodos 2026 creados exitosamente."
        )


if __name__ == "__main__":
    seed_grados()
