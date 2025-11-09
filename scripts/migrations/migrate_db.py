"""
Database migration script for MyBella
Updates persona_profiles table to include new admin management columns
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Update database schema for admin features"""
    db_path = os.path.join('backend', 'database', 'instances', 'mybella.db')
    
    if not os.path.exists(db_path):
        print("Database not found. Please run the app first to create initial database.")
        return
    
    print(f"Migrating database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(persona_profiles)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Add missing columns if they don't exist
        migrations = []
        
        if 'personality_traits' not in columns:
            migrations.append("ALTER TABLE persona_profiles ADD COLUMN personality_traits TEXT")
            
        if 'voice_settings' not in columns:
            migrations.append("ALTER TABLE persona_profiles ADD COLUMN voice_settings VARCHAR(100) DEFAULT 'default'")
            
        if 'communication_style' not in columns:
            migrations.append("ALTER TABLE persona_profiles ADD COLUMN communication_style VARCHAR(50) DEFAULT 'friendly'")

        if 'tagline' not in columns:
            migrations.append("ALTER TABLE persona_profiles ADD COLUMN tagline VARCHAR(150)")

        if 'created_by' not in columns:
            migrations.append("ALTER TABLE persona_profiles ADD COLUMN created_by INTEGER")
            
        if 'updated_at' not in columns:
            migrations.append("ALTER TABLE persona_profiles ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        
        # Add subscription_amount to user_subscriptions if it doesn't exist
        cursor.execute("PRAGMA table_info(user_subscriptions)")
        sub_columns = [column[1] for column in cursor.fetchall()]
        
        if 'subscription_amount' not in sub_columns:
            migrations.append("ALTER TABLE user_subscriptions ADD COLUMN subscription_amount REAL DEFAULT 0.0")
        
        # Execute migrations
        for migration in migrations:
            print(f"Executing: {migration}")
            cursor.execute(migration)
        
        # Update existing personas with default values
        cursor.execute("""
            UPDATE persona_profiles 
            SET personality_traits = COALESCE(personality_traits, 'Friendly, helpful, and engaging AI companion'),
                voice_settings = COALESCE(voice_settings, 'default'),
                communication_style = COALESCE(communication_style, 'friendly')
            WHERE personality_traits IS NULL 
               OR voice_settings IS NULL
               OR communication_style IS NULL
        """)
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Show updated schema
        cursor.execute("PRAGMA table_info(persona_profiles)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"Updated columns: {new_columns}")
        
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()