"""
CBT Games and Interactive Tools Routes
API endpoints for Reframe Puzzle, Memory Match, Daily Notes, Check-ins, and Achievements
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from backend.services.cbt_games_service import (
    ReframePuzzleService, MemoryMatchService, DailyNoteService,
    CheckInService, AchievementService
)
from backend.database.models.wellness_models import MoodScale
from datetime import datetime, date
import json

cbt_games_bp = Blueprint('cbt_games', __name__)


# =============================================================================
# Reframe Puzzle Routes
# =============================================================================

@cbt_games_bp.route('/wellness/games/reframe')
@cbt_games_bp.route('/wellness/reframe-puzzle')  # Alias for dashboard compatibility
@login_required
def reframe_puzzle():
    """Reframe Puzzle game page"""
    return render_template('wellness/reframe_puzzle.html', title='Reframe Puzzle')


@cbt_games_bp.route('/reframe/start', methods=['POST'])
@login_required
def start_reframe():
    """Start a new reframe puzzle"""
    try:
        data = request.get_json()
        negative_thought = data.get('negative_thought', '').strip()
        
        if not negative_thought:
            return jsonify({'success': False, 'error': 'Please enter a thought'}), 400
        
        result = ReframePuzzleService.start_reframe_puzzle(
            user_id=current_user.id,
            negative_thought=negative_thought
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cbt_games_bp.route('/reframe/submit', methods=['POST'])
@login_required
def submit_reframe():
    """Submit a reframed thought"""
    try:
        data = request.get_json()
        puzzle_id = data.get('puzzle_id')
        user_reframe = data.get('user_reframe', '').strip()
        time_spent = data.get('time_spent', 0)
        
        if not user_reframe:
            return jsonify({'success': False, 'error': 'Please enter your reframe'}), 400
        
        result = ReframePuzzleService.submit_reframe(
            puzzle_id=puzzle_id,
            user_reframe=user_reframe,
            time_spent=time_spent
        )
        
        # Check for achievements
        if result.get('success'):
            from backend.database.models.wellness_models import ThoughtReframe
            count = ThoughtReframe.query.filter_by(
                user_id=current_user.id, 
                completed=True
            ).count()
            
            achievements = AchievementService.check_and_award_achievements(
                user_id=current_user.id,
                action_type='reframe',
                count=count
            )
            
            if achievements:
                result['achievements'] = achievements
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# Memory Match Routes
# =============================================================================

@cbt_games_bp.route('/wellness/games/memory-match')
@cbt_games_bp.route('/wellness/memory-match')  # Alias for dashboard compatibility
@login_required
def memory_match():
    """Memory Match game page"""
    return render_template('wellness/memory_match.html', title='Memory Match')


@cbt_games_bp.route('/memory-match/start', methods=['POST'])
@login_required
def start_memory_match():
    """Start a new memory match game"""
    try:
        data = request.get_json()
        game_type = data.get('game_type', 'emotion_coping')
        difficulty = data.get('difficulty', 1)
        
        result = MemoryMatchService.create_game(
            user_id=current_user.id,
            game_type=game_type,
            difficulty=difficulty
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cbt_games_bp.route('/memory-match/complete', methods=['POST'])
@login_required
def complete_memory_match():
    """Complete a memory match game"""
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        matched_pairs = data.get('matched_pairs', 0)
        failed_attempts = data.get('failed_attempts', 0)
        time_seconds = data.get('time_seconds', 0)
        
        result = MemoryMatchService.complete_game(
            game_id=game_id,
            matched_pairs=matched_pairs,
            failed_attempts=failed_attempts,
            time_seconds=time_seconds
        )
        
        # Check for achievements
        if result.get('success') and result.get('accuracy') == 100:
            achievements = AchievementService.check_and_award_achievements(
                user_id=current_user.id,
                action_type='perfect_match',
                count=1
            )
            
            if achievements:
                result['achievements'] = achievements
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# Daily Notes Routes
# =============================================================================

@cbt_games_bp.route('/notes')
@login_required
def daily_notes():
    """Daily notes and journaling page"""
    notes = DailyNoteService.get_user_notes(current_user.id, days=30)
    return render_template('wellness/daily_notes.html', 
                         title='Daily Notes',
                         notes=notes)


@cbt_games_bp.route('/notes/prompt', methods=['GET'])
@login_required
def get_note_prompt():
    """Get a random CBT prompt for journaling"""
    category = request.args.get('category', 'reflection')
    prompt = DailyNoteService.get_random_prompt(category)
    
    return jsonify({
        'success': True,
        'prompt': prompt,
        'category': category
    })


@cbt_games_bp.route('/notes/create', methods=['POST'])
@login_required
def create_daily_note():
    """Create a new daily note"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        note_type = data.get('note_type', 'general')
        prompt = data.get('prompt')
        tags = data.get('tags', [])
        
        if not content:
            return jsonify({'success': False, 'error': 'Note content required'}), 400
        
        result = DailyNoteService.create_note(
            user_id=current_user.id,
            content=content,
            note_type=note_type,
            prompt=prompt,
            tags=tags
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# Check-in Routes (AM/PM)
# =============================================================================

@cbt_games_bp.route('/checkin')
@login_required
def checkin_page():
    """Check-in page"""
    return render_template('wellness/checkin.html', title='Daily Check-in')


@cbt_games_bp.route('/checkin/morning', methods=['POST'])
@login_required
def morning_checkin():
    """Create morning check-in"""
    try:
        data = request.get_json()
        sleep_quality = data.get('sleep_quality')
        morning_mood = data.get('morning_mood')
        intention = data.get('intention', '').strip()
        
        # Convert to enum
        sleep_quality_enum = MoodScale(int(sleep_quality)) if sleep_quality else None
        morning_mood_enum = MoodScale(int(morning_mood)) if morning_mood else None
        
        result = CheckInService.create_morning_checkin(
            user_id=current_user.id,
            sleep_quality=sleep_quality_enum,
            morning_mood=morning_mood_enum,
            intention=intention
        )
        
        # Check achievements
        from backend.database.models.wellness_models import CheckInEntry
        morning_count = CheckInEntry.query.filter_by(
            user_id=current_user.id,
            checkin_type='morning'
        ).count()
        
        achievements = AchievementService.check_and_award_achievements(
            user_id=current_user.id,
            action_type='morning_routine',
            count=morning_count
        )
        
        if achievements:
            result['achievements'] = achievements
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cbt_games_bp.route('/checkin/evening', methods=['POST'])
@login_required
def evening_checkin():
    """Create evening check-in"""
    try:
        data = request.get_json()
        evening_mood = data.get('evening_mood')
        gratitude = data.get('gratitude', [])
        accomplishments = data.get('accomplishments', '').strip()
        
        evening_mood_enum = MoodScale(int(evening_mood)) if evening_mood else None
        
        result = CheckInService.create_evening_checkin(
            user_id=current_user.id,
            evening_mood=evening_mood_enum,
            gratitude=gratitude,
            accomplishments=accomplishments
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# Achievements Routes
# =============================================================================

@cbt_games_bp.route('/achievements')
@login_required
def achievements_page():
    """User achievements and badges page"""
    from backend.database.models.wellness_models import WellnessAchievement
    
    unlocked = WellnessAchievement.query.filter_by(
        user_id=current_user.id,
        is_unlocked=True
    ).order_by(WellnessAchievement.unlocked_at.desc()).all()
    
    total_points = sum(a.points_awarded for a in unlocked)
    
    return render_template('wellness/achievements.html',
                         title='Achievements',
                         achievements=unlocked,
                         total_points=total_points)


@cbt_games_bp.route('/achievements/stats', methods=['GET'])
@login_required
def achievement_stats():
    """Get achievement statistics"""
    from backend.database.models.wellness_models import (
        WellnessAchievement, ThoughtReframe, EmotionMatch, 
        CheckInEntry, DailyNote
    )
    
    achievements = WellnessAchievement.query.filter_by(
        user_id=current_user.id,
        is_unlocked=True
    ).all()
    
    stats = {
        'total_achievements': len(achievements),
        'total_points': sum(a.points_awarded for a in achievements),
        'reframes_completed': ThoughtReframe.query.filter_by(
            user_id=current_user.id, completed=True
        ).count(),
        'games_played': EmotionMatch.query.filter_by(
            user_id=current_user.id, completed=True
        ).count(),
        'morning_checkins': CheckInEntry.query.filter_by(
            user_id=current_user.id, checkin_type='morning'
        ).count(),
        'notes_written': DailyNote.query.filter_by(
            user_id=current_user.id
        ).count()
    }
    
    return jsonify({'success': True, 'stats': stats})


# =============================================================================
# Love Letters Routes (Companion Mode 18+)
# =============================================================================

@cbt_games_bp.route('/love-letters')
@login_required
def love_letters():
    """Love letters page (18+ Companion Mode only)"""
    from backend.database.models.wellness_models import LoveLetter
    
    # Check user age/mode here if needed
    letters = LoveLetter.query.filter_by(
        user_id=current_user.id
    ).order_by(LoveLetter.created_at.desc()).limit(20).all()
    
    return render_template('wellness/love_letters.html',
                         title='Love Letters',
                         letters=letters)


@cbt_games_bp.route('/love-letters/create', methods=['POST'])
@login_required
def create_love_letter():
    """Create a new love letter"""
    try:
        from backend.database.models.wellness_models import LoveLetter
        
        data = request.get_json()
        persona = data.get('persona', 'Isabella')
        subject = data.get('subject', '').strip()
        content = data.get('content', '').strip()
        emotional_theme = data.get('emotional_theme', 'love')
        
        if not content:
            return jsonify({'success': False, 'error': 'Letter content required'}), 400
        
        letter = LoveLetter(
            user_id=current_user.id,
            persona=persona,
            direction='to_persona',
            subject=subject,
            content=content,
            emotional_theme=emotional_theme
        )
        
        from backend.database.models.models import db
        db.session.add(letter)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'letter_id': letter.id,
            'message': f'Your letter to {persona} has been saved.'
        })
        
    except Exception as e:
        from backend.database.models.models import db
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
