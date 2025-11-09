"""
Mood Check-in Routes for MyBella
Daily mood tracking and emotional wellness monitoring
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from backend.database.models.wellness_models import MoodEntry, db
from backend.services.achievements_service import AchievementsService
from datetime import datetime, date, timedelta
from sqlalchemy import func, desc

mood_bp = Blueprint('mood', __name__, url_prefix='/mood')

@mood_bp.route('/checkin')
@login_required
def checkin():
    """Daily mood check-in page"""
    # Check if user already checked in today
    today = date.today()
    existing_checkin = MoodEntry.query.filter(
        MoodEntry.user_id == current_user.id,
        func.date(MoodEntry.entry_date) == today
    ).first()
    
    return render_template('mood/checkin.html', 
                         title='Mood Check-in',
                         existing_checkin=existing_checkin)

@mood_bp.route('/api/submit', methods=['POST'])
@login_required
def submit_checkin():
    """Submit mood check-in"""
    try:
        data = request.get_json()
        
        # Check if already checked in today
        today = date.today()
        existing = MoodEntry.query.filter(
            MoodEntry.user_id == current_user.id,
            func.date(MoodEntry.entry_date) == today
        ).first()
        
        if existing:
            # Update existing entry
            existing.mood_level = data.get('mood_level')
            existing.mood_label = data.get('mood_label')
            existing.emotions = ','.join(data.get('emotions', []))
            existing.activities = ','.join(data.get('activities', []))
            existing.notes = data.get('notes', '')
            existing.energy_level = data.get('energy_level')
            existing.stress_level = data.get('stress_level')
        else:
            # Create new entry
            mood_entry = MoodEntry(
                user_id=current_user.id,
                mood_level=data.get('mood_level'),
                mood_label=data.get('mood_label'),
                emotions=','.join(data.get('emotions', [])),
                activities=','.join(data.get('activities', [])),
                notes=data.get('notes', ''),
                energy_level=data.get('energy_level'),
                stress_level=data.get('stress_level'),
                entry_date=datetime.utcnow()
            )
            db.session.add(mood_entry)
        
        db.session.commit()
        
        # 🏆 Check for achievements and update streak
        newly_unlocked = AchievementsService.check_mood_achievements(current_user.id)
        streak, was_updated, streak_achievements = AchievementsService.record_checkin(current_user.id)
        
        # Combine newly unlocked achievements
        all_new_achievements = newly_unlocked + streak_achievements
        
        return jsonify({
            'success': True,
            'message': 'Mood check-in saved successfully!',
            'redirect': url_for('mood.journal'),
            'achievements': [achievement.to_dict() for achievement in all_new_achievements] if all_new_achievements else []
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@mood_bp.route('/journal')
@login_required
def journal():
    """Mood journal - view past entries"""
    # Get entries for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    entries = MoodEntry.query.filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.entry_date >= thirty_days_ago
    ).order_by(desc(MoodEntry.entry_date)).all()
    
    # Calculate statistics
    if entries:
        avg_mood = sum(e.mood_level for e in entries) / len(entries)
        mood_trend = calculate_mood_trend(entries)
    else:
        avg_mood = 0
        mood_trend = 'neutral'
    
    return render_template('mood/journal.html',
                         title='Mood Journal',
                         entries=entries,
                         avg_mood=round(avg_mood, 1),
                         mood_trend=mood_trend,
                         total_entries=len(entries))

@mood_bp.route('/insights')
@login_required
def insights():
    """Mood insights and analytics"""
    # Get entries for analysis
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    entries = MoodEntry.query.filter(
        MoodEntry.user_id == current_user.id,
        MoodEntry.entry_date >= thirty_days_ago
    ).order_by(MoodEntry.entry_date).all()
    
    if not entries:
        return render_template('mood/insights.html',
                             title='Mood Insights',
                             has_data=False)
    
    # Prepare data for charts
    mood_data = [{
        'date': e.entry_date.strftime('%Y-%m-%d'),
        'mood': e.mood_level,
        'energy': e.energy_level,
        'stress': e.stress_level
    } for e in entries]
    
    # Calculate insights
    avg_mood = sum(e.mood_level for e in entries) / len(entries)
    best_mood = max(e.mood_level for e in entries)
    worst_mood = min(e.mood_level for e in entries)
    
    # Most common emotions
    all_emotions = []
    for e in entries:
        if e.emotions:
            all_emotions.extend(e.emotions.split(','))
    
    emotion_counts = {}
    for emotion in all_emotions:
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    top_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return render_template('mood/insights.html',
                         title='Mood Insights',
                         has_data=True,
                         mood_data=mood_data,
                         avg_mood=round(avg_mood, 1),
                         best_mood=best_mood,
                         worst_mood=worst_mood,
                         top_emotions=top_emotions,
                         total_entries=len(entries))

def calculate_mood_trend(entries):
    """Calculate if mood is improving, declining, or stable"""
    if len(entries) < 2:
        return 'neutral'
    
    # Compare last week to previous week
    recent = entries[:7] if len(entries) >= 7 else entries
    older = entries[7:14] if len(entries) >= 14 else []
    
    if not older:
        return 'neutral'
    
    recent_avg = sum(e.mood_level for e in recent) / len(recent)
    older_avg = sum(e.mood_level for e in older) / len(older)
    
    diff = recent_avg - older_avg
    
    if diff > 0.5:
        return 'improving'
    elif diff < -0.5:
        return 'declining'
    else:
        return 'stable'
