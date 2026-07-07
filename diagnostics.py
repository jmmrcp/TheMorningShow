import os
import requests
from dotenv import load_dotenv

# Importación de las herramientas reales
from tools.ops_reader import read_shift_handoff
from tools.exchange_reader import read_itsm_tickets
from tools.cyber_ai import get_latest_cves
from tools.github_tracker import check_github_status
from tools.transport import inc_transport

# Cargamos las credenciales del archivo .env local
load_dotenv()

def print_status(name, success, message=""):
    """Formatea la salida en consola como un semáforo."""
    if success:
        print(f"🟢 [OK] {name}")
    else:
        print(f"🔴 [FAIL] {name} -> {message}")

def check_telegram_connection():
    """Valida que el token de Telegram es correcto y el bot responde."""
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        return False, "Falta TELEGRAM_TOKEN en las variables de entorno."
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        bot_info = resp.json()
        return True, f"Conectado como @{bot_info['result']['username']}"
    except Exception as e:
        return False, str(e)

def check_elevenlabs_connection():
    """Valida la API Key de ElevenLabs (si está configurada)."""
    from config import USE_PRO_TTS
    if not USE_PRO_TTS:
        return True, "Omitido (USE_PRO_TTS está en False. Se usará gTTS)."
        
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        return False, "Falta ELEVENLABS_API_KEY en el entorno."
    try:
        headers = {"xi-api-key": api_key}
        resp = requests.get("https://api.elevenlabs.io/v1/user", headers=headers, timeout=10)
        resp.raise_for_status()
        return True, "API Key válida y conectada."
    except Exception as e:
        return False, str(e)

def run_all_diagnostics():
    print("\n" + "="*50)
    print("🛠️  INICIANDO DIAGNÓSTICO DE INTEGRACIÓN (DevSecOps)")
    print("="*50 + "\n")

    # 1. Test de APIs Externas (Red y Credenciales)
    print("--- 🌐 SERVICIOS EXTERNOS ---")
    
    # Telegram
    success, msg = check_telegram_connection()
    print_status("API Telegram Webhook", success, msg)
    
    # ElevenLabs / TTS
    success, msg = check_elevenlabs_connection()
    print_status("API ElevenLabs (TTS)", success, msg)
    
    # Ciberseguridad (The Hacker News RSS)
    try:
        res = get_latest_cves()
        if "error" in res.lower():
            print_status("Radar CVE (RSS)", False, res)
        else:
            print_status("Radar CVE (RSS)", True)
    except Exception as e:
        print_status("Radar CVE (RSS)", False, str(e))
        
    # GitHub (Requiere GITHUB_TOKEN)
    try:
        res = check_github_status()
        if "Error" in res:
            print_status("API GitHub Tracker", False, res)
        else:
            print_status("API GitHub Tracker", True)
    except Exception as e:
        print_status("API GitHub Tracker", False, str(e))
        
    # Transporte (Scraping con bypass SSL)
    try:
        res = inc_transport()
        if "Error" in res:
            print_status("Scraper Transporte Murcia", False, res)
        else:
            print_status("Scraper Transporte Murcia", True)
    except Exception as e:
        print_status("Scraper Transporte Murcia", False, str(e))

    # 2. Test de Archivos Locales (Sistema de Archivos)
    print("\n--- 📁 SISTEMA DE ARCHIVOS LOCALES ---")
    
    # Lector ITSM (BMC Helix)
    try:
        res = read_itsm_tickets()
        if "No hay correos" in res or "Error" in res:
            print_status("Lector ITSM (BMC Helix)", False, "Archivo correo_bmc_helix.txt no encontrado o vacío.")
        else:
            print_status("Lector ITSM (BMC Helix)", True)
    except Exception as e:
        print_status("Lector ITSM (BMC Helix)", False, str(e))

    # Lector WhatsApp Handoff
    try:
        res = read_shift_handoff()
        if "No hay archivo" in res or "Error" in res:
            print_status("Lector WhatsApp (Turnos)", False, "Archivo whatsapp_export.txt no encontrado o vacío.")
        else:
            print_status("Lector WhatsApp (Turnos)", True)
    except Exception as e:
        print_status("Lector WhatsApp (Turnos)", False, str(e))

    print("\n" + "="*50)
    print("✅ DIAGNÓSTICO FINALIZADO")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_all_diagnostics()