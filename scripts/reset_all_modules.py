"""
Script de reset COMPLETO de la base de datos.
Crea las tablas si no existen, elimina todos los datos y recrea datos de prueba.
"""

import sys
import os
from datetime import datetime
from sqlmodel import Session, SQLModel, delete, text

# Asegurarse de que el directorio padre esté en el path para importar la app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.db import engine
from app.modules.tests.infrastructure.models import DetallePrueba
from app.modules.enrollment.infrastructure.models import (
    Grado,
    Acudiente,
    Estudiante,
    Docente,
    Periodo,
    Complementario,
    ParametrizarMatricula,
    Matricula,
    DetalleMatricula,
    Pago,
    PagoDetalle,
)


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


def seed_data(session: Session):
    """Genera datos de prueba base para los módulos."""
    print("[*] Generando datos de prueba...")

    # === GRADOS ===
    grado_10 = Grado(nombre="Grado 10")
    grado_11 = Grado(nombre="Grado 11")
    session.add_all([grado_10, grado_11])
    session.commit()
    session.refresh(grado_10)
    session.refresh(grado_11)

    # === ACUDIENTES ===
    acudiente = Acudiente(
        nombre="Acudiente Prueba",
        parentesco="Padre",
        telefono="3001234567",
        correo="acudiente@correo.com",
    )
    session.add(acudiente)
    session.commit()
    session.refresh(acudiente)

    # === ESTUDIANTES GRADO 10 (5 estudiantes) ===
    nombres_10 = [
        ("Pedro Pascal", "1001002001"),
        ("Laura Gomez", "1001002002"),
        ("Andres Cepeda", "1001002003"),
        ("Diana Trujillo", "1001002004"),
        ("Miguel Varoni", "1001002005"),
    ]
    for nombre, doc in nombres_10:
        session.add(
            Estudiante(
                grado_id=int(grado_10.id) if grado_10.id is not None else 0,
                acudiente_id=int(acudiente.id) if acudiente.id is not None else 0,
                nombre=nombre,
                documento=doc,
                activo=True,
            )
        )

    # === ESTUDIANTES GRADO 11 (10 estudiantes) ===
    nombres_11 = [
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
    for nombre, doc in nombres_11:
        session.add(
            Estudiante(
                grado_id=int(grado_11.id) if grado_11.id is not None else 0,
                acudiente_id=int(acudiente.id) if acudiente.id is not None else 0,
                nombre=nombre,
                documento=doc,
                activo=True,
            )
        )

    # === PERIODOS ===
    periodo_1 = Periodo(
        periodo_electivo=datetime(2026, 1, 1),
        estado=True,
        fecha=datetime.now(),
    )
    periodo_2 = Periodo(
        periodo_electivo=datetime(2026, 2, 1),
        estado=True,
        fecha=datetime.now(),
    )
    session.add_all([periodo_1, periodo_2])

    # === PRUEBAS (Complementarios) ===
    # Apegándonos a los nombres de pruebas ya existentes
    pruebas = [
        Complementario(
            tipo_complementario="Simulacro ICFES 2024",
            anio=2026,
            valor=50000,
            estado_complemento="Activo",
            uso_matricula=False,
        ),
        Complementario(
            tipo_complementario="Prueba Saber 10",
            anio=2026,
            valor=40000,
            estado_complemento="Activo",
            uso_matricula=False,
        ),
    ]
    session.add_all(pruebas)
    session.commit()

    print("[*] ¡Datos generados con éxito!")


def main():
    # Asegurarnos de que las tablas existan
    print("[*] Asegurando estructura de la base de datos...")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        truncate_all(session)
        seed_data(session)


if __name__ == "__main__":
    main()
