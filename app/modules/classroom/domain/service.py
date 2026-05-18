from infrastructure.repository import PupitreRepository

class PupitreService():

    def __init__(self, repositorio : PupitreRepository):
        self.repositorio = repositorio


    def actualizar_estado_estudiante(self,estudiante_id : int , nuevo_estado: bool, observacion: str | None):
        pupitre = self.repositorio.obtener_por_estudiante(estudiante_id)
        if pupitre is None:
            raise ValueError(f"No se encontró un pupitre para el estudiante con ID {estudiante_id}")
        pupitre.actualizar_estado(nuevo_estado, observacion)
        self.repositorio.guardar_pupitre(pupitre)


    def actualizar_estado_masivo (self, grado_id : int , nuevo_estado: bool, observacion: str | None):
        pupitres = self.repositorio.obtener_por_grado(grado_id)
        if not pupitres:
            raise ValueError(f"No se encontraron pupitres para el grado {grado_id}")
        for pupitre in pupitres:
            pupitre.actualizar_estado(nuevo_estado, observacion)
            self.repositorio.guardar_pupitre(pupitre)
       
       

        