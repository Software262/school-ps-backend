"""
Script de seed local para pruebas del módulo Pensión.
Lee REGISTROS JSON.txt y puebla: grado, estudiante, parametrizarpension, pension.

USO:
    uv run python seed_local.py
"""

import json
from datetime import datetime

# Importar todos los modelos para que SQLModel los registre
import app.modules.auth.infrastructure.models  # noqa: F401
import app.modules.cafeteria.infrastructure.models  # noqa: F401
import app.modules.classroom.infrastructure.models  # noqa: F401
import app.modules.enrollment.infrastructure.models  # noqa: F401
import app.modules.inventory.infrastructure.models  # noqa: F401
import app.modules.musical_band.infrastructure.models  # noqa: F401
import app.modules.peace_safe.infrastructure.models  # noqa: F401
import app.modules.principal.infrastructure.models  # noqa: F401
import app.modules.tests.infrastructure.models  # noqa: F401
import app.modules.training_schools.infrastructure.models  # noqa: F401
import app.modules.tuition.infrastructure.models  # noqa: F401

from sqlmodel import Session, create_engine
from app.modules.tuition.infrastructure.models import (
    ParametrizarPension,
    Pension,
)

# Importamos los modelos compartidos (grado y estudiante)

# Definimos modelos mínimos para grado y estudiante (ya existen en el proyecto)
# Los buscamos en los módulos del equipo
from app.modules.enrollment.infrastructure.models import Grado, Estudiante, Acudiente  # type: ignore

DATABASE_URL = (
    "mssql+pyodbc://paz:1234@JUANDAVIDPC\\CN_LOCAL/pazysalvo"
    "?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
)
JSON_PATH = r"C:\Users\Rraid\Documents\Juan David\Temporal\REGISTROS JSON.txt"
VALOR_ANUAL = 1_200_000

engine = create_engine(DATABASE_URL, echo=False)


def seed():
    print("Leyendo JSON...")
    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)
    registros = data["datos"]
    print(f"  -> {len(registros)} estudiantes encontrados\n")

    with Session(engine) as session:
        # 1. Grados únicos
        grados_map: dict[str, int] = {}
        print("Insertando grados...")
        for r in registros:
            nombre = r["grado_texto"]
            if nombre not in grados_map:
                grado = Grado(nombre=nombre)
                session.add(grado)
                session.commit()
                session.refresh(grado)
                grados_map[nombre] = grado.id  # type: ignore
                print(f"  -> '{nombre}' id={grado.id}")

        # 2. Parametrización por grado
        para_map: dict[int, int] = {}
        print("\nInsertando parametrizaciones...")
        for grado_nombre, grado_id in grados_map.items():
            para = ParametrizarPension(grado_id=grado_id, anio=2026, valor=VALOR_ANUAL)
            session.add(para)
            session.commit()
            session.refresh(para)
            para_map[grado_id] = para.id  # type: ignore
            print(f"  -> grado_id={grado_id} para_id={para.id}")

        # 3. Estudiantes y sus cuentas de pensión
        print(f"\nInsertando {len(registros)} estudiantes y cuentas de pensión...")
        
        # Insertar un acudiente por defecto para todos
        acudiente = Acudiente(nombre="Acudiente Default", parentesco="Tutor", telefono="0000000", correo="correo@colegio.edu.co")
        session.add(acudiente)
        session.commit()
        session.refresh(acudiente)
        acudiente_id = acudiente.id

        for r in registros:
            grado_id = grados_map[r["grado_texto"]]
            para_id = para_map[grado_id]

            est = Estudiante(
                nombre=r["nombre"], 
                documento=r["documento"],
                grado_id=grado_id,
                acudiente_id=acudiente_id,
                activo=True
            )
            session.add(est)
            session.commit()
            session.refresh(est)

            pension = Pension(
                para_pension_id=para_id,
                estudiante_id=est.id,  # type: ignore
                grado_id=grado_id,
                valor_total=VALOR_ANUAL,
                fecha_registro=datetime.now(),
                estado_pension=False,
            )
            session.add(pension)
            session.commit()

        print("\n✅ Seed completado!")
        print(f"   {len(registros)} estudiantes insertados")
        print(f"   Cuota mensual: ${VALOR_ANUAL // 10:,}")
        print(f"   Usa cualquier estudiante_id del 1 al {len(registros)} en el Swagger")


if __name__ == "__main__":
    seed()
