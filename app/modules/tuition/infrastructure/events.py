from datetime import datetime
from sqlalchemy import event, insert, select

# Modelos involucrados
from app.modules.enrollment.infrastructure.models import Estudiante
from app.modules.tuition.infrastructure.models import ParametrizarPension, Pension, DetallePension
from app.modules.pupitre.infrastructure.models import DetallePupitre
from app.modules.matricula.infrastructure.models import Complementario

@event.listens_for(Estudiante, 'after_insert')
def auto_crear_obligaciones_estudiante(mapper, connection, target):
    """
    Se ejecuta automáticamente en la BD justo después de insertar CUALQUIER Estudiante
    (ya sea por script, seed, API o inserción directa).
    """
    anio_actual = datetime.now().year
    
    # ==========================================
    # 1. CREAR AUTOMÁTICAMENTE LA PENSIÓN
    # ==========================================
    param_stmt = select(ParametrizarPension).where(
        ParametrizarPension.grado_id == target.grado_id,
        ParametrizarPension.anio == anio_actual
    )
    param = connection.execute(param_stmt).first()
    
    if param:
        pension_stmt = insert(Pension).values(
            para_pension_id=param.id,
            estudiante_id=target.id,
            grado_id=target.grado_id,
            valor_total=param.valor * 10,
            fecha_registro=datetime.now(),
            estado_pension=False
        ).returning(Pension.id)
        
        pension_id = connection.execute(pension_stmt).scalar()
        
        detalles_data = [
            {
                "pension_id": pension_id,
                "estudiante_id": target.id,
                "mes": mes,
                "cuota": param.valor,
                "valor_total": param.valor,
                "valor_pagado": 0,
                "fecha_pago": datetime.now(),
                "faltante": True
            }
            for mes in range(1, 11)
        ]
        connection.execute(insert(DetallePension), detalles_data)

    # ==========================================
    # 2. CREAR AUTOMÁTICAMENTE EL PUPITRE EN PENDIENTE
    # ==========================================
    # Buscamos un complemento de tipo 'Pupitre' o creamos el registro por defecto
    comp_stmt = select(Complementario.id).join(
        # Ajusta la relación según tu modelo si el tipo se llama distinto
        # Aquí buscamos cualquier complementario asociado al concepto de pupitre
    ).where(Complementario.nombre.ilike("%pupitre%")).limit(1)
    
    # Si tienes un ID fijo o prefieres buscarlo dinámicamente:
    comp_id = connection.execute(comp_stmt).scalar()
    
    if comp_id:
        # Insertamos el detalle del pupitre explícitamente en estado "pendiente"
        connection.execute(
            insert(DetallePupitre),
            {
                "estudiante_id": target.id,
                "complementario_id": comp_id,
                "estado": "pendiente",
                "observacion": "Pendiente de revisión inicial de pupitre"
            }
        )