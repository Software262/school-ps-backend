class Pupitre():

    def __init__(self, id: int, estado_pupitre: bool = False, observacion: str | None = None):
        self._id = id
        self._estado_pupitre = estado_pupitre
        self._observacion = observacion

    def actualizar_estado(self, nuevo_estado : bool, observacion : str|None):
        if nuevo_estado == False and observacion is None:
            raise ValueError("Debe ingresar una observación del motivo del estado")
        self.estado_pupitre = nuevo_estado
        self.observacion = observacion