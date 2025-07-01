from sqlmodel import Field
from app.domain.entities.base_model import BaseSQLModel

"""
table=True
indicate that the class should be treated as a table in the database. 
it tells SQLAlchemy (which SQLModel is built upon) that this class corresponds to an actual 
table in the database schema.
"""
class AppContact(BaseSQLModel, table=True): # table=True indicates that this is mapped to a real database table
    contact_id: int = Field(primary_key=True, nullable=False)
    sf_contact_id: str = Field(nullable=False)
    account_id: int = Field(nullable=False)
    contact_type: str = Field(nullable=False)