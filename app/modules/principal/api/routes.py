"""
Rectoría Module API Endpoints.

This module exposes the FastAPI endpoints for the Rectoría (Principal) module,
delegating business operations to application layer services and returning
standardized responses.

Author: Yessyth Jaimes
Role: Product Owner and developer of the rectoria module
"""

from fastapi import APIRouter, HTTPException, status

from app.core.db import SessionDep
from app.modules.principal.application.create_observation import (
    CreateObservation,
)
from app.modules.principal.application.create_status import (
    CreateStatus,
)
from app.modules.principal.application.get_teacher import (
    GetTeachers,
)
from app.modules.principal.application.update_status import (
    UpdateStatus,
)
from app.modules.principal.schemas.request import (
    CreateObservationRequest,
    CreateStatusRequest,
    UpdateStatusRequest,
)
from app.modules.principal.schemas.response import (
    PrincipalObservationResponse,
    PrincipalStatusResponse,
)
from app.shared.utils.response import Response


router = APIRouter()


@router.get(
    "/teachers",
    summary="Get all teachers",
    description="Retrieve a list of all teachers, including their consolidated administrative statuses and observations.",
    responses={
        200: {
            "description": "Teachers obtained successfully",
            "content": {
                "application/json": {
                    "example": {
                        "statusCode": 200,
                        "data": [],
                        "message": "Teachers obtained successfully",
                        "details": None,
                    }
                }
            },
        }
    },
)
async def get_teachers(session: SessionDep):
    """
    HTTP GET endpoint to retrieve all teachers with their administrative status and observations.

    Args:
        session (SessionDep): SQLModel Database session.

    Returns:
        dict: Standardized API response containing list of teachers with nested statuses and observations.
    """
    app = GetTeachers(session=session)

    data = await app.execute()

    return Response(
        data=data,
        message="Teachers obtained successfully",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.post(
    "/observations",
    summary="Create administrative observation",
    description="Register a new administrative observation for a teacher. Requires a valid docente_id, periodo_id, and id_usuario with Rectoría or Admin role.",
    responses={
        201: {
            "description": "Administrative observation created successfully",
        },
        400: {
            "description": "Bad Request due to invalid user/docente/periodo identifier or unauthorized role",
        },
    },
)
async def create_observation(
    session: SessionDep,
    observation_data: CreateObservationRequest,
):
    """
    HTTP POST endpoint to register a new administrative observation for a teacher.

    Args:
        observation_data (CreateObservationRequest): Body containing observation details.
        session (SessionDep): SQLModel Database session.

    Returns:
        dict: Standardized API response containing the created observation details.

    Raises:
        HTTPException: 400 Bad Request if validation checks fail.
    """
    app = CreateObservation(session=session)

    try:
        data = await app.execute(observation_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if data.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al persistir el registro en la base de datos.",
        )
    response_data = PrincipalObservationResponse(
        id=data.id,
        docente_id=data.docente_id,
        periodo_id=data.periodo_id,
        descripcion=data.descripcion,
        tipo_observacion=data.tipo_observacion,
        fecha=data.fecha,
    )

    return Response(
        data=response_data,
        message="Administrative observation created successfully",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.post(
    "/status",
    summary="Assign administrative status",
    description="Assign a new administrative status (paz y salvo) to a teacher for a specific academic period. Fails if a status already exists.",
    responses={
        200: {
            "description": "Administrative status created successfully",
        },
        400: {
            "description": "Bad Request due to invalid user/docente/periodo identifier, duplicate status, or unauthorized role",
        },
    },
)
async def create_status(
    session: SessionDep,
    status_data: CreateStatusRequest,
):
    """
    HTTP POST endpoint to assign a new administrative status to a teacher.

    Args:
        status_data (CreateStatusRequest): Body containing status details.
        session (SessionDep): SQLModel Database session.

    Returns:
        dict: Standardized API response containing the created status details.

    Raises:
        HTTPException: 400 Bad Request if validation checks fail or duplicate status exists.
    """
    app = CreateStatus(session=session)

    try:
        data = await app.execute(status_data)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if data.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al persistir el registro en la base de datos.",
        )
    response_data = PrincipalStatusResponse(
        id=data.id,
        docente_id=data.docente_id,
        periodo_id=data.periodo_id,
        motivo_estado=data.motivo_estado,
        fecha_actualizacion=data.fecha_actualizacion,
    )

    return Response(
        data=response_data,
        message="Administrative status created successfully",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.put(
    "/status/{status_id}",
    summary="Update administrative status",
    description="Update an existing administrative status record with a new reason or details.",
    responses={
        200: {
            "description": "Administrative status updated successfully",
        },
        400: {
            "description": "Bad Request due to invalid user identifier or unauthorized role",
        },
        404: {
            "description": "Administrative status record not found",
        },
    },
)
async def update_status(
    session: SessionDep,
    status_id: int,
    status_data: UpdateStatusRequest,
):
    """
    HTTP PUT endpoint to update an existing administrative status record.

    Args:
        status_id (int): The unique ID of the administrative status record to update.
        status_data (UpdateStatusRequest): Body containing the new motivation and updating user ID.
        session (SessionDep): SQLModel Database session.

    Returns:
        dict: Standardized API response containing the updated status details.

    Raises:
        HTTPException: 400 Bad Request if validation checks fail, or 404 Not Found if record is missing.
    """
    app = UpdateStatus(session=session)

    try:
        data = await app.execute(
            status_id,
            status_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Administrative status not found",
        )

    if data.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al persistir el registro en la base de datos.",
        )
    response_data = PrincipalStatusResponse(
        id=data.id,
        docente_id=data.docente_id,
        periodo_id=data.periodo_id,
        motivo_estado=data.motivo_estado,
        fecha_actualizacion=data.fecha_actualizacion,
    )

    return Response(
        data=response_data,
        message="Administrative status updated successfully",
        status_code=status.HTTP_200_OK,
    ).to_dict()
