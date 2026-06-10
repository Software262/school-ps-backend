"""
Script para limpiar TODA la base de datos.
Crea las tablas si no existen y elimina todos los datos sin generar nuevos registros.
"""

import sys
import os
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
    session.commit()


def main():
    # Asegurarnos de que las tablas existan
    print("[*] Asegurando estructura de la base de datos...")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        truncate_all(session)
        print("[*] ¡Base de datos vaciada con éxito!")


if __name__ == "__main__":
    main()
