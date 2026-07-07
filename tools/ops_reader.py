import os
from crewai.tools import tool

@tool("Lector de Novedades del Turno")
def read_shift_handoff() -> str:
    """
    Lee el archivo de texto plano que contiene el volcado del chat de operaciones del último turno.
    """
    ruta_archivo = "datos/whatsapp_export.txt"
    try:
        if not os.path.exists(ruta_archivo):
            return "No hay archivo de traspaso de turno disponible."
            
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            # Leemos solo las últimas 150 líneas para evitar saturar el contexto del LLM
            lineas = archivo.readlines()[-150:]
            return "".join(lineas)
    except Exception as e:
        return f"Error al acceder al registro del turno: {e}"