from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from app.utils.errors import DatabaseError
from pydantic import BaseModel
from sqlalchemy import Column

from app.utils.errors import AppError, ErrorType
from app.utils.variable_types import ENTITY_MODEL
from app.utils.logger import log

class IBaseUseCase(ABC):
    """
    Base implementation for use cases.
    """

    def __init__(
        self,
        error_message: Optional[str] = "Base Use case error",
        field_to_validate: Optional[str] = None,
    ):
        self.error_message = error_message
        self.field_to_validate = field_to_validate

    def set_repository(self, repository: any):
        self.repository = repository

    def set_model(self, model: Type[ENTITY_MODEL]):
        self.model_to_search = model

    @abstractmethod
    def get_by_id(self, id_: str):
        try:
            if self.model_to_search:
                response = self.repository.get_by_id(id_=id_, model=self.model_to_search)
            return response
        except DatabaseError:
            return AppError(
                error_type=ErrorType.DATASOURCE_ERROR, message="database error"
            )
    
    @abstractmethod
    def get_by_unique_field(self, field_name: str, data: str):
        try:
            if self.model_to_search:
                response = self.repository.get_by_unique_field(field_name=field_name, data=data, model=self.model_to_search)
            return response
        except DatabaseError:
            return AppError(
                error_type=ErrorType.DATASOURCE_ERROR, message="database error"
            )
        
    @abstractmethod    
    async def get_all(self):
        try:
            response = self.repository.get_all(model=self.model)
            if not response:
                return AppError(
                    error_type=ErrorType.NOT_FOUND,
                    message=f"{self.error_message} not found",
                )
            try:
                clenead_data = [element.dict() for element in response]
                return clenead_data
            except Exception:
                return response

        except DatabaseError:
            return AppError(
                error_type=ErrorType.DATASOURCE_ERROR, message="database error"
            )
        
    @abstractmethod
    def get_all_by_fields(self, filters: Dict):
        try:
            response = self.repository.get_all_by_fields(
                filters=filters, model=self.model_to_search
            )
            if not response:
                return AppError(
                    error_type=ErrorType.NOT_FOUND,
                    message=f"{self.error_message} not found",
                )
            return response

        except DatabaseError:
            return AppError(
                error_type=ErrorType.DATASOURCE_ERROR, message="Database error"
            )
        
    @abstractmethod
    async def get_all_by_fields_contains(self, filters: Dict):
        try:
            response = self.repository.get_all_by_fields_contains(
                filters=filters, model=self.model
            )
            if not response:
                return AppError(
                    error_type=ErrorType.NOT_FOUND,
                    message=f"{self.error_message} not found",
                )
            return response

        except DatabaseError:
            return AppError(
                error_type=ErrorType.DATASOURCE_ERROR, message="Database error"
            )
        
    @abstractmethod
    def get_all_by_list_ids(
        self,
        list_ids: List[str],
        column_to_search: Column,
        model_to_search: Optional[Type[ENTITY_MODEL]] = None,
    ):
        try:
            if self.model_to_search:
                response = self.repository.get_all_by_list_ids(
                    model=self.model_to_search,
                    list_ids=list_ids,
                    column_to_search=column_to_search,
                )
            
            return response
        except DatabaseError:
            return AppError(
                error_type=ErrorType.DATASOURCE_ERROR, message="database error"
            )
        
    @abstractmethod
    async def save(self, data_model: Type[BaseModel]):
        """
        try:
            data = data_model.dict()
            if self.field_to_validate:
                unique_field = data[self.field_to_validate]
                if self.repository.get_by_unique_field(
                    field=self.field_to_validate, data=unique_field, model=self.model
                ):
                    return AppError(
                        error_type=ErrorType.BAD_REQUEST,
                        message=f"{self.error_message} already exist",
                    )

            data_model = self.model(**data)
            response = self.repository.save(model=self.model, data_model=data_model)
            return response
        except DatabaseError:
            return AppError(
                error_type=ErrorType.DATASOURCE_ERROR, message="Database error"
            )"""
        
    @abstractmethod
    async def update(
        self,
        id_: str,
        update_fields: Dict[str, Any],
    ):
        try:
            if not update_fields:
                return AppError(
                    error_type=ErrorType.BAD_REQUEST,
                    message="Update fields must not be empty",
                )

            if self.field_to_validate:
                unique_field = update_fields.get(self.field_to_validate)
                if unique_field and self.repository.get_by_entity_unique(
                    field=self.field_to_validate, data=unique_field, model=self.model
                ):
                    return AppError(
                        error_type=ErrorType.BAD_REQUEST,
                        message=f"{self.error_message} already exist",
                    )

            response = self.repository.update(
                id_=id_, update_fields=update_fields, model=self.model
            )
            if response is None:
                return AppError(
                    error_type=ErrorType.NOT_FOUND,
                    message=f"{self.error_message} not found",
                )

            return response
        except DatabaseError:
            return AppError(
                error_type=ErrorType.DATASOURCE_ERROR, message="Database error"
            )
        
    @abstractmethod
    async def delete(self, id_: str):
        try:
            response = self.repository.delete(id_=id_, model=self.model)
            if not response:
                return AppError(
                    error_type=ErrorType.NOT_FOUND,
                    message=f"{self.error_message} not found",
                )
        except DatabaseError:
            return AppError(
                error_type=ErrorType.DATASOURCE_ERROR, message="database Error"
            )
