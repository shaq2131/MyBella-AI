"""
Configuration service for MyBella application
Handles environment variables and app configuration
"""

import os

def configure_app(app):
    """Configure Flask app with environment variables and settings"""
    
    # Core config
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-mybella-2024")
    
    # Session configuration - Balanced security for development  
    app.config['SESSION_COOKIE_SECURE'] = False  # Allow over HTTP in development
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS attacks
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
    app.config['SESSION_COOKIE_PATH'] = '/'
    app.config['SESSION_COOKIE_DOMAIN'] = None  # Use default domain
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

    # SQLite DB path using your existing structure
    db_path = os.path.abspath(os.path.join('backend', 'database', 'instances', 'mybella.db'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # API & feature config
    app.config.update(
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
        ELEVENLABS_API_KEY=os.getenv("ELEVENLABS_API_KEY", ""),
        ELEVENLABS_VOICE_ID=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
        FIREBASE_PROJECT_ID=os.getenv("FIREBASE_PROJECT_ID", ""),
        FIREBASE_CLIENT_EMAIL=os.getenv("FIREBASE_CLIENT_EMAIL", ""),
        FIREBASE_PRIVATE_KEY=os.getenv("FIREBASE_PRIVATE_KEY", ""),
        FIREBASE_DB_COLLECTION=os.getenv("FIREBASE_DB_COLLECTION", "mybella"),
        PINECONE_API_KEY=os.getenv("PINECONE_API_KEY", ""),
        PINECONE_ENV=os.getenv("PINECONE_ENVIRONMENT", "us-east-1"),
        PINECONE_INDEX=os.getenv("PINECONE_INDEX", "mybella-memory"),
        MAX_UPLOAD_MB=int(os.getenv("MAX_UPLOAD_MB", "10"))
    )

    # File upload limits
    app.config["MAX_CONTENT_LENGTH"] = app.config["MAX_UPLOAD_MB"] * 1024 * 1024

    # Profile picture settings using your structure
    upload_folder = os.path.abspath(os.path.join('backend', 'database', 'instances', 'uploads'))
    app.config["UPLOAD_FOLDER"] = upload_folder
    app.config["PROFILE_PICS_FOLDER"] = os.path.join(upload_folder, 'profile_pics')
    app.config["PERSONA_PICS_FOLDER"] = os.path.join(upload_folder, 'persona_pics')

    return app

# Constants
ALLOWED_AUDIO_EXT = {".mp3", ".wav", ".m4a"}
ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# Global flags (will be set by services)
firebase_ok = False
pinecone_ok = False