# app/api_services/tables_reports_use_case_impl.py

from typing import List, Dict, Tuple, Optional
from datetime import datetime
import pandas as pd
from unidecode import unidecode
from app.infrastructure.dto.reports_schema import (
    IncidentDTO,
    ServiceRequestDTO,
    ChangeDTO,
    AssetDTO
)

REASON_MAP = {
    "Service Down": "Servicio Caido",
    "Intermittencies and/or Latencies": "Intermitencias o latencias",
    "Service Alarmed": "Servicio Alarmado",
    "Other": "Otros"
}

ATTRIB_MAP = {
    "C&W": "Liberty Networks",
    "C&W Human Error": "Liberty Networks",
    "C&W Implementation": "Liberty Networks",
    "C&W Inside Plant": "Liberty Networks",
    "C&W Maintenance Window": "Liberty Networks",
    "C&W Outside Plant": "Liberty Networks",
    "Carrier": "Liberty Networks",
    "Provider": "Liberty Networks",
    "Tier 1 Support": "Liberty Networks",
    "Tier 2 Support": "Liberty Networks",
    "Tier 3 Support": "Liberty Networks",
    "Customer": "Cliente",
    "Force Majeure": "Fuerza Mayor"
}

def remove_accents(text: str) -> str:
    if not text:
        return text
    return unidecode(text)

class TablesReportsUseCaseImpl:
    def build_incident_table(
        self,
        incidentes: List[IncidentDTO],
        lang: str="es",
        no_data_str: str="No registra"
    ) -> List[Dict]:
        rows = []
        for inc in incidentes:
            if inc.status and inc.status.lower() == "canceled":
                continue
            reason_val = remove_accents(inc.reason) if inc.reason else None
            mapped_reason = REASON_MAP.get(reason_val, "Otros") if reason_val else no_data_str
            attrib = remove_accents(inc.attributed_to) if inc.attributed_to else ""
            if attrib in ATTRIB_MAP:
                attrib = ATTRIB_MAP[attrib]
            symptom_str = remove_accents(inc.symptom) if inc.symptom else no_data_str
            resolution_str = remove_accents(inc.resolution_summary) if inc.resolution_summary else no_data_str
            downtime_str = no_data_str
            if inc.downtime is not None:
                if inc.downtime == 0:
                    downtime_str = "0.0"
                else:
                    downtime_str = str(inc.downtime)

            closure_date = inc.resolution_at if inc.resolution_at else inc.updated_at
            closure_str = closure_date if closure_date else no_data_str
            stype_str = remove_accents(inc.type_incident) if inc.type_incident else no_data_str

            if inc.assets:
                circuit_ids = [remove_accents(a.circuit_id) for a in inc.assets if a.circuit_id]
                cids_str = ", ".join(circuit_ids) if circuit_ids else no_data_str
            else:
                cids_str = no_data_str

            rows.append({
                "incident_number": inc.incident_number or no_data_str,
                "ticket_id": inc.ticket_id if inc.ticket_id else no_data_str,
                "created_at": inc.created_at if inc.created_at else no_data_str,
                "resolution_at": closure_str,
                "type_incident": stype_str,
                "symptom": symptom_str,
                "resolution_summary": resolution_str,
                "reason": mapped_reason,
                "attributed_to": attrib or no_data_str,
                "downtime": downtime_str,
                "cid": cids_str,
                "service_type": stype_str
            })
        return rows

    def build_service_request_table(
        self,
        service_requests: List[ServiceRequestDTO],
        lang: str="es",
        no_data_str: str="No registra"
    ) -> List[Dict]:
        rows = []
        for sr in service_requests:
            if sr.status and sr.status.lower() == "canceled":
                continue
            if sr.resolved_at:
                closure_date = sr.resolved_at
            elif sr.closed_at:
                closure_date = sr.closed_at
            else:
                closure_date = sr.updated_at
            closure_str = closure_date if closure_date else no_data_str

            stype_str = remove_accents(sr.sr_type_actions) if sr.sr_type_actions else no_data_str
            symptom_str = remove_accents(sr.symptom) if sr.symptom else no_data_str
            solution_str = remove_accents(sr.solution) if sr.solution else no_data_str

            if sr.assets:
                circuit_ids = [remove_accents(a.circuit_id) for a in sr.assets if a.circuit_id]
                cid_str = ", ".join(circuit_ids) if circuit_ids else no_data_str
            else:
                cid_str = no_data_str

            rows.append({
                "sr_number": sr.sr_number or no_data_str,
                "ticket_id": sr.ticket_id if sr.ticket_id else no_data_str,
                "sr_type": stype_str,
                "status": remove_accents(sr.status) if sr.status else no_data_str,
                "created_at": sr.created_at if sr.created_at else no_data_str,
                "resolved_at": closure_str,
                "symptom": symptom_str,
                "solution": solution_str,
                "cid": cid_str,
                "service_type": stype_str
            })
        return rows

    def build_cambios_table(
        self,
        cambios: List[ChangeDTO],
        lang: str="es",
        no_data_str: str="No registra"
    ) -> List[Dict]:
        rows = []
        for chg in cambios:
            if chg.status and chg.status.lower() == "canceled":
                continue
            closure_date = chg.updated_at
            closure_str = closure_date if closure_date else no_data_str
            type_of_action_str = remove_accents(chg.type_of_action) if chg.type_of_action else no_data_str
            service_type_str = type_of_action_str
            desc_str = remove_accents(chg.description) if chg.description else no_data_str
            result_str = remove_accents(chg.result) if chg.result else no_data_str
            status_str = remove_accents(chg.status) if chg.status else no_data_str

            if chg.assets:
                circuit_ids = [remove_accents(a.circuit_id) for a in chg.assets if a.circuit_id]
                cid_str = ", ".join(circuit_ids) if circuit_ids else no_data_str
            else:
                cid_str = no_data_str

            rows.append({
                "change_number": chg.change_number or no_data_str,
                "ticket_id": chg.ticket_id if chg.ticket_id else no_data_str,
                "status": status_str,
                "description": desc_str,
                "created_at": chg.created_at if chg.created_at else no_data_str,
                "updated_at": closure_str,
                "result": result_str,
                "cid": cid_str,
                "service_type": service_type_str,
                "type_of_action": type_of_action_str
            })
        return rows


