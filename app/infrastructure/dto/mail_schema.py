from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


class MailBaseDTO(BaseModel):
    to_mails: str
    ticket_id: str
    cid_mgt: str
    branch: str
    country: str
    customer: str
    is_major: bool = False

    class Config:
        extra = "forbid" 
        frozen = False
        
class MailGeneralDTO(BaseModel):
    to_mails: list[EmailStr]
    copy_mails: Optional[list[EmailStr]]=None
    subject: str
    body: str
    class Config:
        extra = "forbid"

class RadarMailDTO(BaseModel):
    to_mails: list[EmailStr]

    radar_checklist_choices: str
    radar_user_email: str
    radar_account_id: str
    radar_country: str
    radar_creation_date: str
    radar_case: str
    radar_contact_name: str
    radar_contact_phone: str
    radar_contact_email: str
    radar_area: str
    radar_type: str
    radar_details: str
