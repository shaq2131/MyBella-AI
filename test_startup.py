"""
Diagnostic script to isolate terminal hang issue
"""
import sys

print("=== STEP 1: Script started ===", flush=True)

try:
    print("=== STEP 2: Importing backend... ===", flush=True)
    from backend import create_app
    print("=== STEP 3: Import successful ===", flush=True)
    
    print("=== STEP 4: Creating app... ===", flush=True)
    app, socketio = create_app()
    print("=== STEP 5: App created ===", flush=True)
    
    print("=== STEP 6: Testing health endpoint... ===", flush=True)
    with app.test_client() as client:
        resp = client.get('/health/healthz')
        print(f"Health check: {resp.status_code} - {resp.data.decode('utf-8')}", flush=True)
    
    print("\n" + "="*60)
    print("✅ App initialization successful!")
    print("   The app can be imported and responds to requests.")
    print("   Issue is likely with socketio.run() blocking behavior.")
    print("="*60 + "\n", flush=True)
    
    print("=== STEP 7: Starting server with Flask only (no Socket.IO)... ===", flush=True)
    print("   Access at: http://127.0.0.1:5000", flush=True)
    print("   Press CTRL+C to stop", flush=True)
    
    # Run with Flask directly to avoid Socket.IO blocking issues
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        use_reloader=False
    )
    
except Exception as e:
    print(f"\n❌ ERROR at current step: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
