"""
MyBella - AI Companion Application
Main entry point for the Flask application with Socket.IO support
"""

from backend import create_app

app, socketio = create_app()

if __name__ == '__main__':
    # Run with Socket.IO support
    # host='0.0.0.0' makes it accessible on your local network
    # Change to '127.0.0.1' for localhost-only access
    import sys
    print("\n" + "="*60)
    print("🚀 Starting MyBella Server...")
    print("   Local: http://127.0.0.1:5000")
    print("   Network: http://192.168.1.100:5000")
    print("="*60 + "\n")
    sys.stdout.flush()
    
    try:
        # Run server with threading mode (Python 3.13 compatible)
        # This should block and keep the server running
        print("Starting server with threading async mode...")
        socketio.run(
            app, 
            debug=True,  # Enable debug to see exact errors
            host='0.0.0.0', 
            port=5000,
            use_reloader=False,
            allow_unsafe_werkzeug=True,
            log_output=True  # Surface server logs for debugging
        )
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("👋 Server stopped by user")
        print("="*60)
    except Exception as e:
        print(f"\n\n❌ Server Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # If execution reaches here without exception, the server exited normally
    # (for example, the process was stopped by another command). No action needed.
