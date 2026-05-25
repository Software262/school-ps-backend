from app.modules.classroom.domain.repositories import PupitreRepository

class PupitreService():

    def __init__(self, repositorio: PupitreRepository):
        self.repositorio = repositorio

    #Actualiza el estado del pupitre de un estudiante, si el estudiante no tiene pupitre, retornamos None
    async def actualizar_estado_estudiante(self, estudiante_id: int, nuevo_estado: bool, observacion: str | None):
        pupitre = await self.repositorio.obtener_por_estudiante(estudiante_id)
        if not pupitre:
            return None
        pupitre.estado_pupitre = nuevo_estado
        pupitre.observacion = observacion
        return await self.repositorio.guardar_pupitre(pupitre) 
    
    # Actualiza el estado de todos los pupitres de un grado, si el grado no tiene pupitres, retornamos None
    async def actualizar_estado_masivo(self, grado_id: int, nuevo_estado: bool, observacion: str | None):
        pupitres = await self.repositorio.obtener_por_grado(grado_id)
        if not pupitres:
            return None
        for pupitre in pupitres:
            pupitre.estado_pupitre = nuevo_estado
            pupitre.observacion = observacion
        total = await self.repositorio.guardar_muchos_pupitres(pupitres)
        return {"total_actualizados": total}
    
    async def obtener_pupitres(self, grado_id: int):
        pupitres = await self.repositorio.obtener_por_grado(grado_id)
        if not pupitres:
            return None
        return pupitres
        
       

        