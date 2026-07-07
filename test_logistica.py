import os

# Importamos las herramientas de logística y clima
from tools.transport import inc_transport
from tools.weather import check_weather_rain

def run_logistics_test():
    """Ejecuta las herramientas de movilidad y guarda los resultados como mocks."""
    
    print("\n" + "="*50)
    print("🚌 INICIANDO PRUEBAS DE LOGÍSTICA Y CLIMA 🌧️")
    print("="*50 + "\n")

    # Aseguramos que el directorio de salida existe
    os.makedirs("datos", exist_ok=True)

    # ---------------------------------------------------------
    # 1. PRUEBA DEL RADAR METEOROLÓGICO (Open-Meteo)
    # ---------------------------------------------------------
    print("📡 Ejecutando 'check_weather_rain'...")
    try:
        resultado_clima = check_weather_rain()
        print(f"Resultado del radar meteorológico: {resultado_clima}")
        # Salida por consola
        print("🟢 [ÉXITO] Respuesta obtenida:")
        print(f"   -> {resultado_clima}\n")
                
    except Exception as e:
        print(f"🔴 [FALLO] Error en la herramienta de clima: {e}\n")

    # ---------------------------------------------------------
    # 2. PRUEBA DEL LECTOR DE TRANSPORTE (Scraping/OCR)
    # ---------------------------------------------------------
    print("🚌 Ejecutando 'inc_transport' (Bypass SSL Activo)...")
    try:
        resultado_transporte = inc_transport()
        
        # Salida por consola
        print("🟢 [ÉXITO] Respuesta obtenida:")
        print(f"   -> {resultado_transporte}\n")
        
    except Exception as e:
        print(f"🔴 [FALLO] Error en la herramienta de transporte: {e}\n")

    print("="*50)
    print("✅ PRUEBAS FINALIZADAS")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_logistics_test()