import sys
from pathlib import Path
from datetime import datetime

# Ajustar la ruta para que Python reconozca el módulo app
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select
from app.core.db import engine

# Importar modelos necesarios (incluyendo Docente)
from app.modules.enrollment.infrastructure.models import (
    Grado,
    Acudiente,
    Estudiante,
    Docente,
)

def insert_mock_students(session: Session):
    print("Verificando si ya existen estudiantes...")
    if session.exec(select(Estudiante)).first():
        print("ℹ️ Ya existen estudiantes en la base de datos. Saltando inserción.")
        return

    # 1. Obtener los grados creados previamente por el seed básico
    grados = session.exec(select(Grado)).all()
    if not grados:
        print("❌ Faltan los grados en la BD. Por favor, corre primero el script 'seed_basico.py'.")
        return

    grado_map = {g.nombre: g for g in grados}
    
    print("📝 Creando Acudientes...")
    acudiente1 = Acudiente(nombre="María García", parentesco="Madre", telefono="3001234567", correo="maria@email.com")
    acudiente2 = Acudiente(nombre="Carlos López", parentesco="Padre", telefono="3009876543", correo="carlos@email.com")
    
    session.add_all([acudiente1, acudiente2])
    session.flush()

    print("📝 Creando Docentes...")
    docente1 = Docente(nombre="Profe. Alberto Ruiz", documento="88001122", asignatura="Matemáticas", estado=True)
    docente2 = Docente(nombre="Profa. Carmen Gómez", documento="88003344", asignatura="Lengua Castellana", estado=True)
    
    session.add_all([docente1, docente2])
    session.flush()

    print("📝 Creando Estudiantes con sus Docentes titulares asociados...")
    est1 = Estudiante(
        grado_id=grado_map["Sexto"].id, 
        acudiente_id=acudiente1.id, 
        docente_id=docente1.id,  # Asignado a Profe. Alberto
        nombre="Juan García Pérez", 
        documento="1005123456", 
        activo=True, 
        fecha_activo=datetime(2026, 1, 15)
    )
    est2 = Estudiante(
        grado_id=grado_map["Décimo"].id, 
        acudiente_id=acudiente2.id, 
        docente_id=docente2.id,  # Asignado a Profa. Carmen
        nombre="Ana López Martínez", 
        documento="1005654321", 
        activo=True, 
        fecha_activo=datetime(2026, 1, 15)
    )
    est3 = Estudiante(
        grado_id=grado_map["Segundo"].id, 
        acudiente_id=acudiente1.id, 
        docente_id=docente1.id,  # Asignado a Profe. Alberto
        nombre="Pedro García Pérez", 
        documento="1005111222", 
        activo=True, 
        fecha_activo=datetime(2026, 2, 1)
    )
    
    session.add_all([est1, est2, est3])

def main():
    print("🚀 Iniciando inserción de estudiantes y docentes...")
    with Session(engine) as session:
        try:
            insert_mock_students(session)
            session.commit()
            print("🎉 Estudiantes y docentes vinculados exitosamente.")
        except Exception as e:
            session.rollback()
            print(f"❌ Ocurrió un error: {e}")

if __name__ == "__main__":
    main()