"""
Simple Flask runner without Socket.IO
Use this to test if the Flask app works without Socket.IO complications
"""

from backend import create_app

app, socketio = create_app()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting MyBella Server (Flask only mode)")
    print("   Socket.IO features will be limited")
    print("   Local: http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    # Run Flask directly without Socket.IO
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False
    )
