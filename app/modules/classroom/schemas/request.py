from pydantic import BaseModel

class PupitreInSchema (BaseModel):
    estado_pupitre : bool
    observacion : str|None

