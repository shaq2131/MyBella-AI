"""
Mood Service for MyBella
Provides mood tracking utilities and mood-based AI tone adjustments
"""

from datetime import datetime, date, timedelta
from backend.database.models.wellness_models import MoodEntry, MoodScale
from typing import Optional, Dict

class MoodService:
    """Service for mood tracking and AI tone adjustments"""
    
    @staticmethod
    def get_recent_mood(user_id: int, days: int = 1) -> Optional[MoodEntry]:
        """
        Get user's most recent mood entry within the specified timeframe
        
        Args:
            user_id: User ID
            days: Number of days to look back (default: 1)
        
        Returns:
            MoodEntry or None if no recent mood found
        """
        cutoff_date = date.today() - timedelta(days=days)
        
        mood = MoodEntry.query.filter(
            MoodEntry.user_id == user_id,
            MoodEntry.entry_date >= cutoff_date
        ).order_by(MoodEntry.entry_date.desc()).first()
        
        return mood
    
    @staticmethod
    def get_mood_context(user_id: int) -> Dict:
        """
        Get comprehensive mood context for AI adjustment
        
        Returns:
            dict: {
                'has_recent_mood': bool,
                'mood_level': int (1-10),
                'anxiety_level': int or None,
                'stress_level': int or None,
                'energy_level': int or None,
                'tone_adjustment': str,
                'days_since_checkin': int
            }
        """
        mood = MoodService.get_recent_mood(user_id, days=2)
        
        if not mood:
            return {
                'has_recent_mood': False,
                'mood_level': None,
                'anxiety_level': None,
                'stress_level': None,
                'energy_level': None,
                'tone_adjustment': None,
                'days_since_checkin': None
            }
        
        # Calculate days since check-in
        days_since = (date.today() - mood.entry_date).days
        
        # Get mood level (MoodScale is 1-10)
        mood_level = mood.overall_mood.value if hasattr(mood.overall_mood, 'value') else 5
        
        # Get additional metrics
        anxiety = mood.anxiety_level.value if mood.anxiety_level and hasattr(mood.anxiety_level, 'value') else None
        stress = mood.stress_level.value if mood.stress_level and hasattr(mood.stress_level, 'value') else None
        energy = mood.energy_level.value if mood.energy_level and hasattr(mood.energy_level, 'value') else None
        
        # Determine tone adjustment based on mood
        tone_adjustment = MoodService._get_tone_adjustment(mood_level, anxiety, stress, energy)
        
        return {
            'has_recent_mood': True,
            'mood_level': mood_level,
            'anxiety_level': anxiety,
            'stress_level': stress,
            'energy_level': energy,
            'tone_adjustment': tone_adjustment,
            'days_since_checkin': days_since
        }
    
    @staticmethod
    def _get_tone_adjustment(mood_level: int, anxiety: Optional[int] = None, 
                            stress: Optional[int] = None, energy: Optional[int] = None) -> str:
        """
        Generate AI tone adjustment prompt based on mood metrics
        
        Args:
            mood_level: Overall mood (1-10 scale)
            anxiety: Anxiety level (1-10 scale or None)
            stress: Stress level (1-10 scale or None)
            energy: Energy level (1-10 scale or None)
        
        Returns:
            str: Tone adjustment instruction for AI system prompt
        """
        # High anxiety or stress override (regardless of mood)
        if anxiety and anxiety >= 7:
            return (
                "The user is experiencing high anxiety. Use a gentle, calming tone. "
                "Be extra reassuring and grounding. Avoid overwhelming information. "
                "Suggest simple breathing exercises if appropriate."
            )
        
        if stress and stress >= 7:
            return (
                "The user is under significant stress. Be supportive and validating. "
                "Use a soothing tone. Acknowledge their challenges without minimizing them. "
                "Offer practical coping suggestions gently."
            )
        
        # Low energy consideration
        if energy and energy <= 3:
            return (
                "The user has low energy. Be gentle and understanding. "
                "Keep responses concise and easy to digest. Don't push for high-energy activities. "
                "Validate their need for rest."
            )
        
        # Mood-based tone adjustments
        if mood_level <= 2:  # VERY_LOW, LOW
            return (
                "The user is feeling quite low emotionally. Use a compassionate, gentle tone. "
                "Be validating and empathetic without being patronizing. Offer hope subtly. "
                "Avoid forced positivity. Focus on being present with them."
            )
        
        elif mood_level <= 4:  # SOMEWHAT_LOW, BELOW_AVERAGE
            return (
                "The user is experiencing some emotional difficulty. Be supportive and encouraging. "
                "Validate their feelings while gently highlighting their strengths. "
                "Use a warm, reassuring tone."
            )
        
        elif mood_level <= 6:  # AVERAGE, SOMEWHAT_GOOD
            return (
                "The user is in a balanced emotional state. Use a conversational, friendly tone. "
                "Be supportive without being overly cautious. Natural and warm interaction."
            )
        
        elif mood_level <= 8:  # GOOD, VERY_GOOD
            return (
                "The user is feeling positive. Match their upbeat energy with enthusiasm. "
                "Be encouraging and celebrate their good mood. Use an energetic, motivational tone. "
                "Reinforce positive momentum."
            )
        
        else:  # EXCELLENT, OUTSTANDING (9-10)
            return (
                "The user is in an excellent mood! Be enthusiastic and celebratory. "
                "Share in their joy with exclamation marks and positive energy. "
                "Use an upbeat, excited tone. Encourage them to savor this moment."
            )
    
    @staticmethod
    def get_mood_adjusted_prompt(base_prompt: str, user_id: int) -> str:
        """
        Adjust AI system prompt based on user's recent mood
        
        Args:
            base_prompt: Original persona system prompt
            user_id: User ID
        
        Returns:
            str: Mood-adjusted system prompt
        """
        mood_context = MoodService.get_mood_context(user_id)
        
        if not mood_context['has_recent_mood']:
            # No recent mood data - use base prompt
            return base_prompt
        
        # Add tone adjustment to base prompt
        tone_adjustment = mood_context['tone_adjustment']
        
        adjusted_prompt = f"""{base_prompt}

--- MOOD-AWARE INTERACTION ---
{tone_adjustment}

Remember: Be authentic to your persona while adapting your tone to support the user's current emotional state.
"""
        
        return adjusted_prompt
    
    @staticmethod
    def should_suggest_mood_checkin(user_id: int) -> bool:
        """
        Determine if AI should suggest a mood check-in
        
        Returns:
            bool: True if user hasn't checked in recently (2+ days)
        """
        mood_context = MoodService.get_mood_context(user_id)
        
        if not mood_context['has_recent_mood']:
            # No mood data at all - suggest check-in
            return True
        
        # Suggest if it's been 2+ days
        return mood_context['days_since_checkin'] >= 2
    
    @staticmethod
    def get_mood_checkin_prompt(persona: str = "Bella") -> str:
        """
        Generate a gentle mood check-in suggestion from the persona
        
        Args:
            persona: Persona name
        
        Returns:
            str: Natural check-in prompt
        """
        prompts = {
            'Isabella': "By the way, I haven't heard how you've been feeling lately. Would you like to do a quick mood check-in? 💙",
            'Maya': "Hey, I'm curious - how has your mood been these past few days? Want to track it together?",
            'Alex': "I've been thinking... we should check in on how you're doing emotionally. Up for a mood tracker session?",
            'Bella': "I'd love to know how you're feeling today. Want to do a mood check-in with me? 😊"
        }
        
        return prompts.get(persona, prompts['Bella'])
