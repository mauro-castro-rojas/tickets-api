from typing import Optional
from sqlmodel import Field
from app.domain.entities.base_model import BaseSQLModel

"""
Field :
An SQLModel class used to define what is the behavior of the attributes in a model, in terms of
validation and data base restroctions.

table=True
indicate that the class should be treated as a table in the database. 
it tells SQLAlchemy (which SQLModel is built upon) that this class corresponds to an actual 
table in the database schema.

nullable False : the field doesnt accept null values
nullable=True: Field can accept NULL values

default=None: El valor por defecto es None.

Optional[str] Indicates that the field can be an empty string or None
"""
class AppAccounts(BaseSQLModel, table=True): 
    account_id: int = Field(primary_key=True, nullable=False)
    sf_account_id: str = Field(nullable=False)

class AppIncident(BaseSQLModel , table=True):
    incident_id: int = Field(primary_key=True, nullable=False)
    sf_incident_id: str = Field(nullable=None)
    owner_id: str = Field(nullable=None)
    incident_number: str = Field(nullable=None)
    failure_class_name: Optional[str] = Field(default=None, nullable=True)
    failure_class_code: Optional[str] = Field(default=None, nullable=True)

class AppAssets(BaseSQLModel, table=True): 
    asset_id: int = Field(primary_key=True, nullable=False)
    sf_asset_id: str = Field(nullable=False)
    circuit_id: str = Field(nullable=False)
    account_id: int = Field(nullable=False)
    city_id: int = Field(nullable=False)

class AppCities(BaseSQLModel, table=True): # table=True indicates that this is mapped to a real database table
    city_id: int = Field(primary_key=True, nullable=False)
    name: str = Field(nullable=False)
    country_id: int = Field(nullable=False)

class AppContact(BaseSQLModel, table=True): # table=True indicates that this is mapped to a real database table
    contact_id: int = Field(primary_key=True, nullable=False)
    sf_contact_id: str = Field(nullable=False)
    account_id: int = Field(nullable=False)
    contact_type: str = Field(nullable=False)
    

   
