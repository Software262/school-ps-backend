"""
Script de seed para cargar datos de prueba en la BD.
Ejecutar con: python -m scripts.seed
"""

from datetime import datetime

from sqlmodel import Session, SQLModel, select

from app.core.db import engine
from app.modules.enrollment.infrastructure.models import (
    Acudiente,
    Complementario,
    DetalleMatricula,
    Estudiante,
    Grado,
    Matricula,
    Pago,
    PagoDetalle,
    ParametrizarMatricula,
    Periodo,
    TipoComplementario,
)
from app.modules.tuition.infrastructure.models import ParametrizarPension


def seed() -> None:
    """Carga datos de prueba para el módulo de matrícula."""
    # Crear todas las tablas
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Verificar si ya hay datos
        existing = session.exec(select(Grado)).first()
        if existing:
            print("[SKIP] Ya existen datos en la BD. Seed omitido.")
            return

        # === GRADOS ===
        grados = [
            Grado(nombre="Preescolar"),
            Grado(nombre="Primero"),
            Grado(nombre="Segundo"),
            Grado(nombre="Tercero"),
            Grado(nombre="Cuarto"),
            Grado(nombre="Quinto"),
            Grado(nombre="Sexto"),
            Grado(nombre="Séptimo"),
            Grado(nombre="Octavo"),
            Grado(nombre="Noveno"),
            Grado(nombre="Décimo"),
            Grado(nombre="Once"),
        ]
        session.add_all(grados)
        session.flush()

        for g in grados:
            assert g.id is not None

        # === ACUDIENTES ===
        acudiente1 = Acudiente(
            nombre="María García",
            parentesco="Madre",
            telefono="3001234567",
            correo="maria.garcia@email.com",
        )
        acudiente2 = Acudiente(
            nombre="Carlos López",
            parentesco="Padre",
            telefono="3009876543",
            correo="carlos.lopez@email.com",
        )
        session.add_all([acudiente1, acudiente2])
        session.flush()

        assert acudiente1.id is not None
        assert acudiente2.id is not None

        # === ESTUDIANTES ===
        estudiante1 = Estudiante(
            grado_id=grados[5].id,  # type: ignore[arg-type]
            acudiente_id=acudiente1.id,
            nombre="Juan García Pérez",
            documento="1005123456",
            activo=True,
            fecha_activo=datetime(2026, 1, 15),
        )
        estudiante2 = Estudiante(
            grado_id=grados[10].id,  # type: ignore[arg-type]
            acudiente_id=acudiente2.id,
            nombre="Ana López Martínez",
            documento="1005654321",
            activo=True,
            fecha_activo=datetime(2026, 1, 15),
        )
        # Estudiante sin matrícula (para probar registro automático)
        estudiante3 = Estudiante(
            grado_id=grados[2].id,  # type: ignore[arg-type]
            acudiente_id=acudiente1.id,
            nombre="Pedro García Pérez",
            documento="1005111222",
            activo=True,
            fecha_activo=datetime(2026, 2, 1),
        )
        session.add_all([estudiante1, estudiante2, estudiante3])
        session.flush()

        assert estudiante1.id is not None
        assert estudiante2.id is not None
        assert estudiante3.id is not None

        # === PERIODOS ===
        periodo = Periodo(
            periodo_electivo=datetime(2026, 1, 1),
            estado=True,
            fecha=datetime(2026, 1, 15),
        )
        session.add(periodo)
        session.flush()

        assert periodo.id is not None

        # === PARAMETRIZAR MATRÍCULA (costo base por grado y año) ===
        params_matricula = []
        param_map = {}
        for g in grados:
            idx = grados.index(g)
            val = 600000 + idx * 50000

            # Ajustamos específicos para mantener los valores originales para Quinto (index 5), Décimo (index 10) y Segundo (index 2)
            if idx == 5:
                val = 850000
            elif idx == 10:
                val = 950000
            elif idx == 2:
                val = 750000

            pm = ParametrizarMatricula(
                grado_id=g.id or 1,
                anio=2026,
                valor=val,  # type: ignore[arg-type]
            )
            params_matricula.append(pm)
            param_map[idx] = pm

        param_sexto = param_map[5]
        param_decimo = param_map[10]
        param_segundo = param_map[2]

        param_sexto_2025 = ParametrizarMatricula(
            grado_id=grados[5].id or 1,
            anio=2025,
            valor=800000,  # type: ignore[arg-type]
        )
        params_matricula.append(param_sexto_2025)

        session.add_all(params_matricula)
        session.flush()

        assert param_sexto.id is not None
        assert param_decimo.id is not None
        assert param_segundo.id is not None
        assert param_sexto_2025.id is not None

        # === PARAMETRIZAR PENSIÓN (costo mensual por grado y año) ===
        pension_sexto = ParametrizarPension(
            grado_id=grados[5].id or 1,
            anio=2026,
            valor=450000,  # type: ignore[arg-type]
        )
        pension_decimo = ParametrizarPension(
            grado_id=grados[10].id or 1,
            anio=2026,
            valor=520000,  # type: ignore[arg-type]
        )
        pension_segundo = ParametrizarPension(
            grado_id=grados[2].id or 1,
            anio=2026,
            valor=350000,  # type: ignore[arg-type]
        )
        pension_sexto_2025 = ParametrizarPension(
            grado_id=grados[5].id or 1,
            anio=2025,
            valor=400000,  # type: ignore[arg-type]
        )
        session.add_all(
            [pension_sexto, pension_decimo, pension_segundo, pension_sexto_2025]
        )
        session.flush()

        assert pension_sexto.id is not None
        assert pension_decimo.id is not None
        assert pension_segundo.id is not None
        assert pension_sexto_2025.id is not None

        # === TIPOS COMPLEMENTARIOS ===
        tipo_matricula = TipoComplementario(nombre="Matricula", estado=True)
        session.add(tipo_matricula)
        session.flush()
        assert tipo_matricula.id is not None

        # === COMPLEMENTARIOS ===
        comp_seguro = Complementario(
            nombre="Seguro Estudiantil",
            tipo_complementario_id=tipo_matricula.id,
            anio=2026,
            valor=120000,
            estado_complemento="Activo",
        )
        comp_agenda = Complementario(
            nombre="Agenda Escolar",
            tipo_complementario_id=tipo_matricula.id,
            anio=2026,
            valor=45000,
            estado_complemento="Activo",
        )
        comp_carnet = Complementario(
            nombre="Carnet Estudiantil",
            tipo_complementario_id=tipo_matricula.id,
            anio=2026,
            valor=25000,
            estado_complemento="Activo",
        )
        comp_plataforma = Complementario(
            nombre="Plataforma Digital",
            tipo_complementario_id=tipo_matricula.id,
            anio=2026,
            valor=80000,
            estado_complemento="Activo",
        )
        session.add_all([comp_seguro, comp_agenda, comp_carnet, comp_plataforma])
        session.flush()

        assert comp_seguro.id is not None
        assert comp_agenda.id is not None
        assert comp_carnet.id is not None
        assert comp_plataforma.id is not None

        # === TIPOS COMPLEMENTARIOS: ESCUELAS DE FORMACIÓN ===
        tipo_escuelas_formacion = TipoComplementario(
            nombre="Escuelas de Formacion", estado=True
        )
        session.add(tipo_escuelas_formacion)
        session.flush()
        assert tipo_escuelas_formacion.id is not None

        tipo_baloncesto = TipoComplementario(
            nombre="Baloncesto",
            estado=True,
            sub_tipo_complementario=tipo_escuelas_formacion.id,
        )
        tipo_ajedrez = TipoComplementario(
            nombre="Ajedrez",
            estado=True,
            sub_tipo_complementario=tipo_escuelas_formacion.id,
        )
        tipo_natacion = TipoComplementario(
            nombre="Natacion",
            estado=True,
            sub_tipo_complementario=tipo_escuelas_formacion.id,
        )
        session.add_all([tipo_baloncesto, tipo_ajedrez, tipo_natacion])
        session.flush()

        assert tipo_baloncesto.id is not None
        assert tipo_ajedrez.id is not None
        assert tipo_natacion.id is not None

        # === COMPLEMENTARIOS: ESCUELAS DE FORMACIÓN ===
        comp_baloncesto = Complementario(
            nombre="Escuela de Baloncesto",
            tipo_complementario_id=tipo_baloncesto.id,
            anio=2026,
            valor=60000,
            estado_complemento="Activo",
        )
        comp_ajedrez = Complementario(
            nombre="Escuela de Ajedrez",
            tipo_complementario_id=tipo_ajedrez.id,
            anio=2026,
            valor=50000,
            estado_complemento="Activo",
        )
        comp_natacion = Complementario(
            nombre="Escuela de Natacion",
            tipo_complementario_id=tipo_natacion.id,
            anio=2026,
            valor=70000,
            estado_complemento="Activo",
        )
        session.add_all([comp_baloncesto, comp_ajedrez, comp_natacion])
        session.flush()

        assert comp_baloncesto.id is not None
        assert comp_ajedrez.id is not None
        assert comp_natacion.id is not None

        # === MATRÍCULAS ===
        # Estudiante 1 (Juan - Sexto): matrícula con pendientes parciales
        matricula1 = Matricula(
            para_matricula_id=param_sexto.id,
            estudiante_id=estudiante1.id,
            periodo_id=periodo.id,
            valor_total=1570000,  # 850k + 120k + 45k + 25k + 80k + 450k
            fecha_registro=datetime(2026, 1, 20),
            estado_matricula="parcial",
            valor_pendiente_base=850000,  # No ha pagado base
        )
        session.add(matricula1)
        session.flush()

        assert matricula1.id is not None

        # Detalles de matrícula para Estudiante 1
        detalles1 = [
            DetalleMatricula(
                matricula_id=matricula1.id,
                complementario_id=comp_seguro.id,
                cuota=1,
                descuento=0,
                valor_completo=120000,
                valor_pendiente=120000,  # No ha pagado
                fecha_abono=datetime(2026, 1, 20),
            ),
            DetalleMatricula(
                matricula_id=matricula1.id,
                complementario_id=comp_agenda.id,
                cuota=1,
                descuento=5000,
                valor_completo=40000,  # 45k - 5k descuento
                valor_pendiente=0,  # Ya pagó
                fecha_abono=datetime(2026, 1, 25),
            ),
            DetalleMatricula(
                matricula_id=matricula1.id,
                complementario_id=comp_carnet.id,
                cuota=1,
                descuento=0,
                valor_completo=25000,
                valor_pendiente=25000,  # No ha pagado
                fecha_abono=datetime(2026, 1, 20),
            ),
            DetalleMatricula(
                matricula_id=matricula1.id,
                complementario_id=comp_plataforma.id,
                cuota=1,
                descuento=10000,
                valor_completo=70000,  # 80k - 10k descuento
                valor_pendiente=0,  # Ya pagó
                fecha_abono=datetime(2026, 2, 1),
            ),
        ]
        session.add_all(detalles1)

        # Estudiante 2 (Ana - Décimo): matrícula completa, todo pagado
        matricula2 = Matricula(
            para_matricula_id=param_decimo.id,
            estudiante_id=estudiante2.id,
            periodo_id=periodo.id,
            valor_total=1740000,
            fecha_registro=datetime(2026, 1, 18),
            estado_matricula="paz_y_salvo",  # Al día
            valor_pendiente_base=0,
        )
        session.add(matricula2)
        session.flush()

        assert matricula2.id is not None

        detalles2 = [
            DetalleMatricula(
                matricula_id=matricula2.id,
                complementario_id=comp_seguro.id,
                cuota=1,
                descuento=0,
                valor_completo=120000,
                valor_pendiente=0,
                fecha_abono=datetime(2026, 1, 18),
            ),
            DetalleMatricula(
                matricula_id=matricula2.id,
                complementario_id=comp_agenda.id,
                cuota=1,
                descuento=0,
                valor_completo=45000,
                valor_pendiente=0,
                fecha_abono=datetime(2026, 1, 18),
            ),
            DetalleMatricula(
                matricula_id=matricula2.id,
                complementario_id=comp_carnet.id,
                cuota=1,
                descuento=0,
                valor_completo=25000,
                valor_pendiente=0,
                fecha_abono=datetime(2026, 1, 18),
            ),
        ]
        session.add_all(detalles2)
        session.flush()

        # Pagos para Estudiante 1 (Juan - Sexto) para respaldar su estado parcial
        pago_juan = Pago(
            matricula_id=matricula1.id,
            codigo_talonario="TAL-J01",
            monto_total=110000,
            fecha_pago=datetime(2026, 1, 25),
            observacion="Abonos iniciales a complementarios",
        )
        session.add(pago_juan)
        session.flush()
        assert pago_juan.id is not None

        session.add_all(
            [
                PagoDetalle(
                    pago_id=pago_juan.id,
                    concepto="complementario",
                    complementario_id=comp_agenda.id,
                    monto_aplicado=40000,
                ),
                PagoDetalle(
                    pago_id=pago_juan.id,
                    concepto="complementario",
                    complementario_id=comp_plataforma.id,
                    monto_aplicado=70000,
                ),
            ]
        )

        # Pagos para Estudiante 2 (Ana - Décimo) para respaldar su estado paz_y_salvo
        pago_ana = Pago(
            matricula_id=matricula2.id,
            codigo_talonario="TAL-A01",
            monto_total=1140000,
            fecha_pago=datetime(2026, 1, 18),
            observacion="Pago completo de matricula y complementarios",
        )
        session.add(pago_ana)
        session.flush()
        assert pago_ana.id is not None

        session.add_all(
            [
                PagoDetalle(
                    pago_id=pago_ana.id,
                    concepto="matricula_base",
                    complementario_id=None,
                    monto_aplicado=950000,
                ),
                PagoDetalle(
                    pago_id=pago_ana.id,
                    concepto="complementario",
                    complementario_id=comp_seguro.id,
                    monto_aplicado=120000,
                ),
                PagoDetalle(
                    pago_id=pago_ana.id,
                    concepto="complementario",
                    complementario_id=comp_agenda.id,
                    monto_aplicado=45000,
                ),
                PagoDetalle(
                    pago_id=pago_ana.id,
                    concepto="complementario",
                    complementario_id=comp_carnet.id,
                    monto_aplicado=25000,
                ),
            ]
        )

        # Estudiante 3 (Pedro - Segundo): SIN matrícula registrada
        # Se usará para probar el endpoint POST /register

        session.commit()
        print("[OK] Seed ejecutado exitosamente.")
        print()
        print("Datos cargados:")
        print(f"   - {len(grados)} grados")
        print("   - 2 acudientes")
        print("   - 3 estudiantes:")
        print(f"     * ID {estudiante1.id}: Juan (Sexto) - Matricula con pendientes")
        print(f"     * ID {estudiante2.id}: Ana (Decimo) - Matricula al dia")
        print(f"     * ID {estudiante3.id}: Pedro (Segundo) - Sin matricula")
        print("   - 4 complementarios de matricula")
        print(
            "   - 3 complementarios de escuelas de formacion "
            "(Baloncesto, Ajedrez, Natacion)"
        )
        print("   - 2 matriculas con detalles")
        print(f"   - 1 periodo (ID: {periodo.id})")
        print()
        print("Prueba los endpoints:")
        print(f"   GET  /api/v1/enrollment/students/{estudiante1.id}/balance?year=2026")
        print(f"   GET  /api/v1/enrollment/students/{estudiante2.id}/balance?year=2026")
        print(f"   GET  /api/v1/enrollment/students/{estudiante3.id}/balance?year=2026")
        print()
        print("Nuevos endpoints:")
        print("   POST /api/v1/enrollment/register")
        print(
            f"        Body: {{estudiante_id: {estudiante3.id}, periodo_id: {periodo.id}, anio: 2026}}"
        )
        print("   POST /api/v1/enrollment/payments/auto")
        print(
            f"        Body: {{matricula_id: {matricula1.id}, monto: 1000000, codigo_talonario: 'TAL-001'}}"
        )
        print("   POST /api/v1/enrollment/payments/directed")


if __name__ == "__main__":
    seed()
