from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from app.utils.logger import log
from typing import Optional
from pydantic import ValidationInfo, field_validator
import os 

env = os.getenv("ENVIRONMENT", "dev")
env_file = f".env.{env}"

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=env_file,  
        extra="ignore",
    )

    secret_key: SecretStr
    project_name: str = "tickets-api"
    api_v1_str: str = "/api"
    tm_db_name: str
    tm_db_user: str
    tm_db_password: SecretStr
    tm_db_host: str
    tm_db_port: int
    tm_db_uri: Optional[str] = None
    esb_id: str
    esb_secret: SecretStr
    esb_env: str
    esb_url: str
    api_key: str
    api_key_name: str

    @field_validator("tm_db_uri", mode='after')
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: 'ValidationInfo') -> str:
        if isinstance(v, str):
            return v
        
        db_user = values.data.get('tm_db_user')
        db_password = values.data.get('tm_db_password')
        db_host = values.data.get('tm_db_host')
        db_port = values.data.get('tm_db_port')
        db_name = values.data.get('tm_db_name')

        return f"mysql+mysqldb://{db_user}:{db_password.get_secret_value()}@{db_host}:{db_port}/{db_name}"

#log(Settings().model_dump())