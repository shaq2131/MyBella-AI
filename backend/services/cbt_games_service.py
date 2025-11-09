"""
CBT Games and Interactive Tools Service
Handles Reframe Puzzle, Memory Match, and other game-like CBT features
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
from flask import current_app
from backend.database.models.models import db
from backend.database.models.wellness_models import (
    ThoughtReframe, EmotionMatch, DailyNote, LoveLetter,
    WellnessRoutine, RoutineCompletion, WellnessAchievement,
    CheckInEntry, MoodScale
)
import json
import random
import re


class ReframePuzzleService:
    """Reframe Puzzle - Interactive thought reframing game"""
    
    # Common cognitive distortions to detect
    DISTORTION_PATTERNS = {
        'all_or_nothing': {
            'keywords': ['always', 'never', 'every time', 'no one', 'everyone'],
            'name': 'All-or-Nothing Thinking',
            'hint': 'Try using words like "sometimes", "often", or "rarely" instead of absolutes.'
        },
        'overgeneralization': {
            'keywords': ['everything', 'nothing', 'totally', 'completely', 'entire'],
            'name': 'Overgeneralization',
            'hint': 'Focus on specific instances rather than broad generalizations.'
        },
        'catastrophizing': {
            'keywords': ['disaster', 'terrible', 'awful', 'horrible', 'worst', 'ruined'],
            'name': 'Catastrophizing',
            'hint': 'What\'s the most realistic outcome? What evidence supports that?'
        },
        'should_statements': {
            'keywords': ['should', 'must', 'ought to', 'have to', 'supposed to'],
            'name': 'Should Statements',
            'hint': 'Replace "should" with "could" or "would like to" for flexibility.'
        },
        'labeling': {
            'keywords': ['i am a', 'i\'m a', 'he is a', 'she is a', 'they are'],
            'name': 'Labeling',
            'hint': 'Describe the behavior, not the person. Actions don\'t define identity.'
        }
    }
    
    @staticmethod
    def detect_cognitive_distortion(thought: str) -> Optional[str]:
        """Detect cognitive distortion in negative thought"""
        thought_lower = thought.lower()
        
        for distortion, pattern in ReframePuzzleService.DISTORTION_PATTERNS.items():
            for keyword in pattern['keywords']:
                if keyword in thought_lower:
                    return distortion
        
        return None
    
    @staticmethod
    def start_reframe_puzzle(user_id: int, negative_thought: str) -> ThoughtReframe:
        """Start a new reframe puzzle"""
        try:
            # Detect cognitive distortion
            distortion = ReframePuzzleService.detect_cognitive_distortion(negative_thought)
            
            puzzle = ThoughtReframe(
                user_id=user_id,
                negative_thought=negative_thought,
                cognitive_distortion=distortion
            )
            
            db.session.add(puzzle)
            db.session.commit()
            
            # Get hint if distortion detected
            hint = None
            if distortion:
                hint = ReframePuzzleService.DISTORTION_PATTERNS[distortion]['hint']
            
            return {
                'puzzle_id': puzzle.id,
                'distortion_type': distortion,
                'distortion_name': ReframePuzzleService.DISTORTION_PATTERNS[distortion]['name'] if distortion else None,
                'hint': hint,
                'success': True
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error starting reframe puzzle: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def score_reframe(original_thought: str, reframe: str) -> Dict[str, int]:
        """Score a reframe based on quality criteria"""
        score = 0
        feedback = []
        
        # Check length (should be substantive)
        if len(reframe) < 10:
            feedback.append("Try elaborating more on your reframe.")
        else:
            score += 2
        
        # Check for positive language
        positive_words = ['can', 'will', 'might', 'possible', 'opportunity', 'learn', 'grow', 'try']
        if any(word in reframe.lower() for word in positive_words):
            score += 2
            feedback.append("Great use of positive language!")
        
        # Check for evidence-based thinking
        evidence_words = ['because', 'evidence', 'shows', 'indicates', 'suggests', 'fact']
        if any(word in reframe.lower() for word in evidence_words):
            score += 2
            feedback.append("Nice evidence-based thinking!")
        
        # Check if absolutes were removed
        absolutes = ['always', 'never', 'everyone', 'no one']
        original_has_absolutes = any(word in original_thought.lower() for word in absolutes)
        reframe_has_absolutes = any(word in reframe.lower() for word in absolutes)
        
        if original_has_absolutes and not reframe_has_absolutes:
            score += 2
            feedback.append("Excellent! You removed absolute thinking.")
        
        # Creativity bonus - check for different structure
        if len(reframe) > len(original_thought):
            score += 1
            feedback.append("You expanded on the thought - great detail!")
        
        return {
            'score': min(score, 10),  # Cap at 10
            'feedback': feedback
        }
    
    @staticmethod
    def submit_reframe(puzzle_id: int, user_reframe: str, time_spent: int) -> Dict:
        """Submit and score a reframe"""
        try:
            puzzle = ThoughtReframe.query.get(puzzle_id)
            if not puzzle:
                return {'success': False, 'error': 'Puzzle not found'}
            
            # Score the reframe
            scoring = ReframePuzzleService.score_reframe(puzzle.negative_thought, user_reframe)
            
            # Generate AI feedback and alternatives
            ai_feedback = f"Nice work! {' '.join(scoring['feedback'])}"
            
            # Simple alternative suggestions
            alternatives = [
                f"What if you thought: '{user_reframe}' - and also added what you learned?",
                f"Another angle: Focus on what you can control in this situation.",
                f"Consider: How would you advise a friend thinking this way?"
            ]
            
            puzzle.user_reframe = user_reframe
            puzzle.ai_feedback = ai_feedback
            puzzle.alternative_reframes = json.dumps(alternatives)
            puzzle.quality_score = scoring['score']
            puzzle.total_points = scoring['score']
            puzzle.time_spent_seconds = time_spent
            puzzle.completed = True
            
            db.session.commit()
            
            return {
                'success': True,
                'score': scoring['score'],
                'feedback': ai_feedback,
                'alternatives': alternatives,
                'points_earned': scoring['score']
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error submitting reframe: {e}")
            return {'success': False, 'error': str(e)}


class MemoryMatchService:
    """Memory Match - Emotion/Coping Strategy Matching Game"""
    
    # Emotion-Coping pairs for matching game
    EMOTION_COPING_PAIRS = {
        'Anxious': 'Deep Breathing',
        'Angry': 'Take a Walk',
        'Sad': 'Talk to a Friend',
        'Overwhelmed': 'Make a To-Do List',
        'Lonely': 'Reach Out to Someone',
        'Stressed': 'Practice Meditation',
        'Frustrated': 'Journal Your Feelings',
        'Worried': 'Challenge the Thought',
        'Tired': 'Take a Short Break',
        'Restless': 'Physical Exercise'
    }
    
    EMOTION_AFFIRMATION_PAIRS = {
        'Anxious': 'I am safe and capable',
        'Angry': 'I choose peace over conflict',
        'Sad': 'This feeling will pass',
        'Overwhelmed': 'I can handle this one step at a time',
        'Lonely': 'I am worthy of connection',
        'Stressed': 'I am doing my best',
        'Frustrated': 'I am patient with myself',
        'Worried': 'I trust in my ability to cope',
        'Tired': 'I deserve rest and care',
        'Restless': 'I channel my energy positively'
    }
    
    @staticmethod
    def create_game(user_id: int, game_type: str = 'emotion_coping', difficulty: int = 1) -> Dict:
        """Create a new memory match game"""
        try:
            # Select pairs based on game type and difficulty
            if game_type == 'emotion_coping':
                all_pairs = MemoryMatchService.EMOTION_COPING_PAIRS
            else:
                all_pairs = MemoryMatchService.EMOTION_AFFIRMATION_PAIRS
            
            # Number of pairs based on difficulty
            pair_count = min(4 + difficulty, len(all_pairs))
            selected_pairs = dict(random.sample(list(all_pairs.items()), pair_count))
            
            # Create game session
            game = EmotionMatch(
                user_id=user_id,
                game_type=game_type,
                difficulty_level=difficulty,
                total_pairs=pair_count,
                pairs_learned=json.dumps(selected_pairs)
            )
            
            db.session.add(game)
            db.session.commit()
            
            # Create card data for frontend
            cards = []
            card_id = 1
            for emotion, strategy in selected_pairs.items():
                cards.append({'id': card_id, 'type': 'emotion', 'content': emotion})
                card_id += 1
                cards.append({'id': card_id, 'type': 'strategy', 'content': strategy})
                card_id += 1
            
            # Shuffle cards
            random.shuffle(cards)
            
            return {
                'success': True,
                'game_id': game.id,
                'cards': cards,
                'total_pairs': pair_count
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating memory match game: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def complete_game(game_id: int, matched_pairs: int, failed_attempts: int, time_seconds: int) -> Dict:
        """Complete a memory match game"""
        try:
            game = EmotionMatch.query.get(game_id)
            if not game:
                return {'success': False, 'error': 'Game not found'}
            
            game.matched_pairs = matched_pairs
            game.failed_attempts = failed_attempts
            game.time_seconds = time_seconds
            game.completed = True
            
            # Calculate score
            accuracy = (matched_pairs / game.total_pairs) * 100
            time_bonus = max(0, 300 - time_seconds) // 10  # Bonus for speed
            failure_penalty = failed_attempts * 5
            
            score = int((accuracy * 10) + time_bonus - failure_penalty)
            game.score = max(0, score)
            game.accuracy_percentage = accuracy
            
            db.session.commit()
            
            return {
                'success': True,
                'score': game.score,
                'accuracy': accuracy,
                'message': 'Great job!' if accuracy >= 80 else 'Keep practicing!'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error completing memory match: {e}")
            return {'success': False, 'error': str(e)}


class DailyNoteService:
    """Daily Notes and Reflections with CBT prompts"""
    
    CBT_PROMPTS = {
        'gratitude': [
            "What are three things you're grateful for today?",
            "Who made a positive impact on your day, and how?",
            "What small moment brought you joy today?"
        ],
        'reflection': [
            "What challenged you today, and how did you handle it?",
            "What did you learn about yourself today?",
            "If you could give today a theme, what would it be?"
        ],
        'reframing': [
            "What negative thought can you reframe right now?",
            "What's a more balanced way to view a recent situation?",
            "What would you tell a friend who had your day?"
        ],
        'future': [
            "What's one thing you're looking forward to tomorrow?",
            "What small goal can you set for this week?",
            "How do you want to feel tomorrow?"
        ]
    }
    
    @staticmethod
    def get_random_prompt(category: str = 'reflection') -> str:
        """Get a random CBT prompt"""
        prompts = DailyNoteService.CBT_PROMPTS.get(category, DailyNoteService.CBT_PROMPTS['reflection'])
        return random.choice(prompts)
    
    @staticmethod
    def create_note(user_id: int, content: str, note_type: str = 'general', 
                    prompt: str = None, tags: List[str] = None) -> Dict:
        """Create a new daily note"""
        try:
            note = DailyNote(
                user_id=user_id,
                content=content,
                note_type=note_type,
                prompt_used=prompt,
                tags=json.dumps(tags) if tags else None,
                note_date=date.today()
            )
            
            db.session.add(note)
            db.session.commit()
            
            return {
                'success': True,
                'note_id': note.id,
                'message': 'Note saved successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating daily note: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_user_notes(user_id: int, days: int = 30, note_type: str = None) -> List[DailyNote]:
        """Get user's recent notes"""
        try:
            query = DailyNote.query.filter(DailyNote.user_id == user_id)
            
            if note_type:
                query = query.filter(DailyNote.note_type == note_type)
            
            start_date = date.today() - timedelta(days=days)
            query = query.filter(DailyNote.note_date >= start_date)
            
            return query.order_by(DailyNote.note_date.desc()).all()
            
        except Exception as e:
            current_app.logger.error(f"Error fetching notes: {e}")
            return []


