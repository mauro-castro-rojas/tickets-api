Salesforce Ticket API that is used to create, update, and close tickets based on network monitoring alarms. 

- Developer: **mcastro** 
- Maintained by: **CSC Toolmaster** team.
- Running base url: http://172.18.93.253:8051/api/tickets


---

# Salesforce Ticket API Documentation

This API exposes endpoints to manage tickets in Salesforce for monitoring alarms. It allows you to:

- **Retrieve incidents** by circuit or Salesforce incident identifiers.
- **Create a new ticket** (incident) in Salesforce.
- **Update an existing ticket** with new details.
- **Close a ticket** once the issue is resolved.

All endpoints use JSON for request and response payloads. Error responses include a message and an error type.

---

## Base URL

_All endpoints are relative to the base API URL._

---

## Endpoints Overview

1. [Get Incidents by Circuit ID](#1-get-incidents-by-circuit-id)
2. [Get Incident Details by Salesforce ID](#2-get-incident-details-by-salesforce-id)
3. [Create Ticket](#3-create-ticket)
4. [Update Ticket](#4-update-ticket)
5. [Close Ticket](#5-close-ticket)

---

## 1. Get Incidents by Circuit ID

- **Method:** GET  
- **URL:** `/incidents_by_cid/{bussinesId}/{circuit_id}`

### URL Parameters

| Parameter    | Type   | Description                         |
| ------------ | ------ | ----------------------------------- |
| bussinesId   | string | The business identifier (e.g., "CO"). |
| circuit_id   | string | The circuit identifier.             |

### Response

A JSON object with incident data related to the given circuit.

#### Example

```http
GET /incidents_by_cid/CO/123456
```

_Response (example):_

```json
{
  "incident_id": "INC7890",
  "status": "acknowledged",
  "priority": "High",
  "description": "Network device alarm triggered...",
  "created_at": "2025-02-07T08:30:00.000+0000"
}
```

---

## 2. Get Incident Details by Salesforce ID

- **Method:** GET  
- **URL:** `/incident_details/{bussinesId}/{incident_id}`

### URL Parameters

| Parameter    | Type   | Description                         |
| ------------ | ------ | ----------------------------------- |
| bussinesId   | string | The business identifier.            |
| incident_id  | string | The Salesforce incident identifier. |

### Response

A JSON object with detailed information about the incident.

#### Example

```http
GET /incident_details/CO/INC7890
```

_Response (example):_

```json
{
  "incident_id": "INC7890",
  "status": "acknowledged",
  "priority": "High",
  "name": "Main Office",
  "description": "Detailed description of the incident...",
  "related_assets": ["Asset123", "Asset456"],
  "updated_at": "2025-02-07T09:00:00.000+0000"
}
```

---
Below is an updated **create ticket** endpoint for FastAPI that **enforces** the requirement to include at least one CID in the `related_cids` list. Additionally, documentation for the **mailer endpoint** is provided, detailing how to send emails related to tickets.

---

## 3. Create Ticket

> **Important**: Although `related_cids` is declared optional in the `TicketBaseDTO`, it is **business-mandatory** for integration with the downstream ESB/API. If `related_cids` is empty or missing, the ESB call fails. Therefore, **at least one CID** must be provided in the `related_cids` list.

- **Method:** POST  
- **URL:** `/create`

### Request Body Example

Just provide a Circuit ID to create a non massive incident (major: false by default).
The major field in the request is used to denote a massive incident if true.

```json
{
  "related_cids": ["CID12345"]
}
```

### Typical curl example

```bash
curl -X 'POST' \
  'http://172.18.93.253:8051/api/tickets/create' \
  -H 'accept: application/json' \
  -H "csc_token: $api_token"  \
  -H 'Content-Type: application/json' \
  -d '{
  "related_cids": ["2041471.CO"]
}'
```
### Custom description Request Body Example

To create an incident with a custom description (by default a template is used as the value of the description field), send the request as follows

```json
{
  "related_cids": ["2041471.CO"],
  "custom_description": "true",
  "description": "custom description"
}
```

### Response Example

The message field in the response contains the original response from the ESB API, so it must be json parsed befor using it.

```json
{
  "status_code": 201, 
  "message": '{\n  "id": "INC-000001082",\n  
                    "externalId": "0nyPl00000011IDIAY",\n  
                    "troubleTicketCharacteristic": 
                    [\n    {\n      "name": "isMajorIncident",\n      "value": false\n    }\n  ]\n}', 
  "id": "INC-000001082", 
  "exernalId": "0nyPl00000011IDIAY"
}

```

If the `related_cids` field is omitted or empty, the API will return a **400** status code with an error message:

```json
{
  "detail": "At least one CID must be provided in related_cids."
}
```


## Code Snippet

```python
@tickets_router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED
)
async def create(
    dto: TicketBaseDTO,
    use_case: ITicketUseCase = Depends(tickets_use_case),
):
    
    # Enforce related_cids business rule
    if not dto.related_cids or len(dto.related_cids) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one CID must be provided in related_cids."
        )

    try:
        data = use_case.create_ticket(dto)
        return data
    except AppError as app_err:
        log(f"AppError caught at the route level: {app_err}")
        return JSONResponse(
            status_code=app_err.error_type.value,
            content={"message": app_err.message, "error_type": app_err.error_type.name}
        )
```

---

## 4. Update Ticket

- **Method:** PATCH  
- **URL:** `/update`

### Purpose

Updates an existing Salesforce ticket with new information such as worklog updates, cause, solution details, and more.

### Request Body

The payload must follow the **TicketUpdateDTO** schema.

> **Important:**  
> - **worklog** is a **required** field and must contain the update details.
> - Other fields are optional with defaults.

### Fields

| Field                           | Type                                           | Default / Requirement                                                                                                         |
| ------------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **location**                    | *LocationEnum* (Customer Premises, Datacenter, External Provider, International Trunk, Last Mile, National Trunk, Node (Core)) | Default: `Datacenter`                                                                                                         |
| **status**                      | *StatusEnum*                                   | Default: `inProgress`                                                                                                         |
| **worklog**                     | string                                         | **Required.** Text describing the update.                                                                                    |
| **sf_incident_id**              | string                                         | Optional. Salesforce incident id.                                                                                             |
| **cause**                       | string                                         | Optional. Explanation of the cause.                                                                                           |
| **symptom**                     | string                                         | Optional. Observed symptoms.                                                                                                  |
| **solution**                    | string                                         | Optional. Explanation of the solution or status change reason.                                                              |
| **related_assets**              | List of strings                                | Optional. List of asset ids related to the incident.                                                                        |
| **related_cases_ids**           | List of strings                                | Optional. List of related case ids.                                                                                           |
| **asset_ids**                   | List of strings                                | Optional. List of asset ids.                                                                                                  |
| **trouble_ticket_characteristic** | List of key/value objects                     | Optional. Additional ticket characteristics.                                                                                |
| **business_id**                 | string                                         | Default: `"CO"`                                                                                                               |
| **major**                       | Literal ("true" or "false")                    | Default: `"false"`                                                                                                            |
| **resolved**                    | Literal ("Customer", "C&W", "Supplier", "CSC") | Default: `"CSC"`                                                                                                              |
| **attributed**                  | *AttributedEnum* (e.g., Customer, C&W, Carrier, etc.) | Default: `Customer`                                                                                                           |
| **downtime_codes**              | *DowntimeCodesEnum* (HardTime, QualityAffected, NoServiceImpacted) | Default: `HardTime`                                                                                                           |
| **start_downtime**              | string                                         | Optional. Timestamp in ISO8601 format with timezone (e.g., `"2025-02-07T09:00:00.000+0000"`).                                  |
| **end_downtime**                | string                                         | Optional. Timestamp in ISO8601 format.                                                                                        |
| **failure_class**               | string                                         | Optional. Code for the failure class.                                                                                         |
| **failure_code**                | string                                         | Optional. Code for the failure reason.                                                                                        |
| **resolved_by_id**              | string                                         | Default: `"00534000009LPwmAAG"` (Salesforce user or group id)                                                                 |

### Example Request

```json
{
  "location": "Datacenter",
  "status": "inProgress",
  "worklog": "Updating ticket with new incident details.",
  "sf_incident_id": "INC123456",
  "cause": "Equipment failure",
  "symptom": "Network outage in region",
  "solution": "Replaced faulty hardware in the backup unit.",
  "related_assets": ["Asset1", "Asset2"],
  "trouble_ticket_characteristic": [
    {"name": "AdditionalInfo", "value": "Updated parameters"}
  ],
  "business_id": "CO",
  "major": "false",
  "resolved": "CSC",
  "attributed": "Customer",
  "downtime_codes": "CSC001_HardTime",
  "start_downtime": "2025-02-07T09:00:00.000+0000",
  "end_downtime": "2025-02-07T09:30:00.000+0000",
  "failure_class": "FaultClass123",
  "failure_code": "FaultCode123",
  "resolved_by_id": "00534000009LPwmAAG"
}
```

### Response

On success, a JSON object with the updated ticket details is returned.

---

## 5. Close Ticket

- **Method:** PATCH  
- **URL:** `/close`

### Purpose

Closes an existing ticket in Salesforce once the issue has been resolved.

### Request Body

The payload must follow the **TicketCloseDTO** schema.

### Fields

| Field               | Type                                           | Default / Requirement                                                                                              |
| ------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **incident_id**     | string                                         | Optional. The internal incident identifier.                                                                      |
| **location**        | *LocationEnum*                                 | Default: `Datacenter`                                                                                              |
| **worklog**         | string                                         | Optional. Closure worklog notes.                                                                                   |
| **sf_incident_id**  | string                                         | Optional. Salesforce incident id.                                                                                  |
| **cause**           | string                                         | Optional. Reason for closure.                                                                                      |
| **symptom**         | string                                         | Optional. Symptoms noted at closure.                                                                               |
| **solution**        | string                                         | Optional. Explanation of the solution implemented.                                                               |
| **resolved**        | Literal ("Customer", "C&W", "Supplier", "CSC") | Default: `"CSC"`                                                                                                   |
| **attributed**      | *AttributedEnum*                               | Default: `Customer`                                                                                                |
| **start_downtime**  | string                                         | Default: Current timestamp formatted to Colombian time (e.g., `"2025-02-07T09:00:00.000-0500"`).                   |
| **end_downtime**    | string                                         | Default: Same as `start_downtime` if not overridden.                                                               |
| **failure_class**   | string                                         | Default: `"aDA4X0000019xurWAA"` (Electric fault failure class)                                                     |
| **failure_code**    | string                                         | Default: `"aD94X000000k9jDSAQ"` (Electric fault failure code)                                                       |
| **owner_id**        | string                                         | Optional. Override the default owner if necessary.                                                               |
| **downtime_codes**  | *DowntimeCodesEnum*                            | Default: `NoServiceImpacted`                                                                                       |

### Example Request

```json
{
  "incident_id": "INC123456",
  "location": "Datacenter",
  "worklog": "Ticket closed after confirmation of resolution.",
  "sf_incident_id": "INC123456",
  "cause": "Resolved issue after maintenance",
  "symptom": "Service restored",
  "solution": "Faulty component replaced",
  "resolved": "CSC",
  "attributed": "Customer",
  "start_downtime": "2025-02-07T09:00:00.000-0500",
  "end_downtime": "2025-02-07T09:30:00.000-0500",
  "failure_class": "aDA4X0000019xurWAA",
  "failure_code": "aD94X000000k9jDSAQ",
  "owner_id": "00G4X000003ZBcbUAG",
  "downtime_codes": "CSC003_No_Service_Impacted"
}
```

### Response

On success, a JSON object with the closed ticket details is returned.

---

## Error Handling

If an error occurs during any operation, the API will respond with a JSON error message in the following format:

```json
{
  "message": "Description of the error.",
  "error_type": "ErrorTypeName"
}
```

The HTTP status code will correspond to the error type as defined in the application.

---

## Additional Notes

- **Excluded Fields:**  
  Some fields (such as `ticketType`, `externalId`, `channel`, `note`, and `@type`) are automatically set by the API and are excluded from the input payload.

- **Timestamps:**  
  Ensure that any timestamps provided (for example, `start_downtime` and `end_downtime`) follow the ISO8601 format with the appropriate timezone offset (e.g., `"2025-02-07T09:00:00.000+0000"`).

- **Enums:**  
  Use the provided enumerated values for fields such as `priority`, `status`, `location`, `attributed`, and `downtime_codes` to avoid validation errors.

---

---

# Mailer Endpoint

This endpoint is used to send emails related to tickets. It accepts minimal data such as the recipient email address, ticket ID, and context (CID, branch, country, etc.) to construct and send the email.

## Code Snippet

```python
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.domain.ports.input_port.mailer_service import IMailerUseCase
from app.container_instance.instances import mailer_use_case
from app.infrastructure.dto.mail_schema import MailBaseDTO
from app.utils.errors import AppError
from app.utils.logger import log

mailer_router = APIRouter(tags=["/"])

@mailer_router.post(
    path="/send_email",
    status_code=status.HTTP_200_OK,
)
def send(
    dto: MailBaseDTO,
    use_case: IMailerUseCase = Depends(mailer_use_case),
):
    """
    Sends an email notification about the specified ticket.

    **Request Body** (`MailBaseDTO`):
    - **to_mails** (str): Recipient email(s). (Comma-separated if multiple)
    - **ticket_id** (str): The ticket/incidence identifier.
    - **cid_mgt** (str): The CID or circuit ID for which we are sending mail.
    - **branch** (str): Name of the branch or location.
    - **country** (str): Country code or name.
    - **customer** (str): Name or reference for the customer.
    - **is_major** (bool, default `False`): Indicates if the incident is marked as major.

    **Response**:
    - On success, returns a JSON object confirming that the email was sent.
    - On error, returns a JSON with `"message"` and `"error_type"`.

    **Example**:
    ```json
    {
      "to_mails": "support@example.com",
      "ticket_id": "INC0012345",
      "cid_mgt": "CID12345",
      "branch": "North",
      "country": "CO",
      "customer": "ACME Corp",
      "is_major": true
    }
    ```
    """
    try:
        data = use_case.send_email(dto)
        return data
    except AppError as app_err:
        log(f"AppError caught at the route level: {app_err}")
        return JSONResponse(
            status_code=app_err.error_type.value,
            content={"message": app_err.message, "error_type": app_err.error_type.name}
        )
```

### MailBaseDTO Schema

```python
from pydantic import BaseModel

class MailBaseDTO(BaseModel):
    to_mails: str
    ticket_id: str
    cid_mgt: str
    branch: str
    country: str
    customer: str
    is_major: bool = False

    class Config:
        extra = "forbid"
        frozen = False
```

### Example Request

```json
{
  "to_mails": "admin@example.com,support@example.com",
  "ticket_id": "INC0012345",
  "cid_mgt": "CID9876",
  "branch": "East",
  "country": "CO",
  "customer": "XYZ Corp",
  "is_major": false
}
```

### Example Response

```json
{
  "status": "Email sent successfully",
  "details": {
    "to_mails": "admin@example.com,support@example.com",
    "ticket_id": "INC0012345"
  }
}
```

If any required field is missing or any other error occurs, the API will return a suitable error response, for example:

```json
{
  "message": "Error sending email: Invalid address",
  "error_type": "INVALID_EMAIL"
}
```
---

This documentation should serve as a quick guide for integrating with the Salesforce Ticket API. For further details or support, please contact the **CSC Toolmaster** team.