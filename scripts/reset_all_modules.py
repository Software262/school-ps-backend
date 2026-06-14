"""
Script para limpiar TODA la base de datos.
Elimina todos los datos de todas las tablas de forma dinámica (TRUNCATE CASCADE).
"""

import os
import sys

from sqlmodel import Session, text

# Asegurarse de que el directorio padre esté en el path para importar la app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.db import engine


def truncate_all(session: Session):
    """Borra todos los datos de todas las tablas dinámicamente usando Postgres."""
    print("[*] Buscando y limpiando TODAS las tablas en la base de datos...")

    # Desactivar temporalmente los triggers/constraints
    session.execute(text("SET session_replication_role = replica;"))

    # Consultar todas las tablas del esquema 'public' omitiendo la de migraciones de alembic
    result = session.execute(
        text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename != 'alembic_version';"
        )
    )
    tables = [row[0] for row in result.fetchall()]

    if tables:
        tables_joined = ", ".join(f'"{table}"' for table in tables)
        try:
            # Ejecutar el truncate masivo y en cascada
            session.execute(text(f"TRUNCATE TABLE {tables_joined} CASCADE;"))
            for table in tables:
                print(f"  OK: Tabla '{table}' limpiada")
        except Exception as e:
            print(f"  ERROR al truncar las tablas: {e}")
            session.rollback()
    else:
        print("  No se encontraron tablas para limpiar.")

    # Restaurar los constraints
    session.execute(text("SET session_replication_role = DEFAULT;"))
    session.commit()


def main():
    with Session(engine) as session:
        truncate_all(session)
        print("[*] ¡Base de datos vaciada con éxito")


if __name__ == "__main__":
    main()
