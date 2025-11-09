"""
Simple Integration Test - Chat Voice Mode and Memory Controls
"""

import sys
sys.path.insert(0, '.')

from backend import create_app
from backend.database.models.models import db
from sqlalchemy import inspect

print("\n" + "="*70)
print("Integration Test: Chat/Voice Mode Toggle & Memory Controls")
print("="*70 + "\n")

app, _ = create_app()

with app.app_context():
    # Check database
    print("1. Checking database schema...")
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('user_settings')]
    
    if 'preferred_chat_mode' in columns:
        print("   OK: Column 'preferred_chat_mode' exists")
    else:
        print("   ADDING: preferred_chat_mode column...")
        try:
            db.engine.execute("""
                ALTER TABLE user_settings 
                ADD COLUMN preferred_chat_mode VARCHAR(20) DEFAULT 'chat'
            """)
            print("   OK: Column added")
        except Exception as e:
            print(f"   ERROR: {e}")
    
    # Check blueprints
    print("\n2. Checking blueprint registration...")
    blueprints = list(app.blueprints.keys())
    
    checks = {
        'user_prefs': 'User Preferences API',
        'memory': 'Memory Routes',
        'api': 'Chat API'
    }
    
    for bp, name in checks.items():
        status = "OK" if bp in blueprints else "MISSING"
        print(f"   {status}: {name} ({bp})")
    
    # Test API routes
    print("\n3. Testing API endpoints...")
    test_client = app.test_client()
    
    endpoints_to_test = [
        ('/health/healthz', 'Health Check'),
        ('/api/user/chat-mode', 'Chat Mode API'),
        ('/api/memory/stats', 'Memory Stats API')
    ]
    
    for endpoint, name in endpoints_to_test:
        try:
            resp = test_client.get(endpoint)
            print(f"   {resp.status_code}: {name} - {endpoint}")
        except Exception as e:
            print(f"   ERROR: {name} - {str(e)[:50]}")
    
    print("\n" + "="*70)
    print("Test Complete!")
    print("="*70)
    print("\nNext Steps:")
    print("1. Start server: python test_startup.py")
    print("2. Visit: http://127.0.0.1:5000/users/chat")
    print("3. Test the Chat/Voice toggle button")
    print("4. Test Memory Controls in sidebar")
    print()
