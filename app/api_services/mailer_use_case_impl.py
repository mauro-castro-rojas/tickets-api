import smtplib
import os
from datetime import datetime
from typing import Dict, List, Type, Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import jinja2
from jinja2 import FileSystemLoader, Environment

from app.domain.ports.input_port.mailer_service import IMailerUseCase
from app.domain.ports.out_port.IToolmasterRepository import IToolmasterRepository
from app.infrastructure.dto.mail_schema import MailBaseDTO, MailGeneralDTO, RadarMailDTO
from app.utils.logger import log
from app.utils.variable_types import ENTITY_MODEL


class MailerUseCaseImpl(IMailerUseCase):
    def __init__(
        self,
        toolmaster_repository: Optional[IToolmasterRepository],
        mail_from: str = "network-monitor@cbs-cloud.com",
        mail_reply_to: str = "csc@libertynet.com, csc-ops@cwc.com",
        ip_smtp: str = "webmail.cbs-cloud.com"
    ):
        self.toolmaster_repository = toolmaster_repository
        self.mail_from = mail_from
        self.mail_reply_to = mail_reply_to
        self.ip_smtp = ip_smtp
        
        templates_path = os.path.join("app", "utils", "templates")
        self.env = Environment(loader=FileSystemLoader(templates_path))

    def read_template(self, template_name: str):
        """
        Devuelve una instancia Template de Jinja para el archivo dado.
        template_name es el nombre del archivo HTML
        """
        return self.env.get_template(template_name)

    def send_radar_email(self, dto: MailGeneralDTO):
        """
        Envío de correo de radar.
        Usa la plantilla 'radar_template.html' y coloca dto.body dentro.
        """
        mail_from = self.mail_from
        mail_to_list = dto.to_mails
        mail_subject = dto.subject

        template = self.read_template("general_template.html")
        context = {
            "body_html": dto.body
        }
        mail_body = template.render(**context)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = mail_subject
        msg['From'] = mail_from
        msg['To'] = ", ".join(mail_to_list)
        msg['Reply-to'] = self.mail_reply_to

        msg.attach(MIMEText(mail_body, 'html'))

        with smtplib.SMTP(self.ip_smtp) as mail:
            mail.send_message(msg)

        return "Correo general enviado satisfactoriamente"
    
    def send_email_radar(self, dto: RadarMailDTO):
        """
        Envía un correo usando la plantilla 'radar_template.html'.
        """
        mail_from = self.mail_from
        mail_to_list = dto.to_mails
        mail_subject = (
            f"{dto.radar_checklist_choices} - CSC - Posible oportunidad - {dto.radar_country} - {dto.radar_account_id}"
        )

        template = self.read_template("radar_template.html") 
        context = {
            "radar_checklist_choices": dto.radar_checklist_choices,
            "radar_user_email": dto.radar_user_email,
            "radar_account_id": dto.radar_account_id,
            "radar_country": dto.radar_country,
            "radar_creation_date": dto.radar_creation_date,
            "radar_case": dto.radar_case,
            "radar_contact_name": dto.radar_contact_name,
            "radar_contact_phone": dto.radar_contact_phone,
            "radar_contact_email": dto.radar_contact_email,
            "radar_area": dto.radar_area,
            "radar_type": dto.radar_type,
            "radar_details": dto.radar_details
        }
        mail_body = template.render(**context)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = mail_subject
        msg['From'] = mail_from
        msg['To'] = ", ".join(mail_to_list)
        msg['Reply-to'] = self.mail_reply_to

        msg.attach(MIMEText(mail_body, 'html'))

        with smtplib.SMTP(self.ip_smtp) as mail:
            mail.send_message(msg)

        return "Correo Radar enviado satisfactoriamente"

    def send_email_general(self, dto: MailGeneralDTO):
        """
        Envío de correo general. 
        Usa la plantilla 'general_template.html' y coloca 'dto.body' dentro.
        Es un caso generico que colocara todo lo del body en el correo
        """
        mail_from = self.mail_from
        mail_to_list = dto.to_mails
        mail_subject = dto.subject

        template = self.read_template("general_template.html")
        context = {
            "body_html": dto.body
        }
        mail_body = template.render(**context)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = mail_subject
        msg['From'] = mail_from
        msg['To'] = ", ".join(mail_to_list)
        msg['Reply-to'] = self.mail_reply_to

        if dto.copy_mails:
            msg['Cc'] = ", ".join(dto.copy_mails)

        msg.attach(MIMEText(mail_body, 'html'))
        all_recipients = mail_to_list + (dto.copy_mails or [])

        with smtplib.SMTP(self.ip_smtp) as mail:
            mail.sendmail(
                from_addr=mail_from,
                to_addrs=all_recipients,  # <= cc incluido
                msg=msg.as_string()
            )

        return "Correo general enviado satisfactoriamente"

    def send_email_none(self, dto: MailBaseDTO):
        """
        Envío de correo con creacion de caso proactivo, por ahora es un template de prueba.
        """

        if dto.is_major:
            mail_to = "santiago.alvarez@cwc.com"
            mail_bcc = dto.to_mails 
        else:
            mail_to = dto.to_mails
            mail_bcc = dto.to_mails

        mail_cc = "santiago.alvarez@cwc.com"
        mail_reply_to = "csc@libertynet.com, csc-ops@cwc.com"

        mail_subject = (
            f"{dto.ticket_id} - P - {dto.country} - {dto.customer} - SERVICIO ALARMADO"
        )

        fault_description = f"""
        Buen día estimado cliente.<br><br>
        En este momento se encuentra alarmado el servicio en la sede <b>{dto.branch}</b>.<br>
        Por favor, informarnos de cualquier actividad que pueda afectar el servicio.<br><br>
        Con el fin de agilizar la solución de falla solicitamos de su amable colaboración:
        <ul>
            <li>Reinicio Eléctrico de equipos en sede (Media convertes y/o Router) para descartar posible bloqueo.</li>
            <li>Fotos visibles con enfoque en los LEDs para propósitos de diagnóstico.</li>
            <li>Nombre y número de contacto.</li>
            <li>Horario de atención.</li>
        </ul>
        Con esta información procedemos a escalar al equipo de conectividad local.<br><br>
        Quedamos atentos.<br><br>
        CSC Monitoring Operator
        """

        template = self.read_template("incident_template.html")
        context = {
            "ticket_id": dto.ticket_id,
            "branch": dto.branch,
            "country": dto.country,
            "customer": dto.customer,
            "description_html": fault_description,
            "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        html_rendered = template.render(**context)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = mail_subject
        msg['From'] = self.mail_from
        msg['To'] = mail_to
        msg['Cc'] = mail_cc
        msg['Bcc'] = mail_bcc
        msg['Reply-to'] = mail_reply_to

        part_html = MIMEText(html_rendered, 'html')
        msg.attach(part_html)

        with smtplib.SMTP(self.ip_smtp) as mail:
            mail.send_message(msg)

        return "Correo de incidente enviado satisfactoriamente"

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
