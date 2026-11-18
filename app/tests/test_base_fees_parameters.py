from datetime import datetime

import pytest
from sqlmodel import SQLModel, Session, create_engine

from app.modules.enrollment.infrastructure.models import (
    Acudiente,
    Estudiante,
    Grado,
    Periodo,
    TipoComplementario,
)
from app.modules.enrollment.application.manage_base_fees import (
    GetBaseFees,
    UpsertBaseFees,
    CopyBaseFees,
    InitializeDefaultBaseFees,
    UpdateSingleGradeFee,
)
from app.modules.enrollment.schemas.request import (
    UpsertBaseFeesRequest,
    BaseFeeGradeItem,
    CopyBaseFeesRequest,
    SingleGradeFeeRequest,
)
from app.modules.enrollment.application.register_enrollment import RegisterEnrollment


@pytest.fixture(name="db_session")
def db_session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as session:
        yield session


def test_get_base_fees_auto_creates_grades(db_session: Session):
    res = GetBaseFees(db_session).execute(2026)
    assert res.total_grados == 12
    assert res.total_configurados == 0
    assert len(res.tarifas) == 12
    assert res.tarifas[0].configurado is False


def test_initialize_defaults_and_get(db_session: Session):
    res_def = InitializeDefaultBaseFees(db_session).execute(2026)
    assert res_def.total_configurados == 12

    # Sexto (850k / 450k)
    sexto = next(t for t in res_def.tarifas if "sexto" in t.grado_nombre.lower())
    assert sexto.matricula_valor == 850000
    assert sexto.pension_valor == 450000
    assert sexto.configurado is True

    # Décimo (950k / 520k)
    decimo = next(
        t
        for t in res_def.tarifas
        if "décimo" in t.grado_nombre.lower() or "decimo" in t.grado_nombre.lower()
    )
    assert decimo.matricula_valor == 950000
    assert decimo.pension_valor == 520000

    # Segundo (750k / 350k)
    segundo = next(t for t in res_def.tarifas if "segundo" in t.grado_nombre.lower())
    assert segundo.matricula_valor == 750000
    assert segundo.pension_valor == 350000


def test_upsert_base_fees(db_session: Session):
    res_init = GetBaseFees(db_session).execute(2026)
    first_grade = res_init.tarifas[0]

    req = UpsertBaseFeesRequest(
        anio=2026,
        tarifas=[
            BaseFeeGradeItem(
                grado_id=first_grade.grado_id,
                matricula_valor=720000,
                pension_valor=360000,
            )
        ],
    )
    res_upsert = UpsertBaseFees(db_session).execute(req)
    first_item = next(t for t in res_upsert.tarifas if t.grado_id == first_grade.grado_id)
    assert first_item.matricula_valor == 720000
    assert first_item.pension_valor == 360000
    assert first_item.configurado is True


def test_copy_base_fees_with_increment(db_session: Session):
    InitializeDefaultBaseFees(db_session).execute(2026)

    copy_req = CopyBaseFeesRequest(
        anio_origen=2026,
        anio_destino=2027,
        incremento_porcentaje=10.0,
    )
    res_2027 = CopyBaseFees(db_session).execute(copy_req)
    assert res_2027.anio == 2027
    assert res_2027.total_configurados == 12

    sexto_2027 = next(t for t in res_2027.tarifas if "sexto" in t.grado_nombre.lower())
    assert sexto_2027.matricula_valor == 935000
    assert sexto_2027.pension_valor == 495000


def test_update_single_grade_fee(db_session: Session):
    res_init = GetBaseFees(db_session).execute(2026)
    first_grade = res_init.tarifas[0]

    single_req = SingleGradeFeeRequest(
        anio=2026,
        matricula_valor=800000,
        pension_valor=400000,
    )
    updated = UpdateSingleGradeFee(db_session).execute(first_grade.grado_id, single_req)
    assert updated.matricula_valor == 800000
    assert updated.pension_valor == 400000
    assert updated.configurado is True


def test_enrollment_blocked_then_unblocked_by_parameterization(db_session: Session):
    g_sexto = Grado(nombre="Sexto")
    db_session.add(g_sexto)
    db_session.commit()
    db_session.refresh(g_sexto)

    acudiente = Acudiente(
        nombre="Pedro Valdez",
        parentesco="Padre",
        telefono="123456",
        correo="pedro@valdez.com",
    )
    db_session.add(acudiente)
    db_session.commit()
    db_session.refresh(acudiente)

    periodo = Periodo(
        periodo_electivo=datetime(2026, 1, 1), estado=True, fecha=datetime.now()
    )
    db_session.add(periodo)
    db_session.commit()
    db_session.refresh(periodo)

    t_mat = TipoComplementario(nombre="Matricula", estado=True)
    db_session.add(t_mat)
    db_session.commit()

    est = Estudiante(
        nombre="Juan Valdez",
        documento="10203040",
        grado_id=g_sexto.id,
        acudiente_id=acudiente.id,
        activo=True,
    )
    db_session.add(est)
    db_session.commit()
    db_session.refresh(est)

    # 1. Enrolling without parameterization fails with the exact error message
    enroll_uc = RegisterEnrollment(db_session)
    with pytest.raises(ValueError) as excinfo:
        enroll_uc.execute(est.id, periodo.id, 2026)
    assert "No hay costo de matrícula parametrizado para grado 'Sexto' en 2026" in str(
        excinfo.value
    )

    # 2. Parameterize Sexto
    single_req = SingleGradeFeeRequest(
        anio=2026,
        matricula_valor=850000,
        pension_valor=450000,
    )
    UpdateSingleGradeFee(db_session).execute(g_sexto.id, single_req)

    # 3. Enrolling now succeeds
    created = enroll_uc.execute(est.id, periodo.id, 2026)
    assert created.matricula_id is not None
    assert created.costo_base == 850000
