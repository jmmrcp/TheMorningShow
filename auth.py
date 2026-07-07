# auth.py
import os
from typing import Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from crewai import LLM

from config import SCOPES, logger

# ==========================================
# 🔒 SCOPES (Permisos OAuth 2.0)
# ==========================================
# Solicitar SOLO LECTURA es una buena práctica de ingeniería y seguridad.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/tasks.readonly'
]

def get_llm():
    """Retorna instancia LLM configurada."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Falta GOOGLE_API_KEY en .env")

    return LLM(
        model="gemini/gemini-flash-latest",
        verbose=True,
        temperature=0,
        google_api_key=api_key
    )

def authenticate_g() -> Optional[Credentials]:
    """Maneja el flujo OAuth 2.0."""
    creds = None
    token_file = 'token.json'
    creds_file = 'credentials.json'

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("🔄 Token refrescado.")
            except Exception:
                logger.warning("⚠️ Token expirado. Re-autenticando...")
                creds = None

        if not creds:
            if not os.path.exists(creds_file):
                logger.error("❌ Falta credentials.json")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    return creds

def authenticate_google():
    """
    Gestiona el flujo de autenticación OAuth 2.0 para Google Workspace.
    Retorna el objeto de credenciales para pasarlo a los servicios de API.
    """
    creds = None
    
    # 1. Comprobar si ya existe un token local válido de sesiones anteriores
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # 2. Si no hay credenciales, o han expirado, iniciamos el flujo de autorización
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Si solo ha expirado pero tenemos refresh_token, lo renovamos silenciosamente
            creds.refresh(Request())
        else:
            # Si no hay token, requerimos el archivo credentials.json descargado de Google Cloud
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("No se encontró 'credentials.json'. Descárgalo desde Google Cloud Console.")
                
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            
            # Levanta un servidor local temporal para recibir el callback de Google
            creds = flow.run_local_server(port=0)
            
        # 3. Guardar las credenciales autorizadas para ejecuciones futuras (como en GitHub Actions)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
            
    return creds