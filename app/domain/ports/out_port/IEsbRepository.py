
from typing import Type
from app.domain.ports.out_port.base_sql_repository import IBaseRepository
from app.utils.variable_types import ENTITY_MODEL
from abc import ABC, abstractmethod
"""
IEsbRepository is an abstraction or contract that defines what operations 
are expected from a repository that handles ticket-related data. It should only 
declare methods without containing any logic. The purpose of this interface is 
to decouple the higher-level application logic (like use cases) from the 
lower-level implementation details (like SQL queries or database connections).
"""


class IEsbRepository(IBaseRepository):
    @abstractmethod
    def create_payload_to_open(self, query_params:  Type[ENTITY_MODEL]):
        pass

    @abstractmethod
    def create_payload_to_update(self, query_params:  Type[ENTITY_MODEL]):
        pass

    @abstractmethod
    def create_ticket(self, bussinesId, payload):
        pass

    @abstractmethod
    def generate_uuid(self):
        pass

