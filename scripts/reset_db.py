"""
Script de reset COMPLETO de la base de datos.
Elimina todos los datos y recrea datos de prueba para todos los módulos.
"""

from datetime import datetime

from sqlmodel import Session, delete, text

from app.core.db import engine
from app.modules.enrollment.infrastructure.models import (
    Acudiente,
    Complementario,
    DetalleMatricula,
    Docente,
    Estudiante,
    Grado,
    Matricula,
    Pago,
    PagoDetalle,
    ParametrizarMatricula,
    Periodo,
)
from app.modules.tests.infrastructure.models import DetallePrueba


def truncate_all(session: Session):
    """Borra todos los datos en orden seguro."""
    print("[*] Limpiando tablas...")
    session.execute(text("SET session_replication_role = replica"))

    tables_models = [
        DetallePrueba,
        PagoDetalle,
        Pago,
        DetalleMatricula,
        Matricula,
        ParametrizarMatricula,
        Estudiante,
        Acudiente,
        Docente,
        Complementario,
        Grado,
        Periodo,
    ]
    for model in tables_models:
        try:
            session.exec(delete(model))
            print(f"  OK: {model.__name__} limpiada")
        except Exception as e:
            print(f"  ERROR en {model.__name__}: {e}")
            session.rollback()

    session.execute(text("SET session_replication_role = DEFAULT"))
    session.commit()
    print()


