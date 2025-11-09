"""
Professional Onboarding Service
Handles 60-second personalization quiz for new users
"""

from datetime import datetime
from typing import Dict, Optional, List, Any
from sqlalchemy.orm import Session

from backend.database.models.models import db, User, UserSettings, PersonaProfile
from backend.database.models.onboarding_models import OnboardingQuiz


class OnboardingService:
    """
    Service for managing user onboarding flow
    
    Features:
    - Create/retrieve onboarding quiz
    - Save quiz responses incrementally
    - Calculate completion percentage
    - Apply preferences to UserSettings
    - Recommend personas based on answers
    """
    
    @staticmethod
    def get_or_create_quiz(user_id: int) -> OnboardingQuiz:
        """
        Get existing quiz or create new one for user
        
        Args:
            user_id: User ID
            
        Returns:
            OnboardingQuiz instance
        """
        quiz = OnboardingQuiz.query.filter_by(user_id=user_id).first()
        
        if not quiz:
            quiz = OnboardingQuiz(user_id=user_id)
            db.session.add(quiz)
            db.session.commit()
        
        return quiz
    
    @staticmethod
    def get_quiz_status(user_id: int) -> Dict[str, Any]:
        """
        Get onboarding quiz status for user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with completion status and data
        """
        quiz = OnboardingQuiz.query.filter_by(user_id=user_id).first()
        
        if not quiz:
            return {
                'completed': False,
                'completion_percentage': 0,
                'quiz_data': None
            }
        
        return {
            'completed': quiz.completed,
            'completion_percentage': quiz.calculate_completion(),
            'quiz_data': {
                'primary_goal': quiz.primary_goal,
                'secondary_goals': quiz.get_secondary_goals_list(),
                'initial_mood': quiz.initial_mood,
                'preferred_tone': quiz.preferred_tone,
                'personality_preference': quiz.personality_preference,
                'preferred_check_in_time': quiz.preferred_check_in_time,
                'selected_persona_id': quiz.selected_persona_id
            }
        }
    
    @staticmethod
    def update_quiz_response(user_id: int, question_data: Dict[str, Any]) -> OnboardingQuiz:
        """
        Update quiz with answer to specific question
        
        Args:
            user_id: User ID
            question_data: Dictionary with question responses
            
        Returns:
            Updated OnboardingQuiz instance
            
        Example question_data:
            {
                'primary_goal': 'mental_health',
                'secondary_goals': ['companionship', 'productivity'],
                'initial_mood': 7,
                'preferred_tone': 'supportive',
                'personality_preference': 'empathetic',
                'preferred_check_in_time': 'morning',
                'selected_persona_id': 3
            }
        """
        quiz = OnboardingService.get_or_create_quiz(user_id)
        
        # Update fields if present in question_data
        if 'primary_goal' in question_data:
            quiz.primary_goal = question_data['primary_goal']
        
        if 'secondary_goals' in question_data:
            quiz.set_secondary_goals_list(question_data['secondary_goals'])
        
        if 'initial_mood' in question_data:
            quiz.initial_mood = question_data['initial_mood']
        
        if 'preferred_tone' in question_data:
            quiz.preferred_tone = question_data['preferred_tone']
        
        if 'personality_preference' in question_data:
            quiz.personality_preference = question_data['personality_preference']
        
        if 'preferred_check_in_time' in question_data:
            quiz.preferred_check_in_time = question_data['preferred_check_in_time']
        
        if 'selected_persona_id' in question_data:
            quiz.selected_persona_id = question_data['selected_persona_id']
        
        quiz.updated_at = datetime.utcnow()
        db.session.commit()
        
        return quiz
    
    @staticmethod
    def complete_onboarding(user_id: int, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete onboarding and apply preferences to UserSettings
        
        Args:
            user_id: User ID
            quiz_data: Full quiz response data
            
        Returns:
            Dictionary with success status and applied settings
        """
        # Get or create user settings
        user_settings = UserSettings.query.filter_by(user_id=user_id).first()
        if not user_settings:
            user_settings = UserSettings(user_id=user_id)
            db.session.add(user_settings)
        
        # Update quiz with final responses
        quiz = OnboardingService.update_quiz_response(user_id, quiz_data)
        
        # Apply preferences to UserSettings
        if quiz.selected_persona_id:
            user_settings.current_persona_id = quiz.selected_persona_id
        
        if quiz.preferred_tone:
            # Map tone to response style
            tone_mapping = {
                'friendly': 'conversational',
                'professional': 'formal',
                'casual': 'casual',
                'supportive': 'empathetic'
            }
            user_settings.preferred_response_style = tone_mapping.get(
                quiz.preferred_tone, 
                'conversational'
            )
        
        if quiz.preferred_check_in_time:
            user_settings.notification_frequency = quiz.preferred_check_in_time
        
        # Enable features based on primary goal
        if quiz.primary_goal == 'mental_health':
            user_settings.wellness_check_enabled = True
            user_settings.crisis_detection_enabled = True
        elif quiz.primary_goal == 'productivity':
            user_settings.wellness_check_enabled = True
        elif quiz.primary_goal == 'companionship':
            user_settings.memory_enabled = True
        
        # Mark quiz as completed
        quiz.completed = True
        quiz.completed_at = datetime.utcnow()
        quiz.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return {
            'success': True,
            'quiz_completed': True,
            'applied_settings': {
                'current_persona_id': user_settings.current_persona_id,
                'preferred_response_style': user_settings.preferred_response_style,
                'notification_frequency': user_settings.notification_frequency,
                'wellness_check_enabled': user_settings.wellness_check_enabled,
                'crisis_detection_enabled': user_settings.crisis_detection_enabled,
                'memory_enabled': user_settings.memory_enabled
            }
        }
    
    @staticmethod
    def get_recommended_persona(quiz_data: Dict[str, Any]) -> Optional[PersonaProfile]:
        """
        Recommend a persona based on quiz responses
        
        Args:
            quiz_data: Quiz response data
            
        Returns:
            Recommended PersonaProfile or None
        """
        primary_goal = quiz_data.get('primary_goal')
        preferred_tone = quiz_data.get('preferred_tone')
        initial_mood = quiz_data.get('initial_mood', 5)
        
        # Build query based on preferences
        query = PersonaProfile.query.filter_by(is_active=True)
        
        # Map goals to persona personality traits
        if primary_goal == 'mental_health':
            # Look for empathetic, supportive personas
            query = query.filter(
                (PersonaProfile.personality_traits.like('%empathetic%')) |
                (PersonaProfile.personality_traits.like('%supportive%')) |
                (PersonaProfile.communication_style == 'therapeutic')
            )
        elif primary_goal == 'productivity':
            # Look for motivational, structured personas
            query = query.filter(
                (PersonaProfile.personality_traits.like('%motivated%')) |
                (PersonaProfile.personality_traits.like('%organized%')) |
                (PersonaProfile.communication_style == 'professional')
            )
        elif primary_goal == 'companionship':
            # Look for friendly, conversational personas
            query = query.filter(
                (PersonaProfile.personality_traits.like('%friendly%')) |
                (PersonaProfile.personality_traits.like('%warm%')) |
                (PersonaProfile.communication_style == 'casual')
            )
        elif primary_goal == 'creativity':
            # Look for creative, imaginative personas
            query = query.filter(
                (PersonaProfile.personality_traits.like('%creative%')) |
                (PersonaProfile.personality_traits.like('%imaginative%')) |
                (PersonaProfile.communication_style == 'enthusiastic')
            )
        
        # Get first matching persona
        persona = query.first()
        
        # Fallback to any active persona if no match
        if not persona:
            persona = PersonaProfile.query.filter_by(is_active=True).first()
        
        return persona
    
    @staticmethod
    def get_all_personas_for_selection() -> List[Dict[str, Any]]:
        """
        Get all active personas formatted for onboarding UI
        
        Returns:
            List of persona dictionaries with relevant info
        """
        personas = PersonaProfile.query.filter_by(is_active=True).all()
        
        return [
            {
                'id': persona.id,
                'name': persona.name,
                'description': persona.description,
                'personality_traits': persona.personality_traits,
                'communication_style': persona.communication_style,
                'profile_picture': persona.profile_picture,
                'tagline': persona.tagline
            }
            for persona in personas
        ]
    
    @staticmethod
    def skip_onboarding(user_id: int) -> Dict[str, Any]:
        """
        Allow user to skip onboarding and use default settings
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with success status
        """
        # Create basic quiz record (marked as skipped)
        quiz = OnboardingService.get_or_create_quiz(user_id)
        quiz.completed = True
        quiz.completed_at = datetime.utcnow()
        quiz.updated_at = datetime.utcnow()
        
        # Set default persona
        default_persona = PersonaProfile.query.filter_by(is_active=True).first()
        if default_persona:
            quiz.selected_persona_id = default_persona.id
        
        # Create default settings
        user_settings = UserSettings.query.filter_by(user_id=user_id).first()
        if not user_settings:
            user_settings = UserSettings(
                user_id=user_id,
                current_persona_id=default_persona.id if default_persona else None,
                preferred_response_style='conversational',
                memory_enabled=True
            )
            db.session.add(user_settings)
        
        db.session.commit()
        
        return {
            'success': True,
            'skipped': True,
            'default_persona_id': default_persona.id if default_persona else None
        }
    
    @staticmethod
    def needs_onboarding(user_id: int) -> bool:
        """
        Check if user needs to complete onboarding
        
        Args:
            user_id: User ID
            
        Returns:
            True if user hasn't completed onboarding, False otherwise
        """
        quiz = OnboardingQuiz.query.filter_by(user_id=user_id).first()
        
        # User needs onboarding if:
        # 1. No quiz record exists, OR
        # 2. Quiz exists but not completed
        return quiz is None or not quiz.completed
