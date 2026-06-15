from datetime import datetime

from sqlmodel import Session, select

from app.core.db import engine
from app.modules.auth.infrastructure.models import Usuario
from app.modules.classroom.infrastructure.models import DetallePupitre
from app.modules.enrollment.infrastructure.models import (
    Acudiente,
    Complementario,
    Docente,
    Estudiante,
    Grado,
    Matricula,
    ParametrizarMatricula,
    Periodo,
    TipoComplementario,
)
from app.modules.inventory.infrastructure.models import EstadoInventario, TipoInventario
from app.modules.tuition.infrastructure.models import ParametrizarPension, Pension


def main():
    admin = Usuario(
        rol="administrador",
        username="admin",
        contrasenia="admin",
        estado=True,
    )

    periodos: list[Periodo] = [
        Periodo(
            periodo_electivo=datetime(year=2026, month=1, day=1),
            estado=True,
            fecha=datetime(year=2026, month=1, day=1),
        ),
        Periodo(
            periodo_electivo=datetime(year=2025, month=1, day=1),
            estado=False,
            fecha=datetime.now(),
        ),
    ]

    tipos_inventario: list[TipoInventario] = [
        TipoInventario(nombre="banda"),
        TipoInventario(nombre="deporte"),
        TipoInventario(nombre="ajedrez"),
    ]

    estados_inventario: list[EstadoInventario] = [
        EstadoInventario(nombre="disponible"),
        EstadoInventario(nombre="prestado"),
        EstadoInventario(nombre="mantenimiento"),
    ]

    docentes: list[Docente] = [
        Docente(
            nombre="VILLAMIZAR FERNANDEZ MILENA DEL PILAR",
            documento="100000001",
            estado=True,
            asignatura="Primaria",
        ),
        Docente(
            nombre="MARTINEZ VERA JOSE ANTONIO",
            documento="100000002",
            estado=True,
            asignatura="Artistica",
        ),
        Docente(
            nombre="MANTILLA TRUJILLO ELISABETH",
            documento="100000003",
            estado=True,
            asignatura="Artistica",
        ),
    ]

    acudientes: list[Acudiente] = [
        Acudiente(
            nombre="Carlos Aguillon",
            parentesco="Padre",
            telefono="3001000001",
            correo="carlos.ag@gmail.com",
        ),
        Acudiente(
            nombre="Laura Capacho",
            parentesco="Madre",
            telefono="3001000002",
            correo="laura.cap@gmail.com",
        ),
        Acudiente(
            nombre="Pedro Anaya",
            parentesco="Padre",
            telefono="3001000003",
            correo="pedro.anaya@gmail.com",
        ),
        Acudiente(
            nombre="Maria Blanco",
            parentesco="Madre",
            telefono="3001000004",
            correo="maria.blanco@gmail.com",
        ),
    ]

    tipos_complementario: list[TipoComplementario] = [
        TipoComplementario(nombre="matricula"),
        TipoComplementario(nombre="pruebas"),
        TipoComplementario(nombre="pupitre"),
        TipoComplementario(nombre="escuelas_formacion"),
    ]

    with Session(engine) as session:
        session.add(admin)
        session.add_all(periodos)
        session.add_all(docentes)
        session.add_all(acudientes)
        session.add_all(tipos_inventario)
        session.add_all(tipos_complementario)
        session.add_all(estados_inventario)
        session.flush()

        # === ESCUELAS DE FORMACIÓN: tipos y complementarios de ejemplo ===
        escuelas_formacion = tipos_complementario[3]
        tipo_baloncesto = TipoComplementario(
            nombre="Baloncesto",
            estado=True,
            sub_tipo_complementario=escuelas_formacion.id,
        )
        tipo_ajedrez = TipoComplementario(
            nombre="Ajedrez",
            estado=True,
            sub_tipo_complementario=escuelas_formacion.id,
        )
        tipo_natacion = TipoComplementario(
            nombre="Natacion",
            estado=True,
            sub_tipo_complementario=escuelas_formacion.id,
        )
        session.add_all([tipo_baloncesto, tipo_ajedrez, tipo_natacion])
        session.flush()

        complementarios_escuelas_formacion: list[Complementario] = [
            Complementario(
                nombre="Escuela de Baloncesto",
                tipo_complementario_id=tipo_baloncesto.id,
                anio=2026,
                valor=60000,
                estado_complemento="Activo",
            ),
            Complementario(
                nombre="Escuela de Ajedrez",
                tipo_complementario_id=tipo_ajedrez.id,
                anio=2026,
                valor=50000,
                estado_complemento="Activo",
            ),
            Complementario(
                nombre="Escuela de Natacion",
                tipo_complementario_id=tipo_natacion.id,
                anio=2026,
                valor=70000,
                estado_complemento="Activo",
            ),
        ]
        session.add_all(complementarios_escuelas_formacion)

        grados: list[Grado] = [
            Grado(nombre="cuarto", docente_titular_id=docentes[0].id),
            Grado(nombre="quinto"),
            Grado(nombre="sexto", docente_titular_id=docentes[2].id),
        ]
        session.add_all(grados)
        session.flush()

        parametrizacion_matricula: list[ParametrizarMatricula] = [
            ParametrizarMatricula(
                grado_id=grados[0].id or 1,
                anio=2026,
                valor=4500000,
            ),
            ParametrizarMatricula(
                grado_id=grados[1].id or 2,
                anio=2025,
                valor=4000000,
            ),
        ]

        parametrizacion_pensiones: list[ParametrizarPension] = [
            ParametrizarPension(
                grado_id=grados[0].id or 1,
                anio=2026,
                valor=1800000,
            ),
            ParametrizarPension(
                grado_id=grados[1].id or 2,
                anio=2025,
                valor=1500000,
            ),
        ]

        session.add_all(parametrizacion_matricula)
        session.add_all(parametrizacion_pensiones)

        estudiantes: list[Estudiante] = [
            Estudiante(
                grado_id=grados[1].id or 1,
                acudiente_id=acudientes[0].id or 1,
                nombre="AGUILLON VARGAS ANGELLY TATIANA",
                documento="2023002",
                activo=True,
                fecha_activo=datetime.now(),
            ),
            Estudiante(
                grado_id=grados[0].id or 2,
                acudiente_id=acudientes[1].id or 2,
                nombre="AMRA CAPACHO ZAREEN NAWAL",
                documento="2019079",
                activo=True,
                fecha_activo=datetime.now(),
            ),
            Estudiante(
                grado_id=grados[1].id or 3,
                acudiente_id=acudientes[2].id or 3,
                nombre="ANAYA BARRERA ANA SOFIA",
                documento="2022042",
                activo=True,
                fecha_activo=datetime.now(),
            ),
            Estudiante(
                grado_id=grados[0].id or 4,
                acudiente_id=acudientes[3].id or 4,
                nombre="BLANCO SERRANO SAHARA VALENTINA",
                documento="2023011",
                activo=True,
                fecha_activo=datetime.now(),
            ),
        ]

        session.add_all(estudiantes)
        session.flush()

        pupitres: list[DetallePupitre] = [
            DetallePupitre(
                estudiante_id=estudiante.id or 1,
                estado="Pendiente",
                observacion=None,
            )
            for estudiante in estudiantes
        ]

        matriculas: list[Matricula] = [
            Matricula(
                para_matricula_id=int(
                    session.exec(
                        select(ParametrizarMatricula.id).where(
                            ParametrizarMatricula.grado_id == estudiante.grado_id
                        )
                    ).one()
                    or 1
                ),
                estudiante_id=estudiante.id or 1,
                periodo_id=periodos[0].id or 1,
                valor_total=int(
                    session.exec(
                        select(ParametrizarMatricula.valor).where(
                            ParametrizarMatricula.grado_id == estudiante.grado_id
                        )
                    ).one()
                    or 0
                ),
                fecha_registro=datetime.now(),
                estado_matricula="pendiente",
                valor_pendiente_base=0,
            )
            for estudiante in estudiantes
        ]

        pensiones: list[Pension] = [
            Pension(
                estudiante_id=estudiante.id or 1,
                para_pension_id=int(
                    session.exec(
                        select(ParametrizarPension.id).where(
                            ParametrizarPension.grado_id == estudiante.grado_id
                        )
                    ).one()
                    or 1
                ),
                grado_id=estudiante.grado_id or 1,
                valor_total=int(
                    session.exec(
                        select(ParametrizarPension.valor).where(
                            ParametrizarPension.grado_id == estudiante.grado_id
                        )
                    ).one()
                )
                or 1,
                fecha_registro=datetime.now(),
                estado_pension=False,
            )
            for estudiante in estudiantes
        ]

        session.add_all(pupitres)
        session.add_all(pensiones)
        session.add_all(matriculas)

        session.commit()


if __name__ == "__main__":
    main()
