"""
Voice Conversation Service for MyBella
Handles real-time voice input/output in chat (replacing old call system)
"""

import base64
import requests
from typing import Optional, Dict, Any
from flask import current_app

# Persona voice IDs for ElevenLabs
# TODO: Replace with actual voice IDs from ElevenLabs dashboard
PERSONA_VOICES = {
    'Isabella': 'EXAVITQu4vr4xnSDxMaL',  # Bella - warm female
    'Alex': 'yoZ06aMxZJJ28mfd3POQ',      # Sam - friendly male
    'Maya': 'MF3mGyEYCl7XYWbV9V6O',      # Elli - calm female
    'Luna': 'ThT5KcBeYPX3keUQqHPh',      # Dorothy - gentle female
    'Sam': 'TX3LPaxmHKxFdv7VOQHJ',       # Liam - energetic male
    'Ethan': 'pNInz6obpgDQGcFmaJgB',     # Adam - professional male
}


class VoiceConversationService:
    """Manage voice conversations in chat"""
    
    @staticmethod
    def generate_voice_response(text: str, persona: str = 'Isabella') -> Optional[bytes]:
        """
        Generate TTS audio for persona response using ElevenLabs
        
        Args:
            text: Text to convert to speech
            persona: Persona name (Isabella, Alex, etc.)
            
        Returns:
            Audio bytes (MP3 format) or None if error
        """
        api_key = current_app.config.get('ELEVENLABS_API_KEY')
        
        if not api_key:
            current_app.logger.warning('ELEVENLABS_API_KEY not configured')
            return None
        
        # Get voice ID for persona
        voice_id = PERSONA_VOICES.get(persona, PERSONA_VOICES['Isabella'])
        
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                current_app.logger.info(f'TTS generated successfully for {persona}')
                return response.content
            else:
                current_app.logger.error(f'TTS API error: {response.status_code} - {response.text}')
                return None
                
        except Exception as e:
            current_app.logger.error(f'TTS generation error: {e}')
            return None
    
    @staticmethod
    def get_persona_voice_id(persona: str) -> str:
        """
        Get ElevenLabs voice ID for a persona
        
        Args:
            persona: Persona name
            
        Returns:
            Voice ID string
        """
        return PERSONA_VOICES.get(persona, PERSONA_VOICES['Isabella'])
    
    @staticmethod
    def get_available_personas() -> Dict[str, str]:
        """
        Get all available personas with voice IDs
        
        Returns:
            Dictionary of persona names to voice IDs
        """
        return PERSONA_VOICES.copy()
    
    @staticmethod
    def validate_api_key() -> bool:
        """
        Check if ElevenLabs API key is configured
        
        Returns:
            True if API key is available
        """
        api_key = current_app.config.get('ELEVENLABS_API_KEY')
        return bool(api_key and len(api_key) > 0)
    
    @staticmethod
    def process_speech_input(audio_data: bytes, language: str = 'en-US') -> Optional[str]:
        """
        Process speech input and return text transcription
        Currently using Web Speech API on frontend, so this is a placeholder
        for future server-side speech-to-text (e.g., Deepgram, Whisper API)
        
        Args:
            audio_data: Raw audio bytes
            language: Language code for transcription
            
        Returns:
            Transcribed text or None
        """
        # TODO: Implement server-side speech-to-text if needed
        # For now, Web Speech API handles this on the client side
        current_app.logger.info('Speech input processing not yet implemented server-side')
        return None


# Convenience function for backward compatibility with existing TTS service
def generate_voice(text: str, persona: str) -> Optional[bytes]:
    """
    Generate voice audio (convenience wrapper)
    
    Args:
        text: Text to speak
        persona: Persona name
        
    Returns:
        Audio bytes or None
    """
    return VoiceConversationService.generate_voice_response(text, persona)
