from datetime import datetime
from crewai import Crew, Agent, Task
from auth import get_llm

# Herramientas del sistema
from tools.transport import inc_transport
from tools.weather import check_weather_rain
from tools.messaging import send_multimedia_telegram
from tools.cyber_ai import get_latest_cves, get_ai_updates
from tools.exchange_reader import read_itsm_tickets
from tools.ops_reader import read_shift_handoff
from tools.google_workspace import get_daily_agenda, get_pending_tasks, get_urgent_emails

def create_crew():
    llm = get_llm()
    fecha = datetime.now().strftime('%d/%m/%Y')

    # --- AGENTES ---
    logistics_agent = Agent(
        role="Analista de Movilidad Urbana y Clima",
        goal="Detectar incidencias de transporte en la ruta Alcantarilla - Murcia Centro y alertar sobre contingencias climáticas.",
        backstory="Especialista en logística diaria. Tu objetivo es asegurar que el trayecto físico del ingeniero sea fluido y que esté preparado para la lluvia.",
        llm=llm, 
        tools=[
            inc_transport, 
            check_weather_rain
            ], 
        verbose=False
    )
    agenda_agent = Agent(
        role="Coordinador de Agenda y Tareas",
        goal="Sintetizar los compromisos del día, tareas pendientes y correos urgentes.",
        backstory="Asistente ejecutivo personal. Aseguras que los problemas de IT no hagan que el ingeniero olvide sus reuniones clave o compromisos.",
        llm=llm, 
        tools=[get_daily_agenda, get_pending_tasks, get_urgent_emails], 
        verbose=False
    )
    
    sec_ai_agent = Agent(
        role="Ingeniero de Inteligencia de Amenazas",
        goal="Vigilar nuevos CVEs y actualizaciones críticas en modelos de Inteligencia Artificial.",
        backstory="Analista DevSecOps nocturno. Buscas vulnerabilidades e innovaciones tecnológicas.",
        llm=llm, tools=[get_latest_cves, get_ai_updates], verbose=False
    )

    ops_agent = Agent(
        role="Jefe de Operaciones IT",
        goal="Filtrar el ruido del chat de operaciones y extraer problemas de infraestructura reales.",
        backstory="Director de IT. Ignoras las bromas del personal y te enfocas en hardware, redes y bloqueos.",
        llm=llm, tools=[read_shift_handoff], verbose=False
    )

    handoff_agent = Agent(
        role="Coordinador de Cambios ITSM",
        goal="Identificar tickets de cambio (CRQ) y asignaciones pendientes en la bandeja corporativa.",
        backstory="Gestor de ITIL. Buscas aprobaciones pendientes y despliegues programados.",
        llm=llm, tools=[read_itsm_tickets], verbose=False
    )

    script_writer_agent = Agent(
        role="Sintetizador Ejecutivo",
        goal="Ensamblar los reportes técnicos en un guion ágil y locutarlo.",
        backstory="Redactor técnico senior. Transformas logs caóticos en inteligencia accionable.",
        llm=llm, tools=[send_multimedia_telegram], verbose=True
    )

    # --- TAREAS ---
    t_logistics = Task(
        description="Analiza la web de transportes para buscar incidencias en la ruta y revisa el radar meteorológico local para decidir si hace falta paraguas.", 
        expected_output="Estado del transporte urbano y recomendación explícita sobre llevar paraguas o no.", 
        agent=logistics_agent
    )
    
    t_sec_ai = Task(
        description="Revisa los feeds de seguridad e IA. Extrae un CVE crítico y un paper de IA relevante.", 
        expected_output="Resumen de 2 viñetas con impacto en Sec/AI.", 
        agent=sec_ai_agent
    )
    
    t_ops = Task(
        description="Lee el volcado del chat del turno de noche. Ignora opiniones. Extrae fallos de red, hardware o cableado.", 
        expected_output="Lista de incidencias físicas y lógicas pendientes.", 
        agent=ops_agent
    )

    t_handoff = Task(
        description="Lee los correos ITSM. Enumera los cambios CRQ que requieren aprobación hoy.", 
        expected_output="Lista de tickets de cambio.", 
        agent=handoff_agent
    )

    t_script = Task(
        description=f"""Ensambla el BRIEFING DEVSECOPS de hoy {fecha}.
        
        Estructura estricta:
        1. Logística y Entorno
        2. Radar Sec & AI
        3. Estado de Operaciones (ITSM y Chat)
        4. Foco del Día (Deduce la prioridad cruzando la info anterior).
        
        Reglas: Formato directo, profesional, sin lenguaje florido. 
        OBLIGATORIO: Utiliza send_multimedia_telegram para enviar el texto y generar el audio MP3.""",
        expected_output="Guion enviado por texto y audio al móvil.",
        agent=script_writer_agent,
        context=[t_logistics, t_sec_ai, t_ops, t_handoff]
    )

    return Crew(
        agents=[logistics_agent, sec_ai_agent, ops_agent, handoff_agent, script_writer_agent],
        tasks=[t_logistics, t_sec_ai, t_ops, t_handoff, t_script],
        verbose=True
    )