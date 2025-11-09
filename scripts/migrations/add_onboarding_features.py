"""
Database migration to add onboarding and enhanced features
Run this to update your database with new columns
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend import create_app
from backend.database.models.models import db

def migrate_database():
    """Add new columns to existing tables"""
    app, socketio = create_app()
    
    with app.app_context():
        try:
            # Add onboarding columns to user_settings
            with db.engine.connect() as conn:
                # Check if columns exist before adding
                try:
                    conn.execute(db.text("""
                        ALTER TABLE user_settings 
                        ADD COLUMN onboarding_completed BOOLEAN DEFAULT 0
                    """))
                    print("✓ Added onboarding_completed column")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print("✓ onboarding_completed column already exists")
                    else:
                        print(f"Warning: {e}")
                
                try:
                    conn.execute(db.text("""
                        ALTER TABLE user_settings 
                        ADD COLUMN onboarding_completed_at DATETIME
                    """))
                    print("✓ Added onboarding_completed_at column")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print("✓ onboarding_completed_at column already exists")
                    else:
                        print(f"Warning: {e}")
                
                try:
                    conn.execute(db.text("""
                        ALTER TABLE user_settings 
                        ADD COLUMN personality_type VARCHAR(50)
                    """))
                    print("✓ Added personality_type column")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print("✓ personality_type column already exists")
                    else:
                        print(f"Warning: {e}")
                
                try:
                    conn.execute(db.text("""
                        ALTER TABLE user_settings 
                        ADD COLUMN communication_style VARCHAR(50) DEFAULT 'friendly'
                    """))
                    print("✓ Added communication_style column")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print("✓ communication_style column already exists")
                    else:
                        print(f"Warning: {e}")
                
                conn.commit()
            
            print("\n✅ Database migration completed successfully!")
            print("You can now restart your application.")
            
        except Exception as e:
            print(f"\n❌ Error during migration: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("🚀 Starting database migration...\n")
    migrate_database()
