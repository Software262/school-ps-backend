import sys
from pathlib import Path

# Ajustar la ruta para que Python reconozca el módulo app
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, text
from app.core.db import engine

def wipe_entire_database():
    print("🧹 Iniciando borrado total de la base de datos...")
    
    with Session(engine) as session:
        try:
            # 1. Obtener todas las tablas del esquema 'public' de PostgreSQL
            result = session.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            todas_las_tablas = [row[0] for row in result.fetchall()]
            
            # 2. Excluir la tabla de migraciones de Alembic para no dañar la configuración del proyecto
            tablas_a_limpiar = [tabla for tabla in todas_las_tablas if tabla != 'alembic_version']
            
            if not tablas_a_limpiar:
                print("ℹ️ No hay tablas para vaciar.")
                return
                
            # 3. Formatear la lista de tablas para el comando SQL
            tablas_str = ", ".join(tablas_a_limpiar)
            print(f"🗑️ Vaciando {len(tablas_a_limpiar)} tablas:\n{tablas_str}")
            
            # 4. Ejecutar TRUNCATE con CASCADE (ignora dependencias) y RESTART IDENTITY (reinicia los IDs a 1)
            comando_sql = f"TRUNCATE TABLE {tablas_str} RESTART IDENTITY CASCADE;"
            session.execute(text(comando_sql))
            session.commit()
            
            print("✅ ABSOLUTAMENTE TODAS las tablas han sido vaciadas con éxito.")
            print("⚠️ Recuerda que ahora debes correr tu seed básico de nuevo para poder iniciar sesión.")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Ocurrió un error al limpiar la base de datos: {e}")

if __name__ == "__main__":
    confirmacion = input("⚠️ ADVERTENCIA: Esto dejará TODA la base de datos en blanco (cero usuarios, cero configuraciones). ¿Continuar? (escribe 'si'): ")
    
    if confirmacion.lower() == 'si':
        wipe_entire_database()
    else:
        print("🛑 Borrado cancelado.")