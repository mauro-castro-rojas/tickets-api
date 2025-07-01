from abc import ABC, abstractmethod
from app.infrastructure.dto.mail_schema import MailBaseDTO, MailGeneralDTO

class IMailerUseCase(ABC):
    
    @abstractmethod
    def send_email_none(self, dto: MailBaseDTO):
        pass
    
    @abstractmethod
    def send_email_general(self, dto: MailGeneralDTO):
        pass