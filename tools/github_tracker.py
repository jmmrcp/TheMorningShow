import os
import requests
import json
from crewai.tools import tool

@tool("Rastreador de GitHub")
def check_github_status() -> str:
    """Se conecta a la API de GitHub para extraer Pull Requests pendientes."""
    github_token = os.environ.get("GITHUB_TOKEN")
    repo_objetivo = os.environ.get("GITHUB_TARGET_REPO", "jmmrcp/AI-Briefing") 
    
    if not github_token:
        return "Simulación GitHub: 1 PR pendiente de revisión de seguridad (Dependabot)."

    headers = {"Authorization": f"Bearer {github_token}", "Accept": "application/vnd.github.v3+json"}
    
    try:
        url_prs = f"https://api.github.com/repos/{repo_objetivo}/pulls?state=open"
        resp_prs = requests.get(url_prs, headers=headers, timeout=10)
        prs = resp_prs.json()
        
        # 💾 GENERACIÓN DE FIXTURE (MOCK)
        ruta_mock = os.path.join("datos", "mock_github.json")
        with open(ruta_mock, "w", encoding="utf-8") as f:
            json.dump(prs, f, indent=4, ensure_ascii=False)
        
        resumen = []
        if prs:
            resumen.append(f"📌 {len(prs)} Pull Request(s) abiertas en {repo_objetivo}.")
            for pr in prs[:2]:
                resumen.append(f" - [{pr['user']['login']}] {pr['title']}")
        else:
            resumen.append("✅ No hay Pull Requests pendientes.")
            
        return "\n".join(resumen)
    except Exception as e:
        return f"Error al consultar GitHub: {e}"