from datetime import datetime
from typing import Any, cast

from app.modules.training_schools.schemas.response import (
    EnrollmentResponse,
    GeneralStatusResponse,
    MonthlyStatusResponse,
    PaymentResponse,
    ProgramResponse,
    StudentResponse,
)


def to_enrollment_response(data: dict) -> EnrollmentResponse:
    return EnrollmentResponse(**data)


def to_payment_response(data: dict) -> PaymentResponse:
    if data.get("updated_at") is None:
        data["updated_at"] = datetime.now()
    return PaymentResponse(**data)


def to_program_response(data: dict) -> ProgramResponse:
    return ProgramResponse(**data)


def to_student_response(data: dict) -> StudentResponse:
    return StudentResponse(**data)


def to_general_status_response(data: dict) -> GeneralStatusResponse:
    return GeneralStatusResponse(
        estudiante_id=cast(int, data["estudiante_id"]),
        paz_y_salvo=cast(bool, data["paz_y_salvo"]),
        detalle=cast(str, data["detalle"]),
    )


def to_monthly_status_response(data: dict) -> MonthlyStatusResponse:
    enrollments = cast(list[dict[str, Any]], data["meses"])
    return MonthlyStatusResponse(
        estudiante_id=cast(int, data["estudiante_id"]),
        complementario_id=cast(int, data["complementario_id"]),
        paz_y_salvo=cast(bool, data["paz_y_salvo"]),
        detalle=cast(str, data["detalle"]),
        meses=[to_enrollment_response(enrollment) for enrollment in enrollments],
    )
