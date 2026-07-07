import os
import re
from O365 import Account
from crewai.tools import tool

@tool("Lector de Exchange Corporativo")
def read_exchange_incidents() -> str:
    """
    Se conecta al buzón de Microsoft Exchange corporativo vía Graph API para extraer 
    correos de incidencias (ServiceNow, Jira) y asignaciones del último turno.
    """
    # Requiere registrar una App en Azure AD y obtener estas claves
    client_id = os.environ.get("MS_CLIENT_ID")
    client_secret = os.environ.get("MS_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        return "Error: Credenciales de Microsoft Graph no configuradas."

    credentials = (client_id, client_secret)
    # Scope mínimo necesario para leer correo
    scopes = ['https://graph.microsoft.com/Mail.Read']
    
    try:
        account = Account(credentials, auth_flow='authorization_code')
        
        # Si no está autenticado, requerirá interacción manual (solo la primera vez)
        if not account.is_authenticated:
            # En un entorno de servidor, esto imprimirá una URL en la terminal para autorizar
            account.authenticate(scopes=scopes)
            
        mailbox = account.mailbox()
        
        # Filtrar correos no leídos de las últimas 12 horas o de remitentes específicos (ej. sistema de tickets)
        query = mailbox.new_query().query('isRead').equals(False)
        mensajes = mailbox.get_messages(limit=10, query=query)
        
        resumen_correos = []
        for msg in mensajes:
            resumen_correos.append(f"- Asunto: {msg.subject} | Urgencia: {msg.importance.name}")
            
        if not resumen_correos:
            return "No hay nuevas incidencias o asignaciones en la bandeja corporativa."
            
        return "\n".join(resumen_correos)

    except Exception as e:
        return f"Excepción de conexión con Exchange: {e}"
    
@tool("Lector de Tickets ITSM")
def read_itsm_tickets() -> str:
    """
    Simula la lectura de la bandeja de entrada corporativa y extrae la información 
    crítica de los correos de gestión de cambios (CRQ) e incidencias.
    """
    # Para el entorno del Hackathon, leeremos un archivo local que contiene el correo bruto.
    # En producción, esto sería reemplazado por la llamada a Microsoft Graph API.
    ruta_correo = "datos/correo_bmc_helix.txt"
    
    if not os.path.exists(ruta_correo):
        return "No hay correos de tickets ITSM pendientes."

    try:
        with open(ruta_correo, 'r', encoding='utf-8') as f:
            raw_email = f.read()

        # Extracción limpia mediante Expresiones Regulares
        crq = re.search(r'Infrastructure Change ID:\s*(CRQ\d+)', raw_email)
        summary = re.search(r'Summary:\s*(.*)', raw_email)
        start_date = re.search(r'Scheduled Start Date:\s*(.*)', raw_email)
        location = re.search(r'Indique Ubicaci[óo]n:\s*(.*)', raw_email)
        
        datos_extraidos = []
        if crq: datos_extraidos.append(f"Ticket: {crq.group(1)}")
        if summary: datos_extraidos.append(f"Resumen: {summary.group(1)}")
        if start_date: datos_extraidos.append(f"Ejecución: {start_date.group(1)}")
        if location: datos_extraidos.append(f"Ubicación: {location.group(1)}")
        
        if datos_extraidos:
            return "Ticket detectado:\n" + "\n".join(datos_extraidos)
        else:
            return "No se encontraron metadatos estructurados en el correo."
            
    except Exception as e:
        return f"Error procesando correos ITSM: {e}"