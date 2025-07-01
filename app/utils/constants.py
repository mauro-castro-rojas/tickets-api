
# use them with import app.constants as const, then : impact = const.impact_values
# TODO cuadrar formato para salesforce
description_templates = {
    'TemplateNetworking' : f'''Buen día estimado cliente.En este momento
                        se encuentra alarmado el servicio en la sede {{branch}}, por favor informarnos 
                        de cualquier actividad que pueda afectar el servicio.<br>        Con el fin 
                        de poder agilizar la solución de falla solicitamos de su amable colaboración 
                        adjuntándolos sobre la línea de este correo.-Realizar 
                        Reinicio Eléctrico de equipos en sede (Media convertes y/o Router) para 
                        descartar posible bloqueo del equipo.-Fotos visibles con enfoque 
                        en los LEDs para propósitos de diagnóstico.     
                        -Nombre y número de contacto.-Horario de atención.      
                        Con esta información procedemos a escalar al equipo de conectividad 
                        local.<br>        <br>        Quedamos atentos.<br>        <br>        CSC 
                        Monitoring Operator    ''',
    'TemplateMassive' : f"""Buen Dia<br> Estimados,<br>
                        En estos momentos se está  presentando un evento masivo que afecta el sector {{city}}. Estamos trabajando para solucionar la afectación.<br>
                        Les estaremos informando los avances.<br>
                        Les estaremos informando los avances.
                        Gracias por su comprensión y quedamos atentos a cualquier inquietud."""
}


worklog_template = f'Opened By Automatic System.'

descritption = ('TemplateSelfService' ,'TemplateNetworking' ,'TemplateWifi' ,'TemplateMasive' )
    




