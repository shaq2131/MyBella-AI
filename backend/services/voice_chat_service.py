"""
Voice Chat Service - Handles voice-enabled chat with automatic fallback
When voice minutes are available: AI responds with voice audio
When voice minutes exhausted: Automatically falls back to text-only chat
"""

from backend.database.models.models import db, UserSubscription, VoiceCall
from datetime import datetime, timedelta
import os

class VoiceChatService:
    """Service for managing voice chat with minute tracking and auto-fallback"""
    
    # Voice minute costs (in minutes)
    COST_PER_MESSAGE = 0.5  # Each AI voice response costs ~30 seconds
    
    @staticmethod
    def get_user_voice_status(user_id):
        """
        Get user's voice chat status and remaining minutes
        
        Returns:
            dict: {
                'has_voice': bool,
                'total_minutes': int,
                'used_minutes': float,
                'remaining_minutes': float,
                'subscription_type': str,
                'can_use_voice': bool
            }
        """
        subscription = UserSubscription.query.filter_by(user_id=user_id).first()
        
        if not subscription:
            # Create default free subscription
            subscription = UserSubscription(
                user_id=user_id,
                subscription_type='free',
                total_minutes=100,
                used_minutes=0.0,
                remaining_minutes=100.0
            )
            db.session.add(subscription)
            db.session.commit()
        
        remaining = subscription.get_remaining_minutes()
        
        return {
            'has_voice': True,
            'total_minutes': subscription.total_minutes,
            'used_minutes': subscription.used_minutes,
            'remaining_minutes': remaining,
            'subscription_type': subscription.subscription_type,
            'can_use_voice': remaining >= VoiceChatService.COST_PER_MESSAGE,
            'minutes_per_message': VoiceChatService.COST_PER_MESSAGE
        }
    
    @staticmethod
    def deduct_voice_minutes(user_id, minutes_used):
        """
        Deduct voice minutes from user's allocation
        
        Args:
            user_id: User ID
            minutes_used: Minutes to deduct (float)
        
        Returns:
            dict: Updated voice status
        """
        subscription = UserSubscription.query.filter_by(user_id=user_id).first()
        
        if not subscription:
            raise ValueError("No subscription found for user")
        
        # Deduct minutes
        subscription.used_minutes += minutes_used
        subscription.remaining_minutes = subscription.get_remaining_minutes()
        subscription.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return VoiceChatService.get_user_voice_status(user_id)
    
    @staticmethod
    def should_use_voice(user_id):
        """
        Check if user should get voice response or text fallback
        
        Returns:
            bool: True if voice should be used, False for text-only
        """
        status = VoiceChatService.get_user_voice_status(user_id)
        return status['can_use_voice']
    
    @staticmethod
    def generate_voice_response(text, persona='Bella', user_id=None):
        """
        Generate voice audio from text using ElevenLabs
        If user has no minutes, return None (fallback to text)
        
        Args:
            text: Text to convert to speech
            persona: Persona name for voice selection
            user_id: User ID for minute tracking
        
        Returns:
            dict: {
                'audio_url': str or None,
                'text': str,
                'voice_used': bool,
                'minutes_used': float,
                'remaining_minutes': float
            }
        """
        # Check if user can use voice
        if user_id and not VoiceChatService.should_use_voice(user_id):
            return {
                'audio_url': None,
                'text': text,
                'voice_used': False,
                'minutes_used': 0.0,
                'remaining_minutes': 0.0,
                'fallback_reason': 'Voice minutes exhausted'
            }
        
        # Check if ElevenLabs is configured
        elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
        if not elevenlabs_key:
            return {
                'audio_url': None,
                'text': text,
                'voice_used': False,
                'minutes_used': 0.0,
                'remaining_minutes': VoiceChatService.get_user_voice_status(user_id)['remaining_minutes'],
                'fallback_reason': 'ElevenLabs API not configured'
            }
        
        try:
            # Import ElevenLabs service
            from backend.services.elevenlabs.elevenlabs_service import ElevenLabsService
            
            # Get persona voice ID
            voice_id = ElevenLabsService.get_persona_voice_id(persona)
            
            # Generate voice audio
            audio_data = ElevenLabsService.text_to_speech(text, voice_id)
            
            if audio_data:
                # Save audio file
                filename = f"voice_{user_id}_{datetime.utcnow().timestamp()}.mp3"
                audio_path = os.path.join('backend', 'database', 'instances', 'uploads', 'voice_responses', filename)
                
                # Create directory if not exists
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                
                # Save audio
                with open(audio_path, 'wb') as f:
                    f.write(audio_data)
                
                # Deduct voice minutes (estimate based on text length)
                # Roughly: 150 words per minute of speech
                words = len(text.split())
                minutes_used = max(VoiceChatService.COST_PER_MESSAGE, words / 150.0)
                
                if user_id:
                    status = VoiceChatService.deduct_voice_minutes(user_id, minutes_used)
                else:
                    status = {'remaining_minutes': 0}
                
                return {
                    'audio_url': f'/uploads/voice_responses/{filename}',
                    'text': text,
                    'voice_used': True,
                    'minutes_used': minutes_used,
                    'remaining_minutes': status.get('remaining_minutes', 0)
                }
            
        except Exception as e:
            print(f"Voice generation error: {e}")
        
        # Fallback to text
        return {
            'audio_url': None,
            'text': text,
            'voice_used': False,
            'minutes_used': 0.0,
            'remaining_minutes': VoiceChatService.get_user_voice_status(user_id)['remaining_minutes'],
            'fallback_reason': 'Voice generation failed'
        }
    
    @staticmethod
    def get_subscription_limits():
        """Get voice minute limits for each subscription tier"""
        return {
            'free': {
                'minutes': 100,
                'price': 0,
                'description': '100 voice minutes per month'
            },
            'basic': {
                'minutes': 500,
                'price': 9.99,
                'description': '500 voice minutes per month'
            },
            'premium': {
                'minutes': 999999,
                'price': 19.99,
                'description': 'Unlimited voice chat'
            }
        }
    
    @staticmethod
    def reset_monthly_minutes():
        """
        Reset voice minutes for all users (run monthly via cron)
        """
        subscriptions = UserSubscription.query.all()
        
        for sub in subscriptions:
            # Reset used minutes
            sub.used_minutes = 0.0
            sub.remaining_minutes = sub.total_minutes
            sub.updated_at = datetime.utcnow()
        
        db.session.commit()
    print(f"Reset voice minutes for {len(subscriptions)} users")
