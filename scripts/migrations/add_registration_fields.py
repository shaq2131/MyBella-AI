"""
Database migration to add registration fields to user_settings
Adds: nickname, pronouns, support_focus, support_topics, check_in_preference
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend import create_app
from backend.database.models.models import db

def migrate_database():
    """Add registration fields to user_settings table"""
    app, socketio = create_app()
    
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # Add nickname column
                try:
                    conn.execute(db.text("""
                        ALTER TABLE user_settings 
                        ADD COLUMN nickname VARCHAR(100)
                    """))
                    print("✓ Added nickname column")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print("✓ nickname column already exists")
                    else:
                        print(f"Warning: {e}")
                
                # Add pronouns column
                try:
                    conn.execute(db.text("""
                        ALTER TABLE user_settings 
                        ADD COLUMN pronouns VARCHAR(50)
                    """))
                    print("✓ Added pronouns column")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print("✓ pronouns column already exists")
                    else:
                        print(f"Warning: {e}")
                
                # Add support_focus column
                try:
                    conn.execute(db.text("""
                        ALTER TABLE user_settings 
                        ADD COLUMN support_focus VARCHAR(50)
                    """))
                    print("✓ Added support_focus column")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print("✓ support_focus column already exists")
                    else:
                        print(f"Warning: {e}")
                
                # Add support_topics column
                try:
                    conn.execute(db.text("""
                        ALTER TABLE user_settings 
                        ADD COLUMN support_topics TEXT
                    """))
                    print("✓ Added support_topics column")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print("✓ support_topics column already exists")
                    else:
                        print(f"Warning: {e}")
                
                # Add check_in_preference column
                try:
                    conn.execute(db.text("""
                        ALTER TABLE user_settings 
                        ADD COLUMN check_in_preference VARCHAR(50)
                    """))
                    print("✓ Added check_in_preference column")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print("✓ check_in_preference column already exists")
                    else:
                        print(f"Warning: {e}")
                
                conn.commit()
            
            print("\n✅ Database migration completed successfully!")
            print("Registration form fields are now supported.")
            
        except Exception as e:
            print(f"\n❌ Error during migration: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("🚀 Starting database migration for registration fields...\n")
    migrate_database()
