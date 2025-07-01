from enum import Enum
from typing import TypeVar

#from app.generic.generic_resources.base_model import BaseSQLModel
from app.domain.entities.base_model import BaseSQLModel
ENTITY_MODEL = TypeVar("ENTITY_MODEL", bound="BaseSQLModel")

