"""
Exercises routes for MyBella
Handles breathing exercises, meditation, and journaling prompts
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from backend.database.models.models import db
from backend.database.models.exercise_models import ExerciseCompletion, JournalingPrompt
from backend.services.achievements_service import AchievementsService
from datetime import datetime, timedelta
from sqlalchemy import func

exercises_bp = Blueprint('exercises', __name__, url_prefix='/exercises')


@exercises_bp.route('/')
@login_required
def index():
    """Main exercises hub page"""
    # Get user's exercise stats
    total_completed = ExerciseCompletion.query.filter_by(user_id=current_user.id).count()
    
    # Get completions this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_completed = ExerciseCompletion.query.filter(
        ExerciseCompletion.user_id == current_user.id,
        ExerciseCompletion.completed_at >= week_ago
    ).count()
    
    # Get favorite exercise type
    favorite_type = db.session.query(
        ExerciseCompletion.exercise_type,
        func.count(ExerciseCompletion.id).label('count')
    ).filter(
        ExerciseCompletion.user_id == current_user.id
    ).group_by(
        ExerciseCompletion.exercise_type
    ).order_by(
        func.count(ExerciseCompletion.id).desc()
    ).first()
    
    return render_template(
        'exercises/index.html',
        total_completed=total_completed,
        weekly_completed=weekly_completed,
        favorite_type=favorite_type[0] if favorite_type else None
    )


@exercises_bp.route('/breathing')
@login_required
def breathing():
    """Breathing exercises page"""
    return render_template('exercises/breathing.html')


@exercises_bp.route('/breathing/<exercise_name>')
@login_required
def breathing_exercise(exercise_name):
    """Individual breathing exercise page"""
    exercises = {
        '4-7-8': {
            'name': '4-7-8 Breathing',
            'description': 'A calming technique: Breathe in for 4, hold for 7, exhale for 8 seconds.',
            'benefits': ['Reduces anxiety', 'Improves sleep', 'Manages stress'],
            'inhale': 4,
            'hold': 7,
            'exhale': 8
        },
        'box': {
            'name': 'Box Breathing',
            'description': 'Equal breathing: Breathe in, hold, out, hold - all for 4 seconds.',
            'benefits': ['Enhances focus', 'Lowers stress', 'Regulates emotions'],
            'inhale': 4,
            'hold': 4,
            'exhale': 4,
            'hold_after': 4
        },
        'calm': {
            'name': 'Calm Breathing',
            'description': 'Simple deep breathing: In for 4, out for 6 seconds.',
            'benefits': ['Quick stress relief', 'Easy to learn', 'Anytime, anywhere'],
            'inhale': 4,
            'hold': 0,
            'exhale': 6
        }
    }
    
    exercise = exercises.get(exercise_name)
    if not exercise:
        return "Exercise not found", 404
    
    return render_template('exercises/breathing_exercise.html', exercise=exercise, exercise_key=exercise_name)


@exercises_bp.route('/meditation')
@login_required
def meditation():
    """Meditation sessions page"""
    return render_template('exercises/meditation.html')


@exercises_bp.route('/journaling')
@login_required
def journaling():
    """Journaling prompts page"""
    # Get random prompt or specific category
    category = request.args.get('category', 'all')
    
    if category == 'all':
        prompt = JournalingPrompt.query.order_by(func.random()).first()
    else:
        prompt = JournalingPrompt.query.filter_by(category=category).order_by(func.random()).first()
    
    # Get all categories for filter
    categories = db.session.query(JournalingPrompt.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template(
        'exercises/journaling.html',
        prompt=prompt,
        categories=categories,
        selected_category=category
    )


@exercises_bp.route('/api/complete', methods=['POST'])
@login_required
def complete_exercise():
    """Record exercise completion"""
    data = request.get_json()
    
    completion = ExerciseCompletion(
        user_id=current_user.id,
        exercise_type=data.get('exercise_type'),
        exercise_name=data.get('exercise_name'),
        duration_minutes=data.get('duration_minutes'),
        notes=data.get('notes'),
        mood_before=data.get('mood_before'),
        mood_after=data.get('mood_after')
    )
    
    db.session.add(completion)
    db.session.commit()
    
    # 🏆 Check for achievements and update streak
    newly_unlocked = AchievementsService.check_exercise_achievements(current_user.id)
    streak, was_updated, streak_achievements = AchievementsService.record_checkin(current_user.id)
    
    # Combine newly unlocked achievements
    all_new_achievements = newly_unlocked + streak_achievements
    
    return jsonify({
        'ok': True,
        'message': 'Exercise completed!',
        'completion_id': completion.id,
        'achievements': [achievement.to_dict() for achievement in all_new_achievements] if all_new_achievements else []
    })


@exercises_bp.route('/api/stats')
@login_required
def exercise_stats():
    """Get user's exercise statistics"""
    # Total by type
    type_stats = db.session.query(
        ExerciseCompletion.exercise_type,
        func.count(ExerciseCompletion.id).label('count')
    ).filter(
        ExerciseCompletion.user_id == current_user.id
    ).group_by(
        ExerciseCompletion.exercise_type
    ).all()
    
    # Recent completions
    recent = ExerciseCompletion.query.filter_by(
        user_id=current_user.id
    ).order_by(
        ExerciseCompletion.completed_at.desc()
    ).limit(10).all()
    
    # Streak calculation
    completions = ExerciseCompletion.query.filter_by(
        user_id=current_user.id
    ).order_by(
        ExerciseCompletion.completed_at.desc()
    ).all()
    
    streak = 0
    if completions:
        current_date = datetime.utcnow().date()
        for completion in completions:
            completion_date = completion.completed_at.date()
            if completion_date == current_date or completion_date == current_date - timedelta(days=streak):
                streak += 1
                current_date = completion_date - timedelta(days=1)
            else:
                break
    
    return jsonify({
        'ok': True,
        'type_stats': {t: c for t, c in type_stats},
        'recent': [r.to_dict() for r in recent],
        'streak': streak
    })


@exercises_bp.route('/history')
@login_required
def history():
    """View exercise completion history"""
    completions = ExerciseCompletion.query.filter_by(
        user_id=current_user.id
    ).order_by(
        ExerciseCompletion.completed_at.desc()
    ).all()
    
    return render_template('exercises/history.html', completions=completions)
