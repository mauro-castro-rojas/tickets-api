
from app.domain.ports.out_port.base_sql_repository import IBaseRepository
from abc import ABC
"""
acts as an interface or contract that defines the specific behaviors expected from any repository
handling data related to "Toolmaster" operations.

If you have multiple repositories that need to interact with "Toolmaster" data, they can all inherit from IToolmasterRepository, ensuring they conform to a consistent interface.
This also allows you to easily swap or extend repositories in the future without altering the core logic of the BaseSQLRepository or other unrelated repositories.

ABC is also included because IToolmasterRepository might be an abstract class itself, especially if it introduces any new abstract methods specific to the Toolmaster context.
"""


class IToolmasterRepository(IBaseRepository, ABC):
    # Inherits generic database behavior from BaseSQLRepository
    # Can add additional abstract methods specific to Toolmaster if needed
    pass

    """Example: Maybe Toolmaster repositories must implement a specific query
    @abstractmethod
    def some_toolmaster_specific_method(self):
        pass
    """