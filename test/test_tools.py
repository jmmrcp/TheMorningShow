# Archivo: tests/test_tools.py

import pytest
import json
from unittest.mock import patch, mock_open

# Importación de las herramientas a testear
from tools.ops_reader import read_shift_handoff
from tools.exchange_reader import read_itsm_tickets
from tools.cyber_ai import get_latest_cves
from tools.github_tracker import check_github_status

# ==========================================
# TEST 1: Lector de Traspaso de Turnos (WhatsApp)
# ==========================================
@patch('os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open, read_data="20:44\nCésar: Router reiniciado en planta baja\n21:00\nJuan: Todo OK")
def test_read_shift_handoff_success(mock_file, mock_exists):
    """Prueba que la herramienta lee correctamente las últimas líneas del archivo de texto."""
    resultado = read_shift_handoff()
    
    assert "Router reiniciado" in resultado
    assert "Todo OK" in resultado
    mock_file.assert_called_once_with("datos/whatsapp_export.txt", 'r', encoding='utf-8')

# ==========================================
# TEST 2: Lector de Tickets ITSM (BMC Helix)
# ==========================================
CORREO_MOCK = """
Infrastructure Change ID: CRQ0000012345
Summary: Actualización de firewall perimetral
Scheduled Start Date: 05/07/2026 22:00:00
Indique Ubicación: CPD Principal
"""

@patch('os.path.exists', return_value=True)
@patch('builtins.open', new_callable=mock_open, read_data=CORREO_MOCK)
def test_read_itsm_tickets_regex(mock_file, mock_exists):
    """Prueba que las Expresiones Regulares extraen los campos clave ignorando el ruido."""
    resultado = read_itsm_tickets()
    
    assert "CRQ0000012345" in resultado
    assert "Actualización de firewall perimetral" in resultado
    assert "CPD Principal" in resultado
    assert "Ticket detectado" in resultado

# ==========================================
# TEST 3: Ciberseguridad (Extracción de CVEs)
# ==========================================
# Simulamos una respuesta XML de un feed RSS
MOCK_RSS_FEED = b"""
<rss><channel>
    <item>
        <title>CRÍTICO: Vulnerabilidad Zero-Day en OpenSSH (CVE-2026-9999)</title>
        <link>https://thehackernews.com/cve-2026-9999</link>
    </item>
</channel></rss>
"""

@patch('requests.get')
def test_get_latest_cves_success(mock_get):
    """Prueba que el parseador RSS convierte las alertas en un JSON válido."""
    # Configuramos el mock para que devuelva nuestro XML falso
    mock_get.return_value.content = MOCK_RSS_FEED
    
    resultado_str = get_latest_cves()
    datos = json.loads(resultado_str)
    
    assert "alertas_seguridad" in datos
    assert len(datos["alertas_seguridad"]) > 0
    assert datos["alertas_seguridad"][0]["titulo"] == "CRÍTICO: Vulnerabilidad Zero-Day en OpenSSH (CVE-2026-9999)"

# ==========================================
# TEST 4: Estado de GitHub (Pull Requests)
# ==========================================
MOCK_GITHUB_API_RESPONSE = [
    {"title": "Fix: Actualización de dependencias críticas", "user": {"login": "dev_ops_ninja"}}
]

@patch('os.environ.get')
@patch('requests.get')
def test_check_github_status_success(mock_get, mock_env):
    """Prueba la conexión a la API de GitHub y el formateo de PRs pendientes."""
    # Simulamos que tenemos un token en el entorno
    mock_env.return_value = "token_falso_123"
    
    # Simulamos la respuesta JSON de la API de GitHub
    mock_get.return_value.json.return_value = MOCK_GITHUB_API_RESPONSE
    
    resultado = check_github_status()
    
    assert "Pull Request(s) abiertas" in resultado
    assert "Fix: Actualización de dependencias críticas" in resultado
    assert "[dev_ops_ninja]" in resultado