def build_availability_table(incidentes: List[IncidentDTO]) -> List[Dict]:
    if not incidentes:
        return []
    rows_items = []
    for inc in incidentes:
        if inc.status and inc.status.lower() == "canceled":
            continue
        attrib_final = remove_accents(inc.attributed_to) if inc.attributed_to else ""
        if attrib_final in ATTRIB_MAP:
            attrib_final = ATTRIB_MAP[attrib_final]
        if attrib_final != "Liberty Networks":
            continue
        downtime_val = inc.downtime if inc.downtime else 0

        if inc.assets:
            for asset in inc.assets:
                address_val = asset.location if asset.location else "N/A"
                address_val = remove_accents(address_val)
                rows_items.append({
                    "circuit_id": remove_accents(asset.circuit_id) if asset.circuit_id else None,
                    "product_family": remove_accents(asset.product_family) if asset.product_family else None,
                    "address": address_val,
                    "incident_number": remove_accents(inc.incident_number) if inc.incident_number else "",
                    "downtime": downtime_val
                })
        else:
            rows_items.append({
                "circuit_id": None,
                "product_family": None,
                "address": "N/A",
                "incident_number": remove_accents(inc.incident_number) if inc.incident_number else "",
                "downtime": downtime_val
            })

    if not rows_items:
        return []
    df = pd.DataFrame(rows_items)
    if df.empty:
        return []

    df["downtime"] = pd.to_numeric(df["downtime"], errors="coerce").fillna(0)
    grouped = df.groupby(["circuit_id","product_family","address"], dropna=False).agg({
        "downtime": "sum",
        "incident_number": lambda x: list(x.dropna())
    }).reset_index()

    total_minutes_month=43200
    final_rows=[]
    for _, rowx in grouped.iterrows():
        circuit_val=rowx["circuit_id"] if rowx["circuit_id"] else "No registra"
        product_val=rowx["product_family"] if rowx["product_family"] else "No registra"
        address_val=rowx["address"] if rowx["address"] else "N/A"
        dt_total=rowx["downtime"]
        availability=1-(dt_total/total_minutes_month)
        availability_percent=f"{availability*100:.2f}%"
        inc_list=rowx["incident_number"]
        inc_join=", ".join(inc_list)
        dt_str="0.0" if dt_total==0 else str(dt_total)
        final_rows.append({
            "cid": circuit_val,
            "service_type": product_val,
            "address": address_val,
            "case_related": inc_join,
            "downtime": dt_str,
            "disponibilidad": availability_percent,
            "disponibility":"99.6%"
        })

    def disp_to_float(v):
        return float(v.replace("%","",1))
    final_rows.sort(key=lambda r: disp_to_float(r["disponibilidad"]))
    return final_rows

