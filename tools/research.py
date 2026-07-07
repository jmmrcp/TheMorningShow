import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from crewai.tools import tool

@tool("Investigacion Web")
def web_search(query: str) -> str:
    """
    Ejecuta una búsqueda en internet en tiempo real. 
    Útil para investigar entidades, clientes o noticias específicas extraídas de la agenda.
    """
    try:
        resultados = DDGS().text(query, max_results=3)
        if not resultados:
            return "La búsqueda no arrojó resultados concluyentes."
        return str(resultados)
    except Exception as e:
        return f"Excepción durante la búsqueda web: {e}"

@tool("Lector de Articulos Web")
def read_webpage(url: str) -> str:
    """
    Extrae y devuelve el texto principal de una página web pública.
    Útil cuando se necesita analizar el contexto completo de un enlace provisto en un correo o noticia.
    """
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Extracción de todos los párrafos de texto
        parrafos = soup.find_all('p')
        texto_limpio = ' '.join([p.text.strip() for p in parrafos if p.text.strip()])
        
        # Se limita la salida para proteger la ventana de contexto del LLM
        return texto_limpio[:2500] 
    except Exception as e:
        return f"Excepción durante la extracción del artículo: {e}"