#!/usr/bin/env python3
"""
Migration script to add gender field to users table
Run this script to add gender column for gender-based persona assignment
"""

import sqlite3
import os
from datetime import datetime

def migrate_add_gender():
    """Add gender column to users table"""
    # Get database path
    db_path = os.path.join('backend', 'database', 'instances', 'mybella.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if gender column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'gender' not in columns:
            print("Adding gender column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN gender VARCHAR(20)")
            print("✅ Gender column added successfully")
        else:
            print("ℹ️ Gender column already exists")
        
        conn.commit()
        conn.close()
        
        print("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔄 Starting gender field migration...")
    print(f"📅 Migration started at: {datetime.now()}")
    
    success = migrate_add_gender()
    
    if success:
        print("\n🎉 Migration completed! Users can now specify gender for persona assignment.")
        print("📋 Next steps:")
        print("   1. Update registration forms to capture gender")
        print("   2. Update user settings to allow gender changes")
        print("   3. Test gender-based persona assignment")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")