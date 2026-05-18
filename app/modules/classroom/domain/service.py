from app.modules.classroom.domain.repositories import PupitreRepository

class PupitreService():

    def __init__(self, repositorio: PupitreRepository):
        self.repositorio = repositorio

    async def actualizar_estado_estudiante(self, estudiante_id: int, nuevo_estado: bool, observacion: str | None):
        pupitre = await self.repositorio.obtener_por_estudiante(estudiante_id)
        if not pupitre:
            return None
        pupitre.actualizar_estado(nuevo_estado, observacion)
        return await self.repositorio.guardar_pupitre(pupitre)

    async def actualizar_estado_masivo(self, grado_id: int, nuevo_estado: bool, observacion: str | None):
        pupitres = await self.repositorio.obtener_por_grado(grado_id)
        if not pupitres:
            return None
        for pupitre in pupitres:
            pupitre.actualizar_estado(nuevo_estado, observacion)
            await self.repositorio.guardar_pupitre(pupitre)
        return {"total_actualizados": len(pupitres)}
       

        