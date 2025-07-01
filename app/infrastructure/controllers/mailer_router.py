from fastapi import APIRouter, Depends, Security, status
from fastapi.responses import JSONResponse
from app.conf.settings.dependencies import validate_api_key
from app.domain.ports.input_port.mailer_service import IMailerUseCase
from app.container_instance.instances import mailer_use_case
from app.infrastructure.dto.mail_schema import MailBaseDTO, MailGeneralDTO, RadarMailDTO
from app.utils.errors import AppError
from app.utils.logger import log

mailer_router = APIRouter(dependencies=[Security(validate_api_key)],tags=["/"])

@mailer_router.post(
    path="/send_email",
    status_code=status.HTTP_200_OK,
)
def send(
    dto: MailBaseDTO,
    use_case: IMailerUseCase = Depends(mailer_use_case),
):
    try:
        data = use_case.send_email_none(dto)
        return data
    except AppError as app_err:
        log(f"AppError caught at the route level: {app_err}")
        return JSONResponse(
            status_code=app_err.error_type.value,
            content={"message": app_err.message, "error_type": app_err.error_type.name}
        )

@mailer_router.post(
    path="/sent_email_general",
    status_code=status.HTTP_200_OK,
)
def send_general_email(
    dto: MailGeneralDTO,
    use_case: IMailerUseCase = Depends(mailer_use_case),
):
    """
    Envía un correo basado en la plantilla general_template.html,
    usando un caso de uso general.
    """
    try:
        data = use_case.send_email_general(dto)
        return {"message": data}
    except AppError as app_err:
        log(f"AppError caught at the route level: {app_err}")
        return JSONResponse(
            status_code=app_err.error_type.value,
            content={"message": app_err.message, "error_type": app_err.error_type.name}
        )
        
@mailer_router.post(
    path="/send_email_radar",
    status_code=status.HTTP_200_OK,
)
def send_radar_email(
    dto: RadarMailDTO,
    use_case: IMailerUseCase = Depends(mailer_use_case),
):
    """
    Envía un correo basado en la plantilla radar_template.html,
    usando los campos de RadarMailDTO.
    """
    try:
        data = use_case.send_email_radar(dto)
        return {"message": data}
    except AppError as app_err:
        log(f"AppError caught at the route level: {app_err}")
        return JSONResponse(
            status_code=app_err.error_type.value,
            content={"message": app_err.message, "error_type": app_err.error_type.name})