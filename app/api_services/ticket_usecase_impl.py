from typing import Any, Dict, List, Type
from app.domain.ports.out_port.IToolmasterRepository import IToolmasterRepository
from app.domain.ports.out_port.IEsbRepository import IEsbRepository
from app.utils.logger import log
from app.domain.ports.input_port.ticket_service import ITicketUseCase
import json
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from app.utils.errors import ErrorType, AppError
from app.infrastructure.dto.ticket_schema import TicketBaseDTO, TicketUpdateDTO, RelatedParty, TicketCloseDTO
from app.domain.entities.app_models import AppAccounts, AppAssets, AppCities, AppContact, AppIncident
from app.domain.entities.net_inventory_devices import NetInventoryDevices
from app.utils.constants import description_templates, worklog_template
from app.utils.variable_types import ENTITY_MODEL

class TicketUseCaseImpl(ITicketUseCase):
    def __init__( self, 
                  toolmaster_repository: IToolmasterRepository, 
                  esb_repository: IEsbRepository):
        self.toolmaster_repository = toolmaster_repository
        self.esb_repository = esb_repository
        super().__init__()
    
    def set_logging_headers(self, process: str):
        bogota_tz = ZoneInfo("America/Bogota")
        current_time = datetime.now(bogota_tz)
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        chr="-"
        log(chr*100)
        log(f"Ticket {process} process at: {formatted_time}")
        
    def create_ticket(self, dto: TicketBaseDTO):
        self.set_logging_headers('creation')
        self.dto = dto
        # stored in self.app_assets, AppAssets objects
        self.get_toolmaster_app_assets() 

        if not dto.custom_description:
            self.process_description()

        # Related Entity, array of sf_asset_ids ex [01ds3323 , 1313432fdf2, etc] stored in self.dto.sf_asset_ids
        self.get_sf_asset_ids() 
        self.set_related_party()
        
        if self.dto.branch != '': 
            self.dto.name = self.dto.branch # Subject

        self.set_major()
        self.set_affected_date()
        self.set_owner_id()

        if dto.worklog == '':
            # self.dto.worklog = worklog_template.format(alarm_info=self.dto.alarm_info)
            self.dto.worklog = self.dto.alarm_info
        
        esb_payload = self.esb_repository.create_payload_to_open(self.dto)

        log(f"esb_payload: {esb_payload}")
        response = self.esb_repository.create_ticket('CO', esb_payload)

        if response['status_code'] == 201:
            sf_incident_id = json.loads(response["message"]).get("externalId")
            worklog_response = self.worklog_update(
                sf_incident_id, 
                self.dto.bool_to_str(self.dto.major), 
                self.dto.worklog, self.dto.summary, 
                self.dto.attach_image, 
                self.dto.attachment_content
            )

            if worklog_response['status_code'] == 200:
                inc_id = json.loads(response['message'])['id']
                external_id = json.loads(response['message'])['externalId']
                response['id'] = inc_id
                response['exernalId'] = external_id
                log("Response: ")
                log(response)
            else:
                log("Failed to update worlog.")
                log(worklog_response)
            return response
        else:
            return AppError(error_type=response["status_code"], message=response["message"])

    def set_related_party(self):
        if self.dto.relatedParty:
            related_party_list = [party.model_dump() for party in self.dto.relatedParty]
            self.dto.relatedParty = related_party_list
        else:
            self.get_account_ids() # Related party, array of account ids , stored in self.account_ids
            self.get_toolmaster_app_accounts() # stored in self.app_accounts , AppAccount objects
            if self.app_accounts:
                self.dto.related_party_id = self.app_accounts[0].sf_account_id  # Related party id

            self.get_toolmaster_app_contact() # Related party name, stored in self.app_contact, AppContact objects
            if self.app_contact:
                self.dto.sf_contact_id = self.app_contact[0].sf_contact_id
            
            self.dto.relatedParty = [RelatedParty(id= self.dto.related_party_id, name=self.dto.sf_contact_id).model_dump()] #{"id": self.dto.related_party_id,"name": self.dto.sf_contact_id,"role": "User"}], # id: salesforce account ids# name: sf_contact_id

    def get_sf_asset_ids(self):
        sf_asset_ids = [asset.sf_asset_id for asset in self.app_assets]

        if not sf_asset_ids:
            raise AppError(
                error_type=ErrorType.NOT_FOUND,
                message=f"Salesforce Account id not found.",
            )
        self.dto.sf_asset_ids = sf_asset_ids
    
    def get_account_ids(self):
        account_ids = [asset.account_id for asset in self.app_assets]

        if not account_ids:
            raise AppError(
                error_type=ErrorType.NOT_FOUND,
                message=f"Account id not found",
            )
        #log(f"account ids: {account_ids}")
        self.account_ids = account_ids

    def process_description(self):
        if self.dto.major:
            self.get_massive_description() 
        else:
            self.get_single_description()
    
    def get_tm_branch(self):
        # return if Branch was sent in the payload
        if self.dto.branch != "": 
            return

        if self.dto.related_cids != []:
            self.set_repository(self.toolmaster_repository)
            self.set_model(NetInventoryDevices)  
            net_inventory = super().get_all_by_list_ids(list_ids=self.dto.related_cids, 
                                                   column_to_search=self.model_to_search.cid_mgt) 
        
        if not isinstance(net_inventory, AppError):
            self.dto.branch = net_inventory[0].branch

    def get_single_description(self):
        self.get_tm_branch()
        self.dto.description = description_templates['TemplateNetworking'].format(branch=self.dto.branch)
  
    def get_massive_description(self):
        if self.dto.city != '':
            self.dto.description = description_templates['TemplateMassive'].format(city=self.dto.city)
        else:
            self.get_incident_city()
            self.dto.description = description_templates['TemplateMassive'].format(city=self.dto.city)
    
    def get_incident_city(self):
        if self.app_assets[0].city_id == None:
            return
        else:
            self.set_repository(self.toolmaster_repository)
            self.set_model(AppCities)
            city = super().get_by_id(self.app_assets[0].city_id) 
            if isinstance(city, AppError):
                self.dto.city = ''
            else:
                self.dto.city = city.name

    def set_owner_id(self):
        if self.dto.owner_id != '':
            for item in self.dto.troubleTicketCharacteristic:
                if item['name'] == 'OwnerId':
                    item['value'] = self.dto.owner_id
                    break

    def set_affected_date(self):
        if self.dto.affected_date != '':
            for item in self.dto.troubleTicketCharacteristic:
                if item['name'] == 'AffectedDate':
                    item['value'] = self.dto.affected_date
                    break
             
    def set_major(self):
        for item in self.dto.troubleTicketCharacteristic:
             if item['name'] == 'isMajorIncident':
                item['value'] = self.dto.bool_to_str(self.dto.major)
                break
    
    def get_toolmaster_app_contact(self):
        self.set_repository(self.toolmaster_repository)
        self.set_model(AppContact)

        filters = {
            'contact_type': ('Help Desk Contact', 'Technical Contact'),
            'account_id' : self.account_ids
        }
        sf_contact_id = super().get_all_by_fields(filters=filters)

        if isinstance(sf_contact_id, AppError):
            log(f"Warning, no contact id associated for the given account id.")
            sf_contact_id = ""
        self.app_contact = sf_contact_id
    
    def get_toolmaster_app_accounts(self):
        self.set_repository(self.toolmaster_repository)
        self.set_model(AppAccounts)
        if self.account_ids:
            app_accounts = super().get_all_by_list_ids(list_ids=self.account_ids, 
                                            column_to_search=self.model_to_search.account_id) 
    
            if isinstance(app_accounts, AppError):
                raise AppError(
                        error_type=ErrorType.NOT_FOUND,
                        message=f"Salesforce account id not found for account_id: {self.account_ids}",
                    )
            self.app_accounts = app_accounts
    
    def get_toolmaster_app_assets(self):
        self.set_repository(self.toolmaster_repository)
        self.set_model(AppAssets)  
        assets = super().get_all_by_list_ids(list_ids=self.dto.related_cids, 
                                          column_to_search=self.model_to_search.circuit_id) 
        
        if isinstance(assets, AppError):
            raise AppError(
                    error_type=ErrorType.NOT_FOUND,
                    message=f"Salesforce related asset not found for CIDs: {self.dto.related_cids}",
                )
        else:
            self.app_assets = list(assets)

    
    # only need to pass the new asset values,  failure class and failurecode only can be defined once 
    # fisrt need to add a worklog before close 
    def update_ticket(self, dto: TicketUpdateDTO):
        self.set_logging_headers('update')
        self.dto = dto
        # sf_incident_id is the ext id given in the response when creating a ticket
        incident_details = self.esb_repository.get_incident_details_by_id('CO',self.dto.sf_incident_id) 
        data = json.loads(incident_details)

        if not self.dto.related_cases_ids:
            for relationship in data.get("troubleTicketRelationship", []):
                if "id" in relationship:
                    self.dto.related_cases_ids.append(relationship["id"])
        
        if self.dto.owner_id == "":
            for relationship in data.get("troubleTicketRelationship", []):
                if "id" in relationship:
                    self.dto.related_cases_ids.append(relationship["id"])

        payload_to_update = self.esb_repository.create_payload_to_update(worklog=self.dto.worklog,
                status=self.dto.status.value,
                related_cases_ids=[self.dto.related_cases_ids],
                trouble_ticket_characteristic=[
                    {"name": "isMajorIncident",           "value": self.dto.major },
                    {"name": "DownTimeEndDateAndTime",    "value": self.dto.end_downtime },
                    {"name": "DownTimeStartDateAndTime",  "value": self.dto.start_downtime},
                    {"name": "FailureClass",              "value": self.dto.failure_class},
                    {"name": "FailureCode",               "value": self.dto.failure_code},
                    {"name": "ResolvedById",              "value": self.dto.resolved_by_id},
                    {"name": "cause",                     "value": self.dto.cause},
                    {"name": "Symptom",                   "value": self.dto.symptom},
                    {"name": "statusChangeReason",        "value": self.dto.solution},
                    {"name": "FailureLocation",           "value": self.dto.location.value},
                    {"name": "Attributed",                "value": self.dto.attributed.value},
                    {"name": "ResolvedBy",                "value": self.dto.resolved}
                ])
        
        response = self.esb_repository.update_ticket('CO',self.dto.sf_incident_id,payload_to_update) 
        log(f"response at the use case level: {response}")

        # if response['status_code'] == 200:
        #     return response
        # else:
        #     return AppError(error_type=response["status_code"], message=response["message"])

    def worklog_update(self, sf_incident_id: str, major: str, worklog: str, summary: str, attach_image: bool, attachment_content: str ):
        mimeType = False
        content = ''
        note_text = ''

        if summary:
            note_text = summary
        else:
            note_text = worklog_template
        
        if attach_image:
            mimeType = "image/png"
            if attachment_content:
                content = f"<br><hr><img src='data:image/png;base64,{attachment_content}' alt='Base64 Image' />"
            else:
                
                content = "<img src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADEAAAAYCAYAAABTPxXiAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAUzSURBVFhHzZhJbFdVFMZPS6EF2lKmDiKoBTrQ2mKZWqpUDBZFwAlBBcHEhYgJRhcmLowLpwRjYmJMNMZEcENMNCRGjUhiXOjClYobYxyCUaMGZ+IUPX5f7zu+8+7/vpZGFyy+8Pq/99x3fvee4T6kp1502cyg/lmigy2i6xaKDp8l2tMg2lwjWlclOkVEp0Iz8dyQqR6aAXG8FpqWzTHVQLSryiQl4li1VEHp8XJVQdUqBvAvRCsgFuUQ8wFRC4MYggB8LkBAHoCiY+MBUAEiKDWeFgESEMsngOBO03ECGMR0yCBiANpMBmKieUU5CIZTTwLi6nbR5y4SPbFN9LebRPXmoD92i361Q/TwOtGFdQHCTqEdazy+RvQz2HCe2dD+U/x2/wWYO6XSITo/rVp02zmib14u+v2Non9nttSPO0Xfu1J0x3neLobIQJY3iY7gBF7YUHQipW+vD+FnJ3FffxE2peNwZG6tdyRoaL7oR9ekbbyeGIxtYwhozRzRt69ILxCLEH0ZxE7s0K8TAFApiC0oIj9hp1PzY5VC9GYA/PfwSPEY/9oj+hpOZXBuOG7GO0Potg7Ro5fCpjFAHBstvuydzbCZl+fFYuTWXT2iL64vQvTNFv1ie9H2S4Tq/u58Xg3euwLvf3JI9IGB3DYogthzrugvu/LF/kQ4HYDRPMQwE5qJRwgms4kAbXjZB9hhszuFNTYvCM5TZcnK349ckttR72OdBTPS8yvlcsIgXsIu+QXfuEy0C3kyGxB03iBYUglgpbUNJ+MheJLctVrs4HgVZwC7e/KG3O4HJPMIelRqbloRxHok1onr8gUZ33fi+DsB0ZSAiHvDkWgDCPLuVtENbcEu5cQ9fUWbowjJsrmVcgAUT2ELXvad25WT2JVrEV5LcbSEsKZFCIaQVSTr0gOJ2DZ9js25vSvEtnfkqbXFeY+t/o994tbF2H2XDx+jpo8irpdOF52Fl6cg7BSsSzMU6LB3zIt1fgkKgTlxbGNxfB9Ai06ejhzELWhsp1yZ+xrlcysa3hJANALCOq9B2CkYCH8n6JypoveiX7DCeAdNBGnBmnTgVVQ3P/ZgReU5HTmITdhFn2SsMHuxM+1I2oYIggBjEHim7NJn5ZTi81Wo/3EDY67c3RscYM33Y6xUkw8nlxMr0bSOIxH9oi+jPxCiPoKwExg7hew3D8B5FJ+bcDKvRz2EvYJO7EYIs4zb79zEVegtlc6WyecEKlA39AzKon8ZT4O54iHorA8jqhV94pGVodQaiIk2d6Bx+XUZRnSCDTDOIY41ArzS4ZQSEKPN4WLnF/0dpfbgMMZxUnSKEItQsejYW5vQR5CohGCf+Bk5dQAwHXCOc9knNuIe9gmKhF/Tx/5DePY3BIohuB2VsT6DqUN1XI0Tev5i0YdX5LZJiC44tx95wBPwi5bpGyT/MkC0RB17PDHhe1GOzRE6+ArCNjU3peLdKQOgeAXvBgAh+nGL3YtdpoOpRbw4pxsQzYDgxS41x4sdeRfCM3ciiCBPo2fwnpay8xoXggCdKH28Wg/xe+LscNmic7zL2yI8et71GUr7OlFus3zhRe7gheGbwV/H+fwhwuPRVYBFznjnY3VgQw7h+4WnlfoWeRbrc05uUwLBj6IhlNthdHCeSiu/r2HgK04NkpkVyVclG481uZI5WTkI5gMBxiDgOCHWAqIPzy3Zpymdoc5ciOwUOhwEQ+p8nEpzCQSdN50REAylDsQrRYhBlFr+tw0/eOxbogyCf5dBmE3agf9DBlGl/wAprooJSkdlTQAAAABJRU5ErkJggg==' />"
        else:     
            mimeType = "application/text"
            if worklog:
                content = worklog
            else:
                content = "Attachment content text."
        data = {
            
            'relatedEntity': [{'id': 'sf', 'role': 'MonitoringTicket', '@referredType': 'InstalledSoftware'}], 
            'troubleTicketCharacteristic': [{'name': 'isMajorIncident', 'value': major}],
            "note": [{"id": "0124X000001WLDcQAO",
                    "text": f"{note_text}-CLIENTNOTE",  # summary
                    "@type": "Note"}],
            "attachment": [ 
                {
                    "description": "Modem Signals Snapshot",
                    "mimeType": mimeType,
                    "name": "ModemImage",
                    "content": content, # detail
                    "@type": "Attachment"
                }
                ]}

        payload = json.dumps(data)
        response = self.esb_repository.update_ticket('CO',sf_incident_id,payload)
        return response


    def close_ticket(self, dto: TicketCloseDTO):
        self.set_logging_headers('close')
        self.dto = dto
        self.get_app_incident()
        
        incident_details = self.get_incident_details_by_sf_id('CO', self.dto.sf_incident_id)
        incident_details_dict = json.loads(incident_details)

        log(f"incident details: {incident_details_dict}")
        
        major = None
        for characteristic in incident_details_dict.get("troubleTicketCharacteristic"):
            if characteristic['name'] == 'isMajorIncident':
                major = characteristic['value']
        
        if isinstance(major, bool):
            major = str(major).lower()

        trouble_ticket_characteristic=[
                    {"name": "isMajorIncident",           "value": major },
                    {"name": "DownTimeEndDateAndTime",    "value": self.dto.end_downtime },
                    {"name": "DownTimeStartDateAndTime",  "value": self.dto.start_downtime},
                    {"name": "FailureClass",              "value": self.dto.failure_class},
                    {"name": "FailureCode",               "value": self.dto.failure_code},
                    {"name": "cause",                     "value": self.dto.cause},
                    {"name": "Symptom",                   "value": self.dto.symptom},
                    {"name": "statusChangeReason",        "value": self.dto.solution},
                    {"name": "FailureLocation",           "value": self.dto.location.value},
                    {"name": "Attributed",                "value": self.dto.attributed.value}, 
                    {"name": "ResolvedBy",                "value": self.dto.resolved},
                    {"name": "DownTimeCode",              "value": self.dto.downtime_codes},
                ]
        
        # App person sf id to close tickets when the toolmaster database has no owner designated. (proc)
        # context: proactive cases where the fault doesnt reach a support level so the ticket can be closed because is assigned to proactive CSC (a group not a person)
        if self.dto.owner_id == None:
            owner = {"name": "OwnerId","value": "0054X00000F8aALQAZ"}
            trouble_ticket_characteristic.append(owner)

        self.worklog_update(
            sf_incident_id=self.dto.sf_incident_id,
            major=major,
            worklog=self.dto.worklog, 
            summary=self.dto.summary,
            attach_image=False,
            attachment_content=self.dto.attachment_content
        )

        data = {
            'status': 'resolved', 
            'relatedEntity': [{'id': 'sf', 'role': 'MonitoringTicket', '@referredType': 'InstalledSoftware'}], 
            'troubleTicketCharacteristic': trouble_ticket_characteristic
        }
        
        payload = json.dumps(data)
        log("Payload ready to close the ticket")
        log(payload)
        response = self.esb_repository.update_ticket('CO',self.dto.sf_incident_id,payload) 
        log(f"Close response at the use case level: {response}")
        if response['status_code'] == 200:
            response['message'] = 'Incident closed successfully.'
            return response
        else:
            return AppError(error_type=response["status_code"], message=response["message"])

    def get_app_incident(self):
        self.set_repository(self.toolmaster_repository)
        self.set_model(AppIncident)  
        sf_incident_id = super().get_by_unique_field(field_name='incident_number', data=self.dto.incident_id)

        if isinstance(sf_incident_id, AppError):
            raise AppError(
                    error_type=ErrorType.NOT_FOUND,
                    message=f"Salesforce incident ID not found for given incident number: {self.dto.incident_id}",
                )
        else:
            self.dto.sf_incident_id = sf_incident_id.sf_incident_id
            self.dto.owner_id = sf_incident_id.owner_id

    def get_incident_by_circuit_id(self, bussinesId, circuit_id ):
        response = self.esb_repository.get_incident_by_circuit_id(bussinesId,circuit_id)
        #log(f"Response: {response}")
        return response
    
    def get_incident_details_by_sf_id(self, bussinesId, sf_incident_id):
        self.set_logging_headers('Get sf incident details')
        response = self.esb_repository.get_incident_details_by_sf_id(bussinesId,sf_incident_id)
        #log(f"Response: {response}")
        return response

    def get_incident_details_by_id(self, bussinesId, incident_id):
        self.set_logging_headers('Get incident details')
        self.dto = TicketBaseDTO(incident_id=incident_id)
        self.get_app_incident()
        log(f"sf_incident_id: {self.dto.sf_incident_id}")
        response = self.get_incident_details_by_sf_id(self.dto.business_id, self.dto.sf_incident_id)
        log(f"Response: {response}")
        return response

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

    def get_by_unique_field(self, field_name: str, data: str, model: Type[ENTITY_MODEL] = None):
        pass

    def save(self, model: ENTITY_MODEL):
        pass

    def update(self, id_: int, model: ENTITY_MODEL):
        pass