def seed_all(session: Session):
    print("[*] Sembrando datos...\n")

    # -- 1. DOCENTES (primero porque grados dependen de ellos)
    print("[1] Docentes...")
    docentes = [
        Docente(
            nombre="Prof. Ramirez",
            documento="555001",
            estado=True,
            asignatura="Matematicas",
        ),
        Docente(
            nombre="Prof. Serrano",
            documento="555002",
            estado=True,
            asignatura="Espanol",
        ),
        Docente(
            nombre="Prof. Mendoza",
            documento="555003",
            estado=True,
            asignatura="Ciencias",
        ),
        Docente(
            nombre="Prof. Gutierrez",
            documento="555004",
            estado=True,
            asignatura="Historia",
        ),
        Docente(
            nombre="Prof. Vargas", documento="555005", estado=True, asignatura="Ingles"
        ),
        Docente(
            nombre="Prof. Castro", documento="555006", estado=True, asignatura="Fisica"
        ),
    ]
    session.add_all(docentes)
    session.commit()
    for d in docentes:
        session.refresh(d)
    print(f"   OK: {len(docentes)} docentes\n")

    # -- 2. GRADOS (con docente titular asignado)
    print("[2] Grados...")
    grados_data = [
        ("Sexto", docentes[0].id),
        ("Septimo", docentes[1].id),
        ("Octavo", docentes[2].id),
        ("Noveno", docentes[3].id),
        ("Decimo", docentes[4].id),
        ("Once", docentes[5].id),
    ]
    grados = [Grado(nombre=n, docente_titular_id=did) for n, did in grados_data]
    # -- 1. GRADOS
    print("[1] Grados...")
    grados_data = ["Sexto", "Septimo", "Octavo", "Noveno", "Decimo", "Once"]
    grados = [Grado(nombre=n) for n in grados_data]
    session.add_all(grados)
    session.commit()
    for g in grados:
        session.refresh(g)
    grado_decimo = grados[4]
    grado_once = grados[5]
    print(f"   OK: {len(grados)} grados\n")

    # -- 3. ACUDIENTES
    print("[3] Acudientes...")
    # -- 2. ACUDIENTES
    print("[2] Acudientes...")
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
        Acudiente(
            nombre="Luis Torres",
            parentesco="Padre",
            telefono="3001111003",
            correo="luis@mail.com",
        ),
        Acudiente(
            nombre="Ana Ruiz",
            parentesco="Madre",
            telefono="3001111004",
            correo="ana@mail.com",
        ),
        Acudiente(
            nombre="Jose Martinez",
            parentesco="Padre",
            telefono="3001111005",
            correo="jose@mail.com",
        ),
    ]
    session.add_all(acudientes)
    session.commit()
    for a in acudientes:
        session.refresh(a)
    print(f"   OK: {len(acudientes)} acudientes\n")

    # -- 3. DOCENTES
    print("[3] Docentes...")
    docentes = [
        Docente(
            nombre="Prof. Ramirez",
            documento="555001",
            estado=True,
            asignatura="Matematicas",
        ),
        Docente(
            nombre="Prof. Serrano",
            documento="555002",
            estado=True,
            asignatura="Espanol",
        ),
        Docente(
            nombre="Prof. Mendoza",
            documento="555003",
            estado=True,
            asignatura="Ciencias",
        ),
    ]
    session.add_all(docentes)
    session.commit()
    print(f"   OK: {len(docentes)} docentes\n")

    # -- 4. PERIODOS
    print("[4] Periodos...")
    periodos = [
        Periodo(
            periodo_electivo=datetime(2026, 1, 1),
            estado=True,
            fecha=datetime(2026, 1, 15),
        ),
        Periodo(
            periodo_electivo=datetime(2026, 6, 1),
            estado=True,
            fecha=datetime(2026, 6, 15),
        ),
    ]
    session.add_all(periodos)
    session.commit()
    for p in periodos:
        session.refresh(p)
    print(f"   OK: {len(periodos)} periodos\n")

    # -- 5. COMPLEMENTARIOS
    print("[5] Complementarios...")
    comps = [
        Complementario(
            tipo_complementario="Seguro Estudiantil",
            anio=2026,
            valor=30000,
            estado_complemento="Activo",
            uso_matricula=True,
        ),
        Complementario(
            tipo_complementario="Transporte",
            anio=2026,
            valor=150000,
            estado_complemento="Activo",
            uso_matricula=True,
        ),
        Complementario(
            tipo_complementario="Simulacro ICFES 2026",
            anio=2026,
            valor=50000,
            estado_complemento="Activo",
            uso_matricula=False,
        ),
        Complementario(
            tipo_complementario="Prueba Saber 11",
            anio=2026,
            valor=45000,
            estado_complemento="Activo",
            uso_matricula=False,
        ),
        Complementario(
            tipo_complementario="Evaluacion Diagnostica",
            anio=2026,
            valor=20000,
            estado_complemento="Activo",
            uso_matricula=False,
        ),
    ]
    session.add_all(comps)
    session.commit()
    for c in comps:
        session.refresh(c)
    print(f"   OK: {len(comps)} complementarios\n")
    pruebas = [c for c in comps if not c.uso_matricula]
    print(
        f"   OK: {len(comps)} complementarios ({len(pruebas)} para pruebas, {len(comps) - len(pruebas)} para matricula)\n"
    )

    # -- 6. PARAMETRIZAR MATRICULA
    print("[6] Parametrizacion de matriculas...")
    valores = [350000, 360000, 370000, 380000, 400000, 420000]
    params = [
        ParametrizarMatricula(
            grado_id=int(grados[i].id),  # type: ignore
            anio=2026,
            valor=valores[i],
        )
        for i in range(len(grados))
    ]
    session.add_all(params)
    session.commit()
    print(f"   OK: {len(params)} parametrizaciones\n")

    # -- 7. ESTUDIANTES
    print("[7] Estudiantes...")
    nombres_decimo = [
        ("Juan Perez", "1001001001"),
        ("Maria Gomez", "1001001002"),
        ("Carlos Lopez", "1001001003"),
        ("Ana Martinez", "1001001004"),
        ("Luis Rodriguez", "1001001005"),
        ("Sofia Hernandez", "1001001006"),
        ("Andres Garcia", "1001001007"),
        ("Valentina Diaz", "1001001008"),
        ("Santiago Moreno", "1001001009"),
        ("Camila Torres", "1001001010"),
    ]
    nombres_once = [
        ("Pedro Vargas", "1001002001"),
        ("Laura Castro", "1001002002"),
        ("David Jimenez", "1001002003"),
        ("Isabella Romero", "1001002004"),
        ("Felipe Suarez", "1001002005"),
    ]

    estudiantes = []
    for i, (nombre, doc) in enumerate(nombres_decimo):
        acudiente_actual = acudientes[i % len(acudientes)]
        estudiantes.append(
            Estudiante(
                grado_id=int(grado_decimo.id) if grado_decimo.id is not None else 0,
                acudiente_id=int(acudiente_actual.id)
                if acudiente_actual.id is not None
                else 0,
                nombre=nombre,
                documento=doc,
                activo=True,
                fecha_activo=datetime.now(),
            )
        )
    for i, (nombre, doc) in enumerate(nombres_once):
        acudiente_actual = acudientes[i % len(acudientes)]
        estudiantes.append(
            Estudiante(
                grado_id=int(grado_once.id) if grado_once.id is not None else 0,
                acudiente_id=int(acudiente_actual.id)
                if acudiente_actual.id is not None
                else 0,
                nombre=nombre,
                documento=doc,
                activo=True,
                fecha_activo=datetime.now(),
            )
        )

    session.add_all(estudiantes)
    session.commit()

    print(f"  Docentes:            {len(docentes)}")
    print(f"  Grados:              {len(grados)}")
    print(f"  Acudientes:          {len(acudientes)}")
    print(f"  Acudientes:          {len(acudientes)}")
    print(f"  Docentes:            {len(docentes)}")
    print(f"  Períodos:            {len(periodos)}")
    print(f"  Complementarios:     {len(comps)}")
    print(f"  Parametr. matríc.:   {len(params)}")
    print(f"  Estudiantes:         {len(estudiantes)}")
    print()
    print("📋 El módulo de PRUEBAS INTERNAS está vacío — usa la UI para asignar.")
    print("📋 El módulo de MATRÍCULA está vacío — usa la UI para registrar.")


if __name__ == "__main__":
    with Session(engine) as session:
        truncate_all(session)
    with Session(engine) as session:
        seed_all(session)
