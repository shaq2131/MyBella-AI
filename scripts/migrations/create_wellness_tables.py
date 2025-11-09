#!/usr/bin/env python3
"""
Database migration script to create wellness tables
"""
import sys
import os

# Add the project root to Python path
# Since this script is in the project root, just use its directory
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine, text
from backend.database.models.models import db
from backend.database.models.wellness_models import CBTSession, MoodEntry, WellnessGoal, FinanceEntry, SocialConnection, CopingStrategy, WellnessInsight

def main():
    # Database path
    db_path = os.path.join(project_root, 'backend', 'database', 'instances', 'mybella.db')
    
    print(f"Creating wellness tables in: {db_path}")
    
    # Ensure directory exists
    db_dir = os.path.dirname(db_path)
    os.makedirs(db_dir, exist_ok=True)
    
    # Create database engine
    engine = create_engine(f'sqlite:///{db_path}')
    
    try:
        # Create all wellness tables
        print('Creating wellness tables...')
        db.metadata.create_all(engine)
        
        print('✅ Wellness database tables created successfully!')
        print('Tables created:')
        print('- cbt_sessions')
        print('- mood_entries') 
        print('- wellness_goals')
        print('- finance_entries')
        print('- social_connections')
        print('- coping_strategies')
        print('- wellness_insights')
        
        # Verify tables exist
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            wellness_tables = [t for t in tables if t in ['cbt_sessions', 'mood_entries', 'wellness_goals', 'finance_entries', 'social_connections', 'coping_strategies', 'wellness_insights']]
            print(f'\nVerified {len(wellness_tables)} wellness tables in database: {wellness_tables}')
            
        print('\n🎉 Database migration completed successfully!')
        
    except Exception as e:
        print(f'❌ Error creating wellness tables: {str(e)}')
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())