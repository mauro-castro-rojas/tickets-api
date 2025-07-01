from typing import Type

from fastapi import Depends
from sqlmodel import Session

from app.adapters.db import get_toolmaster_db_connection
from app.adapters.repositories.toolmaster_repository import ToolmasterRepository
from app.adapters.repositories.esb_repository import EsbRepository

from app.api_services.mailer_use_case_impl import MailerUseCaseImpl
from app.api_services.ticket_usecase_impl import TicketUseCaseImpl

def tickets_use_case(session: Type[Session] = Depends(get_toolmaster_db_connection)) -> TicketUseCaseImpl:    
    toolmaster_repository = ToolmasterRepository(session=session)
    esb_repository = EsbRepository()
    tickets_use_case = TicketUseCaseImpl(
        toolmaster_repository=toolmaster_repository,
        esb_repository=esb_repository
    )
    return tickets_use_case

def mailer_use_case(session: Type[Session] = Depends(get_toolmaster_db_connection)) -> MailerUseCaseImpl:    
    toolmaster_repository = ToolmasterRepository(session=session)
    mailer_use_case = MailerUseCaseImpl(
        toolmaster_repository=toolmaster_repository
    )
    return mailer_use_case


