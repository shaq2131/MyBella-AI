"""
Cleanup old voice call system tables
Removes voice_calls and user_subscriptions tables
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from mybella import app
from backend.database.models.models import db

with app.app_context():
    print("Cleaning up old voice call system tables...")
    
    try:
        # Drop old tables
        db.session.execute(db.text("DROP TABLE IF EXISTS voice_calls"))
        db.session.execute(db.text("DROP TABLE IF EXISTS user_subscriptions"))
        db.session.execute(db.text("DROP TABLE IF EXISTS subscription_plans"))
        db.session.commit()
        
        print("✅ Successfully removed old tables:")
        print("   - voice_calls")
        print("   - user_subscriptions")
        print("   - subscription_plans")
        
    except Exception as e:
        print(f"❌ Error cleaning up tables: {e}")
        db.session.rollback()
