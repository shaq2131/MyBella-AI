"""
Create CBT Games Tables
Migration to add Reframe Puzzle, Memory Match, Daily Notes, Love Letters, etc.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from backend import create_app
from backend.database.models.models import db
from backend.database.models.wellness_models import (
    ThoughtReframe, EmotionMatch, DailyNote, LoveLetter,
    WellnessRoutine, RoutineCompletion, WellnessAchievement, CheckInEntry
)

def create_cbt_games_tables():
    """Create all CBT games tables"""
    print("Creating CBT Games tables...")
    
    app, socketio = create_app()
    
    with app.app_context():
        try:
            # Create all new tables
            db.create_all()
            
            print("✅ Successfully created CBT games tables:")
            print("   - thought_reframes")
            print("   - emotion_matches")
            print("   - daily_notes")
            print("   - love_letters")
            print("   - wellness_routines")
            print("   - routine_completions")
            print("   - wellness_achievements")
            print("   - checkin_entries")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False

if __name__ == '__main__':
    success = create_cbt_games_tables()
    sys.exit(0 if success else 1)
