class ModuloStatus:
    def __init__(self, clave: str, nombre: str, estado: str, detalle: str):
        self.clave = clave
        self.nombre = nombre
        self.estado = estado
        self.detalle = detalle

    def to_dict(self) -> dict:
        return {
            "clave": self.clave,
            "nombre": self.nombre,
            "estado": self.estado,
            "detalle": self.detalle,
        }


class EstudianteInfo:
    def __init__(self, entity, grado_nombre: str | None = None):
        self.id = entity.id
        self.nombre = entity.nombre
        self.documento = entity.documento
        self.grado = grado_nombre or ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "documento": self.documento,
            "grado": self.grado,
        }


class DocenteInfo:
    def __init__(self, entity):
        self.id = entity.id
        self.nombre = entity.nombre
        self.documento = entity.documento
        self.asignatura = entity.asignatura

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "documento": self.documento,
            "asignatura": self.asignatura,
        }


class SearchResult:
    def __init__(self, items: list, tipo: str):
        self.tipo = tipo
        self.items = [item.to_dict() for item in items]

    def to_dict(self) -> dict:
        return {"tipo": self.tipo, "items": self.items}


class StatusResponse:
    def __init__(self, entidad: dict, modulos: list[dict]):
        self.entidad = entidad
        self.modulos = modulos
        total = len(modulos)
        ok_count = sum(1 for m in modulos if m["estado"] == "ok")
        self.total_modulos = total
        self.modulos_ok = ok_count
        self.modulos_error = total - ok_count
        self.paz_y_salvo = ok_count == total

    def to_dict(self) -> dict:
        return {
            "entidad": self.entidad,
            "modulos": self.modulos,
            "total_modulos": self.total_modulos,
            "modulos_ok": self.modulos_ok,
            "modulos_error": self.modulos_error,
            "paz_y_salvo": self.paz_y_salvo,
        }


class GenerateResponse:
    def __init__(self, record, detalles: list[dict]):
        self.id = record.id
        self.codigo = record.codigo_certificado
        self.estado_final = record.estado_final
        self.fecha = (
            record.fecha_generacion.isoformat() if record.fecha_generacion else ""
        )
        self.detalles = detalles

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "codigo": self.codigo,
            "estado_final": self.estado_final,
            "fecha": self.fecha,
            "detalles": self.detalles,
        }


class PazYSalvoDetail:
    def __init__(self, record, detalles, entidad_info: dict):
        self.id = record.id
        self.codigo = record.codigo_certificado
        self.entidad_tipo = record.entidad_tipo
        self.estado_final = record.estado_final
        self.fecha_generacion = (
            record.fecha_generacion.isoformat() if record.fecha_generacion else ""
        )
        self.entidad = entidad_info
        self.detalles = [
            {
                "modulo": d.modulo,
                "nombre_modulo": d.nombre_modulo,
                "estado": d.estado,
                "detalle": d.detalle,
            }
            for d in (detalles or [])
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "codigo": self.codigo,
            "entidad_tipo": self.entidad_tipo,
            "estado_final": self.estado_final,
            "fecha_generacion": self.fecha_generacion,
            "entidad": self.entidad,
            "detalles": self.detalles,
        }
