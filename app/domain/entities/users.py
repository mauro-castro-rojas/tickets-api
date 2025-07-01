import uuid

from pydantic import EmailStr
from sqlmodel import Field

from app.domain.entities.base_model import BaseSQLModel


class Users(BaseSQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_name: str = Field(default=None, max_length=255, nullable=False)
    email: EmailStr = Field(nullable=False, unique=True)
    password: str = Field(nullable=False, min_length=10)
    rol_id: str = Field(nullable=False)
    status: str = Field(nullable=False, max_length=255)
