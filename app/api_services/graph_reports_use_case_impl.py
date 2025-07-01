# app/api_services/graph_reports_use_case_impl.py

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from io import BytesIO
from typing import List, Optional

from app.infrastructure.dto.reports_schema import IncidentDTO, ServiceRequestDTO, ChangeDTO

class GraphReportsUseCaseImpl:
    def generate_proactivity_graph(
        self,
        incidentes: List[IncidentDTO],
        service_requests: List[ServiceRequestDTO],
        cambios: List[ChangeDTO]
    ) -> Optional[BytesIO]:
        data = []
        for inc in incidentes:
            if inc.status and inc.status.lower() == "canceled":
                continue
            if inc.type_incident:
                data.append({"class": "INC", "tipo": inc.type_incident})
        for sr in service_requests:
            if sr.status and sr.status.lower() == "canceled":
                continue
            if sr.sr_type_actions:
                data.append({"class": "SR", "tipo": sr.sr_type_actions})
        for chg in cambios:
            if chg.status and chg.status.lower() == "canceled":
                continue
            if chg.type_of_action:
                data.append({"class": "CHG", "tipo": chg.type_of_action})
        df = pd.DataFrame(data)
        if df.empty:
            return None
        def custom_color(x):
            if str(x) == "Proactive":
                return "#ff6000"
            elif str(x) == "Reactive":
                return "#4D4D4D"
            else:
                return "#4B2C9F"
        fig = px.histogram(df, x="class", color="tipo", barmode="group")
        fig.update_layout(
            title="Casos Proactivos vs Reactivos",
            xaxis_title="Clase de Caso",
            yaxis_title="Cantidad",
            legend_title="Tipo",
            template="simple_white"
        )
        fig.update_yaxes(dtick=1)
        for dtrace in fig.data:
            dtrace.marker.color = custom_color(dtrace.name)
            dtrace.texttemplate = "%{y}"
            dtrace.textposition = "outside"
        img_bytes = fig.to_image(format="png")
        stream = BytesIO(img_bytes)
        stream.seek(0)
        return stream

    def generate_top_sedes_graph(self, incidentes: List[IncidentDTO]) -> Optional[BytesIO]:
        if not incidentes:
            return None
        items = []
        for inc in incidentes:
            if inc.status and inc.status.lower() == "canceled":
                continue
            if inc.assets:
                for asset in inc.assets:
                    if asset.circuit_id:
                        items.append({"circuit_id": asset.circuit_id, "ticket_id": inc.ticket_id})
        df = pd.DataFrame(items)
        if df.empty:
            return None
        df_count = df.groupby("circuit_id")["ticket_id"].nunique().reset_index(name="count")
        df_count = df_count.sort_values("count", ascending=False)
        df_top3 = df_count.head(3)
        if df_top3.empty:
            return None
        fig = px.bar(df_top3, x="count", y="circuit_id", orientation='h')
        fig.update_traces(marker_color="#4D4D4D", texttemplate="%{x}", textposition="outside")
        fig.update_layout(
            title="Top 3 Circuit IDs con mayor número de tickets (Incidentes)",
            xaxis_title="Cantidad de Tickets",
            yaxis_title="Circuit ID",
            template="simple_white"
        )
        fig.update_yaxes(categoryorder='total ascending')
        fig.update_xaxes(dtick=1)
        img_bytes = fig.to_image(format="png")
        stream = BytesIO(img_bytes)
        stream.seek(0)
        return stream

    def generate_attributions_graph(self, incidentes: List[IncidentDTO]) -> Optional[BytesIO]:
        if not incidentes:
            return None
        data = []
        for inc in incidentes:
            if inc.status and inc.status.lower() == "canceled":
                continue
            if inc.attributed_to:
                data.append({"attributed_to": inc.attributed_to})
        df = pd.DataFrame(data)
        if df.empty:
            return None
        map_attrib = {
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
        df["categoria"] = df["attributed_to"].apply(lambda x: map_attrib.get(x, "Otros"))
        df_count = df.groupby("categoria").size().reset_index(name="count")
        def custom_color(cat):
            lower = str(cat).lower()
            if "liberty" in lower:
                return "#ff6000"
            elif "cliente" in lower:
                return "#4D4D4D"
            else:
                return "#4B2C9F"
        bars = []
        for _, row in df_count.iterrows():
            cat = row["categoria"]
            cnt = row["count"]
            bars.append(go.Bar(x=[cat], y=[cnt], marker_color=custom_color(cat), name=str(cat),
                               text=[cnt], texttemplate="%{text}", textposition="outside"))
        fig = go.Figure(data=bars)
        fig.update_layout(
            title="Atribución de Incidentes",
            xaxis_title="Categoría de Atribución",
            yaxis_title="Cantidad",
            template="simple_white",
            barmode="group"
        )
        fig.update_yaxes(dtick=1)
        img_bytes = fig.to_image(format="png")
        stream = BytesIO(img_bytes)
        stream.seek(0)
        return stream
