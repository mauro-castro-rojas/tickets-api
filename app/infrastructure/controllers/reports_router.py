# app/infrastructure/controllers/reports_router.py
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from unidecode import unidecode
from app.adapters.db import get_toolmaster_db_connection
from app.adapters.repositories.toolmaster_repository import ToolmasterRepository
from app.infrastructure.dto.reports_schema import (
    ChangeDTO,
    CustomerDTO,
    IncidentDTO,
    ServiceRequestDTO,
    WordReportDTO,
    WorklogDTO,
)
from app.api_services.word_report_di import word_report_use_case
from app.domain.ports.input_port.report_service import IWordReportUseCase

reports_router = APIRouter()

MONTHS_ES = [
    "ENERO",
    "FEBRERO",
    "MARZO",
    "ABRIL",
    "MAYO",
    "JUNIO",
    "JULIO",
    "AGOSTO",
    "SEPTIEMBRE",
    "OCTUBRE",
    "NOVIEMBRE",
    "DICIEMBRE",
]
MONTHS_EN = [
    "JANUARY",
    "FEBRUARY",
    "MARCH",
    "APRIL",
    "MAY",
    "JUNE",
    "JULY",
    "AUGUST",
    "SEPTEMBER",
    "OCTOBER",
    "NOVEMBER",
    "DECEMBER",
]


def _sanitize(name: str) -> str:
    return unidecode((name or "NO_NAME").upper()).replace(" ", "_")


def _build_filename(
    prefix_es: str,
    prefix_en: str,
    client_name: str,
    language: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    extension: str = "docx",
    extra_part: str | None = None,
) -> str:
    months = MONTHS_ES if language.lower() == "es" else MONTHS_EN
    prefix = prefix_es if language.lower() == "es" else prefix_en
    name = _sanitize(client_name)
    if start_date and end_date:
        same_month_year = (
            start_date.year == end_date.year and start_date.month == end_date.month
        )
        sm = months[start_date.month - 1]
        em = months[end_date.month - 1]
        date_part = (
            f"{sm}_{start_date.year}"
            if same_month_year
            else f"{sm}_{start_date.year}_{em}_{end_date.year}"
        )
    else:
        date_part = extra_part or datetime.utcnow().strftime("%Y%m%d")
    return f"{prefix}_{name}_{date_part}.{extension}"


