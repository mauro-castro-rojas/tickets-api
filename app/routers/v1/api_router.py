from fastapi import APIRouter, Depends
from app.conf.settings.dependencies import validate_api_key
from app.infrastructure.controllers.mailer_router import mailer_router
from app.infrastructure.controllers.ticket_router import tickets_router
from app.infrastructure.controllers.reports_router import reports_router

router = APIRouter()

router.include_router(
    tickets_router,
    prefix="/tickets",
    dependencies=[Depends(validate_api_key)]
)

router.include_router(
    mailer_router,
    prefix="/mailer",
    dependencies=[Depends(validate_api_key)]
)

router.include_router(
    reports_router,
    prefix="/report",
    tags=["Customer Service Center Reports"],
    dependencies=[Depends(validate_api_key)]
)
