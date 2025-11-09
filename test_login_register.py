"""
Quick test to check if login/register routes are accessible
"""
import sys
sys.path.insert(0, '.')

from backend import create_app

app, socketio = create_app()

with app.app_context():
    # Test 1: Check if routes exist
    print("=" * 60)
    print("🔍 Testing MyBella Routes")
    print("=" * 60)
    
    print("\n📋 Registered Routes:")
    routes = []
    for rule in app.url_map.iter_rules():
        if any(keyword in str(rule) for keyword in ['login', 'register', 'signup', 'dashboard', 'chat']):
            routes.append(f"  {rule.methods} {rule}")
    
    for route in sorted(routes):
        print(route)
    
    # Test 2: Check database connection
    print("\n💾 Database Check:")
    try:
        from backend.database.models.models import db, User
        user_count = User.query.count()
        print(f"  ✅ Database connected")
        print(f"  ✅ Users in database: {user_count}")
    except Exception as e:
        print(f"  ❌ Database error: {e}")
    
    # Test 3: Check templates exist
    print("\n📄 Template Check:")
    import os
    templates_to_check = [
        'frontend/templates/auth/login.html',
        'frontend/templates/auth/register.html',
        'frontend/templates/auth/register_multistep.html',
        'frontend/templates/users/dashboard.html',
        'frontend/templates/users/chat.html'
    ]
    
    for template in templates_to_check:
        if os.path.exists(template):
            print(f"  ✅ {template}")
        else:
            print(f"  ❌ {template} NOT FOUND")
    
    # Test 4: Try to render login page
    print("\n🎨 Template Rendering Test:")
    try:
        from flask import render_template
        with app.test_request_context():
            result = render_template('auth/login.html', title='Sign In')
            print(f"  ✅ login.html renders successfully ({len(result)} bytes)")
    except Exception as e:
        print(f"  ❌ login.html error: {e}")
    
    try:
        from flask import render_template
        from datetime import date
        with app.test_request_context():
            result = render_template('auth/register_multistep.html', 
                                   title='Join MyBella',
                                   today_date=date.today().isoformat())
            print(f"  ✅ register_multistep.html renders successfully ({len(result)} bytes)")
    except Exception as e:
        print(f"  ❌ register_multistep.html error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Diagnostic Complete")
    print("=" * 60)
    print("\n💡 To test in browser:")
    print("   1. Make sure server is running: python mybella.py")
    print("   2. Go to: http://127.0.0.1:5000/login")
    print("   3. Go to: http://127.0.0.1:5000/signup")
    print("   4. Go to: http://127.0.0.1:5000/register")
    print()
