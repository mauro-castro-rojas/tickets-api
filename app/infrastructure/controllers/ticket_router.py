from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.responses import JSONResponse

from app.conf.settings.dependencies import validate_api_key
from app.domain.ports.input_port.ticket_service import ITicketUseCase

from app.container_instance.instances import tickets_use_case

from app.infrastructure.dto.ticket_schema import (
    TicketBaseDTO,
    TicketUpdateDTO,
    TicketCloseDTO
)
from app.utils.errors import AppError
from app.utils.logger import log

tickets_router = APIRouter(dependencies=[Security(validate_api_key)],tags=["/"])

@tickets_router.get(
    path="/incidents_by_cid/{bussinesId}/{circuit_id}",
    status_code=status.HTTP_200_OK,
)
async def get_incident_by_circuit_id(
    bussinesId: str,
    circuit_id: str,
    use_case: ITicketUseCase = Depends(tickets_use_case),
):
    incident_data = use_case.get_incident_by_circuit_id(bussinesId,circuit_id)
    return incident_data

@tickets_router.get(
    path="/incidents_details",
    status_code=status.HTTP_200_OK,
)
async def get_incidents_by_id(
    bussinesId: str,
    incident_id: str,
    use_case: ITicketUseCase = Depends(tickets_use_case),
):
    incident_data = use_case.get_incident_details_by_id(bussinesId, incident_id)
    return incident_data

@tickets_router.get(
    path="/incident_details/{bussinesId}/{incident_id}",
    status_code=status.HTTP_200_OK,
)
async def get_incident_details_by_sf_id(
    bussinesId: str,
    sf_incident_id: str,
    use_case: ITicketUseCase = Depends(tickets_use_case),
):
    incident_data = use_case.get_incident_details_by_sf_id(bussinesId,sf_incident_id)
    return incident_data

@tickets_router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,)
async def create(
    dto: TicketBaseDTO, # controlador valida que sea de este tipo lo hace pydantic por dentro
    use_case: ITicketUseCase = Depends(tickets_use_case)):
    try:
        data = use_case.create_ticket(dto)
        return data
    except AppError as app_err:
        log(f"AppError caught at the route level: {app_err}")
        return JSONResponse(
            status_code=app_err.error_type.value,
            content={"message": app_err.message, "error_type": app_err.error_type.name}
        )

# Update ticket
@tickets_router.patch(
    path="/update",
    status_code=status.HTTP_200_OK,)
async def update_ticket(
    updated_data: TicketUpdateDTO,
    use_case: ITicketUseCase = Depends(tickets_use_case)):

    try:
        updated_data = use_case.update_ticket(updated_data)
        return updated_data
    except AppError as app_err:
        log(f"AppError caught at the route level: {app_err}")
        return JSONResponse(
            status_code=app_err.error_type.value,
            content={"message": app_err.message, "error_type": app_err.error_type.name}
        )



@tickets_router.patch(
    path="/close",
    status_code=status.HTTP_200_OK,)
async def close_ticket(
    data: TicketCloseDTO,
    use_case: ITicketUseCase = Depends(tickets_use_case)):

    try:
        data = use_case.close_ticket(data)
        return data
    except AppError as app_err:
        log(f"AppError caught at the route level: {app_err}")
        return JSONResponse(
            status_code=app_err.error_type.value,
            content={"message": app_err.message, "error_type": app_err.error_type.name}
        )








