import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from crewai.tools import tool

# Importamos tu función de autenticación (Asegúrate de que auth.py esté en la raíz)
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import authenticate_google

# Aseguramos que el directorio de datos existe para los Mocks
os.makedirs("datos", exist_ok=True)

@tool("Lector de Google Calendar")
def get_daily_agenda() -> str:
    """Extrae las reuniones y eventos programados en el calendario para el día de hoy."""
    try:
        creds = authenticate_google()
        if not creds: return "Error: No hay credenciales de Google."
        
        service = build('calendar', 'v3', credentials=creds)
        
        # Definir rango de tiempo: Desde ahora hasta la medianoche
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indica UTC
        end_of_day = (datetime.utcnow() + timedelta(days=1)).replace(hour=0, minute=0, second=0).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary', timeMin=now, timeMax=end_of_day,
            maxResults=10, singleEvents=True, orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # 💾 GENERACIÓN DE FIXTURE (MOCK)
        with open(os.path.join("datos", "mock_calendar.json"), "w", encoding="utf-8") as f:
            json.dump(events, f, indent=4, ensure_ascii=False)
            
        if not events:
            return "Agenda despejada. No hay eventos programados para hoy."
            
        agenda = ["📅 *Agenda de Hoy:*"]
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            # Formatear la hora (asumiendo formato ISO 8601)
            if 'T' in start:
                hora = start.split('T')[1][:5]
            else:
                hora = "Todo el día"
            agenda.append(f" - {hora} | {event['summary']}")
            
        return "\n".join(agenda)
    except Exception as e:
        return f"Error al acceder a Google Calendar: {e}"

@tool("Lector de Google Tasks")
def get_pending_tasks() -> str:
    """Extrae las tareas pendientes (urgentes) de la lista principal de Google Tasks."""
    try:
        creds = authenticate_google()
        if not creds: return "Error: No hay credenciales de Google."
        
        service = build('tasks', 'v1', credentials=creds)
        
        # Obtener la lista de tareas principal ('@default')
        results = service.tasks().list(tasklist='@default', showHidden=False).execute()
        items = results.get('items', [])
        
        # Filtrar solo las que no están completadas
        tareas_pendientes = [t for t in items if t.get('status') != 'completed']
        
        # 💾 GENERACIÓN DE FIXTURE (MOCK)
        with open(os.path.join("datos", "mock_tasks.json"), "w", encoding="utf-8") as f:
            json.dump(tareas_pendientes, f, indent=4, ensure_ascii=False)
            
        if not tareas_pendientes:
            return "✅ No hay tareas pendientes en Google Tasks."
            
        tareas_str = ["📋 *Tareas Pendientes:*"]
        for t in tareas_pendientes[:5]: # Limitamos a las 5 primeras para no saturar
            tareas_str.append(f" - [ ] {t['title']}")
            
        return "\n".join(tareas_str)
    except Exception as e:
        return f"Error al acceder a Google Tasks: {e}"

@tool("Escáner de Correos VIP (Gmail)")
def get_urgent_emails() -> str:
    """Escanea Gmail en busca de correos recientes marcados como importantes o de remitentes clave."""
    try:
        creds = authenticate_google()
        if not creds: return "Error: No hay credenciales de Google."
        
        service = build('gmail', 'v1', credentials=creds)
        
        # Query: Correos no leídos, recibidos en las últimas 24h, marcados como importantes
        query = "is:unread is:important newer_than:1d"
        results = service.users().messages().list(userId='me', q=query, maxResults=3).execute()
        messages = results.get('messages', [])
        
        # 💾 GENERACIÓN DE FIXTURE (MOCK)
        with open(os.path.join("datos", "mock_gmail.json"), "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)
            
        if not messages:
            return "Bandeja limpia. No hay correos VIP sin leer."
            
        resumen_correos = ["📧 *Correos Prioritarios:*"]
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = txt.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sin Asunto')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Desconocido')
            # Limpiar el remitente para que sea más corto
            sender_name = sender.split('<')[0].strip() if '<' in sender else sender
            
            resumen_correos.append(f" - De: {sender_name} | Asunto: {subject}")
            
        return "\n".join(resumen_correos)
    except Exception as e:
        return f"Error al acceder a Gmail: {e}"