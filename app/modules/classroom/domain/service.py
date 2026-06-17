from app.modules.classroom.domain.repositories import PupitreRepository
from app.modules.classroom.domain.entities import (
    ComplementarioEntity,
    DetallePupitreEntity,
)
from app.modules.classroom.application.contracts import ClassroomEnrollmentService

ESTADO_PENDIENTE = "pendiente"
ESTADO_PAGADO = "pagado"


class PupitreService:
    def __init__(
        self,
        repositorio: PupitreRepository,
        enrollment_service: ClassroomEnrollmentService,
    ):
        self.repositorio = repositorio
        self.enrollment_service = enrollment_service

    # Obtiene el complementario de pupitre (valor parametrizado vigente)
    async def get_complementario_pupitre(
        self, nombre_complementario: str = "Pupitre"
    ) -> ComplementarioEntity | None:
        return await self.enrollment_service.get_complementary_by_name(
            nombre_complementario
        )

    def _map_to_entity(self, data) -> DetallePupitreEntity:
        return DetallePupitreEntity(
            id=data.id or 0,
            estudiante_id=data.estudiante_id,
            estado=data.estado,
            observacion=data.observacion,
        )

    # Se confirma el pago de UN pupitre (no recibe valor, solo confirma)
    async def update_payment_status(
        self, estudiante_id: int, observacion: str | None
    ) -> DetallePupitreEntity | None:

        complementario = await self.get_complementario_pupitre()
        if not complementario:
            return None

        pupitre = await self.repositorio.get_student_desk(
            estudiante_id, complementario.id
        )
        if not pupitre:
            return None

        pupitre.estado = (
            ESTADO_PENDIENTE if pupitre.estado == ESTADO_PAGADO else ESTADO_PAGADO
        )
        pupitre.observacion = observacion

        pupitre_actualizado = await self.repositorio.update_desk(pupitre)
        return self._map_to_entity(pupitre_actualizado)

    # Confirma el pago de varios pupitres de un mismo grado, retorna cantidad actualizados
    async def bulk_update_desk_states(
        self, grado_id: int, ids_estudiantes: list[int]
    ) -> dict | None:

        pupitres = await self.repositorio.list_desks_by_grado_id(grado_id)

        if not pupitres:
            return None

        encontrados_ids = {p.estudiante_id for p in pupitres}

        ids_validos = [i for i in ids_estudiantes if i in encontrados_ids]
        ids_no_encontrados = [i for i in ids_estudiantes if i not in encontrados_ids]

        pupitres_a_actualizar = [p for p in pupitres if p.estudiante_id in ids_validos]

        for pupitre in pupitres_a_actualizar:
            pupitre.estado = ESTADO_PAGADO

        total = await self.repositorio.bulk_update_desk_states(pupitres_a_actualizar)

        return {
            "total_actualizados": total,
            "ids_no_encontrados": ids_no_encontrados,
        }

    # Lista los pupitres de un grupo de estudiantes
    async def get_desks_by_students(
        self, estudiante_ids: list[int]
    ) -> list[DetallePupitreEntity] | None:
        pupitres = await self.repositorio.list_desks_by_students(estudiante_ids)

        if not pupitres:
            return None

        return [self._map_to_entity(p) for p in pupitres]

    # Obtiene el pupitre de un estudiante
    async def get_desk_by_student(
        self, estudiante_id: int
    ) -> DetallePupitreEntity | None:
        complementario = await self.get_complementario_pupitre()

        if not complementario:
            return None

        pupitre = await self.repositorio.get_student_desk(
            estudiante_id, complementario.id
        )

        return self._map_to_entity(pupitre) if pupitre else None
