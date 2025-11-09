"""
Quick Test Script for Persona System
Tests API endpoints and database structure
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend import create_app
from backend.database.models.models import db, PersonaProfile, UserSettings
from backend.database.models.memory_models import ChatMessage, ConversationMemory

def test_persona_system():
    """Test persona system implementation"""
    app, socketio = create_app()
    
    with app.app_context():
        print("\n🎭 Testing Persona System Implementation\n")
        
        # Test 1: Database schema
        print("1️⃣ Checking Database Schema...")
        inspector = db.inspect(db.engine)
        
        # Check persona_profiles columns
        persona_cols = {col['name'] for col in inspector.get_columns('persona_profiles')}
        required_persona_cols = {'voice_id', 'custom_voice_url', 'is_custom', 'user_id'}
        if required_persona_cols.issubset(persona_cols):
            print("   ✅ persona_profiles has all required columns")
        else:
            print(f"   ❌ Missing columns: {required_persona_cols - persona_cols}")
        
        # Check chat_messages columns
        chat_cols = {col['name'] for col in inspector.get_columns('chat_messages')}
        if 'persona_id' in chat_cols:
            print("   ✅ chat_messages has persona_id column")
        else:
            print("   ❌ chat_messages missing persona_id column")
        
        # Check user_settings columns
        settings_cols = {col['name'] for col in inspector.get_columns('user_settings')}
        if 'current_persona_id' in settings_cols:
            print("   ✅ user_settings has current_persona_id column")
        else:
            print("   ❌ user_settings missing current_persona_id column")
        
        # Test 2: System personas
        print("\n2️⃣ Checking System Personas...")
        system_personas = PersonaProfile.query.filter_by(is_custom=False).all()
        print(f"   📊 Found {len(system_personas)} system personas:")
        for persona in system_personas[:6]:  # Show first 6
            print(f"      • {persona.name} - {persona.description[:50]}...")
        
        # Test 3: Check migration status
        print("\n3️⃣ Checking Migration Status...")
        total_messages = ChatMessage.query.count()
        migrated_messages = ChatMessage.query.filter(ChatMessage.persona_id != None).count()
        
        if total_messages > 0:
            migration_percent = (migrated_messages / total_messages) * 100
            print(f"   📊 Messages migrated: {migrated_messages}/{total_messages} ({migration_percent:.1f}%)")
            if migration_percent == 100:
                print("   ✅ All messages have persona_id")
            elif migration_percent > 0:
                print("   ⚠️  Partial migration - run migration script again")
            else:
                print("   ❌ No messages migrated - run migration script")
        else:
            print("   ℹ️  No messages in database yet")
        
        # Test 4: API Blueprint registration
        print("\n4️⃣ Checking Blueprint Registration...")
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        if 'custom_persona' in blueprint_names:
            print("   ✅ custom_persona blueprint registered")
        else:
            print("   ❌ custom_persona blueprint NOT registered")
        
        # Test 5: Routes
        print("\n5️⃣ Checking Routes...")
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        persona_routes = [r for r in routes if '/api/personas' in r or '/personas' in r]
        print(f"   📊 Found {len(persona_routes)} persona-related routes:")
        for route in sorted(persona_routes)[:10]:  # Show first 10
            print(f"      • {route}")
        
        # Summary
        print("\n" + "="*50)
        print("🎯 SUMMARY")
        print("="*50)
        
        checks = {
            "Database schema": required_persona_cols.issubset(persona_cols) and 'persona_id' in chat_cols,
            "System personas": len(system_personas) >= 6,
            "Blueprint registered": 'custom_persona' in blueprint_names,
            "Routes available": len(persona_routes) > 0
        }
        
        passed = sum(checks.values())
        total = len(checks)
        
        for check, status in checks.items():
            symbol = "✅" if status else "❌"
            print(f"{symbol} {check}")
        
        print(f"\n{passed}/{total} checks passed")
        
        if passed == total:
            print("\n✨ All systems operational! Ready to test in browser.")
            print("\nNext steps:")
            print("1. Start server: python mybella.py")
            print("2. Visit: http://127.0.0.1:5000/users/personas")
            print("3. Create a custom persona and test memory isolation")
        else:
            print("\n⚠️  Some checks failed. Review output above.")
            if 'persona_id' not in chat_cols:
                print("\n🔧 Fix: Run migration script:")
                print("   python scripts/migrations/add_persona_isolation.py")

if __name__ == '__main__':
    try:
        test_persona_system()
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
