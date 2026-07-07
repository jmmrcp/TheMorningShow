import requests
import feedparser
import json
import os
from datetime import datetime, timedelta, timezone
from crewai.tools import tool

@tool("Radar de Ciberseguridad (NVD CVEs)")
def get_latest_cves() -> str:
    """Extrae las vulnerabilidades (CVEs) más recientes desde la base de datos oficial del NIST (NVD)."""
    
    # La API 2.0 del NVD requiere un formato de fecha estricto ISO 8601 con offset codificado
    # Formato esperado: YYYY-MM-DDThh:mm:ss.000%2B00:00
    now = datetime.now(timezone.utc)
    start_date = (now - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S.000") + "%2B00:00"
    end_date = now.strftime("%Y-%m-%dT%H:%M:%S.000") + "%2B00:00"
    
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?pubStartDate={start_date}&pubEndDate={end_date}"
    
    # El NVD permite 5 peticiones cada 30s sin API Key. 
    # Con API Key (gratuita), el límite sube a 50. Lo preparamos por si la añades.
    headers = {}
    nvd_key = os.environ.get("NVD_API_KEY")
    if nvd_key:
        headers["apiKey"] = nvd_key

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        
        alertas = []
        vulnerabilities = data.get("vulnerabilities", [])
        
        # Invertimos la lista para obtener los más recientes publicados y filtramos hasta 4
        for item in reversed(vulnerabilities):
            if len(alertas) >= 4:
                break
                
            cve = item.get("cve", {})
            cve_id = cve.get("id", "CVE-Desconocido")
            
            # Extraer descripción (Priorizamos inglés)
            desc = "Sin descripción."
            for d in cve.get("descriptions", []):
                if d.get("lang") == "en":
                    desc = d.get("value")
                    break
                    
            # Truncar descripción larga para no saturar al LLM ni la locución
            if len(desc) > 120:
                desc = desc[:117] + "..."
                
            # Extraer métricas CVSS V3.1 si están disponibles
            cvss = "N/A"
            metrics = cve.get("metrics", {})
            if "cvssMetricV31" in metrics:
                try:
                    cvss = metrics["cvssMetricV31"][0]["cvssData"]["baseScore"]
                except (IndexError, KeyError):
                    pass
            
            # Formatear salida para el agente
            titulo = f"[{cve_id}] (Score CVSS: {cvss}) - {desc}"
            enlace = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
            
            alertas.append({"titulo": titulo, "enlace": enlace})
            
        # 💾 GENERACIÓN DE FIXTURE (MOCK)
        os.makedirs("datos", exist_ok=True)
        resultado_json = json.dumps({"alertas_seguridad": alertas}, ensure_ascii=False)
        ruta_mock = os.path.join("datos", "mock_cves.json")
        
        with open(ruta_mock, "w", encoding="utf-8") as f:
            f.write(resultado_json)
            
        return resultado_json
        
    except Exception as e:
        # Fallback de seguridad en caso de caída del NIST
        return json.dumps({"error": f"Fallo al recuperar CVEs del NVD: {e}"})

@tool("Radar de Inteligencia Artificial")
def get_ai_updates() -> str:
    """Extrae las últimas actualizaciones de modelos de IA y machine learning."""
    url = "https://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=2"
    try:
        resp = requests.get(url, timeout=10)
        feed = feedparser.parse(resp.content)
        papers = [{"titulo": entry.title.replace('\n', ' ')} for entry in feed.entries]
        return json.dumps({"actualizaciones_ia": papers}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Fallo al recuperar papers de IA: {e}"})