import os
import sys
import telebot
from config import logger
from crew_setup import create_crew
import json
from tools.ops_reader import read_shift_handoff

# Importación directa de herramientas para uso manual
from tools.cyber_ai import get_latest_cves
from tools.transport import inc_transport

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
chat_id_autorizado = os.environ.get("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN:
    logger.critical("Falta TELEGRAM_TOKEN en el entorno.")
    sys.exit(1)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- COMANDOS BÁSICOS ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    texto_ayuda = (
        "🤖 *AI-Briefing DevSecOps Activo*\n\n"
        "Comandos disponibles:\n"
        "🔸 `/briefing` - Ejecuta la síntesis completa (Texto + Audio).\n"
        "🔸 `/cve` - Consulta rápida de alertas de seguridad.\n"
        "🔸 `/logistica` - Estado del transporte Alcantarilla-Murcia.\n"
        "🔸 `/ping` - Test de conexión del servidor.\n"
        "🔸 `/ops` - Reporte de operaciones (Handoff)."
    )
    bot.reply_to(message, texto_ayuda, parse_mode="Markdown")

@bot.message_handler(commands=['ping'])
def system_ping(message):
    """Comprobación rápida del estado del sistema."""
    if str(message.chat.id) != str(chat_id_autorizado): return
    bot.reply_to(message, "🟢 *Sistema Operativo.* Escuchando comandos en tiempo real.", parse_mode="Markdown")

# --- COMANDOS DE EJECUCIÓN AISLADA (HERRAMIENTAS DIRECTAS) ---

@bot.message_handler(commands=['cve'])
def trigger_cve(message):
    """Ejecuta la herramienta de ciberseguridad saltándose a los agentes LLM."""
    if str(message.chat.id) != str(chat_id_autorizado): return
    
    mensaje_estado = bot.reply_to(message, "🔍 *Escaneando NVD y fuentes RSS...*", parse_mode="Markdown")
    
    try:
        # Llamamos a la herramienta directamente
        resultado_crudo = get_latest_cves()
        
        # Como nuestra herramienta devuelve un JSON en formato string, lo parseamos para mostrarlo bonito
        datos = json.loads(resultado_crudo)
        
        if "error" in datos:
            respuesta = f"❌ Error en el escáner: {datos['error']}"
        else:
            respuesta = "🚨 *Últimas Alertas de Seguridad:*\n\n"
            for alerta in datos.get("alertas_seguridad", []):
                respuesta += f"⚠️ [{alerta['titulo']}]({alerta['enlace']})\n\n"
                
        bot.edit_message_text(respuesta, chat_id=message.chat.id, message_id=mensaje_estado.message_id, parse_mode="Markdown", disable_web_page_preview=True)
        
    except Exception as e:
        bot.edit_message_text(f"❌ *Error interno:*\n`{e}`", chat_id=message.chat.id, message_id=mensaje_estado.message_id, parse_mode="Markdown")

@bot.message_handler(commands=['logistica'])
def trigger_logistica(message):
    """Ejecuta el scraper de transporte (OCR) de forma aislada."""
    if str(message.chat.id) != str(chat_id_autorizado): return
    
    mensaje_estado = bot.reply_to(message, "🚌 *Extrayendo boletín de transporte vía OCR...*", parse_mode="Markdown")
    
    try:
        resultado = inc_transport()
        bot.edit_message_text(f"🌦️ *Estado de Movilidad:*\n\n{resultado}", chat_id=message.chat.id, message_id=mensaje_estado.message_id, parse_mode="Markdown")
    except Exception as e:
        bot.edit_message_text(f"❌ *Error al leer el transporte:*\n`{e}`", chat_id=message.chat.id, message_id=mensaje_estado.message_id, parse_mode="Markdown")


@bot.message_handler(commands=['ops'])
def trigger_ops(message):
    """Ejecuta el lector de traspaso de turnos de forma aislada."""
    if str(message.chat.id) != str(chat_id_autorizado): return
    
    mensaje_estado = bot.reply_to(message, "🚨 *Analizando log de operaciones nocturnas...*", parse_mode="Markdown")
    
    try:
        # Llamamos a la herramienta directamente
        resultado_crudo = read_shift_handoff()
        
        # Formateamos la salida para que sea legible en Telegram
        respuesta = (
            "🛠️ *Reporte Rápido de Operaciones (Handoff)*\n\n"
            f"{resultado_crudo}\n\n"
            "_Nota: Lectura en crudo sin síntesis de IA._"
        )
        
        bot.edit_message_text(respuesta, chat_id=message.chat.id, message_id=mensaje_estado.message_id, parse_mode="Markdown")
        
    except Exception as e:
        bot.edit_message_text(f"❌ *Error al leer el registro de operaciones:*\n`{e}`", chat_id=message.chat.id, message_id=mensaje_estado.message_id, parse_mode="Markdown")
@bot.message_handler(commands=['briefing'])
def trigger_briefing(message):
    """Escucha el comando /briefing y lanza la orquestación de CrewAI."""
    logger.info(f"Comando /briefing recibido del usuario ID: {message.from_user.id}")
    
    # Validación de seguridad: Solo responder si el usuario es el autorizado
    chat_id_autorizado = os.environ.get("TELEGRAM_CHAT_ID")
    if str(message.chat.id) != str(chat_id_autorizado):
        bot.reply_to(message, "⛔ Acceso denegado. No tienes autorización para interactuar con este sistema.")
        return

    # Notificar inicio del proceso
    mensaje_estado = bot.reply_to(message, "⏳ *Iniciando protocolos...* Coordinando agentes DevSecOps para generar el briefing. Esto puede tardar 1-2 minutos.", parse_mode="Markdown")
    
    try:
        # Ejecutar el orquestador
        crew = create_crew()
        crew.kickoff()
        
        # El ScriptWriterAgent se encarga de enviar el resultado final a través de messaging.py,
        # por lo que aquí solo actualizamos el mensaje de estado inicial.
        bot.edit_message_text("✅ Análisis finalizado y enviado.", chat_id=message.chat.id, message_id=mensaje_estado.message_id)
        
    except Exception as e:
        logger.error(f"Fallo en la ejecución a demanda: {e}")
        bot.edit_message_text(f"❌ *Error crítico durante la ejecución:*\n`{e}`", chat_id=message.chat.id, message_id=mensaje_estado.message_id, parse_mode="Markdown")


if __name__ == "__main__":
    logger.info("📡 Bot de Telegram iniciado. Escuchando comandos...")
    bot.infinity_polling()