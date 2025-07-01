from typing import Type
from fastapi import Depends
from sqlmodel import Session

from app.adapters.db import get_toolmaster_db_connection
from app.adapters.repositories.toolmaster_repository import ToolmasterRepository
from app.domain.ports.input_port.report_service import IWordReportUseCase
from app.api_services.report_use_case_impl import UnifiedReportUseCaseImpl

def word_report_use_case(
    session: Type[Session] = Depends(get_toolmaster_db_connection)
) -> IWordReportUseCase:

    toolmaster_repository = ToolmasterRepository(session=session)
    use_case = UnifiedReportUseCaseImpl()
    return use_case