class CheckInService:
    """AM/PM Check-in Service"""
    
    MORNING_AFFIRMATIONS = [
        "Today is full of possibilities.",
        "I am capable and strong.",
        "I choose to focus on what I can control.",
        "I deserve good things today.",
        "I am ready to face today's challenges.",
        "My efforts matter and make a difference."
    ]
    
    EVENING_PROMPTS = [
        "What went well today?",
        "What are you proud of accomplishing?",
        "What challenged you, and how did you respond?"
    ]
    
    @staticmethod
    def create_morning_checkin(user_id: int, sleep_quality: MoodScale, 
                               morning_mood: MoodScale, intention: str = None) -> Dict:
        """Create morning check-in"""
        try:
            # Get random affirmation
            affirmation = random.choice(CheckInService.MORNING_AFFIRMATIONS)
            
            checkin = CheckInEntry(
                user_id=user_id,
                checkin_type='morning',
                sleep_quality=sleep_quality,
                morning_mood=morning_mood,
                morning_intention=intention,
                morning_affirmation=affirmation
            )
            
            db.session.add(checkin)
            db.session.commit()
            
            return {
                'success': True,
                'affirmation': affirmation,
                'message': 'Good morning! Have a wonderful day ahead.'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating morning check-in: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def create_evening_checkin(user_id: int, evening_mood: MoodScale,
                               gratitude: List[str], accomplishments: str = None) -> Dict:
        """Create evening check-in"""
        try:
            checkin = CheckInEntry(
                user_id=user_id,
                checkin_type='evening',
                evening_mood=evening_mood,
                gratitude_items=json.dumps(gratitude),
                accomplishments=accomplishments
            )
            
            db.session.add(checkin)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Sleep well! Tomorrow is a new day.'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating evening check-in: {e}")
            return {'success': False, 'error': str(e)}


class AchievementService:
    """Wellness Achievement and Badge System"""
    
    ACHIEVEMENT_DEFINITIONS = {
        'first_reframe': {
            'name': '🎯 First Reframe',
            'description': 'Completed your first thought reframing exercise',
            'category': 'reframing',
            'tier': 'bronze',
            'points': 10
        },
        'reframe_streak_7': {
            'name': '🔥 Week Warrior',
            'description': 'Reframed thoughts for 7 days in a row',
            'category': 'reframing',
            'tier': 'silver',
            'points': 50
        },
        'mood_tracker_30': {
            'name': '📊 Consistent Tracker',
            'description': 'Logged mood for 30 consecutive days',
            'category': 'mood_tracking',
            'tier': 'gold',
            'points': 100
        },
        'perfect_match': {
            'name': '🎮 Perfect Match',
            'description': 'Completed Memory Match with 100% accuracy',
            'category': 'games',
            'tier': 'silver',
            'points': 25
        },
        'morning_routine_10': {
            'name': '🌅 Early Bird',
            'description': 'Completed morning routine 10 times',
            'category': 'routine',
            'tier': 'bronze',
            'points': 20
        }
    }
    
    @staticmethod
    def check_and_award_achievements(user_id: int, action_type: str, count: int = 1) -> List[Dict]:
        """Check if user earned any achievements"""
        awarded = []
        
        try:
            # Define achievement triggers
            triggers = {
                'first_reframe': lambda: count == 1 and action_type == 'reframe',
                'reframe_streak_7': lambda: count >= 7 and action_type == 'reframe_streak',
                'mood_tracker_30': lambda: count >= 30 and action_type == 'mood_streak',
                'morning_routine_10': lambda: count >= 10 and action_type == 'morning_routine'
            }
            
            for achievement_key, should_award in triggers.items():
                if should_award():
                    # Check if already awarded
                    existing = WellnessAchievement.query.filter_by(
                        user_id=user_id,
                        badge_name=AchievementService.ACHIEVEMENT_DEFINITIONS[achievement_key]['name'],
                        is_unlocked=True
                    ).first()
                    
                    if not existing:
                        # Award new achievement
                        achievement_def = AchievementService.ACHIEVEMENT_DEFINITIONS[achievement_key]
                        achievement = WellnessAchievement(
                            user_id=user_id,
                            achievement_type='milestone',
                            category=achievement_def['category'],
                            badge_name=achievement_def['name'],
                            badge_description=achievement_def['description'],
                            badge_tier=achievement_def['tier'],
                            points_awarded=achievement_def['points'],
                            is_unlocked=True,
                            unlocked_at=datetime.utcnow(),
                            current_count=count,
                            required_count=count
                        )
                        
                        db.session.add(achievement)
                        awarded.append(achievement_def)
            
            if awarded:
                db.session.commit()
            
            return awarded
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error awarding achievements: {e}")
            return []