@reports_router.post("/generate-monthly-report")
def generate_monthly_report(
    sf_account_id: str,
    start_date: datetime,
    end_date: datetime,
    language: str = "es",
    session: Session = Depends(get_toolmaster_db_connection),
    use_case: IWordReportUseCase = Depends(word_report_use_case),
):
    repo = ToolmasterRepository(session=session)
    c_dto = repo.get_customer_info(sf_account_id, start_date, end_date)
    if not c_dto:
        raise HTTPException(status_code=404, detail="No se encontró la cuenta con ese SF ID")
    dto = WordReportDTO(
        cust=c_dto.name,
        language=language.lower(),
        start_date=start_date,
        end_date=end_date,
        incidentes=c_dto.incidents,
        service_requests=c_dto.service_requests,
        cambios=c_dto.changes,
        customers=[c_dto],
    )
    buf = use_case.generate_monthly_report(dto)
    buf.seek(0)
    filename = _build_filename(
        "REPORTE_DISPONIBILIDAD",
        "MONTHLY_REPORT",
        c_dto.name,
        language,
        start_date,
        end_date,
    )
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@reports_router.post("/generate-incident-report")
def generate_incident_report(
    sf_account_id: str,
    start_date: datetime,
    end_date: datetime,
    language: str = "es",
    session: Session = Depends(get_toolmaster_db_connection),
    use_case: IWordReportUseCase = Depends(word_report_use_case),
):
    repo = ToolmasterRepository(session=session)
    c_dto = repo.get_customer_info(sf_account_id, start_date, end_date)
    if not c_dto:
        raise HTTPException(status_code=404, detail="No se encontró la cuenta con ese SF ID")
    dto = WordReportDTO(
        cust=c_dto.name,
        language=language.lower(),
        start_date=start_date,
        end_date=end_date,
        incidentes=c_dto.incidents,
        customers=[c_dto],
    )
    buf = use_case.generate_incidents_report(dto)
    buf.seek(0)
    filename = _build_filename(
        "REPORTE_INCIDENCIAS",
        "INCIDENTS_REPORT",
        c_dto.name,
        language,
        start_date,
        end_date,
    )
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@reports_router.post("/generate-saso-report")
def generate_saso_report(
    sf_account_id: str,
    start_date: datetime,
    end_date: datetime,
    session: Session = Depends(get_toolmaster_db_connection),
    use_case: IWordReportUseCase = Depends(word_report_use_case),
):
    repo = ToolmasterRepository(session=session)
    c_dto = repo.get_customer_info(sf_account_id, start_date, end_date)
    if not c_dto:
        raise HTTPException(status_code=404, detail="No se encontró la cuenta con ese SF ID")
    dto = WordReportDTO(
        cust=c_dto.name,
        start_date=start_date,
        end_date=end_date,
        incidentes=c_dto.incidents,
        service_requests=c_dto.service_requests,
        cambios=c_dto.changes,
        customers=[c_dto],
    )
    result_buffer = use_case.generate_saso_excel_report(dto)
    result_buffer.seek(0)
    filename = _build_filename(
        "SERVICES_AND_SUPPORT_REPORT",
        "SERVICES_AND_SUPPORT_REPORT",
        c_dto.name,
        "en",
        start_date,
        end_date,
        extension="xlsx",
    )
    return StreamingResponse(
        result_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@reports_router.post("/generate-case-report")
def generate_case_report(
    case_number: str,
    language: str = "es",
    session: Session = Depends(get_toolmaster_db_connection),
    use_case: IWordReportUseCase = Depends(word_report_use_case),
):
    repo = ToolmasterRepository(session=session)
    result_case = repo.get_case_by_number(case_number)
    if not result_case:
        raise HTTPException(status_code=404, detail="No se encontró el caso.")
    row = result_case["data"]
    tipo = result_case["type"]
    account_name = row.get("account_name", "NO_ACCOUNT")
    inc_list, sr_list, ch_list = [], [], []
    if tipo == "incident":
        inc_list = [IncidentDTO(**row)]
    elif tipo == "sr":
        sr_list = [ServiceRequestDTO(**row)]
    elif tipo == "change":
        ch_list = [ChangeDTO(**row)]
    wl_rows = repo.get_worklogs_by_case_number(case_number)
    w_list = [WorklogDTO(**w) for w in wl_rows]
    cust_dto = CustomerDTO(name=account_name, worklogs=w_list)
    dto = WordReportDTO(
        cust=account_name,
        incidentes=inc_list,
        service_requests=sr_list,
        cambios=ch_list,
        customers=[cust_dto],
        language=language,
    )
    result_buffer = use_case.generate_single_case_report(case_number, dto)
    result_buffer.seek(0)
    filename = _build_filename(
        "REPORTE_DE_CASO",
        "CASE_REPORT",
        account_name,
        language,
        extra_part=case_number,
    )
    return StreamingResponse(
        result_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

@reports_router.post("/generate-rfo-report")
def generate_rfo_report(
    incident_number: str,
    language: str = "es",
    session: Session = Depends(get_toolmaster_db_connection),
    use_case: IWordReportUseCase = Depends(word_report_use_case),
):
    repo = ToolmasterRepository(session=session)
    result = repo.get_case_by_number(incident_number)
    if not result or result["type"] != "incident":
        raise HTTPException(status_code=404, detail="No se encontró la incidencia.")

    row = result["data"]
    inc_dto = IncidentDTO(**row)

    if language.lower() == "es" and inc_dto.priority:
        inc_dto.priority = {
            "Planning": "Planeación",
            "Low": "Baja",
            "Medium": "Media",
            "High": "Alta",
            "Critical": "Crítica",
        }.get(inc_dto.priority, inc_dto.priority)

    cust_country = row.get("country_name") or ""
    cust_assets = row.get("product_categories") or ""
    subject_raw = (row.get("subject") or "").strip()
    subject_clean = (
        "_".join(subject_raw.split())[:60] if subject_raw else "SIN_ASUNTO"
    )

    dto = WordReportDTO(
        cust=subject_clean,
        cust_country=cust_country,
        cust_assets=cust_assets,
        incidentes=[inc_dto],
        language=language,
    )

    template_file = (
        "Informe_RFO.docx" if language.lower() == "es" else "RFO_Report.docx"
    )
    template_path = os.path.join(use_case.templates_path, template_file)

    buf = use_case.generate_incident_overview_report(dto, template_path=template_path)
    buf.seek(0)

    filename = _build_filename(
        "REPORTE_DE_RFO",
        "RFO_REPORT",
        subject_clean,
        language,
    )

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
