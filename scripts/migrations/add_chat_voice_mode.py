"""
Migration: Add preferred_chat_mode to user_settings
Run this once to add the new column for chat/voice mode toggle
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.database.models.models import db
from backend import create_app

def migrate():
    """Add preferred_chat_mode column to user_settings"""
    app, _ = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('user_settings')]
            
            if 'preferred_chat_mode' in columns:
                print("✅ Column 'preferred_chat_mode' already exists. Skipping.")
                return
            
            # Add column using raw SQL for SQLite compatibility
            db.engine.execute("""
                ALTER TABLE user_settings 
                ADD COLUMN preferred_chat_mode VARCHAR(20) DEFAULT 'chat'
            """)
            
            print("✅ Successfully added 'preferred_chat_mode' column to user_settings")
            print("   Default value: 'chat'")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔄 Running Migration: Add Chat/Voice Mode Preference")
    print("="*60 + "\n")
    migrate()
    print("\n" + "="*60)
    print("✅ Migration Complete!")
    print("="*60 + "\n")
