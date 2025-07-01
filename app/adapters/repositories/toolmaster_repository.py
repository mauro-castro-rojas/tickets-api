from typing import Any, Dict, Optional, Set, Type, List
from datetime import datetime

from sqlalchemy import RowMapping
from sqlmodel import Session, select, text, Column

from app.domain.ports.out_port.IToolmasterRepository import IToolmasterRepository
from app.utils.errors import handle_database_error
from app.utils.variable_types import ENTITY_MODEL
from app.utils.logger import log
from app.utils.errors import DatabaseError, ErrorType, AppError

from app.infrastructure.dto.reports_schema import (
    AssetDTO,
    ContactDTO,
    IncidentDTO,
    ServiceRequestDTO,
    ChangeDTO,
    CustomerDTO,
    WorklogDTO,
)


class ToolmasterRepository(IToolmasterRepository):
    def __init__(self, session: Session):
        super().__init__(session)

    @handle_database_error
    def get_incident(
        self,
        field_name: str,
        data: str,
        model: Type[ENTITY_MODEL]):
        
        try: 
            response = super().get_by_unique_field(field_name, data, model)

            if not response:
                return AppError(
                    error_type=ErrorType.NOT_FOUND,
                    message="Resource not found."
                )

            return response
        except DatabaseError as e:
            raise DatabaseError(
                message="Database error occurred while fetching data.",
                original_exception=e,
                error_code=ErrorType.DATASOURCE_ERROR
            )
        
    
    @handle_database_error
    def get_all_by_list_ids(
        self,
        column_to_search: Column,
        list_ids: List[str],
        model: Type[ENTITY_MODEL]):
        
        try: 
            response = super().get_all_by_list_ids(column_to_search, list_ids, model)

            if not response:
                return AppError(
                    error_type=ErrorType.NOT_FOUND,
                    message="Resource not found."
                )

            return response
        except DatabaseError as e:
            raise DatabaseError(
                message="Database error occurred while fetching data.",
                original_exception=e,
                error_code=ErrorType.DATASOURCE_ERROR
            )
        
    
    @handle_database_error
    def get_by_unique_field(self, field_name: str, data: str, model: Type[ENTITY_MODEL]):
        try:
            response = super().get_by_unique_field(field_name=field_name, data=data, model=model)

            if not response:
                return AppError(
                    error_type=ErrorType.NOT_FOUND,
                    message="Resource not found."
                )
            return response
        except DatabaseError as e:
            raise DatabaseError(
                message="Database error occurred while fetching data.",
                original_exception=e,
                error_code=ErrorType.DATASOURCE_ERROR
            )
    
    @handle_database_error
    def get_by_id(self, id_: int, model: Type[ENTITY_MODEL] = None):
        try: 
            response = super().get_by_id(id_, model)
            if not response:
                return AppError(
                    error_type=ErrorType.NOT_FOUND,
                    message="Resource not found."
                )

            return response
        except DatabaseError as e:
            raise DatabaseError(
                message="Database error occurred while fetching data.",
                original_exception=e,
                error_code=ErrorType.DATASOURCE_ERROR
            )
    

    @handle_database_error
    def get_all_by_fields(self, filters: Dict, model: Type[ENTITY_MODEL] = None): 
        try: 
            response = super().get_all_by_fields(filters=filters, model=model)
            if not response:
                return AppError(
                    error_type=ErrorType.NOT_FOUND,
                    message="Resource not found."
                )
            return response
        except DatabaseError as e:
            raise DatabaseError(
                message="Database error occurred while fetching data.",
                original_exception=e,
                error_code=ErrorType.DATASOURCE_ERROR
            )

    
    def delete(self, id_: int, model: Type[ENTITY_MODEL]):
        pass

    def get_all(self, model: Type[ENTITY_MODEL] = None):
        pass

    def get_all_by_fields_contains(self, filters: Dict, model: Type[ENTITY_MODEL] = None):
        pass

    def save(self, model: ENTITY_MODEL):
        pass

    def update(self, id_: int, model: ENTITY_MODEL):
        pass


    @handle_database_error
    def _get_ticket_meta(self, case_number: str) -> RowMapping:
        q = text(
            "SELECT ticket_id, LOWER(case_type_name) AS case_type "
            "FROM   csctoolmaster.app_ticket "
            "WHERE  case_number = :num "
            "LIMIT  1"
        )
        return self.session.execute(q, {"num": case_number}).mappings().fetchone()

    @handle_database_error
    def get_case_by_number(self, case_number: str) -> Optional[Dict[str, Any]]:
        digits = "".join(ch for ch in case_number if ch.isdigit())
        variants = [
            case_number,
            f"CHG-{digits}",
            f"SR-{digits}",
            f"INC-{digits}",
            digits
        ]

        meta = None
        for v in variants:
            meta = self.session.execute(
                text(
                    "SELECT ticket_id, lower(case_type_name) AS tp "
                    "FROM csctoolmaster.app_ticket "
                    "WHERE case_number = :num"
                ),
                {"num": v},
            ).mappings().fetchone()
            if meta:
                break

        if not meta and digits:
            meta = self.session.execute(
                text(
                    "SELECT ticket_id, lower(case_type_name) AS tp "
                    "FROM csctoolmaster.app_ticket "
                    "WHERE case_number LIKE :num "
                    "ORDER BY ticket_id LIMIT 1"
                ),
                {"num": f"%{digits}"},
            ).mappings().fetchone()

        if not meta:
            return None

        tid = meta["ticket_id"]
        raw = (meta["tp"] or "").lower()
        tipo = (
            "sr" if raw in {"sr", "service_request", "request"} else
            "change" if raw in {"change_request", "change"} else
            "incident"
        )
        rows = self.session.execute(self._BASE_QUERIES[tipo], {"tid": tid}).mappings().all()
        if not rows:
            return None
        base: Dict[str, Any] = dict(rows[0])
        assets: List[AssetDTO] = []
        for r in rows:
            if r.get("asset_id") or r.get("asset") or r.get("asset_location") or r.get("asset_type"):
                assets.append(
                    AssetDTO(
                        asset_id=r["asset_id"],
                        sf_asset_id=r["asset_sfid"],
                        circuit_id=r["asset"],
                        product_family=r.get("product_family"),
                        product_category=r.get("asset_type"),
                        product_name=None,
                        status=None,
                        location=r.get("asset_location"),
                    )
                )
        if not assets:
            assets = [AssetDTO()]
        base["assets"] = assets
        enrich = self.session.execute(self._ENRICH_QUERY, {"tid": tid}).mappings().fetchone()
        if enrich:
            base["account_name"]       = enrich["account_name"]
            base["circuit_ids"]        = enrich["circuit_ids"]
            base["product_families"]   = enrich["product_families"]
            base["product_categories"] = enrich["product_categories"]
            base["country_name"]       = enrich["country_name"]
            base["country"]            = enrich["country_name"]

        return {"type": tipo, "data": base}

    _BASE_QUERIES = {
        "incident": text(
            "SELECT "
            "  i.*, "
            "  i.resolution_summary AS solution, "
            "  a.asset_id         AS asset_id, "
            "  a.sf_asset_id      AS asset_sfid, "
            "  a.circuit_id       AS asset, "
            "  a.product_family   AS product_family, "
            "  a.product_category AS asset_type, "
            "  a.location         AS asset_location, "
            "  COALESCE(acc.name, acc2.name, 'NO_ACCOUNT') AS account_name, "
            "  COALESCE(c1.name, c2.name, 'NO_COUNTRY') AS country_name "
            "FROM csctoolmaster.app_incident i "
            "LEFT JOIN csctoolmaster.app_ticket_assets ta ON i.ticket_id = ta.ticket_id "
            "LEFT JOIN csctoolmaster.app_assets a         ON ta.assets_id   = a.asset_id "
            "LEFT JOIN csctoolmaster.app_ticket_accounts tacc ON i.ticket_id = tacc.ticket_id "
            "LEFT JOIN csctoolmaster.app_accounts acc      ON acc.account_id   = tacc.accounts_id "
            "LEFT JOIN csctoolmaster.app_accounts acc2     ON acc2.account_id  = a.account_id "
            "LEFT JOIN csctoolmaster.app_countries c1      ON c1.country_id    = acc.country_id "
            "LEFT JOIN csctoolmaster.app_countries c2      ON c2.country_id    = acc2.country_id "
            "WHERE i.ticket_id = :tid"
        ),
        "sr": text(
            "SELECT "
            "  sr.*, "
            "  sr.resolution_summary AS solution, "
            "  a.asset_id         AS asset_id, "
            "  a.sf_asset_id      AS asset_sfid, "
            "  a.circuit_id       AS asset, "
            "  a.product_family   AS product_family, "
            "  a.product_category AS asset_type, "
            "  a.location         AS asset_location, "
            "  COALESCE(acc.name, acc2.name, 'NO_ACCOUNT') AS account_name, "
            "  COALESCE(c1.name, c2.name, 'NO_COUNTRY')     AS country_name "
            "FROM csctoolmaster.app_sr sr "
            "LEFT JOIN csctoolmaster.app_ticket_assets ta ON sr.ticket_id = ta.ticket_id "
            "LEFT JOIN csctoolmaster.app_assets a         ON ta.assets_id   = a.asset_id "
            "LEFT JOIN csctoolmaster.app_ticket_accounts tacc ON sr.ticket_id = tacc.ticket_id "
            "LEFT JOIN csctoolmaster.app_accounts acc      ON acc.account_id   = tacc.accounts_id "
            "LEFT JOIN csctoolmaster.app_accounts acc2     ON acc2.account_id  = a.account_id "
            "LEFT JOIN csctoolmaster.app_countries c1      ON c1.country_id    = acc.country_id "
            "LEFT JOIN csctoolmaster.app_countries c2      ON c2.country_id    = acc2.country_id "
            "WHERE sr.ticket_id = :tid"
        ),
        "change": text(
            "SELECT "
            "  c.*, "
            "  COALESCE(c.urgency, c.impact) AS priority, "
            "  c.result            AS solution, "
            "  a.asset_id          AS asset_id, "
            "  a.sf_asset_id       AS asset_sfid, "
            "  a.circuit_id        AS asset, "
            "  a.product_family    AS product_family, "
            "  a.product_category  AS asset_type, "
            "  a.location          AS asset_location, "
            "  COALESCE(acc.name, acc2.name, 'NO_ACCOUNT') AS account_name, "
            "  COALESCE(c1.name, c2.name, 'NO_COUNTRY')     AS country_name "
            "FROM csctoolmaster.app_changes c "
            "LEFT JOIN csctoolmaster.app_ticket_assets ta ON c.ticket_id = ta.ticket_id "
            "LEFT JOIN csctoolmaster.app_assets a         ON ta.assets_id   = a.asset_id "
            "LEFT JOIN csctoolmaster.app_ticket_accounts tacc ON c.ticket_id = tacc.ticket_id "
            "LEFT JOIN csctoolmaster.app_accounts acc      ON acc.account_id   = tacc.accounts_id "
            "LEFT JOIN csctoolmaster.app_accounts acc2     ON acc2.account_id  = a.account_id "
            "LEFT JOIN csctoolmaster.app_countries c1      ON c1.country_id    = acc.country_id "
            "LEFT JOIN csctoolmaster.app_countries c2      ON c2.country_id    = acc2.country_id "
            "WHERE c.ticket_id = :tid"
        ),
    }

    _ENRICH_QUERY = text(
        "WITH "
        " accs AS ( "
        "   SELECT ta.ticket_id, "
        "          GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') AS account_name "
        "   FROM csctoolmaster.app_ticket_accounts ta "
        "   JOIN csctoolmaster.app_accounts a ON a.account_id = ta.accounts_id "
        "   GROUP BY ta.ticket_id "
        " ), "
        " asset_accs AS ( "
        "   SELECT ta.ticket_id, "
        "          GROUP_CONCAT(DISTINCT aa.name SEPARATOR ', ') AS asset_account_name "
        "   FROM csctoolmaster.app_ticket_assets ta "
        "   JOIN csctoolmaster.app_assets ast ON ast.asset_id = ta.assets_id "
        "   JOIN csctoolmaster.app_accounts aa ON aa.account_id = ast.account_id "
        "   GROUP BY ta.ticket_id "
        " ), "
        " asts AS ( "
        "   SELECT ta.ticket_id, "
        "          GROUP_CONCAT(DISTINCT ast.circuit_id SEPARATOR ', ')       AS circuit_ids, "
        "          GROUP_CONCAT(DISTINCT ast.product_family SEPARATOR ', ')   AS product_families, "
        "          GROUP_CONCAT(DISTINCT ast.product_category SEPARATOR ', ') AS product_categories "
        "   FROM csctoolmaster.app_ticket_assets ta "
        "   JOIN csctoolmaster.app_assets ast ON ast.asset_id = ta.assets_id "
        "   GROUP BY ta.ticket_id "
        " ), "
        " ctry AS ( "
        "   SELECT ta.ticket_id, c.name AS country_name "
        "   FROM csctoolmaster.app_ticket_accounts ta "
        "   JOIN csctoolmaster.app_accounts a ON a.account_id = ta.accounts_id "
        "   JOIN csctoolmaster.app_countries c ON c.country_id = a.country_id "
        "   WHERE ta.ticket_id = :tid "
        "   UNION ALL "
        "   SELECT ta.ticket_id, c.name AS country_name "
        "   FROM csctoolmaster.app_ticket_assets ta "
        "   JOIN csctoolmaster.app_assets ast ON ast.asset_id = ta.assets_id "
        "   JOIN csctoolmaster.app_accounts a ON a.account_id = ast.account_id "
        "   JOIN csctoolmaster.app_countries c ON c.country_id = a.country_id "
        "   WHERE ta.ticket_id = :tid "
        " ) "
        "SELECT "
        "  COALESCE(accs.account_name, asset_accs.asset_account_name, 'NO_ACCOUNT') AS account_name, "
        "  COALESCE(asts.circuit_ids,        'NO_ASSET')    AS circuit_ids, "
        "  COALESCE(asts.product_families,   'NO_ASSET')    AS product_families, "
        "  COALESCE(asts.product_categories, 'NO_ASSET')    AS product_categories, "
        "  COALESCE(ctry.country_name,       'NO_COUNTRY')  AS country_name "
        "FROM (SELECT :tid AS ticket_id) t "
        "LEFT JOIN accs         ON accs.ticket_id = t.ticket_id "
        "LEFT JOIN asset_accs   ON asset_accs.ticket_id = t.ticket_id "
        "LEFT JOIN asts         ON asts.ticket_id = t.ticket_id "
        "LEFT JOIN ctry         ON ctry.ticket_id = t.ticket_id"
    )

    @handle_database_error
    def get_worklogs_by_case_number(self, case_number: str) -> List[WorklogDTO]:
        q = text(
            "SELECT worklog_id, sf_worklog_id, created_by_name, type_worklog, created_at, "
            "       description, ticket_number, worklog_number "
            "FROM   csctoolmaster.app_worklogs "
            "WHERE  ticket_number = :num"
        )
        rows = self.session.execute(q, {"num": case_number}).fetchall()
        return [WorklogDTO(*r) for r in rows if r[0] is not None]


    @handle_database_error
    def get_customer_info(self, sf_account_id: str, start_date: datetime, end_date: datetime) -> Optional[CustomerDTO]:
        q_acc = text(
            "SELECT a.account_id, a.sf_account_id, a.name, "
            "       a.sccd_id, COALESCE(a.sf_category, a.category) AS category, "
            "       c.name AS country_name "
            "FROM   csctoolmaster.app_accounts a "
            "LEFT   JOIN csctoolmaster.app_countries c ON c.country_id = a.country_id "
            "WHERE  a.sf_account_id = :sfid "
            "LIMIT  1"
        )
        acc_row = self.session.execute(q_acc, {"sfid": sf_account_id}).fetchone()
        if not acc_row:
            return None
        account_id, sfid, name, sccd_id, category, country_name = acc_row

        q_assets = text(
            "SELECT asset_id, sf_asset_id, circuit_id, product_family, product_category, "
            "       product_name, status, location "
            "FROM   csctoolmaster.app_assets "
            "WHERE  account_id = :acct"
        )
        assets = [
            AssetDTO(
                asset_id=r[0],
                sf_asset_id=r[1],
                circuit_id=r[2],
                product_family=r[3],
                product_category=r[4],
                product_name=r[5],
                status=r[6],
                location=r[7],
            )
            for r in self.session.execute(q_assets, {"acct": account_id}).fetchall()
        ]

        q_contacts = text(
            "SELECT contact_id, sf_contact_id, name, contact_type, email, phone, mobile_phone, "
            "       account_id "
            "FROM   csctoolmaster.app_contact "
            "WHERE  account_id = :acct"
        )
        contacts = [
            ContactDTO(
                contact_id=r[0],
                sf_contact_id=r[1],
                name=r[2],
                contact_type=r[3],
                email=r[4],
                phone=r[5],
                account_id=r[7],
            )
            for r in self.session.execute(q_contacts, {"acct": account_id}).fetchall()
        ]

        q_inc = text(
            "SELECT i.incident_id, i.sf_incident_id, i.incident_number, i.source_incident, "
            "       i.reported_at, i.affected_at, i.resolution_at, i.status, i.priority, "
            "       i.created_at AS incident_created, i.updated_at AS incident_updated, "
            "       i.start_at_dw, i.end_at_dw, i.downtime, i.is_major AS inc_is_major, "
            "       i.symptom, i.cause, i.resolution_summary, i.description, i.subject, "
            "       i.attributed_to, i.reason, i.type_incident, i.stop_dw, "
            "       t.ticket_id, a.asset_id, a.sf_asset_id AS asset_sfid, a.circuit_id, "
            "       a.product_family, a.product_category, a.location "
            "FROM   csctoolmaster.app_ticket t "
            "LEFT   JOIN csctoolmaster.app_ticket_assets ta ON t.ticket_id = ta.ticket_id "
            "LEFT   JOIN csctoolmaster.app_assets a ON ta.assets_id = a.asset_id "
            "LEFT   JOIN csctoolmaster.app_ticket_accounts tacc ON t.ticket_id = tacc.ticket_id "
            "LEFT   JOIN csctoolmaster.app_incident i ON i.ticket_id = t.ticket_id "
            "WHERE  t.case_type_name = 'incident' "
            "  AND  t.created_at >= :startd AND t.created_at <= :endd "
            "  AND  (a.account_id = :acct OR tacc.accounts_id = :acct)"
        )
        inc_rows = self.session.execute(
            q_inc, {"acct": account_id, "startd": start_date, "endd": end_date}
        ).mappings().all()
        inc_map: Dict[int, IncidentDTO] = {}
        for r in inc_rows:
            iid = r["incident_id"]
            if not iid:
                continue
            if iid not in inc_map:
                inc_map[iid] = IncidentDTO(
                    incident_id=r["incident_id"],
                    ticket_id=r["ticket_id"],
                    sf_incident_id=r["sf_incident_id"],
                    incident_number=r["incident_number"],
                    subject=r["subject"],
                    source_incident=r["source_incident"],
                    reported_at=r["reported_at"],
                    affected_at=r["affected_at"],
                    resolution_at=r["resolution_at"],
                    status=r["status"],
                    priority=r["priority"],
                    created_at=r["incident_created"],
                    updated_at=r["incident_updated"],
                    start_at_dw=r["start_at_dw"],
                    end_at_dw=r["end_at_dw"],
                    downtime=r["downtime"],
                    is_major=r["inc_is_major"],
                    symptom=r["symptom"],
                    cause=r["cause"],
                    resolution_summary=r["resolution_summary"],
                    description=r["description"],
                    attributed_to=r["attributed_to"],
                    reason=r["reason"],
                    type_incident=r["type_incident"],
                    stop_dw=r["stop_dw"],
                    assets=[],
                )
            if r["asset_id"]:
                inc_map[iid].assets.append(
                    AssetDTO(
                        asset_id=r["asset_id"],
                        sf_asset_id=r["asset_sfid"],
                        circuit_id=r["circuit_id"],
                        product_family=r["product_family"],
                        product_category=r["product_category"],
                        location=r["location"],
                    )
                )
        q_sr = text(
            "SELECT sr.sr_id, sr.sf_sr_id, sr.sr_number, sr.status, sr.priority, "
            "       sr.sr_type, sr.source, sr.symptom, sr.resolution_summary AS solution, "
            "       sr.created_at AS sr_created, sr.updated_at AS sr_updated, "
            "       sr.resolved_at, sr.closed_at, sr.sr_category, sr.sr_type_actions, "
            "       t.ticket_id, a.asset_id, a.sf_asset_id AS asset_sfid, a.circuit_id, "
            "       a.product_family, a.product_category, a.location "
            "FROM   csctoolmaster.app_ticket t "
            "LEFT   JOIN csctoolmaster.app_ticket_assets ta ON t.ticket_id = ta.ticket_id "
            "LEFT   JOIN csctoolmaster.app_assets a ON ta.assets_id = a.asset_id "
            "LEFT   JOIN csctoolmaster.app_ticket_accounts tacc ON t.ticket_id = tacc.ticket_id "
            "LEFT   JOIN csctoolmaster.app_sr sr ON sr.ticket_id = t.ticket_id "
            "WHERE  t.case_type_name IN ('request','service_request','sr') "
            "  AND  t.created_at >= :startd AND t.created_at <= :endd "
            "  AND  (a.account_id = :acct OR tacc.accounts_id = :acct)"
        )
        sr_rows = self.session.execute(
            q_sr, {"acct": account_id, "startd": start_date, "endd": end_date}
        ).mappings().all()
        sr_map: Dict[int, ServiceRequestDTO] = {}
        for r in sr_rows:
            sid = r["sr_id"]
            if not sid:
                continue
            if sid not in sr_map:
                sr_map[sid] = ServiceRequestDTO(
                    sr_id=r["sr_id"],
                    ticket_id=r["ticket_id"],
                    sf_sr_id=r["sf_sr_id"],
                    sr_number=r["sr_number"],
                    status=r["status"],
                    sr_type=r["sr_type"],
                    source=r["source"],
                    symptom=r["symptom"],
                    solution=r["solution"],
                    created_at=r["sr_created"],
                    updated_at=r["sr_updated"],
                    resolved_at=r["resolved_at"],
                    closed_at=r["closed_at"],
                    sr_category=r["sr_category"],
                    sr_type_actions=r["sr_type_actions"],
                    priority=r["priority"],
                    asset=None,
                    asset_location=None,
                    asset_type=None,
                    assets=[],
                )
            if r["asset_id"]:
                sr_map[sid].asset = r["circuit_id"]
                sr_map[sid].asset_location = r["location"]
                sr_map[sid].asset_type = r["product_category"]
                sr_map[sid].assets.append(
                    AssetDTO(
                        asset_id=r["asset_id"],
                        sf_asset_id=r["asset_sfid"],
                        circuit_id=r["circuit_id"],
                        product_family=r["product_family"],
                        product_category=r["product_category"],
                        location=r["location"],
                    )
                )
        q_ch = text(
            "SELECT c.change_id, c.ticket_id, c.sf_change_id, c.change_number, c.status, "
            "       c.urgency, c.impact, c.type_change, c.subject, c.description, "
            "       c.risk_level, c.failure_probability, c.change_downtime, "
            "       c.created_at AS chg_created, c.updated_at AS chg_updated, "
            "       c.start_at_activity, c.end_at_activity, c.bussines_reason, "
            "       c.result, c.type_of_action, "
            "       a.asset_id, a.sf_asset_id AS asset_sfid, a.circuit_id, "
            "       a.product_family, a.product_category, a.location "
            "FROM   csctoolmaster.app_ticket t "
            "LEFT   JOIN csctoolmaster.app_ticket_assets ta ON t.ticket_id = ta.ticket_id "
            "LEFT   JOIN csctoolmaster.app_assets a ON ta.assets_id = a.asset_id "
            "LEFT   JOIN csctoolmaster.app_ticket_accounts tacc ON t.ticket_id = tacc.ticket_id "
            "LEFT   JOIN csctoolmaster.app_changes c ON c.ticket_id = t.ticket_id "
            "WHERE  t.case_type_name = 'Change_Request' "
            "  AND  t.created_at >= :startd AND t.created_at <= :endd "
            "  AND  (a.account_id = :acct OR tacc.accounts_id = :acct)"
        )
        ch_rows = self.session.execute(
            q_ch, {"acct": account_id, "startd": start_date, "endd": end_date}
        ).mappings().all()
        ch_map: Dict[int, ChangeDTO] = {}
        for r in ch_rows:
            cid = r["change_id"]
            if not cid:
                continue
            if cid not in ch_map:
                ch_map[cid] = ChangeDTO(
                    change_id=r["change_id"],
                    ticket_id=r["ticket_id"],
                    sf_change_id=r["sf_change_id"],
                    change_number=r["change_number"],
                    status=r["status"],
                    type_change=r["type_change"],
                    description=r["description"],
                    created_at=r["chg_created"],
                    updated_at=r["chg_updated"],
                    result=r["result"],
                    type_of_action=r["type_of_action"],
                    bussines_reason=r["bussines_reason"],
                    urgency=r["urgency"],
                    impact=r["impact"],
                    subject=r["subject"],
                    risk_level=r["risk_level"],
                    failure_probability=r["failure_probability"],
                    change_downtime=r["change_downtime"],
                    start_at_activity=r["start_at_activity"],
                    end_at_activity=r["end_at_activity"],
                    priority=(r["urgency"] or r["impact"]),
                    asset=None,
                    asset_location=None,
                    asset_type=None,
                    assets=[],
                )
            if r["asset_id"]:
                ch_map[cid].asset = r["circuit_id"]
                ch_map[cid].asset_location = r["location"]
                ch_map[cid].asset_type = r["product_category"]
                ch_map[cid].assets.append(
                    AssetDTO(
                        asset_id=r["asset_id"],
                        sf_asset_id=r["asset_sfid"],
                        circuit_id=r["circuit_id"],
                        product_family=r["product_family"],
                        product_category=r["product_category"],
                        location=r["location"],
                    )
                )
        q_wl = text(
            "SELECT w.worklog_id, w.sf_worklog_id, w.created_by_name, w.type_worklog, "
            "       w.created_at, w.ticket_id, w.description, w.ticket_number, w.worklog_number "
            "FROM   csctoolmaster.app_worklogs w "
            "JOIN   csctoolmaster.app_ticket t ON w.ticket_id = t.ticket_id "
            "LEFT   JOIN csctoolmaster.app_ticket_accounts tacc ON t.ticket_id = tacc.ticket_id "
            "LEFT   JOIN csctoolmaster.app_ticket_assets ta ON t.ticket_id = ta.ticket_id "
            "LEFT   JOIN csctoolmaster.app_assets a ON ta.assets_id = a.asset_id "
            "WHERE  (a.account_id = :acct OR tacc.accounts_id = :acct) "
            "  AND  t.created_at >= :startd AND t.created_at <= :endd"
        )
        wl_rows = self.session.execute(
            q_wl, {"acct": account_id, "startd": start_date, "endd": end_date}
        ).fetchall()
        worklogs = [
            WorklogDTO(
                worklog_id=r[0],
                sf_worklog_id=r[1],
                created_by_name=r[2],
                type_worklog=r[3],
                created_at=r[4],
                ticket_id=r[5],
                description=r[6],
                ticket_number=r[7],
                worklog_number=r[8],
            )
            for r in wl_rows
            if r[0]
        ]
        return CustomerDTO(
            account_id=account_id,
            sf_account_id=sfid,
            name=name,
            sccd_id=sccd_id,
            country=country_name,
            category=category,
            assets=assets,
            contacts=contacts,
            incidents=list(inc_map.values()),
            service_requests=list(sr_map.values()),
            changes=list(ch_map.values()),
            worklogs=worklogs,
        )