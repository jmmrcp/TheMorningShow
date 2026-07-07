import requests
import urllib3
import os
from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
from urllib.parse import urlparse
from crewai.tools import tool

# 1. Silenciar la advertencia de conexión insegura
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@tool("Lector de Transporte Murcia")
def inc_transport():
    """OCR para incidencias de transporte."""
    URL = 'https://tmpmurcia.es/ultima.asp'
    try:
        resp = requests.get(URL, timeout=15, verify=False)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Buscar enlace del día
        enlace = None
        parsed = urlparse(URL)
        base = f"{parsed.scheme}://{parsed.netloc}/"
        for a in soup.find_all('a', href=True):
            if "Cuerpo.asp?codigo=" in a['href']:
                enlace = base + a['href']
                break
        
        if not enlace: return "No hay parte diario."
        
        # Buscar imagen
        r = requests.get(enlace, timeout=15, verify=False)
        sub_soup = BeautifulSoup(r.text, 'html.parser')
        img_tag = sub_soup.find('img', src=lambda x: x and '/fotos/noticias/' in x)
        
        if not img_tag: return "No imagen encontrada."
        
        img_url = img_tag['src']
        if not img_url.startswith('http'): img_url = f"https://tmpmurcia.es/{img_url.lstrip('/')}"
        
        # OCR
        img_data = requests.get(img_url, timeout=15, verify=False).content
        imagen = Image.open(BytesIO(img_data))
        with open(img_url.split('/')[-1], "wb") as f:
            f.write(img_data)
        
        # Intento robusto de OCR (Español -> Inglés fallback)
        try:
            texto = pytesseract.image_to_string(imagen, lang='spa')
        except:
            texto = pytesseract.image_to_string(imagen, lang='eng')
        
        data = {"texto": texto[:600], "enlace": enlace}
        
        ruta_mock = os.path.join("datos", "mock_transport.txt")
        with open(ruta_mock, "w", encoding="utf-8") as f:
            f.write(texto)
        
        return data
        
    except Exception as e: return f"Error transporte: {e}"