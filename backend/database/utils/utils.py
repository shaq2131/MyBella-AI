"""
Utility functions for MyBella application
Helper functions for file handling, user sessions, and common operations
"""

import os
from flask import session
from flask_login import current_user
from backend.services.config import ALLOWED_AUDIO_EXT, ALLOWED_IMAGE_EXT
from backend.database.models.models import db

def get_db_connection():
    """Get database session for queries"""
    return db.session

def safe_filename(name):
    """Create a safe filename by removing invalid characters"""
    return "".join(c for c in name if c.isalnum() or c in ("_", "-", ".", " ")).strip()[:100]

def allowed_audio_file(filename):
    """Check if uploaded file has allowed audio extension"""
    ext = os.path.splitext(filename.lower())[1]
    return ext in ALLOWED_AUDIO_EXT

def allowed_image_file(filename):
    """Check if uploaded file has allowed image extension"""
    ext = os.path.splitext(filename.lower())[1]
    return ext in ALLOWED_IMAGE_EXT

def get_user_id():
    """Get current user ID (authenticated user preferred, fallback to session)"""
    if current_user.is_authenticated:
        return str(current_user.id)
    return session.get("user_id", "demo-user")

def get_persona():
    """Get current persona (from user settings or gender-based default)"""
    if (current_user.is_authenticated and 
        hasattr(current_user, "settings") and 
        current_user.settings and 
        current_user.settings.current_persona):
        return current_user.settings.current_persona
    elif current_user.is_authenticated:
        # Use gender-based default if no settings persona
        return current_user.get_default_persona()
    return session.get("persona", "Isabella")

def get_mode():
    """Get current mode (from user settings or session)"""
    if (current_user.is_authenticated and 
        hasattr(current_user, "settings") and 
        current_user.settings and 
        current_user.settings.mode):
        return current_user.settings.mode
    return session.get("mode", "Companion")

def get_tts_enabled():
    """Check if TTS is enabled for current user"""
    if (current_user.is_authenticated and 
        current_user.settings and 
        current_user.settings.tts_enabled is not None):
        return current_user.settings.tts_enabled
    return True  # Default to enabled

def get_persona_voice_id(user_id, persona_name):
    """Get custom voice ID for a specific user and persona combination"""
    from backend.database.models.models import UserSettings
    
    # Get user settings
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    if not settings or not settings.voice_assignments:
        return None
    
    # Check if persona has a custom voice assigned
    persona_key = persona_name.lower()
    return settings.voice_assignments.get(persona_key)

def set_persona_voice_id(user_id, persona_name, voice_id):
    """Set custom voice ID for a specific user and persona combination"""
    from backend.database.models.models import UserSettings
    
    # Get or create user settings
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.session.add(settings)
    
    # Initialize voice_assignments if None
    if not settings.voice_assignments:
        settings.voice_assignments = {}
    
    # Set the voice for this persona
    persona_key = persona_name.lower()
    settings.voice_assignments[persona_key] = voice_id
    
    db.session.commit()
    return True