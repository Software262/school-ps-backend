from datetime import datetime
from sqlmodel import Session, SQLModel, text
from app.core.db import engine
from app.modules.enrollment.infrastructure.models import (
    Grado,
    Acudiente,
    Estudiante,
    Periodo,
    Complementario,
    TipoComplementario,
)


def seed_grados():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Limpiar datos previos si existen
        session.execute(
            text(
                "TRUNCATE TABLE estudiante, acudiente, grado, periodo, complementario, tipocomplementario, detalleprueba CASCADE"
            )
        )
        session.commit()

        # 1. Crear Acudientes reales
        acudientes = [
            Acudiente(
                nombre="Carlos Perez",
                parentesco="Padre",
                telefono="3001111001",
                correo="carlos@mail.com",
            ),
            Acudiente(
                nombre="Maria Gomez",
                parentesco="Madre",
                telefono="3001111002",
                correo="maria@mail.com",
            ),
        ]
        session.add_all(acudientes)
        session.commit()
        for a in acudientes:
            session.refresh(a)

        # 2. Crear Grados 10 y 11 solamente
        grado_10 = Grado(nombre="Décimo")
        grado_11 = Grado(nombre="Once")
        session.add_all([grado_10, grado_11])
        session.commit()
        session.refresh(grado_10)
        session.refresh(grado_11)

        # 3. Crear Estudiantes reales para Décimo
        nombres_decimo = [
            ("Juan Perez", "1001001001"),
            ("Maria Gomez", "1001001002"),
            ("Carlos Lopez", "1001001003"),
            ("Ana Martinez", "1001001004"),
            ("Luis Rodriguez", "1001001005"),
        ]
        for i, (nombre, doc) in enumerate(nombres_decimo):
            session.add(
                Estudiante(
                    grado_id=int(grado_10.id) if grado_10.id is not None else 0,
                    acudiente_id=int(acudientes[i % 2].id)
                    if acudientes[i % 2].id is not None
                    else 0,
                    nombre=nombre,
                    documento=doc,
                    activo=True,
                    fecha_activo=datetime.now(),
                )
            )

        # 4. Crear Estudiantes reales para Once
        nombres_once = [
            ("Pedro Vargas", "1001002001"),
            ("Laura Castro", "1001002002"),
            ("David Jimenez", "1001002003"),
            ("Isabella Romero", "1001002004"),
            ("Felipe Suarez", "1001002005"),
        ]
        for i, (nombre, doc) in enumerate(nombres_once):
            session.add(
                Estudiante(
                    grado_id=int(grado_11.id) if grado_11.id is not None else 0,
                    acudiente_id=int(acudientes[i % 2].id)
                    if acudientes[i % 2].id is not None
                    else 0,
                    nombre=nombre,
                    documento=doc,
                    activo=True,
                    fecha_activo=datetime.now(),
                )
            )

        # 5. Crear Periodos 2026-01 y 2026-02
        p1 = Periodo(
            periodo_electivo=datetime(2026, 1, 1), estado=True, fecha=datetime.now()
        )
        p2 = Periodo(
            periodo_electivo=datetime(2026, 7, 1), estado=True, fecha=datetime.now()
        )
        session.add_all([p1, p2])

        # 6. Crear SOLO las 2 pruebas solicitadas: Prueba ICFES y Simulacro
        tipo_prueba = TipoComplementario(nombre="Prueba", estado=True)
        session.add(tipo_prueba)
        session.flush()
        c1 = Complementario(
            nombre="Prueba ICFES",
            tipo_complementario_id=tipo_prueba.id,
            anio=2026,
            valor=45000,
            estado_complemento="Activo",
        )
        c2 = Complementario(
            nombre="Simulacro",
            tipo_complementario_id=tipo_prueba.id,
            anio=2026,
            valor=25000,
            estado_complemento="Activo",
        )
        session.add_all([c1, c2])

        session.commit()
        print(
            "[OK] Base de datos formateada: SOLO Grados Décimo y Once, Periodos 2026-01/02 y 2 Pruebas (ICFES/Simulacro) con nombres reales."
        )


if __name__ == "__main__":
    seed_grados()
