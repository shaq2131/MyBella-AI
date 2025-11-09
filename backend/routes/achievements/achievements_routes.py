"""
Achievements routes for MyBella
Streaks, badges, achievements, and leaderboard
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from backend.services.achievements_service import AchievementsService
from datetime import datetime

achievements_bp = Blueprint('achievements', __name__, url_prefix='/achievements')


@achievements_bp.route('/')
@login_required
def dashboard():
    """Main achievements dashboard"""
    # Get user stats
    stats = AchievementsService.get_user_stats(current_user.id)
    
    # Get achievements
    achievements = AchievementsService.get_user_achievements(current_user.id, include_locked=True)
    
    # Get streak calendar
    streak = AchievementsService.get_or_create_streak(current_user.id)
    calendar_data = streak.get_streak_calendar(days=30)
    
    return render_template(
        'achievements/dashboard.html',
        stats=stats,
        achievements=achievements,
        calendar_data=calendar_data
    )


@achievements_bp.route('/api/stats')
@login_required
def api_stats():
    """Get user statistics"""
    stats = AchievementsService.get_user_stats(current_user.id)
    return jsonify({'ok': True, 'data': stats})


@achievements_bp.route('/api/achievements')
@login_required
def api_achievements():
    """Get all achievements"""
    include_locked = request.args.get('include_locked', 'true').lower() == 'true'
    achievements = AchievementsService.get_user_achievements(current_user.id, include_locked=include_locked)
    return jsonify({'ok': True, 'data': achievements})


@achievements_bp.route('/api/streak')
@login_required
def api_streak():
    """Get streak information"""
    streak = AchievementsService.get_or_create_streak(current_user.id)
    return jsonify({
        'ok': True,
        'data': {
            'streak': streak.to_dict(),
            'calendar': streak.get_streak_calendar(days=30)
        }
    })


@achievements_bp.route('/api/checkin', methods=['POST'])
@login_required
def api_checkin():
    """Record a check-in"""
    streak, was_updated, newly_unlocked = AchievementsService.record_checkin(current_user.id)
    
    return jsonify({
        'ok': True,
        'data': {
            'streak': streak.to_dict(),
            'was_updated': was_updated,
            'newly_unlocked': [achievement.to_dict() for achievement in newly_unlocked]
        }
    })


@achievements_bp.route('/api/mark-viewed', methods=['POST'])
@login_required
def api_mark_viewed():
    """Mark achievements as viewed"""
    data = request.get_json()
    achievement_ids = data.get('achievement_ids', [])
    
    if not achievement_ids:
        return jsonify({'ok': False, 'error': 'No achievement IDs provided'}), 400
    
    AchievementsService.mark_achievements_viewed(current_user.id, achievement_ids)
    
    return jsonify({'ok': True})


@achievements_bp.route('/leaderboard')
@login_required
def leaderboard():
    """Leaderboard page"""
    # Get leaderboard data
    rankings = AchievementsService.get_leaderboard(limit=100, opt_in_only=True)
    
    # Get current user's entry
    from backend.database.models.achievement_models import LeaderboardEntry
    user_entry = LeaderboardEntry.query.filter_by(user_id=current_user.id).first()
    
    return render_template(
        'achievements/leaderboard.html',
        rankings=rankings,
        user_entry=user_entry
    )


@achievements_bp.route('/api/leaderboard')
@login_required
def api_leaderboard():
    """Get leaderboard data"""
    limit = int(request.args.get('limit', 50))
    rankings = AchievementsService.get_leaderboard(limit=limit, opt_in_only=True)
    
    return jsonify({'ok': True, 'data': rankings})


@achievements_bp.route('/api/toggle-opt-in', methods=['POST'])
@login_required
def api_toggle_opt_in():
    """Toggle leaderboard opt-in"""
    new_status = AchievementsService.toggle_leaderboard_opt_in(current_user.id)
    
    return jsonify({
        'ok': True,
        'data': {
            'opt_in': new_status
        }
    })


@achievements_bp.route('/api/check-all', methods=['POST'])
@login_required
def api_check_all():
    """
    Check all achievement types for new unlocks
    Used after completing activities
    """
    newly_unlocked = []
    
    # Check all categories
    newly_unlocked.extend(AchievementsService.check_mood_achievements(current_user.id))
    newly_unlocked.extend(AchievementsService.check_exercise_achievements(current_user.id))
    newly_unlocked.extend(AchievementsService.check_conversation_achievements(current_user.id))
    
    # Also check streak achievements
    streak = AchievementsService.get_or_create_streak(current_user.id)
    newly_unlocked.extend(AchievementsService.check_streak_achievements(current_user.id, streak.current_streak))
    
    return jsonify({
        'ok': True,
        'data': {
            'newly_unlocked': [achievement.to_dict() for achievement in newly_unlocked],
            'count': len(newly_unlocked)
        }
    })


@achievements_bp.route('/api/new-count')
@login_required
def api_new_count():
    """Get count of unviewed achievements"""
    count = AchievementsService.get_new_achievements_count(current_user.id)
    return jsonify({'ok': True, 'data': {'count': count}})