def build_availability_table_by_month(
    incidentes: List[IncidentDTO],
    lang: str="es"
) -> Dict[Tuple[int,int], List[Dict]]:
    if not incidentes:
        return {}

    rows_items=[]
    for inc in incidentes:
        if inc.status and inc.status.lower()=="canceled":
            continue
        attrib_final=remove_accents(inc.attributed_to) if inc.attributed_to else ""
        if attrib_final in ATTRIB_MAP:
            attrib_final=ATTRIB_MAP[attrib_final]
        if attrib_final!="Liberty Networks":
            continue
        downtime_val=inc.downtime if inc.downtime else 0
        if not inc.created_at:
            continue
        yy=inc.created_at.year
        mm=inc.created_at.month

        if inc.assets:
            for asset in inc.assets:
                address_val=asset.location if asset.location else "N/A"
                address_val=remove_accents(address_val)
                rows_items.append({
                    "year": yy,
                    "month": mm,
                    "circuit_id": remove_accents(asset.circuit_id) if asset.circuit_id else None,
                    "product_family": remove_accents(asset.product_family) if asset.product_family else None,
                    "address": address_val,
                    "incident_number": remove_accents(inc.incident_number) if inc.incident_number else "",
                    "downtime": downtime_val
                })
        else:
            rows_items.append({
                "year": yy,
                "month": mm,
                "circuit_id": None,
                "product_family": None,
                "address": "N/A",
                "incident_number": remove_accents(inc.incident_number) if inc.incident_number else "",
                "downtime": downtime_val
            })

    if not rows_items:
        return {}

    df=pd.DataFrame(rows_items)
    if df.empty:
        return {}

    df["downtime"]=pd.to_numeric(df["downtime"], errors="coerce").fillna(0)
    grouped=df.groupby(["year","month","circuit_id","product_family","address"], dropna=False).agg({
        "downtime":"sum",
        "incident_number": lambda x: list(x.dropna())
    }).reset_index()

    total_minutes_month=43200

    months_set=set()
    for _, rowx in grouped.iterrows():
        months_set.add((rowx["year"], rowx["month"]))

    final_dict={}

    for (yy, mm) in sorted(months_set):
        subset=grouped[(grouped["year"]==yy)&(grouped["month"]==mm)]
        if subset.empty:
            final_dict[(yy, mm)] = []
            continue

        rowset=[]
        for _, rowm in subset.iterrows():
            circuit_val=rowm["circuit_id"] if rowm["circuit_id"] else "No registra"
            product_val=rowm["product_family"] if rowm["product_family"] else "No registra"
            address_val=rowm["address"] if rowm["address"] else "N/A"

            dt_total=rowm["downtime"]
            availability=1-(dt_total/total_minutes_month)
            availability_percent=f"{availability*100:.2f}%"

            inc_list=rowm["incident_number"]
            inc_join=", ".join(inc_list)
            dt_str="0.0" if dt_total==0 else str(dt_total)

            rowdict={
                "cid":circuit_val,
                "service_type":product_val,
                "address":address_val,
                "case_related":inc_join,
                "downtime":dt_str,
                "disponibilidad":availability_percent,
                "disponibility":"99.6%"
            }
            rowset.append(rowdict)
        final_dict[(yy, mm)]=rowset

    return final_dict
