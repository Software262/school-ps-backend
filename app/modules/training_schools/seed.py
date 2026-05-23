"""
Seed script para cargar programas complementarios (Escuelas de Formación).

Uso:
    Desde la carpeta school-ps-backend ejecutar:
    uv run python -m app.modules.training_schools.seed
"""

from app.core.db import engine
from sqlmodel import Session, select
from app.modules.enrollment.infrastructure.models import Complementario


PROGRAMAS = [
    {
        "tipo_complementario": "Fútbol",
        "anio": 2026,
        "valor": 50000,
        "estado_complemento": "activo",
        "uso_matricula": False,
    },
    {
        "tipo_complementario": "Natación",
        "anio": 2026,
        "valor": 60000,
        "estado_complemento": "activo",
        "uso_matricula": False,
    },
    {
        "tipo_complementario": "Baloncesto",
        "anio": 2026,
        "valor": 45000,
        "estado_complemento": "activo",
        "uso_matricula": False,
    },
    {
        "tipo_complementario": "Voleibol",
        "anio": 2026,
        "valor": 40000,
        "estado_complemento": "activo",
        "uso_matricula": False,
    },
]


def seed_programas():
    with Session(engine) as session:
        creados = 0
        omitidos = 0

        for programa in PROGRAMAS:
            # Verificar si ya existe para no duplicar
            existing = session.exec(
                select(Complementario).where(
                    Complementario.tipo_complementario == programa["tipo_complementario"],
                    Complementario.anio == programa["anio"],
                )
            ).first()

            if existing:
                print(f"  [SKIP] Ya existe: {programa['tipo_complementario']} ({programa['anio']})")
                omitidos += 1
                continue

            nuevo = Complementario(**programa)
            session.add(nuevo)
            print(f"  [OK] Creado: {programa['tipo_complementario']} ({programa['anio']}) - Valor: ${programa['valor']:,}")
            creados += 1

        session.commit()
        print(f"\nResumen: {creados} programas creados, {omitidos} omitidos (ya existian).")


if __name__ == "__main__":
    print("Sembrando programas de Escuelas de Formacion...\n")
    seed_programas()
    print("\nSeed completado!")
