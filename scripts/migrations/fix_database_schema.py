"""
Fix Database Schema Issues
Adds missing columns to match the current models
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from backend import create_app
from backend.database.models.models import db
from sqlalchemy import text, inspect

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def fix_user_settings_table():
    """Add missing columns to user_settings table"""
    print("\n📝 Fixing user_settings table...")
    
    with db.engine.connect() as conn:
        # Check and add preferred_chat_mode
        if not check_column_exists('user_settings', 'preferred_chat_mode'):
            print("  Adding preferred_chat_mode column...")
            conn.execute(text("""
                ALTER TABLE user_settings 
                ADD COLUMN preferred_chat_mode VARCHAR(20) DEFAULT 'chat';
            """))
            conn.commit()
            print("  ✅ Added preferred_chat_mode")
        else:
            print("  ℹ️  preferred_chat_mode already exists")
        
        # Check and add communication_style
        if not check_column_exists('user_settings', 'communication_style'):
            print("  Adding communication_style column...")
            conn.execute(text("""
                ALTER TABLE user_settings 
                ADD COLUMN communication_style VARCHAR(50);
            """))
            conn.commit()
            print("  ✅ Added communication_style")
        else:
            print("  ℹ️  communication_style already exists")

def fix_mood_routes_compatibility():
    """Add missing columns to mood_entries for compatibility with mood_routes"""
    print("\n📝 Checking mood_entries table...")
    
    with db.engine.connect() as conn:
        # Check if mood_level exists
        if not check_column_exists('mood_entries', 'mood_level'):
            print("  Adding mood_level column (as integer representation)...")
            conn.execute(text("""
                ALTER TABLE mood_entries 
                ADD COLUMN mood_level INTEGER;
            """))
            # Update mood_level based on overall_mood enum value
            conn.execute(text("""
                UPDATE mood_entries 
                SET mood_level = CAST(overall_mood AS INTEGER);
            """))
            conn.commit()
            print("  ✅ Added mood_level")
        else:
            print("  ℹ️  mood_level already exists")
        
        # Check if mood_label exists
        if not check_column_exists('mood_entries', 'mood_label'):
            print("  Adding mood_label column...")
            conn.execute(text("""
                ALTER TABLE mood_entries 
                ADD COLUMN mood_label VARCHAR(100);
            """))
            conn.commit()
            print("  ✅ Added mood_label")
        else:
            print("  ℹ️  mood_label already exists")
        
        # Check if emotions exists
        if not check_column_exists('mood_entries', 'emotions'):
            print("  Adding emotions column...")
            conn.execute(text("""
                ALTER TABLE mood_entries 
                ADD COLUMN emotions TEXT;
            """))
            conn.commit()
            print("  ✅ Added emotions")
        else:
            print("  ℹ️  emotions already exists")
        
        # Check if activities exists
        if not check_column_exists('mood_entries', 'activities'):
            print("  Adding activities column...")
            conn.execute(text("""
                ALTER TABLE mood_entries 
                ADD COLUMN activities TEXT;
            """))
            conn.commit()
            print("  ✅ Added activities")
        else:
            print("  ℹ️  activities already exists")
        
        # Check if notes exists (different from reflection_note)
        if not check_column_exists('mood_entries', 'notes'):
            print("  Adding notes column...")
            conn.execute(text("""
                ALTER TABLE mood_entries 
                ADD COLUMN notes TEXT;
            """))
            conn.commit()
            print("  ✅ Added notes")
        else:
            print("  ℹ️  notes already exists")

def verify_persona_migration():
    """Verify that persona migration columns exist"""
    print("\n📝 Verifying persona migration...")
    
    required_columns = {
        'persona_profiles': ['voice_id', 'custom_voice_url', 'is_custom', 'user_id'],
        'chat_messages': ['persona_id'],
        'conversation_memories': ['persona_id'],
        'user_settings': ['current_persona_id']
    }
    
    all_good = True
    for table, columns in required_columns.items():
        for column in columns:
            if not check_column_exists(table, column):
                print(f"  ❌ Missing: {table}.{column}")
                all_good = False
            else:
                print(f"  ✅ Exists: {table}.{column}")
    
    return all_good

def run_fixes():
    """Run all database fixes"""
    print("\n" + "="*60)
    print("🔧 DATABASE SCHEMA FIXES")
    print("="*60)
    
    app, socketio = create_app()
    
    with app.app_context():
        try:
            # Fix user_settings
            fix_user_settings_table()
            
            # Fix mood_entries for mood_routes compatibility
            fix_mood_routes_compatibility()
            
            # Verify persona migration
            if verify_persona_migration():
                print("\n✅ All persona migration columns exist!")
            else:
                print("\n⚠️  Some persona migration columns are missing")
                print("   Run: python scripts/migrations/add_persona_isolation.py")
            
            print("\n" + "="*60)
            print("🎉 DATABASE FIXES COMPLETED!")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error during fixes: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = run_fixes()
    sys.exit(0 if success else 1)
