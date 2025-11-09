"""
Migration Script: Remove Old Voice Call System
Run this to clean up old call/subscription infrastructure
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from flask import Flask
from backend.database.models.models import db
from backend.services.config import Config

def create_app():
    """Create Flask app for migration"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    return app

def remove_voice_call_tables():
    """Remove old voice call and subscription tables"""
    print("🗑️  Removing old voice call system tables...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Drop tables if they exist
            db.session.execute(db.text('DROP TABLE IF EXISTS voice_calls'))
            db.session.execute(db.text('DROP TABLE IF EXISTS user_subscriptions'))
            db.session.execute(db.text('DROP TABLE IF EXISTS subscription_plans'))
            
            db.session.commit()
            
            print("✅ Successfully removed old tables:")
            print("   - voice_calls")
            print("   - user_subscriptions")
            print("   - subscription_plans")
            
        except Exception as e:
            print(f"❌ Error removing tables: {e}")
            db.session.rollback()
            return False
    
    return True

def list_files_to_remove():
    """List files that should be manually removed"""
    print("\n📋 Files to manually remove:")
    
    files_to_remove = [
        "frontend/templates/users/voice_calls.html",
        "frontend/templates/users/voice_call_history.html",
        "frontend/templates/subscription.html",
        "backend/funcs/voice/voice_crud.py",
    ]
    
    for file_path in files_to_remove:
        full_path = os.path.join(os.getcwd(), file_path)
        exists = "✅ EXISTS" if os.path.exists(full_path) else "⚠️  NOT FOUND"
        print(f"   {exists} - {file_path}")
    
    print("\n💡 Note: These files can be deleted manually or kept for reference")

def check_new_files():
    """Check if new voice conversation files exist"""
    print("\n📦 New voice conversation files:")
    
    new_files = [
        "backend/services/voice/voice_conversation_service.py",
        "frontend/static/js/voice_conversation.js",
    ]
    
    for file_path in new_files:
        full_path = os.path.join(os.getcwd(), file_path)
        exists = "✅ EXISTS" if os.path.exists(full_path) else "❌ MISSING"
        print(f"   {exists} - {file_path}")

def main():
    """Main migration function"""
    print("=" * 60)
    print("🔄 MyBella Voice System Migration")
    print("=" * 60)
    print()
    
    # Check new files
    check_new_files()
    
    # List files to remove
    list_files_to_remove()
    
    print()
    print("⚠️  This will remove old voice call system tables!")
    print()
    
    response = input("Continue with database cleanup? (yes/no): ").strip().lower()
    
    if response == 'yes':
        success = remove_voice_call_tables()
        
        if success:
            print("\n✅ Migration completed successfully!")
            print()
            print("📝 Next steps:")
            print("   1. Manually delete the old files listed above")
            print("   2. Update navigation menus to remove voice call links")
            print("   3. Test the new voice conversation feature")
            print("   4. Update documentation")
        else:
            print("\n❌ Migration failed. Please check errors above.")
            return 1
    else:
        print("\n🚫 Migration cancelled.")
        return 0
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
