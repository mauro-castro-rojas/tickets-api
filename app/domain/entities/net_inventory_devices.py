from sqlmodel import SQLModel, Field
from app.domain.entities.base_model import BaseSQLModel

class NetInventoryDevices(BaseSQLModel, table=True):
    """
    SQLModel (and SQLAlchemy) automatically generates the table name based on the model class name, 
    but it doesn't handle cases where there are underscores in the table name by default.
    """
    __tablename__ = "net_inventory__devices"  # Explicitly set the correct table name

    id: int = Field(primary_key=True, nullable=False)
    branch: str
    cid_mgt: str


class NetMonitoringAlarms(BaseSQLModel, table=True):
    """
    SQLModel (and SQLAlchemy) automatically generates the table name based on the model class name, 
    but it doesn't handle cases where there are underscores in the table name by default.
    """
    __tablename__ = "net_monitoring__alarms_active"  # Explicitly set the correct table name

    id: int = Field(primary_key=True, nullable=False)
    branch: str
    cid_mgt: str
    customer: str
    city: str
    country: str
    department: str
    category: str
    um: str
    comment: str
