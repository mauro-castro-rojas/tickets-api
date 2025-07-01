from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class AssetDTO(BaseModel):
    asset_id:         Optional[int]   = None
    sf_asset_id:      Optional[str]   = None
    circuit_id:       Optional[str]   = None
    product_family:   Optional[str]   = None
    product_category: Optional[str]   = None
    product_name:     Optional[str]   = None
    status:           Optional[str]   = None
    location:         Optional[str]   = None

class ContactDTO(BaseModel):
    contact_id:     Optional[int]  = None
    sf_contact_id:  Optional[str]  = None
    name:           Optional[str]  = None
    contact_type:   Optional[str]  = None
    email:          Optional[str]  = None
    phone:          Optional[str]  = None
    account_id:     Optional[int]  = None

class WorklogDTO(BaseModel):
    worklog_id:     Optional[int]      = None
    sf_worklog_id:  Optional[str]      = None
    created_by_name: Optional[str]     = None
    type_worklog:   Optional[str]      = None
    created_at:     Optional[datetime] = None
    ticket_id:      Optional[int]      = None
    description:    Optional[str]      = None
    ticket_number:  Optional[str]      = None
    worklog_number: Optional[str]      = None


class IncidentDTO(BaseModel):
    incident_id:     Optional[int]      = None
    ticket_id:       Optional[int]      = None
    sf_incident_id:  Optional[str]      = None
    incident_number: Optional[str]      = None
    subject:         Optional[str]      = None
    priority:        Optional[str]      = None
    source_incident: Optional[str]      = None
    reported_at:     Optional[datetime] = None
    affected_at:     Optional[datetime] = None
    resolution_at:   Optional[datetime] = None
    status:          Optional[str]      = None
    created_at:      Optional[datetime] = None
    updated_at:      Optional[datetime] = None
    start_at_dw:     Optional[datetime] = None
    end_at_dw:       Optional[datetime] = None
    downtime:        Optional[float]    = None
    is_major:        Optional[bool]     = None
    symptom:         Optional[str]      = None
    cause:           Optional[str]      = None
    resolution_summary: Optional[str] = None
    description:     Optional[str]      = None
    attributed_to:   Optional[str]      = None
    reason:          Optional[str]      = None
    type_incident:   Optional[str]      = None
    stop_dw:         Optional[float]    = None
    affectation_type: Optional[str]     = None
    duration:        Optional[str]      = None
    asset:           Optional[str]      = None
    asset_location:  Optional[str]      = None
    asset_type:      Optional[str]      = None
    assets:          List[AssetDTO]     = []

class ServiceRequestDTO(BaseModel):
    sr_id:          Optional[int]      = None
    ticket_id:      Optional[int]      = None
    sf_sr_id:       Optional[str]      = None
    sr_number:      Optional[str]      = None
    subject:        Optional[str]      = None
    priority:       Optional[str]      = None
    status:         Optional[str]      = None
    sr_type:        Optional[str]      = None
    source:         Optional[str]      = None
    symptom:        Optional[str]      = None
    solution:       Optional[str]      = None
    created_at:     Optional[datetime] = None
    updated_at:     Optional[datetime] = None
    resolved_at:    Optional[datetime] = None
    closed_at:      Optional[datetime] = None
    sr_category:    Optional[str]      = None
    sr_type_actions: Optional[str]     = None
    asset:           Optional[str]     = None
    asset_location:  Optional[str]     = None
    asset_type:      Optional[str]     = None
    assets:          List[AssetDTO]    = []

class ChangeDTO(BaseModel):
    change_id:      Optional[int]      = None
    ticket_id:      Optional[int]      = None
    sf_change_id:   Optional[str]      = None
    change_number:  Optional[str]      = None
    subject:        Optional[str]      = None
    priority:       Optional[str]      = None
    status:         Optional[str]      = None
    is_deleted:     Optional[bool]     = None
    type_change:    Optional[str]      = None
    description:    Optional[str]      = None
    created_at:     Optional[datetime] = None
    updated_at:     Optional[datetime] = None
    result:         Optional[str]      = None
    type_of_action: Optional[str]      = None
    bussines_reason: Optional[str]     = None
    urgency:        Optional[str]      = None
    impact:         Optional[str]      = None
    risk_level:     Optional[str]      = None
    failure_probability: Optional[str] = None
    change_downtime: Optional[float]   = None
    start_at_activity: Optional[datetime] = None
    end_at_activity:   Optional[datetime] = None
    bussines_justification: Optional[str] = None
    service_impact: Optional[str]      = None
    evidence_delivery_at: Optional[datetime] = None
    final_review_at: Optional[datetime] = None
    cab_assesment:  Optional[str]      = None
    cab_closure:    Optional[str]      = None
    category:       Optional[str]      = None
    client_auth_decision: Optional[str] = None
    list_of_standard_changes: Optional[str] = None
    asset:           Optional[str]     = None
    asset_location:  Optional[str]     = None
    asset_type:      Optional[str]     = None
    assets:          List[AssetDTO]    = []

class CustomerDTO(BaseModel):
    account_id:     Optional[int]   = None
    sf_account_id:  Optional[str]   = None
    name:           Optional[str]   = None
    sccd_id:        Optional[str]   = None
    country:        Optional[str]   = None
    category:       Optional[str]   = None
    assets:         List[AssetDTO]  = []
    contacts:       List[ContactDTO] = []
    incidents:      List[IncidentDTO] = []
    service_requests: List[ServiceRequestDTO] = []
    changes:        List[ChangeDTO] = []
    worklogs:       List[WorklogDTO] = []

class WordReportDTO(BaseModel):
    cust:                 Optional[str]   = None
    total_incidentes:     int             = 0
    total_service_request: int            = 0
    total_cambios:        int             = 0
    incidentes:           List[IncidentDTO] = []
    service_requests:     List[ServiceRequestDTO] = []
    cambios:              List[ChangeDTO]   = []
    start_date:           Optional[datetime] = None
    end_date:             Optional[datetime] = None
    customers:            List[CustomerDTO]  = []
    language:             Optional[str]      = None
    start_day_num:        Optional[int]      = None
    end_day_num:          Optional[int]      = None
    start_month_name:     Optional[str]      = None
    end_month_name:       Optional[str]      = None
    start_year_str:       Optional[str]      = None
    end_year_str:         Optional[str]      = None
    cust_country:         Optional[str]      = None
    cust_assets:          Optional[str]      = None
    report_date:          Optional[str]      = None
