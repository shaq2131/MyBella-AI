"""
Create Achievement System Tables
Migration script for achievements, streaks, and leaderboard
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend import create_app
from backend.database.models.models import db
from backend.database.models.achievement_models import Achievement, UserAchievement, Streak, LeaderboardEntry

def create_tables():
    """Create achievement system tables"""
    app, socketio = create_app()
    
    with app.app_context():
        print("Creating achievement system tables...")
        
        # Create tables
        db.create_all()
        
        print("✅ Tables created successfully!")
        
        # Seed default achievements
        seed_default_achievements()
        
        print("✅ Default achievements seeded!")

def seed_default_achievements():
    """Seed default achievement definitions"""
    
    default_achievements = [
        # Streak Achievements
        {
            'name': 'First Steps',
            'description': 'Complete your first daily check-in',
            'category': 'streak',
            'tier': 'bronze',
            'condition_type': 'streak_days',
            'condition_value': 1,
            'icon': '🌟',
            'color': '#CD7F32',
            'points': 5
        },
        {
            'name': 'Week Warrior',
            'description': 'Maintain a 7-day streak',
            'category': 'streak',
            'tier': 'silver',
            'condition_type': 'streak_days',
            'condition_value': 7,
            'icon': '🔥',
            'color': '#C0C0C0',
            'points': 25
        },
        {
            'name': 'Month Master',
            'description': 'Maintain a 30-day streak',
            'category': 'streak',
            'tier': 'gold',
            'condition_type': 'streak_days',
            'condition_value': 30,
            'icon': '⭐',
            'color': '#FFD700',
            'points': 100
        },
        {
            'name': 'Century Club',
            'description': 'Maintain a 100-day streak',
            'category': 'streak',
            'tier': 'platinum',
            'condition_type': 'streak_days',
            'condition_value': 100,
            'icon': '💎',
            'color': '#E5E4E2',
            'points': 500,
            'is_secret': True
        },
        
        # Mood Achievements
        {
            'name': 'Mood Tracker',
            'description': 'Log 10 mood entries',
            'category': 'mood',
            'tier': 'bronze',
            'condition_type': 'total_moods',
            'condition_value': 10,
            'icon': '😊',
            'color': '#CD7F32',
            'points': 10
        },
        {
            'name': 'Emotion Explorer',
            'description': 'Log 50 mood entries',
            'category': 'mood',
            'tier': 'silver',
            'condition_type': 'total_moods',
            'condition_value': 50,
            'icon': '🎭',
            'color': '#C0C0C0',
            'points': 30
        },
        {
            'name': 'Feeling Master',
            'description': 'Log 100 mood entries',
            'category': 'mood',
            'tier': 'gold',
            'condition_type': 'total_moods',
            'condition_value': 100,
            'icon': '🌈',
            'color': '#FFD700',
            'points': 75
        },
        
        # Exercise Achievements
        {
            'name': 'Wellness Beginner',
            'description': 'Complete 5 guided exercises',
            'category': 'exercise',
            'tier': 'bronze',
            'condition_type': 'total_exercises',
            'condition_value': 5,
            'icon': '🧘',
            'color': '#CD7F32',
            'points': 10
        },
        {
            'name': 'Mindful Practitioner',
            'description': 'Complete 25 guided exercises',
            'category': 'exercise',
            'tier': 'silver',
            'condition_type': 'total_exercises',
            'condition_value': 25,
            'icon': '🧘‍♀️',
            'color': '#C0C0C0',
            'points': 35
        },
        {
            'name': 'Zen Master',
            'description': 'Complete 100 guided exercises',
            'category': 'exercise',
            'tier': 'gold',
            'condition_type': 'total_exercises',
            'condition_value': 100,
            'icon': '☮️',
            'color': '#FFD700',
            'points': 100
        },
        
        # Conversation Achievements
        {
            'name': 'Chatty Starter',
            'description': 'Have 10 conversations',
            'category': 'conversation',
            'tier': 'bronze',
            'condition_type': 'total_conversations',
            'condition_value': 10,
            'icon': '💬',
            'color': '#CD7F32',
            'points': 10
        },
        {
            'name': 'Social Butterfly',
            'description': 'Have 50 conversations',
            'category': 'conversation',
            'tier': 'silver',
            'condition_type': 'total_conversations',
            'condition_value': 50,
            'icon': '🦋',
            'color': '#C0C0C0',
            'points': 30
        },
        {
            'name': 'Communication Expert',
            'description': 'Have 100 conversations',
            'category': 'conversation',
            'tier': 'gold',
            'condition_type': 'total_conversations',
            'condition_value': 100,
            'icon': '🗣️',
            'color': '#FFD700',
            'points': 75
        },
        
        # Wellness Achievements
        {
            'name': 'Wellness Warrior',
            'description': 'Complete at least one activity (mood, exercise, or conversation) every day for 14 days',
            'category': 'wellness',
            'tier': 'gold',
            'condition_type': 'wellness_streak',
            'condition_value': 14,
            'icon': '💪',
            'color': '#FFD700',
            'points': 150
        },
        {
            'name': 'Self-Care Champion',
            'description': 'Reach 500 total points',
            'category': 'milestone',
            'tier': 'platinum',
            'condition_type': 'total_points',
            'condition_value': 500,
            'icon': '👑',
            'color': '#E5E4E2',
            'points': 100,
            'is_secret': True
        }
    ]
    
    # Add achievements to database
    for achievement_data in default_achievements:
        # Check if already exists
        existing = Achievement.query.filter_by(name=achievement_data['name']).first()
        if not existing:
            achievement = Achievement(**achievement_data)
            db.session.add(achievement)
    
    db.session.commit()
    print(f"✅ Seeded {len(default_achievements)} achievements")

if __name__ == '__main__':
    create_tables()
