import sys
from pathlib import Path
from datetime import datetime

# Ajustar la ruta para que Python reconozca el módulo app
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select
from app.core.db import engine

# ----------------- IMPORTACIONES -----------------
from app.modules.auth.infrastructure.models import Usuario
from app.modules.enrollment.infrastructure.models import (
    Grado,
    Periodo,
    TipoComplementario,
    ParametrizarMatricula,
    Complementario,
)
from app.modules.tuition.infrastructure.models import ParametrizarPension
from app.modules.inventory.infrastructure.models import TipoInventario, EstadoInventario
# ------------------------------------------------------------

def insert_admin(session: Session):
    usuario = session.exec(select(Usuario).where(Usuario.username == "admin")).first()
    
    if not usuario:
        session.add(
            Usuario(
                rol="ADMIN",
                username="admin",
                contrasenia="admin",
                estado=True
            )
        )
        print("✅ Usuario 'admin' (pass: 'admin' en texto plano) insertado.")
    else:
        usuario.contrasenia = "admin"
        session.add(usuario)
        print("ℹ️ Usuario 'admin' ya existía. Contraseña actualizada a texto plano.")

def insert_catalogs(session: Session):
    # 1. Grados Académicos
    grados_nombres = [
        "Preescolar", "Primero", "Segundo", "Tercero", "Cuarto", 
        "Quinto", "Sexto", "Séptimo", "Octavo", "Noveno", "Décimo", "Once"
    ]
    grados_creados = []
    
    if not session.exec(select(Grado)).first():
        for nombre in grados_nombres:
            grado = Grado(nombre=nombre)
            session.add(grado)
            grados_creados.append(grado)
        session.flush()
        print(f"✅ {len(grados_nombres)} Grados académicos insertados.")
    else:
        grados_creados = session.exec(select(Grado)).all()
        print("ℹ️ Grados académicos ya existían.")

    # 2. Periodo Académico
    periodo = session.exec(select(Periodo)).first()
    if not periodo:
        periodo = Periodo(
            periodo_electivo=datetime(2026, 1, 1),
            estado=True,
            fecha=datetime.now()
        )
        session.add(periodo)
        session.flush()
        print("✅ Periodo académico inicial insertado.")

    # 3. Tipos de Inventario (Asegurando explícitamente banda, deporte y ajedrez)
    tipos_inv = [
        "banda", "deporte", "ajedrez", 
        "Equipos", "Mobiliario", "Material Didáctico"
    ]
    
    existing_tipos = {t.nombre.lower() for t in session.exec(select(TipoInventario)).all()}
    nuevos_tipos = [TipoInventario(nombre=t) for t in tipos_inv if t.lower() not in existing_tipos]
    if nuevos_tipos:
        session.add_all(nuevos_tipos)
        session.flush()
        print(f"✅ Tipos de Inventario insertados/actualizados correctamente.")

    # 4. Estados de Inventario (disponible, prestado, mantenimiento)
    estados_inv = ["disponible", "prestado", "mantenimiento"]
    existing_estados = {e.nombre.lower() for e in session.exec(select(EstadoInventario)).all()}
    nuevos_estados = [EstadoInventario(nombre=e) for e in estados_inv if e.lower() not in existing_estados]
    if nuevos_estados:
        session.add_all(nuevos_estados)
        session.flush()
        print(f"✅ Estados de Inventario insertados/actualizados.")

    # 5. Tipos Complementarios Base (Catálogos Padres)
    tipo_pupitre = session.exec(select(TipoComplementario).where(TipoComplementario.nombre == "Pupitre")).first()
    if not tipo_pupitre:
        tipo_matricula = TipoComplementario(nombre="Matricula", estado=True)
        tipo_escuelas = TipoComplementario(nombre="Escuelas de Formacion", estado=True)
        tipo_pupitre = TipoComplementario(nombre="Pupitre", estado=True)
        session.add_all([tipo_matricula, tipo_escuelas, tipo_pupitre])
        session.flush()
        
        # Sub-tipos de Escuelas de Formación
        session.add_all([
            TipoComplementario(nombre="Baloncesto", estado=True, sub_tipo_complementario=tipo_escuelas.id),
            TipoComplementario(nombre="Ajedrez", estado=True, sub_tipo_complementario=tipo_escuelas.id),
            TipoComplementario(nombre="Natacion", estado=True, sub_tipo_complementario=tipo_escuelas.id)
        ])
        print("✅ Tipos Complementarios (Matrícula, Escuelas y Pupitre) insertados.")

    # 5.1 Complementario por defecto para Pupitres (Soluciona el 404 de classroom/pupitre/complementario)
    if not session.exec(select(Complementario).where(Complementario.nombre == "Garantía Pupitre")).first():
        comp_pupitre = Complementario(
            nombre="Garantía Pupitre",
            tipo_complementario_id=tipo_pupitre.id,
            anio=2026,
            valor=0,
            estado_complemento="Activo"
        )
        session.add(comp_pupitre)
        print("✅ Complementario base de Pupitre insertado.")

    # 6. Parámetros Base (Matrícula y Pensión)
    if grados_creados and not session.exec(select(ParametrizarMatricula)).first():
        parametros_matricula = []
        parametros_pension = []
        
        for idx, g in enumerate(grados_creados):
            val_matricula = 600000 + idx * 50000
            val_pension = 300000 + idx * 25000 
            
            if idx == 5: # Sexto
                val_matricula, val_pension = 850000, 450000
            elif idx == 10: # Décimo
                val_matricula, val_pension = 950000, 520000
            elif idx == 2: # Segundo
                val_matricula, val_pension = 750000, 350000

            parametros_matricula.append(
                ParametrizarMatricula(grado_id=g.id, anio=2026, valor=val_matricula)
            )
            parametros_pension.append(
                ParametrizarPension(grado_id=g.id, anio=2026, valor=val_pension)
            )
            
        session.add_all(parametros_matricula)
        session.add_all(parametros_pension)
        print("✅ Costos base de Matrícula y Pensión parametrizados para 2026.")

def main():
    print("🚀 Iniciando Inserción de Datos Básicos del Sistema...")
    with Session(engine) as session:
        try:
            insert_admin(session)
            insert_catalogs(session)
            session.commit()
            print("🎉 Estructura paramétrica cargada exitosamente.")
        except Exception as e:
            session.rollback()
            print(f"❌ Ocurrió un error: {e}")

if __name__ == "__main__":
    main()