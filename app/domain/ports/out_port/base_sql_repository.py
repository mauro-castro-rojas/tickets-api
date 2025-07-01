from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type

from sqlalchemy import Column
from sqlmodel import Session, SQLModel, select
from sqlalchemy.orm import scoped_session, sessionmaker


from app.utils.errors import handle_database_error
from app.utils.variable_types import ENTITY_MODEL
from app.utils.logger import log

class IBaseRepository(ABC):
    def __init__(self, session: scoped_session):
        self.session: scoped_session = session

    @abstractmethod
    @handle_database_error
    def get_by_id(self, id_: str, model: Type[ENTITY_MODEL]):
        try:
            result = self.session.query(model).get(id_)
            return result
        except Exception as e:
            raise e
            
    @abstractmethod
    @handle_database_error
    def get_all(self, model: Type[ENTITY_MODEL] = None):
        try:
            result = self.session.query(model).all()
            return result
        except Exception as e:
            log(f"Exception: {e}")
            raise e

    @abstractmethod
    @handle_database_error
    def get_all_by_fields(self, filters: Dict, model: Type[ENTITY_MODEL] = None):
        try:
            query = self.session.query(model)
            for field, value in filters.items():
                if isinstance(value, (list, tuple)): 
                    query = query.filter(getattr(model, field).in_(value))
                else:
                    query = query.filter(getattr(model, field) == value)

            result = query.all()
            return result
        except Exception as e:
            log(f"Exception: {e}")
            raise e
        
    @abstractmethod
    @handle_database_error
    def get_all_by_fields_contains(self, filters: Dict, model: Type[ENTITY_MODEL]):
        try:
            if not filters:
                result = self.session.query(model).all()
            else:
                query = self.session.query(model)
                for key, value in filters.items():
                    if value is not None:
                        column = getattr(model, key)
                        if isinstance(value, (float, int, bool)):
                            # Si el valor es float o int, aplicar filtro de igualdad (==)
                            query = query.filter(column == value)
                        else:
                            # Si el valor no es float o int, aplicar filtro ILIKE para búsquedas de texto
                            query = query.filter(column.ilike(f"%{value}%"))

                result = query.all()
            return result
        except Exception as e:
            raise e

    @abstractmethod
    @handle_database_error
    def get_by_unique_field(self, field_name: str, data: str, model: Type[ENTITY_MODEL]):
        try:
            result = self.session.query(model).filter_by(**{field_name: data}).first()
            return result
        except Exception as e:
            raise e

    @abstractmethod
    @handle_database_error
    def get_all_by_list_ids(
        self,
        column_to_search: Column,
        list_ids: List[str],
        model: Type[ENTITY_MODEL] = None,
    ):
        try:
            query = (
                self.session.query(model).filter(column_to_search.in_(list_ids)).all()
            )
            return query
        except Exception as e:
            raise e

    @abstractmethod
    @handle_database_error
    def save(self, model: Type[ENTITY_MODEL], data_model: SQLModel):
        try:
            instance = model.from_orm(data_model)
            self.session.add(instance)
            self.session.commit()
            self.session.refresh(instance)
            return instance
        except Exception as e:
            raise e

    @abstractmethod
    @handle_database_error
    def update(self, id_: str, update_fields: Dict[str, Any], model: Type[ENTITY_MODEL]):
        try:
            result = self.get_by_id(id_, model)
            if result is not None:
                for key, value in update_fields.items():
                    setattr(result, key, value)
                self.session.commit()
                self.session.refresh(result)
                return result
        except Exception as e:
            raise e

    @abstractmethod
    @handle_database_error
    def delete(self, id_: str, model: Type[ENTITY_MODEL]):
        try:
            result = self.get_by_id(id_, model=model)
            if result is not None:
                self.session.delete(result)
                self.session.commit()
                return result
        except Exception as e:
            raise e
