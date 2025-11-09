"""
ElevenLabs Text-to-Speech service for MyBella
Handles voice synthesis and voice uploading
"""

import base64
import requests
from flask import current_app, session
from backend.database.utils.utils import get_persona_voice_id, set_persona_voice_id

def generate_speech(text, persona, user_id, voice_id=None):
    """Generate speech audio using ElevenLabs API"""
    elevenlabs_api_key = current_app.config.get('ELEVENLABS_API_KEY')
    
    if not elevenlabs_api_key:
        return {
            "audio_b64": None,
            "note": "(demo) Provide ELEVENLABS_API_KEY to enable audio."
        }
    
    if not voice_id:
        voice_id = resolve_persona_voice_id(user_id, persona)
    
    try:
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": elevenlabs_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.7
            }
        }
        
        response = requests.post(tts_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        audio_b64 = base64.b64encode(response.content).decode('utf-8')
        return {"audio_b64": audio_b64}
        
    except Exception as e:
        current_app.logger.debug(f"TTS error: {e}")
        return {"error": str(e), "audio_b64": None}

def resolve_persona_voice_id(user_id, persona):
    """Resolve voice ID for a persona (env default -> Firestore -> session cache)"""
    # Start with environment default
    voice_id = session.get("voice_override") or current_app.config.get('ELEVENLABS_VOICE_ID')
    
    # Try Firestore persona voice
    firestore_voice_id = get_persona_voice_id(user_id, persona)
    if firestore_voice_id:
        voice_id = firestore_voice_id
    
    # Session cache fallback
    try:
        cache = session.get("voice_ids", {})
        cached_voice_id = cache.get(persona.lower())
        if cached_voice_id:
            voice_id = cached_voice_id
    except Exception:
        pass
    
    return voice_id

def upload_voice(file, voice_name, persona, user_id):
    """Upload custom voice to ElevenLabs"""
    elevenlabs_api_key = current_app.config.get('ELEVENLABS_API_KEY')
    
    if not elevenlabs_api_key:
        return {
            "ok": False,
            "error": "(demo) ELEVENLABS_API_KEY missing; cannot upload."
        }
    
    try:
        url = "https://api.elevenlabs.io/v1/voices/add"
        headers = {"xi-api-key": elevenlabs_api_key}
        data = {"name": voice_name}
        
        # Try primary upload method
        response = requests.post(
            url,
            headers=headers,
            files={"files": (file.filename, file.stream, file.mimetype or "audio/mpeg")},
            data=data,
            timeout=120
        )
        
        voice_id = None
        try:
            resp_data = response.json()
            voice_id = resp_data.get("voice_id") or resp_data.get("id")
        except Exception:
            resp_data = None
        
        # Fallback upload method if first fails
        if response.status_code >= 400 or not voice_id:
            try:
                file.stream.seek(0)
            except Exception:
                pass
            
            response2 = requests.post(
                url,
                headers=headers,
                files={"file": (file.filename, file.stream, file.mimetype or "audio/mpeg")},
                data=data,
                timeout=120
            )
            
            try:
                resp_data = response2.json()
                voice_id = resp_data.get("voice_id") or resp_data.get("id")
            except Exception:
                pass
            
            if response2.status_code >= 400 and not voice_id:
                return {
                    "ok": False,
                    "error": f"ElevenLabs error {response2.status_code}",
                    "details": resp_data
                }
        
        # If still no voice_id, try to find it by name
        if not voice_id:
            voice_id = _find_voice_by_name(voice_name, elevenlabs_api_key)
        
        if not voice_id:
            return {
                "ok": False,
                "error": "Could not determine new voice_id from ElevenLabs response."
            }
        
        # Persist voice_id per user+persona
        set_persona_voice_id(user_id, persona, voice_id)
        
        # Also cache in session
        cache = session.get("voice_ids", {})
        cache[persona.lower()] = voice_id
        session["voice_ids"] = cache
        
        return {
            "ok": True,
            "voice_id": voice_id,
            "persona": persona
        }
        
    except Exception as e:
        return {"ok": False, "error": str(e)}

def _find_voice_by_name(voice_name, api_key):
    """Find voice ID by name in user's ElevenLabs voices"""
    try:
        response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": api_key},
            timeout=60
        )
        voices_data = response.json()
        
        for voice in voices_data.get("voices", []):
            if voice.get("name") == voice_name:
                return voice.get("voice_id") or voice.get("id")
                
    except Exception:
        pass
    
    return None