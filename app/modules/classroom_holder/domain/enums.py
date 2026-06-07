from enum import Enum


class TipoIncidencia(str, Enum):
    DANIO_MATERIAL = "danio_material"
    INDISCIPLINA = "indisciplina"
    INASISTENCIA = "inasistencia"
    OTRO = "otro"
