
from typing import Type, List, Dict, Any
from app.infrastructure.dto.ticket_schema import TicketBaseDTO
from app.utils.variable_types import ENTITY_MODEL
from app.utils.logger import log
import requests
import json
import uuid
from urllib3.exceptions import InsecureRequestWarning
from app.utils.errors import DatabaseError, ErrorType, AppError

from app.conf.config import get_app_settings
app_settings = get_app_settings()

class EsbRepository(requests.Session):
    def __init__(self) -> None:
        super().__init__()
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        
        self.base_url = app_settings.esb_url
        self.id = app_settings.esb_id
        self.secret = app_settings.esb_secret.get_secret_value()
        self.environment = app_settings.esb_env
        #log(f"App settings: {app_settings}")

        self.api_request_timeout = 120
        self.verify = False
        self.headers.update( {
            "client_id" : f"{self.id}",
            "client_secret" : f"{self.secret}",
            "X-Correlation-ID" : f'{self.generate_uuid()}:{self.environment}',
            'Content-Type': "application/json"
            })
    
    def generate_uuid(self):
        generated_uuid = str(uuid.uuid4())
        return generated_uuid
    
    def create_payload_to_open(self, dto: TicketBaseDTO):
        ticket_template = {
            "description": dto.description,
            "ticketType": "incident-case",
            "externalId": "0124X000001hi9aQAA-0124X000001hi9WQAQ",#fixed value recordtype for inc-case
            "name": dto.name,
            "priority": dto.priority.value,
            "severity": dto.severity.value, # impact
            "status": dto.status.value,
            "channel": dto.channel,
            "relatedParty": [{"id": dto.related_party_id,"name": dto.sf_contact_id,"role": "User"}], # id: salesforce account ids# name: sf_contact_id
            "relatedEntity": [{"id": "sf", "role": "MonitoringTicket","@referredType": "InstalledSoftware"}],
            "troubleTicketCharacteristic":  dto.troubleTicketCharacteristic,
            "TroubleTicketRelationships": [],
            "@type": "TroubleTicket",
        }
    
        asset_ids = dto.sf_asset_ids
        for asset_id in asset_ids:
            ticket_template["relatedEntity"].append({
                "id": asset_id,
                "role": "MonitoringTicket",
                "@referredType": "AssetId"
        })
        

        ticket_template["relatedParty"] = dto.relatedParty 
        ticket_template['troubleTicketCharacteristic'] = [
            item for item in ticket_template['troubleTicketCharacteristic'] if item['value']
        ]

        payload = json.dumps(ticket_template, ensure_ascii=False)
        # exclude = {"description"}
        # exclude = {}
        # log(f"payload to create: ")
        # [log(f"{k}, {v}") for k, v in ticket_template.items() if k not in exclude]
        
        return payload
    
    
    
    def create_payload_to_update(self,**kwargs):
        # "note id: recordtypeid of type for worklog
        # need to add isMajorIncident : false in trouble ticket characteristic , other caracteristics are optional
        ticket_template = {
            "status": kwargs.get("status", ""),
            "note": [{"id": "0124X000001WLDcQAO", "text": kwargs.get("worklog", "-")+"-"+"CLIENTNOTE", "@type": "Note" }],
            "relatedEntity": [{"id": "sf", "role": "MonitoringTicket","@referredType": "InstalledSoftware"} ],
            "troubleTicketCharacteristic":  [{"name": "caseReason","value": "Service Down"},],
            "TroubleTicketRelationships": kwargs.get("trouble_ticket_relationships", []),#need to put the related cases ids
            "@type": "TroubleTicket" 
        }
        
        asset_ids = kwargs.get("asset_ids", [])
    
        for asset_id in asset_ids:
            ticket_template["relatedEntity"].append({"id": asset_id,"role": "MonitoringTicket","@referredType": "AssetId"})
            
        related_cases_ids = kwargs.get("related_cases_ids", [])
        for case_id in related_cases_ids:
            ticket_template["TroubleTicketRelationships"].append({"id": case_id, "relationshipType": "Case", "@type": "TroubleTicketRelationship"})

        additional_characteristics = kwargs.get("trouble_ticket_characteristic", [])
        ticket_template["troubleTicketCharacteristic"].extend(additional_characteristics)

        #ticket_template = self.clean_nested_dicts(ticket_template)
        #ticket_template = self.clean_dict(ticket_template)

        ticket_template['troubleTicketCharacteristic'] = [
            item for item in ticket_template['troubleTicketCharacteristic'] if item['value']
        ]
        
        log("Payload to update in esb repo")
        log(ticket_template)
        
        # for field, value in ticket_template.items():
        #     log(f"{field}: {value}")
        
        payload = json.dumps(ticket_template)
        return payload

    
    def create_ticket(self, bussinesId, payload):
        url = self.base_url + f"/{bussinesId}/troubleTicket"
        headers = self.headers
        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 400:
            raise AppError(error_type=ErrorType.BAD_REQUEST,message=response.text)
        
        # log(f"Create Response at the esb repo level, Status code: {response.status_code}, Response message: {response.text}")
        return {
            "status_code": response.status_code,
            "message": response.text,
        }   

    def update_ticket(self, bussinesId,externalId, payload):
        url = self.base_url + f"/{bussinesId}/troubleTicket/{externalId}"
        headers = self.headers
        response = requests.request("PATCH", url, headers=headers, data=payload)
        # log(f"payload at update step: {payload}")
        # log(f"Update Response at the esb repo level, Status code: {response.status_code}, Response message: {response.text}")

        if response.status_code != 200:
            raise AppError(error_type=ErrorType.BAD_REQUEST,message=response.text)
        
        return {
            "status_code": response.status_code,
            "message": response.text,
        }  


    def close_ticket(self, bussinesId,externalId, payload):
        url = self.base_url + f"/{bussinesId}/troubleTicket/{externalId}"
        headers = self.headers

        response = requests.request("PATCH", url, headers=headers, data=payload)
        log(f"response at close ticket method in esb repo: {response}")

        if response.status_code == 400:
            raise AppError(error_type=ErrorType.BAD_REQUEST,message=response.text)
        
        log(f"Response at the esb repo level, Status code: {response.status_code}, Response message: {response.text}")
        return {
            "status_code": response.status_code,
            "message": response.text,
        }    
        
    
    def get_incident_by_circuit_id(self, bussinesId, circuit_id):
        url = self.base_url + f"/{bussinesId}/troubleTicket?@type=ToolMasterTicket&@baseType=TroubleTicket&relatedEntity.name=Toolmaster&relatedEntity.id={circuit_id}&relatedEntity.role=Service"
        headers = self.headers
        #log(f"url: {url}")
        response = requests.request("GET", url, headers=headers)
        return response.text

    def get_incident_details_by_sf_id(self, bussinesId, sf_incident_id):
        url = self.base_url + f"/{bussinesId}/troubleTicket/{sf_incident_id}?@type=ToolMasterTicket&@baseType=TroubleTicket"
        headers = self.headers
        response = requests.request("GET", url, headers=headers)

        data = response.json()
        log("incident details:")
        # Ensure the data is a dictionary
        if isinstance(data, dict):
            log(data)
        else:
            log('The response JSON is not a dictionary.')
       
        
        return response.text
    
    def clean_dict(self, d):
                """ Remove keys with empty or default values from a dictionary."""
                return {k: v for k, v in d.items() if v not in ["", [], {}, None]}
    
    def clean_nested_dicts(self, template):
            if "note" in template:
                template["note"] = [self.clean_dict(note) for note in template["note"] if note]
            if "relatedParty" in template:
                template["relatedParty"] = [self.clean_dict(party) for party in template["relatedParty"] if party]
            if "relatedEntity" in template:
                template["relatedEntity"] = [self.clean_dict(entity) for entity in template["relatedEntity"] if entity]
            if "TroubleTicketRelationships" in template:
                template["TroubleTicketRelationships"] = [self.clean_dict(entity) for entity in template["TroubleTicketRelationships"] if entity]
            if "troubleTicketCharacteristic" in template:
                log("cleaning troublet ticket characteristic before:")
                log(template["troubleTicketCharacteristic"])
                template["troubleTicketCharacteristic"] = [self.clean_dict(characteristic) for characteristic in template["troubleTicketCharacteristic"] if characteristic]
                log("cleaning troublet ticket characteristic after cleaning:")
                log(template["troubleTicketCharacteristic"])
            return template
        

    def delete(self, id_: int, model: Type[ENTITY_MODEL]):
        pass

    def get_all(self, model: Type[ENTITY_MODEL] = None):
        pass

    def get_all_by_fields(self, filters: Dict, model: Type[ENTITY_MODEL] = None):
        pass

    def get_all_by_fields_contains(self, filters: Dict, model: Type[ENTITY_MODEL] = None):
        pass

    def get_all_by_list_ids(self, ids: List[int], model: Type[ENTITY_MODEL] = None):
        pass

    def get_by_id(self, id_: int, model: Type[ENTITY_MODEL] = None):
        pass

    def get_by_unique_field(self, field_name: str, value: Any, model: Type[ENTITY_MODEL] = None):
        pass

    def save(self, model: ENTITY_MODEL):
        pass

    def update(self, id_: int, model: ENTITY_MODEL):
        pass

