import requests
import os
from crewai.tools import tool

@tool("Radar Meteorológico Local")
def check_weather_rain() -> str:
    """
    Consulta el pronóstico del tiempo para el día de hoy en la zona de operaciones (Murcia).
    Informa sobre temperaturas y la necesidad estricta de llevar paraguas.
    """
    # Coordenadas de Murcia (España)
    lat = "37.97"
    lon = "-1.208"

    # Consultamos la probabilidad máxima de precipitación diaria y las temperaturas
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,uv_index_max&timezone=auto&forecast_days=1"
    print(f"Consultando API de Open-Meteo: {url}")

    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        print(f"Datos recibidos de Open-Meteo: {data}")

        ruta_mock = os.path.join("datos", "mock_wheather.txt")
        with open(ruta_mock, "w", encoding="utf-8") as f:
            f.write(str(data))

        prob_lluvia = data['daily']['precipitation_probability_max'][0]
        temp_max = data['daily']['temperature_2m_max'][0]
        temp_min = data['daily']['temperature_2m_min'][0]

        # Lógica de decisión para el paraguas
        if prob_lluvia >= 40:
            return f"🌧️ ALERTA CLIMA: {prob_lluvia}% de probabilidad de lluvia hoy. Temperaturas: {temp_min}°C - {temp_max}°C. IMPRESCINDIBLE LLEVAR PARAGUAS."
        elif prob_lluvia > 15:
            return f"⛅ AVISO CLIMA: {prob_lluvia}% de probabilidad de lluvia débil. Temperaturas: {temp_min}°C - {temp_max}°C. Recomendable paraguas plegable por si acaso."
        else:
            return f"☀️ CLIMA SEGURO: Solo {prob_lluvia}% de probabilidad de lluvia. Temperaturas: {temp_min}°C - {temp_max}°C. Puedes dejar el paraguas en casa."
            
    except Exception as e:
        return f"Error al consultar la meteorología: {e}. Ante la duda tecnológica, coge un paraguas plegable."