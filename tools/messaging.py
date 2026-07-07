import os
import requests
from crewai.tools import tool
from openai import OpenAI
from gtts import gTTS
from config import USE_PRO_TTS

@tool("Enviar Briefing en Audio")
def send_audio_telegram(texto_guion: str) -> str:
    """Convierte el guion a voz (TTS) y lo envía por Telegram como archivo de audio."""
    telegram_token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if not all([telegram_token, chat_id, openai_key]): 
        return "Error: Faltan credenciales para TTS o Telegram."
    
    archivo_audio = "briefing_matutino.mp3"
    
    try:
        # 1. Generación de Audio con OpenAI (Voz 'alloy' - neutra y profesional)
        client = OpenAI(api_key=openai_key)
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=texto_guion
        )
        response.stream_to_file(archivo_audio)
        
        # 2. Envío del archivo de audio por Telegram
        url = f"https://api.telegram.org/bot{telegram_token}/sendAudio"
        with open(archivo_audio, 'rb') as audio:
            payload = {"chat_id": chat_id, "caption": "🎙️ Tu Briefing Ejecutivo de hoy."}
            files = {"audio": audio}
            requests.post(url, data=payload, files=files, timeout=20)
            
        return "Audio generado y enviado por Telegram con éxito."
        
    except Exception as e: 
        return f"Error en la generación o envío de audio: {e}"
    finally:
        # Limpieza del archivo temporal
        if os.path.exists(archivo_audio):
            os.remove(archivo_audio)

@tool("Enviar Briefing Multimedia")
def send_multimedia_telegram(texto_guion: str) -> str:
    """Envía el guion por texto y genera una locución en MP3 (Modo Pruebas o Producción)."""
    telegram_token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not all([telegram_token, chat_id]): 
        return "Error: Faltan credenciales de Telegram en el entorno."
    
    archivo_audio = "briefing_matutino.mp3"
    url_base = f"https://api.telegram.org/bot{telegram_token}"
    
    # FASE 1: Envío garantizado del texto
    try:
        payload_text = {"chat_id": chat_id, "text": texto_guion, "parse_mode": "Markdown"}
        requests.post(f"{url_base}/sendMessage", json=payload_text, timeout=10)
    except Exception as e:
        return f"Error crítico: Imposible contactar con la API de Telegram: {e}"

    # FASE 2: Generación Inteligente de Audio
    try:
        if USE_PRO_TTS:
            # 🚀 MODO PRODUCCIÓN: Motor Profesional OpenAI
            openai_key = os.environ.get("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError("Falta OPENAI_API_KEY en el entorno para usar el modo PRO.")
            
            client = OpenAI(api_key=openai_key)
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=texto_guion
            )
            response.stream_to_file(archivo_audio)
            caption_texto = "🎙️ Briefing Ejecutivo (Voz PRO - OpenAI)"
            
        else:
            # 🛠️ MODO PRUEBAS: Motor Gratuito gTTS
            tts = gTTS(text=texto_guion, lang='es', tld='es')
            tts.save(archivo_audio)
            caption_texto = "🎙️ Briefing Ejecutivo (Modo Pruebas - gTTS)"
        
        # Transmisión del archivo MP3 generado
        with open(archivo_audio, 'rb') as audio:
            payload_audio = {"chat_id": chat_id, "caption": caption_texto}
            requests.post(f"{url_base}/sendAudio", data=payload_audio, files={"audio": audio}, timeout=20)
            
        estado_final = f"Transmisión multimedia completada con éxito. (Modo PRO: {USE_PRO_TTS})"
        
    except Exception as error_tts: 
        # DEGRADACIÓN ELEGANTE: Notifica el fallo del audio sin afectar el texto
        payload_fallback = {
            "chat_id": chat_id, 
            "text": f"⚠️ *Aviso del Sistema:* Fallo en la generación de audio ({error_tts}). El texto superior está completo.", 
            "parse_mode": "Markdown"
        }
        requests.post(f"{url_base}/sendMessage", json=payload_fallback, timeout=10)
        estado_final = f"Transmisión degradada: Texto enviado correctamente. Fallo en TTS (Modo PRO: {USE_PRO_TTS})."
        
    finally:
        # Limpieza del contenedor/disco
        if os.path.exists(archivo_audio):
            os.remove(archivo_audio)
            
    return estado_final

@tool("Enviar Briefing Multimedia (Optimizado)")
def send_multimedia(texto_guion: str) -> str:
    """Envía el guion por texto y genera una locución en MP3 (Modo Pruebas o ElevenLabs)."""
    telegram_token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not all([telegram_token, chat_id]): 
        return "Error: Faltan credenciales de Telegram."
    
    archivo_audio = "briefing_matutino.mp3"
    url_base = f"https://api.telegram.org/bot{telegram_token}"
    
    # FASE 1: Envío garantizado del texto
    try:
        payload_text = {"chat_id": chat_id, "text": texto_guion, "parse_mode": "Markdown"}
        requests.post(f"{url_base}/sendMessage", json=payload_text, timeout=10)
    except Exception as e:
        return f"Error crítico: Imposible contactar con la API de Telegram: {e}"

    # FASE 2: Generación Inteligente de Audio
    try:
        if USE_PRO_TTS:
            # 🚀 MODO PRODUCCIÓN: Motor Profesional ElevenLabs
            eleven_key = os.environ.get("ELEVENLABS_API_KEY")
            if not eleven_key:
                raise ValueError("Falta ELEVENLABS_API_KEY en el entorno.")
            
            # Reemplaza esto con el ID de la voz en español que elijas en ElevenLabs
            voice_id = "pNInz6obpgDQGcFmaJcg" # ID de ejemplo
            
            url_tts = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": eleven_key
            }
            data = {
                "text": texto_guion,
                "model_id": "eleven_multilingual_v2", # Fundamental para español nativo
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = requests.post(url_tts, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            with open(archivo_audio, 'wb') as f:
                f.write(response.content)
                
            caption_texto = "🎙️ Briefing Ejecutivo (Voz PRO - ElevenLabs)"
            
        else:
            # 🛠️ MODO PRUEBAS: Motor Gratuito gTTS
            tts = gTTS(text=texto_guion, lang='es', tld='es')
            tts.save(archivo_audio)
            caption_texto = "🎙️ Briefing Ejecutivo (Modo Pruebas - gTTS)"
        
        # Transmisión del archivo MP3 generado
        with open(archivo_audio, 'rb') as audio:
            payload_audio = {"chat_id": chat_id, "caption": caption_texto}
            requests.post(f"{url_base}/sendAudio", data=payload_audio, files={"audio": audio}, timeout=20)
            
        estado_final = f"Transmisión multimedia completada con éxito. (Modo PRO: {USE_PRO_TTS})"
        
    except Exception as error_tts: 
        # DEGRADACIÓN ELEGANTE
        payload_fallback = {
            "chat_id": chat_id, 
            "text": f"⚠️ *Aviso del Sistema:* Fallo en la generación de audio ({error_tts}).", 
            "parse_mode": "Markdown"
        }
        requests.post(f"{url_base}/sendMessage", json=payload_fallback, timeout=10)
        estado_final = f"Transmisión degradada: Fallo en TTS (Modo PRO: {USE_PRO_TTS})."
        
    finally:
        if os.path.exists(archivo_audio):
            os.remove(archivo_audio)
            
    return estado_final