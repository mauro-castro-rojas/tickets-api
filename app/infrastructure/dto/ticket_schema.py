from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Dict
from typing import Literal
from pydantic import BaseModel, Field
from app.utils.constants import description_templates
from app.utils.logger import log
from datetime import datetime, timedelta, timezone

def colombia_now_iso():
    now_utc = datetime.now(timezone.utc)
    return (now_utc - timedelta(hours=5)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + '-0500'

def trouble_ticket_characteristics_default() -> List[Dict[str, Any]]:
    """Fresh list for each DTO instance with a live timestamp."""
    return [
        {'name': 'caseReason',     'value': 'Service Alarmed'},
        {'name': 'TypeOfAction',   'value': 'Proactive'},
        {'name': 'isSecurityIncident', 'value': 'false'},
        {'name': 'isMajorIncident',    'value': 'false'},
        {'name': 'OwnerId',        'value': '00G4X000003ZBcbUAG'}, # cola - app_group - CSC PROACTIVE MONITORING
        {'name': 'AffectedDate',   'value': colombia_now_iso()},
    ]

class PriorityEnum(str, Enum):
    Critical = 'Critical'
    High = 'High'
    Medium = 'Medium'
    Low = 'Low'
    Planning = 'Planning'

class StatusEnum(str, Enum):
    New = 'acknowledged'
    Queued = 'held'
    InProgress = 'inProgress'
    Pending = 'pending',
    Resolved = 'resolved'
    Closed = 'closed'
    Canceled = 'cancelled'

class LocationEnum(str, Enum):
    CustomerPremises = 'Customer Premises'
    Datacenter =  'Datacenter'
    ExtProvider = 'External Provider'
    InternationalTrunk = 'International Trunk'
    LastMile = 'Last Mile'
    NationalTrunk = 'National Trunk'
    Node = ' Node (Core)'

class AttributedEnum(str, Enum):
    CW ='C&W'
    CWHumanError = 'C&W Human Error'
    CWImplementation = 'C&W Implementation'
    CWInsidePlant = 'C&W Inside Plant'
    CWMaintenanceWindow ='C&W Maintenance Window'
    CWOutsidePlant ='C&W Outside Plant'
    Carrier = 'Carrier'
    Customer = 'Customer'
    ForceMajeure = 'Force Majeure'
    Provider = 'Provider'
    Tier1 = 'Tier 1 Support'
    Tier2 = 'Tier 2 Support'
    Tier3 = 'Tier 3 Support'

class DowntimeCodesEnum(str, Enum):
    HardTime = 'CSC001_HardTime'
    QualityAffected = 'CSC002_Quality_Affected'
    NoServiceImpacted = 'CSC003_No_Service_Impacted'

class RelatedParty(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    role: str = Field(
        default="User",  # Default value
        Literal=True,      # Ensures this field is Literalant
    )

class RelatedEntity(BaseModel):
    id: Optional[str] = Field(default="", description="Unique identifier for the related entity")
    role: str = Field(default="MonitoringTicket", Literal=True, exclude=True)
    referred_type: str = Field(default="AssetId", alias="@referredType", Literal=True, exclude=True)

class TicketBaseDTO(BaseModel):
    custom_description: Optional[bool] =  Field(
        default=False
    )
    description: Optional[str] = description_templates['TemplateNetworking']
    ticketType: str = Field(
        default = "incident-case",
        Literal = True,
        exclude = True
    )
    externalId: str = Field(
        default = "0124X000001hi9aQAA-0124X000001hi9WQAQ",
        Literal = True,
        exclude = True
    )
    name: Optional[str] = 'Sede'
    priority: Optional[PriorityEnum] = PriorityEnum.Medium
    severity: Optional[PriorityEnum] = PriorityEnum.Medium
    status: Optional[StatusEnum] = StatusEnum.New
    channel: dict = Field(
        default={"id": "", "name": "Toolmaster", "@type": ""},
        Literal=True,  # This ensures the value is Literalant
        exclude=True # Exclude from the request
    )
    note: list = Field(
        default=[{"text": "", "@type": "Note" }],
        Literal=True,
        exclude=True
    )
    relatedParty: Optional[List[RelatedParty]] = None
    # Define relatedEntity with a default value
    relatedEntity: Optional[List[RelatedEntity]] = Field(
        default=[
            {"id": "sf", "role": "MonitoringTicket", "@referredType": "InstalledSoftware"}
        ]
    )
    # Owner id qa '00505000005JfIEAA0' 
    #  owner id cscops en producción 00G4X000003ZBcbUAG
    troubleTicketCharacteristic: List[Dict[str, Any]] = Field(
        default_factory=trouble_ticket_characteristics_default
    )
    type_: str = Field(default="TroubleTicket", Literal=True, alias="@type")
    description_type: Optional[str] = 'TemplateNetworking'  
    related_cids: Optional[List[str]] = []
    business_id: Optional[str] = 'CO' 
    branch: Optional[str] = ""
    major: Optional[bool] = False
    city: Optional[str] = ''
    worklog: Optional[str] = ''
    related_party_id: Optional[str] = '' # sf_account_id
    sf_contact_id: Optional[str] = ''
    sf_asset_ids: Optional[List[str]] = []
    affected_date: Optional[str] = ''
    owner_id: Optional[str] = ''
    alarm_info: Optional[str] = ''
    summary: Optional[str] = ''
    attach_image: Optional[bool] = False
    attachment_content: Optional[str] = ''
    incident_id: Optional[str] = ""
    sf_incident_id: Optional[str] = ""
     

    class Config:
        extra = "forbid" 
        populate_by_name = True  # Allows '@referredType' to be used and @type to be used as alias
        frozen = False

    def bool_to_str(self, field_value: bool) -> str:
        return str(field_value).lower()


class TicketUpdateDTO(BaseModel):
    location: Optional[LocationEnum] = LocationEnum.Datacenter
    status: Optional[StatusEnum] = StatusEnum.InProgress
    worklog: str
    sf_incident_id: Optional[str] = ""
    cause: Optional[str] = ""
    symptom: Optional[str] = ""
    solution: Optional[str] = "" # status change reason
    related_assets: Optional[List[str]] = []
    related_cases_ids: Optional[List[str]] = Field(default_factory=list)
    asset_ids: Optional[List[str]] = Field(default_factory=list)
    trouble_ticket_characteristic: Optional[List[Dict[str, Any]]] = [] 
    business_id: Optional[str] = 'CO'
    major : Optional[Literal['true','false']] = 'false'
    resolved : Optional[Literal['Customer', 'C&W', 'Supplier', 'CSC']] = 'CSC'
    attributed : Optional[AttributedEnum] = AttributedEnum.Customer
    downtime_codes : Optional[DowntimeCodesEnum] = DowntimeCodesEnum.HardTime
    start_downtime: Optional[str] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "+0000"
    end_downtime : Optional[str] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "+0000"
    failure_class: Optional[str] = ""
    failure_code : Optional[str] = ""
    resolved_by_id: Optional[str] = "00534000009LPwmAAG" # salesforce id de un usuario(agente) o un grupo (cola) de app person

    class Config:
        extra = "forbid" 
        populate_by_name = True  # Allows '@referredType' to be used and @type to be used as alias
        frozen = False


class TicketCloseDTO(BaseModel):
    incident_id: Optional[str] = ""
    location: Optional[LocationEnum] = LocationEnum.Datacenter #
    worklog: Optional[str] = ""
    summary: Optional[str] = "Ticket closed"
    sf_incident_id: Optional[str] = ""
    cause: Optional[str] = "" #
    symptom: Optional[str] = "" #
    solution: Optional[str] = "" # status change reason #
    resolved : Optional[Literal['Customer', 'C&W', 'Supplier', 'CSC']] = 'CSC'
    attributed : Optional[AttributedEnum] = AttributedEnum.Customer #
    start_downtime: str = Field(default_factory=colombia_now_iso)
    end_downtime  : str = Field(default_factory=colombia_now_iso)
    failure_class: Optional[str] = "aDA4X0000019xurWAA" # Electric fault failure class -> CSC011 Customer
    failure_code : Optional[str] = "aD94X000000k9jDSAQ" # Electric fault failure code -> FA025 Power Issue
    owner_id: Optional[str] = ""
    downtime_codes : Optional[DowntimeCodesEnum] = DowntimeCodesEnum.NoServiceImpacted
    attachment_content: Optional[str] = ''
    
    class Config:
        extra = "forbid" 
        populate_by_name = True  # Allows '@referredType' to be used and @type to be used as alias
        frozen = False
