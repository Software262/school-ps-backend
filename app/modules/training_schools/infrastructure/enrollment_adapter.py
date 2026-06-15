from sqlmodel import col, or_, select

from app.core.db import SessionDep
from app.modules.enrollment.infrastructure.models import (
    Complementario,
    DetalleMatricula,
    Estudiante,
    Grado,
    Periodo,
    TipoComplementario,
)
from app.modules.training_schools.infrastructure.models import (
    DetalleEscuelaFormacion,
)
from app.modules.training_schools.application.contracts import EnrollmentDataService
from app.modules.training_schools.domain.entities import (
    ComplementarioInfo,
    PeriodInfo,
    ProgramInfo,
    StudentInfo,
    TipoComplementarioInfo,
)


class EnrollmentAdapter(EnrollmentDataService):
    """Adapter that implements EnrollmentDataService using enrollment's DB models."""

    def __init__(self, session: SessionDep) -> None:
        self.session = session

    def _matricula_type_ids(self) -> set[int]:
        matricula_type = self.session.exec(
            select(TipoComplementario).where(TipoComplementario.nombre == "Matricula")
        ).first()

        if not matricula_type or matricula_type.id is None:
            return set()

        ids = self.session.exec(
            select(col(TipoComplementario.id)).where(
                or_(
                    TipoComplementario.id == matricula_type.id,
                    TipoComplementario.sub_tipo_complementario == matricula_type.id,
                )
            )
        ).all()
        return {i for i in ids if i is not None}

    async def get_all_programs(self) -> list[ProgramInfo]:
        excluded_ids = self._matricula_type_ids()

        statement = select(Complementario).where(
            Complementario.estado_complemento == "Activo"
        )
        if excluded_ids:
            statement = statement.where(
                col(Complementario.tipo_complementario_id).not_in(excluded_ids)
            )

        rows = self.session.exec(statement).all()
        return [
            ProgramInfo(
                id=c.id if c.id is not None else 0,
                tipo_complementario=c.nombre,
                anio=c.anio,
                valor=c.valor,
                estado_complemento=c.estado_complemento,
            )
            for c in rows
        ]

    async def search_students(self, query: str) -> list[StudentInfo]:
        term = f"%{query}%"
        rows = self.session.exec(
            select(Estudiante)
            .where(
                or_(
                    col(Estudiante.documento).ilike(term),
                    col(Estudiante.nombre).ilike(term),
                )
            )
            .limit(20)
        ).all()
        return [
            StudentInfo(
                id=est.id if est.id is not None else 0,
                nombre=est.nombre,
                documento=est.documento,
                activo=est.activo,
            )
            for est in rows
        ]

    async def get_student_by_id(self, student_id: int) -> StudentInfo | None:
        result = self.session.exec(
            select(Estudiante, Grado)
            .join(Grado, col(Estudiante.grado_id) == col(Grado.id))
            .where(Estudiante.id == student_id)
        ).first()
        if not result:
            return None
        est, grado = result
        return StudentInfo(
            id=est.id if est.id is not None else 0,
            nombre=est.nombre,
            documento=est.documento,
            activo=est.activo,
            grado_nombre=grado.nombre,
        )

    async def get_periods(self) -> list[PeriodInfo]:
        rows = self.session.exec(select(Periodo).where(col(Periodo.estado))).all()
        return [
            PeriodInfo(
                id=p.id if p.id is not None else 0,
                periodo_electivo=p.periodo_electivo,
                estado=p.estado,
            )
            for p in rows
        ]

    def _tipo_to_info(self, tipo: TipoComplementario) -> TipoComplementarioInfo:
        padre_nombre = None
        if tipo.sub_tipo_complementario is not None:
            padre = self.session.get(
                TipoComplementario, tipo.sub_tipo_complementario
            )
            padre_nombre = padre.nombre if padre else None
        return TipoComplementarioInfo(
            id=tipo.id if tipo.id is not None else 0,
            nombre=tipo.nombre,
            estado=tipo.estado,
            sub_tipo_complementario=tipo.sub_tipo_complementario,
            padre_nombre=padre_nombre,
        )

    async def list_tipos_complementario(self) -> list[TipoComplementarioInfo]:
        rows = self.session.exec(select(TipoComplementario)).all()
        return [self._tipo_to_info(t) for t in rows]

    async def get_tipo_complementario(
        self, tipo_id: int
    ) -> TipoComplementarioInfo | None:
        tipo = self.session.get(TipoComplementario, tipo_id)
        if not tipo:
            return None
        return self._tipo_to_info(tipo)

    async def create_tipo_complementario(
        self, nombre: str, sub_tipo_complementario: int | None
    ) -> TipoComplementarioInfo:
        tipo = TipoComplementario(
            nombre=nombre,
            estado=True,
            sub_tipo_complementario=sub_tipo_complementario,
        )
        self.session.add(tipo)
        self.session.commit()
        self.session.refresh(tipo)
        return self._tipo_to_info(tipo)

    async def update_tipo_complementario(
        self,
        tipo_id: int,
        nombre: str | None,
        estado: bool | None,
        sub_tipo_complementario: int | None,
    ) -> TipoComplementarioInfo:
        tipo = self.session.get(TipoComplementario, tipo_id)
        if not tipo:
            raise ValueError("Tipo de complementario no encontrado.")

        if nombre is not None:
            tipo.nombre = nombre
        if estado is not None:
            tipo.estado = estado
        if sub_tipo_complementario is not None:
            tipo.sub_tipo_complementario = sub_tipo_complementario

        self.session.add(tipo)
        self.session.commit()
        self.session.refresh(tipo)
        return self._tipo_to_info(tipo)

    async def delete_tipo_complementario(self, tipo_id: int) -> None:
        tipo = self.session.get(TipoComplementario, tipo_id)
        if not tipo:
            raise ValueError("Tipo de complementario no encontrado.")
        tipo.estado = False
        self.session.add(tipo)
        self.session.commit()

    async def tipo_complementario_has_children_or_concepts(
        self, tipo_id: int
    ) -> bool:
        hijo = self.session.exec(
            select(TipoComplementario).where(
                TipoComplementario.sub_tipo_complementario == tipo_id
            )
        ).first()
        if hijo:
            return True

        concepto = self.session.exec(
            select(Complementario).where(
                Complementario.tipo_complementario_id == tipo_id
            )
        ).first()
        return concepto is not None

    def _complementario_to_info(self, comp: Complementario) -> ComplementarioInfo:
        tipo = self.session.get(TipoComplementario, comp.tipo_complementario_id)
        return ComplementarioInfo(
            id=comp.id if comp.id is not None else 0,
            nombre=comp.nombre,
            anio=comp.anio,
            valor=comp.valor,
            estado_complemento=comp.estado_complemento,
            tipo_complementario_id=comp.tipo_complementario_id,
            tipo_complementario_nombre=tipo.nombre if tipo else "",
        )

    async def list_complementarios(self) -> list[ComplementarioInfo]:
        rows = self.session.exec(select(Complementario)).all()
        return [self._complementario_to_info(c) for c in rows]

    async def get_complementario(
        self, complementario_id: int
    ) -> ComplementarioInfo | None:
        comp = self.session.get(Complementario, complementario_id)
        if not comp:
            return None
        return self._complementario_to_info(comp)

    async def create_complementario(
        self,
        nombre: str,
        anio: int,
        valor: int,
        estado_complemento: str,
        tipo_complementario_id: int,
    ) -> ComplementarioInfo:
        comp = Complementario(
            nombre=nombre,
            anio=anio,
            valor=valor,
            estado_complemento=estado_complemento,
            tipo_complementario_id=tipo_complementario_id,
        )
        self.session.add(comp)
        self.session.commit()
        self.session.refresh(comp)
        return self._complementario_to_info(comp)

    async def update_complementario(
        self,
        complementario_id: int,
        nombre: str | None,
        anio: int | None,
        valor: int | None,
        estado_complemento: str | None,
        tipo_complementario_id: int | None,
    ) -> ComplementarioInfo:
        comp = self.session.get(Complementario, complementario_id)
        if not comp:
            raise ValueError("Complementario no encontrado.")

        if nombre is not None:
            comp.nombre = nombre
        if anio is not None:
            comp.anio = anio
        if valor is not None:
            comp.valor = valor
        if estado_complemento is not None:
            comp.estado_complemento = estado_complemento
        if tipo_complementario_id is not None:
            comp.tipo_complementario_id = tipo_complementario_id

        self.session.add(comp)
        self.session.commit()
        self.session.refresh(comp)
        return self._complementario_to_info(comp)

    async def delete_complementario(self, complementario_id: int) -> None:
        comp = self.session.get(Complementario, complementario_id)
        if not comp:
            raise ValueError("Complementario no encontrado.")
        comp.estado_complemento = "Inactivo"
        self.session.add(comp)
        self.session.commit()

    async def complementario_has_references(self, complementario_id: int) -> bool:
        en_matricula = self.session.exec(
            select(DetalleMatricula).where(
                DetalleMatricula.complementario_id == complementario_id
            )
        ).first()
        if en_matricula:
            return True

        en_escuela = self.session.exec(
            select(DetalleEscuelaFormacion).where(
                DetalleEscuelaFormacion.complementario_id == complementario_id
            )
        ).first()
        return en_escuela is not None
