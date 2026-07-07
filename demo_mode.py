# demo_mode.py
import sys
from datetime import datetime
from crewai import Crew, Agent, Task
from config import logger
# Nota: Si usaste un LLM específico en auth.py, asegúrate de que demo_mode pueda usar 
# una API key gratuita o un modelo local. Para la demo en Kaggle, se asume que proveerán su propia key de Gemini/OpenAI.
from auth import get_llm 

# --- 1. MOCK DE HERRAMIENTAS ---
# Usamos decoradores de CrewAI (o langchain) para simular las herramientas
from langchain.tools import tool

@tool("inc_transport_mock")
def inc_transport_mock() -> str:
    """Simula la lectura OCR de incidencias de transporte."""
    return "ALERTA URBANA: Retrasos de 15 minutos en la línea de autobús Alcantarilla - Centro de Murcia por obras en la vía principal."

@tool("read_emails_mock")
def read_emails_mock() -> str:
    """Simula la lectura de correos de Gmail."""
    return "1. URGENTE: El cliente de Madrid confirma la reunión de mañana. 2. Factura de la luz disponible (95.40€)."

@tool("get_todays_agenda_mock")
def get_todays_agenda_mock() -> str:
    """Simula los eventos de Google Calendar."""
    return "10:00 AM - Daily Standup (Zoom). 13:30 PM - Comida con equipo."

@tool("get_todays_tasks_mock")
def get_todays_tasks_mock() -> str:
    """Simula las tareas de Google Tasks."""
    return "VENCIDA: Enviar informe fiscal. HOY: Revisar PR en GitHub."

@tool("get_market_mock")
def get_market_mock() -> str:
    """Simula datos financieros y de mercado."""
    return "REP.MC (Repsol) cotiza a 14.20€ (-1.2%). Noticia: Caída leve en precios del crudo."

@tool("send_telegram_mock")
def send_telegram_mock(mensaje: str) -> str:
    """Simula el envío por Telegram imprimiendo en consola."""
    print("\n" + "="*40)
    print("📱 SIMULACIÓN DE MENSAJE TELEGRAM 📱")
    print("="*40)
    print(mensaje)
    print("="*40 + "\n")
    return "Mensaje enviado por Telegram exitosamente."

# --- 2. CONFIGURACIÓN DEL CREW PARA LA DEMO ---
def run_demo():
    logger.info("🛠️ Iniciando AI-Briefing en MODO DEMO...")
    llm = get_llm()
    fecha = datetime.now().strftime('%d/%m/%Y')

    # Recreamos el Jefe de Gabinete con la herramienta Mock
    briefing_agent = Agent(
        role="Jefe de Gabinete",
        goal="Generar y enviar reporte.",
        backstory="Consolidas info y envías el resumen final a primera hora.",
        llm=llm,
        tools=[send_telegram_mock], 
        verbose=True
    )

    # Tarea unificada para la demo (simplificada para que corra rápido ante los jueces)
    t_briefing = Task(
        description=f"""Genera el BRIEFING para hoy {fecha}.
        Usa los siguientes datos recuperados por tu equipo:
        - Transporte: {inc_transport_mock.run()}
        - Correos: {read_emails_mock.run()}
        - Agenda: {get_todays_agenda_mock.run()}
        - Tareas: {get_todays_tasks_mock.run()}
        - Mercado: {get_market_mock.run()}
        
        Estructura el mensaje de forma profesional y clara usando emojis.
        Obligatorio: Al terminar, envía el mensaje usando tu herramienta send_telegram_mock.""",
        expected_output="Reporte estructurado y confirmación de envío.",
        agent=briefing_agent
    )

    demo_crew = Crew(
        agents=[briefing_agent],
        tasks=[t_briefing],
        verbose=True
    )

    result = demo_crew.kickoff()
    logger.info("✅ Demo completada.")
    return result

if __name__ == "__main__":
    try:
        run_demo()
    except Exception as e:
        logger.critical(f"🔥 Fallo en la Demo: {e}")
        sys.exit(1)