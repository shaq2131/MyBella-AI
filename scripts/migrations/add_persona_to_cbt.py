"""
Migration: Add persona_id to CBT tables for persona continuity
This ensures CBT exercises remember which persona guided the user through the activity.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend import create_app
from backend.database.models.models import db
from sqlalchemy import inspect, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    try:
        app, _ = create_app()
        with app.app_context():
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            return column_name in columns
    except Exception as e:
        logger.error(f"Error checking column {table_name}.{column_name}: {e}")
        return False


def add_persona_to_thought_reframes():
    """Add persona_id to thought_reframes table"""
    logger.info("🔧 Adding persona_id to thought_reframes...")
    
    if check_column_exists('thought_reframes', 'persona_id'):
        logger.info("   ✅ persona_id already exists in thought_reframes")
        return True
    
    try:
        app, _ = create_app()
        with app.app_context():
            # Add persona_id column
            db.session.execute(text("""
                ALTER TABLE thought_reframes 
                ADD COLUMN persona_id INTEGER 
                REFERENCES persona_profiles(id) ON DELETE SET NULL
            """))
            
            # Create index for performance
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_thought_reframes_persona 
                ON thought_reframes(persona_id)
            """))
            
            db.session.commit()
            logger.info("   ✅ Added persona_id to thought_reframes")
            return True
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return False


def add_persona_to_daily_notes():
    """Add persona_id to daily_notes table"""
    logger.info("🔧 Adding persona_id to daily_notes...")
    
    if check_column_exists('daily_notes', 'persona_id'):
        logger.info("   ✅ persona_id already exists in daily_notes")
        return True
    
    try:
        app, _ = create_app()
        with app.app_context():
            # Add persona_id column
            db.session.execute(text("""
                ALTER TABLE daily_notes 
                ADD COLUMN persona_id INTEGER 
                REFERENCES persona_profiles(id) ON DELETE SET NULL
            """))
            
            # Create index for performance
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_daily_notes_persona 
                ON daily_notes(persona_id)
            """))
            
            db.session.commit()
            logger.info("   ✅ Added persona_id to daily_notes")
            return True
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return False


def add_persona_to_checkin_entries():
    """Add persona_id to checkin_entries table (replace persona_used string)"""
    logger.info("🔧 Adding persona_id to checkin_entries...")
    
    if check_column_exists('checkin_entries', 'persona_id'):
        logger.info("   ✅ persona_id already exists in checkin_entries")
        return True
    
    try:
        app, _ = create_app()
        with app.app_context():
            # Add persona_id column
            db.session.execute(text("""
                ALTER TABLE checkin_entries 
                ADD COLUMN persona_id INTEGER 
                REFERENCES persona_profiles(id) ON DELETE SET NULL
            """))
            
            # Create index for performance
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_checkin_entries_persona 
                ON checkin_entries(persona_id)
            """))
            
            db.session.commit()
            logger.info("   ✅ Added persona_id to checkin_entries")
            logger.info("   ℹ️  Note: persona_used (string) column still exists for backward compatibility")
            return True
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return False


def add_persona_to_cbt_sessions():
    """Add persona_id to cbt_sessions table (replace persona string)"""
    logger.info("🔧 Adding persona_id to cbt_sessions...")
    
    if check_column_exists('cbt_sessions', 'persona_id'):
        logger.info("   ✅ persona_id already exists in cbt_sessions")
        return True
    
    try:
        app, _ = create_app()
        with app.app_context():
            # Add persona_id column
            db.session.execute(text("""
                ALTER TABLE cbt_sessions 
                ADD COLUMN persona_id INTEGER 
                REFERENCES persona_profiles(id) ON DELETE SET NULL
            """))
            
            # Create index for performance
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_cbt_sessions_persona 
                ON cbt_sessions(persona_id)
            """))
            
            db.session.commit()
            logger.info("   ✅ Added persona_id to cbt_sessions")
            logger.info("   ℹ️  Note: persona (string) column still exists for backward compatibility")
            return True
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return False


def add_persona_to_emotion_matches():
    """Add persona_id to emotion_matches table"""
    logger.info("🔧 Adding persona_id to emotion_matches...")
    
    if check_column_exists('emotion_matches', 'persona_id'):
        logger.info("   ✅ persona_id already exists in emotion_matches")
        return True
    
    try:
        app, _ = create_app()
        with app.app_context():
            # Add persona_id column
            db.session.execute(text("""
                ALTER TABLE emotion_matches 
                ADD COLUMN persona_id INTEGER 
                REFERENCES persona_profiles(id) ON DELETE SET NULL
            """))
            
            # Create index for performance
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_emotion_matches_persona 
                ON emotion_matches(persona_id)
            """))
            
            db.session.commit()
            logger.info("   ✅ Added persona_id to emotion_matches")
            return True
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return False


def verify_all_columns():
    """Verify all persona_id columns were added"""
    logger.info("\n📋 Verifying all CBT persona columns...")
    
    tables_to_check = [
        'thought_reframes',
        'daily_notes',
        'checkin_entries',
        'cbt_sessions',
        'emotion_matches'
    ]
    
    all_exist = True
    for table in tables_to_check:
        exists = check_column_exists(table, 'persona_id')
        status = "✅" if exists else "❌"
        logger.info(f"   {status} {table}.persona_id")
        if not exists:
            all_exist = False
    
    return all_exist


def run_migration():
    """Run the complete migration"""
    logger.info("="*60)
    logger.info("🚀 PERSONA-CBT INTEGRATION MIGRATION")
    logger.info("="*60)
    logger.info("This migration adds persona_id foreign keys to CBT tables")
    logger.info("for persona continuity in wellness activities.\n")
    
    results = []
    
    # Add persona_id to all CBT tables
    results.append(add_persona_to_thought_reframes())
    results.append(add_persona_to_daily_notes())
    results.append(add_persona_to_checkin_entries())
    results.append(add_persona_to_cbt_sessions())
    results.append(add_persona_to_emotion_matches())
    
    # Verify all columns were added
    all_verified = verify_all_columns()
    
    logger.info("\n" + "="*60)
    if all(results) and all_verified:
        logger.info("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        logger.info("="*60)
        logger.info("\n✨ Next Steps:")
        logger.info("   1. Update wellness_models.py to add persona_id relationships")
        logger.info("   2. Update CBT service functions to accept persona_id")
        logger.info("   3. Update CBT routes to pass current persona_id")
        logger.info("   4. Test persona continuity in CBT exercises")
    else:
        logger.info("⚠️  MIGRATION COMPLETED WITH WARNINGS")
        logger.info("="*60)
        logger.info("Some columns may have already existed (which is fine)")
    
    return all(results)


if __name__ == '__main__':
    try:
        success = run_migration()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"\n❌ MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
