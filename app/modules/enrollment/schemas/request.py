from pydantic import BaseModel, Field, model_validator


class RegisterEnrollmentRequest(BaseModel):
    """Solicitud para registrar matrícula a un estudiante."""

    estudiante_id: int = Field(description="ID del estudiante")
    periodo_id: int = Field(description="ID del periodo electivo")
    anio: int = Field(description="Año de la matrícula")


class ComplementaryModification(BaseModel):
    """Modificación a un complementario existente en la matrícula."""

    detalle_id: int = Field(description="ID del DetalleMatricula a modificar")
    nuevo_valor_completo: int | None = Field(
        default=None, ge=0, description="Sobrescribir el costo total del complementario"
    )
    descuento: int | None = Field(
        default=None,
        ge=0,
        description="Aplicar un descuento (se resta del valor completo). Debe ser mayor o igual a 0",
    )

    @model_validator(mode="after")
    def validate_modification_modes(self) -> "ComplementaryModification":
        if self.nuevo_valor_completo is not None and self.descuento is not None:
            raise ValueError(
                "No se puede especificar 'nuevo_valor_completo' y 'descuento' simultáneamente"
            )
        return self


class ModifyEnrollmentRequest(BaseModel):
    """Solicitud para modificar los costos y descuentos de una matrícula en tiempo real."""

    motivo: str = Field(
        min_length=5,
        description="Motivo obligatorio del ajuste (requerido por auditoría según MAT-RF-07)",
    )
    nuevo_costo_base: int | None = Field(
        default=None, ge=0, description="Sobrescribir el valor de la matrícula base"
    )
    descuento_base: int | None = Field(
        default=None, ge=0, description="Aplicar descuento a la matrícula base"
    )
    complementarios: list[ComplementaryModification] | None = Field(
        default=None, description="Modificaciones a los complementarios asignados"
    )
    observaciones: str | None = Field(
        default=None,
        description="Observaciones adicionales opcionales para la modificación",
    )

    @model_validator(mode="after")
    def validate_modification_modes(self) -> "ModifyEnrollmentRequest":
        if self.nuevo_costo_base is not None and self.descuento_base is not None:
            raise ValueError(
                "No se puede especificar 'nuevo_costo_base' y 'descuento_base' simultáneamente"
            )
        return self


class ConceptoAsignacion(BaseModel):
    """Cuánto asignar a un concepto específico."""

    concepto: str = Field(
        description=(
            "Tipo de concepto: 'matricula_base', 'complementario', o 'pension'"
        ),
    )
    complementario_id: int | None = Field(
        default=None,
        description="ID del complementario (obligatorio si concepto='complementario')",
    )
    monto: int = Field(gt=0, description="Monto a aplicar a este concepto")


class DirectedPaymentRequest(BaseModel):
    """Pago con asignación dirigida (el padre elige a dónde va cada monto)."""

    matricula_id: int = Field(description="ID de la matrícula a pagar")
    asignaciones: list[ConceptoAsignacion] = Field(
        min_length=1,
        description="Lista de conceptos con sus montos a pagar",
    )
    codigo_talonario: str = Field(
        min_length=1,
        description="Código del talonario físico",
    )
    observacion: str | None = Field(
        default=None, description="Observación opcional del pago"
    )


class ComplementaryCreateRequest(BaseModel):
    """Solicitud para crear un nuevo concepto complementario."""

    tipo_complementario: str = Field(
        max_length=50, description="Nombre del concepto (ej: Banda Marcial)"
    )
    anio: int = Field(description="Año al que aplica este cobro")
    valor: int = Field(gt=0, description="Costo total del concepto")
    estado_complemento: str = Field(max_length=50, description="Estado (ej: Activo)")
    uso_matricula: bool = Field(
        default=False,
        description="Si es True, se asigna automáticamente a las matrículas nuevas",
    )


class AssignComplementaryRequest(BaseModel):
    """Solicitud para asignar un complementario a una matrícula existente."""

    complementario_id: int = Field(description="ID del concepto complementario")
    descuento: int = Field(
        default=0, ge=0, description="Descuento a aplicar (en pesos)"
    )
