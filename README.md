# 🤖 AI-Briefing DevSecOps (Chief of Staff)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CrewAI](https://img.shields.io/badge/AI-CrewAI-orange)
![Structure](https://img.shields.io/badge/Architecture-Modular-purple)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

Un sistema de **Agentes de IA Autónomos** diseñado para actuar como un Jefe de Gabinete personal. Este "Crew" se despierta, consulta múltiples fuentes de datos (Gmail, Calendar, Bolsa, Transporte Urbano) y redacta un **Briefing Matutino** conciso y accionable, enviándolo directamente a tu móvil.

---

**AI-Briefing** es un sistema multiagente autónomo de última generación diseñado específicamente para orquestar, optimizar y revolucionar la rutina matutina de un ingeniero de DevSecOps, SRE (Site Reliability Engineer) o líder de infraestructura técnica. En un ecosistema tecnológico moderno, donde la fatiga por alertas (alert fatigue), el exceso de notificaciones multiplataforma y la fragmentación masiva de la información son el pan de cada día, este sistema interviene proactivamente para eliminar el "ruido blanco", priorizar incidentes y reducir drásticamente la sobrecarga cognitiva.

Actuando como un verdadero "Jefe de Gabinete" (Chief of Staff) digital y ultra-personalizado, el sistema asume la responsabilidad delegada de recopilar, filtrar, correlacionar y sintetizar de manera inteligente volúmenes masivos de datos provenientes de múltiples fuentes heterogéneas. Estas fuentes abarcan una visión de 360 grados de la vida del ingeniero:

* **El entorno físico y logístico:** Estado del tráfico local, alertas meteorológicas severas, horarios de transporte público (incluyendo incidencias locales mediante OCR).
* **La infraestructura corporativa y observabilidad:** Repositorios de código (PRs bloqueantes), tickets de gestión de cambios críticos (CRQ), logs de operaciones nocturnas en chats no estructurados y alertas globales de vulnerabilidades *zero-day*.
* **El ámbito estrictamente personal y de agenda:** Reuniones clave del día, bloqueos de calendario, correos prioritarios no leídos de *stakeholders* VIP y tareas críticas pendientes.

El resultado final de este procesamiento orquestado no es un simple panel de control estático o un dashboard más que revisar, sino un **briefing ejecutivo diario, conversacional y altamente priorizado**. Este resumen es transmitido mediante una locución de voz de alta fidelidad directamente a través de Telegram. Esto permite al profesional prepararse mentalmente para los desafíos más críticos de su jornada mientras se desplaza a la oficina, se prepara el desayuno o toma su primer café, brindándole el contexto táctico exacto que necesita sin necesidad de abrir su ordenador portátil ni ahogarse en bandejas de entrada abarrotadas desde el minuto cero de la mañana.

Este proyecto ha sido desarrollado como Capstone Project para la categoría **"Concierge Agents"** del Hackathon, demostrando cómo la inteligencia artificial generativa, cuando es orquestada mediante principios de ingeniería DevSecOps, puede trascender la mera automatización de tareas repetitivas para convertirse en un aliado estratégico y un copiloto indispensable en la gestión integral de operaciones de alta criticidad.

---

## ✨ Características Principales y Arquitectura del Enjambre

El corazón del sistema utiliza el framework **CrewAI** emparejado con modelos LLM de alto rendimiento (Google Gemini 1.5 Flash) para coordinar un "enjambre" (swarm) de agentes especializados, cada uno con un rol, objetivo y conjunto de herramientas definidos:

* **🛡️ Analista de Ciberseguridad (Integración NVD NIST):** En lugar de depender de feeds de noticias genéricos, este agente se conecta directamente a la API 2.0 del Instituto Nacional de Estándares y Tecnología (NIST). Extrae los últimos CVEs (Common Vulnerabilities and Exposures) y aplica lógica de negocio para filtrar incidentes, destacando únicamente aquellos que superan un umbral crítico de puntuación CVSS V3.1 (ej. scores > 7.0), traduciendo la jerga técnica a un impacto de negocio comprensible.
* **🧑‍💻 Coordinador de Infraestructura y Despliegues (GitHub & ITSM):** Evita cuellos de botella en los pipelines de CI/CD rastreando Pull Requests pendientes de revisión vía GitHub API. Paralelamente, parsea tickets de cambios planificados (CRQ) exportados de plataformas ITSM corporativas como BMC Helix o ServiceNow, utilizando Expresiones Regulares (Regex) avanzadas para aislar la fecha, el impacto y los sistemas afectados.
* **📟 Ingeniero de Operaciones / Handoff Nocturno (WhatsApp/Slack):** Entiende que gran parte de la comunicación crítica de TI ocurre en canales no estructurados. Este agente lee exportaciones de chats de guardias nocturnas, aislando verdaderas caídas de red o problemas de hardware ocurridos de madrugada, e ignorando conversaciones triviales o despedidas de turno ("Todo OK", "Buenas noches").
* **📅 Asistente Ejecutivo Personal (Google Workspace):** Mediante una robusta autenticación OAuth 2.0 basada en el principio de mínimo privilegio (estrictos permisos `readonly`), este agente se infiltra de forma segura en tu ecosistema de Google. Lee citas superpuestas en **Google Calendar**, prioriza tareas urgentes de **Google Tasks** y escanea **Gmail** en busca de correos de remitentes VIP recibidos en las últimas 24 horas.
* **🌧️ Analista de Logística Urbana y Entorno:** Combina técnicas de web scraping y Reconocimiento Óptico de Caracteres (Tesseract OCR) con estrategias tácticas de SSL-bypass para extraer horarios e incidencias en imágenes publicadas por servicios de autobuses locales. Esta información logística se cruza en tiempo real con datos meteorológicos milimétricos de la API **Open-Meteo**, calculando la probabilidad de lluvia para emitir recomendaciones tangibles (ej. "Lleva un paraguas hoy").
* **🎙️ Director de Comunicaciones (Síntesis de Voz Dinámica):** El último eslabón de la cadena. Soporta múltiples motores Text-to-Speech (TTS). Permite integración directa con **ElevenLabs** y **OpenAI TTS-1** para generar un audio con entonación hiperrealista, pausas dramáticas y un tono ejecutivo profesional. Para entornos de desarrollo local, incluye un fallback a **gTTS** (Google TTS), garantizando pruebas ilimitadas a coste cero.

---

## 🛠️ Resiliencia y Buenas Prácticas (DevSecOps)

* **Snapshot Testing / Offline Mode:** Por diseño, todas las herramientas cachean su último payload exitoso en la carpeta `datos/` (ej. `mock_cves.json`, `mock_transport.txt`). Esto sirve como traza de auditoría y permite que el sistema funcione mediante degradación elegante (Mocks) si las APIs externas sufren caídas.
* **Principio de Mínimo Privilegio:** Los *scopes* de Google Workspace están limitados exclusivamente a lectura (`readonly`), garantizando que un compromiso del token no permita la modificación o envío de datos.
* **Degradación Elegante en Mensajería:** Si el motor de audio falla o se agota la cuota de la API, el sistema alerta del error de forma silenciosa y envía el texto completo para asegurar que la información siempre llegue.

---

## 🚀 Requisitos e Instalación

### 1. Dependencias del Sistema

Necesitas instalar el motor OCR en tu sistema operativo:

* **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`
* **Windows:** Instalar el binario de Tesseract y añadirlo al PATH.

### 2. Entorno Python

```bash
# Crear entorno (opcional)
conda create -n ai-briefing python=3.12
conda activate ai-briefing

# Instalar dependencias
pip install -r requirements.txt

```

### 3. Configuración de Credenciales

Crea un archivo `.env` en la raíz con las siguientes variables:

```env
GOOGLE_API_KEY="tu_gemini_api_key"
TELEGRAM_TOKEN="tu_bot_token"
TELEGRAM_CHAT_ID="tu_id_de_chat"
GITHUB_TOKEN="tu_github_token"
NVD_API_KEY="opcional_para_cve"
# Interruptor de Voz (False = gTTS gratis / True = ElevenLabs)
USE_PRO_TTS=False 
ELEVENLABS_API_KEY="tu_elevenlabs_key"

```

**Google Workspace (OAuth 2.0):** 1. Descarga tu `credentials.json` desde Google Cloud Console.
2. Ejecuta localmente `python diagnostics.py` para autorizar la app en tu navegador.
3. Se generará un archivo `token.json` que mantendrá la sesión activa de forma segura.

---

## 📱 Uso: El CLI de Telegram

El sistema expone un webhook a través de Telegram para funcionar como un Centro de Operaciones de bolsillo. Comandos disponibles:

* `/start` o `/help` - Muestra el menú de ayuda.
* `/briefing` - 🚀 Ejecuta el enjambre completo de agentes y genera el audio matutino.
* `/cve` - Consulta instantánea a la base de datos del NVD (sin ejecutar LLMs).
* `/logistica` - Consulta del estado del transporte (OCR) y clima.
* `/ops` - Lector inmediato del log de operaciones de infraestructura.
* `/ping` - Health check del bot.

---

## 🧪 Testing y Diagnósticos

El repositorio incluye una batería de pruebas para garantizar la fiabilidad del despliegue:

**1. Pruebas de Integración (Health Check):**
Verifica tokens, conectividad de red y permisos de lectura sin gastar cuota de LLM.

```bash
python diagnostics.py

```

**2. Pruebas Unitarias (Pytest):**
Evalúa el parseo de Regex, OCR y fallos de API aislando las respuestas de red mediante Mocks.

```bash
pytest tests/test_tools.py -v

```

---

## 💰 Viabilidad Financiera (OpEx)

La arquitectura es fuertemente *serverless* y prioriza las capas gratuitas de grado industrial.

| **Concepto de Gasto** | **Consumo Estimado** | **Coste Semanal** |
| --- | --- | --- |
| **LLM (Gemini 1.5 Flash)** | ~120k tokens totales. | $0.00 (Free Tier) |
| **Clima & Ciberseguridad** | APIs Públicas (Open-Meteo, NVD). | $0.00 |
| **Síntesis de Voz (TTS)** | ElevenLabs (Free Tier) o gTTS. | $0.00 |
| **Infraestructura CI/CD** | GitHub Actions / Máquina Local | $0.00 |
| **TOTAL** | Operación Diaria Continua | **$0.00** |

*Desarrollado para la mejora de flujos de trabajo en equipos DevSecOps de alto rendimiento.*

```

¡Espero que ahora puedas copiarlo sin problemas y quede perfecto en tu proyecto! Si necesitas algo más antes de la entrega final, aquí sigo.

```
