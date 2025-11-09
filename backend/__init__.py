"""
MyBella Backend Application Package
Main Flask application with authentication, chat, AI integrations, and real-time communication
"""

import os
import logging
from flask import Flask
from flask_login import LoginManager

# Import database initialization
from backend.database.models.models import db, init_db

# Import all models to ensure they're registered with SQLAlchemy
from backend.database.models import onboarding_models  # SaaS features
from backend.database.models import wellness_models  # CBT features
from backend.database.models import age_verification_models  # Age-gated features

# Import configuration
from backend.services.config import configure_app

# Import services
from backend.services.firebase.firebase_service import initialize_firebase
from backend.services.chat.pinecone_service import initialize_pinecone
from backend.services.socketio import init_socketio

# Login manager
login_manager = LoginManager()

def create_app():
    """Application factory pattern"""
    import os
    # Get the absolute path to the project root
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    
    app = Flask(__name__, 
                template_folder=os.path.join(project_root, 'frontend', 'templates'),
                static_folder=os.path.join(project_root, 'frontend', 'static'))

    # Configure the app
    configure_app(app)

    # Create upload directories in your existing structure
    try:
        upload_folder = app.config.get('UPLOAD_FOLDER')
        profile_pics_folder = app.config.get('PROFILE_PICS_FOLDER')
        persona_pics_folder = app.config.get('PERSONA_PICS_FOLDER')
        
        if upload_folder:
            os.makedirs(upload_folder, exist_ok=True)
        if profile_pics_folder:
            os.makedirs(profile_pics_folder, exist_ok=True)
        if persona_pics_folder:
            os.makedirs(persona_pics_folder, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create upload directories: {e}")

    # Initialize database
    init_db(app)
    
    # Initialize default personas
    with app.app_context():
        from backend.services.persona_init import initialize_default_personas
        initialize_default_personas()

    # Setup login manager
    login_manager.login_view = 'user_auth.login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.session_protection = 'basic'  # Less strict than 'strong'
    login_manager.init_app(app)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        try:
            from backend.database.models.models import User
            if user_id is None or user_id == 'None':
                return None
            user = User.query.get(int(user_id))
            if user and user.active:  # Only return active users
                return user
            return None
        except (ValueError, TypeError):
            return None

    # Initialize external services
    initialize_firebase(app)
    initialize_pinecone(app)
    
    # Initialize Socket.IO for real-time communication
    socketio = init_socketio(app)

    # Register blueprints
    from backend.routes.auth.users.user_auth import user_auth_bp
    from backend.routes.auth.admin.admin_auth_routes import admin_auth_bp
    from backend.routes.views.main_routes import main_bp
    from backend.routes.views.users.user_views import user_views_bp
    from backend.routes.views.admin.admin_views import admin_views_bp
    from backend.routes.views.onboarding_routes import onboarding_bp
    from backend.routes.mood.mood_routes import mood_bp
    from backend.routes.crisis.crisis_routes import crisis_bp
    from backend.routes.voice.voice_routes import voice_bp
    from backend.routes.exercises.exercises_routes import exercises_bp
    from backend.routes.memory.memory_routes import memory_bp
    from backend.routes.analytics.analytics_routes import analytics_bp
    from backend.routes.api.health_routes import health_bp
    from backend.routes.api.analytics_events_routes import analytics_events_bp
    from backend.routes.api.user_preferences_routes import user_prefs_bp
    from backend.routes.api.custom_persona_routes import custom_persona_bp
    from backend.routes.achievements.achievements_routes import achievements_bp
    from backend.routes.api.chat_routes import api_bp
    from backend.routes.admin.dashboard import admin_bp
    from backend.routes.admin.user_management import user_mgmt_bp
    from backend.routes.wellness.wellness_routes import wellness_bp
    from backend.routes.wellness.cbt_games_routes import cbt_games_bp
    from backend.routes.age_gate_routes import age_gate_bp  # AGE VERIFICATION (NEW)
    from backend.routes.secrets_routes import secrets_bp  # SECRETS VAULT
    from backend.routes.moderation_routes import moderation_bp  # CONTENT MODERATION (NEW)
    
    app.register_blueprint(user_auth_bp, url_prefix='/')
    app.register_blueprint(admin_auth_bp)
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(user_views_bp, url_prefix='/')
    app.register_blueprint(admin_views_bp, url_prefix='/')
    app.register_blueprint(onboarding_bp)  # Already has url_prefix='/onboarding' defined in blueprint
    app.register_blueprint(age_gate_bp)  # AGE VERIFICATION - /age-gate, /api/age-verification/*
    app.register_blueprint(secrets_bp)  # SECRETS VAULT - /secrets/*
    app.register_blueprint(moderation_bp)  # CONTENT MODERATION - /moderation/*
    app.register_blueprint(mood_bp)  # Already has url_prefix='/mood' defined in blueprint
    app.register_blueprint(crisis_bp)  # Already has url_prefix='/crisis' defined in blueprint - NO LOGIN REQUIRED
    app.register_blueprint(voice_bp)  # Already has url_prefix='/voice' defined in blueprint
    app.register_blueprint(exercises_bp)  # Already has url_prefix='/exercises' defined in blueprint
    app.register_blueprint(memory_bp)  # Already has url_prefix='/memory' defined in blueprint
    app.register_blueprint(analytics_bp)  # Already has url_prefix='/analytics' defined in blueprint
    app.register_blueprint(health_bp)  # /health/healthz, /health/readyz
    app.register_blueprint(analytics_events_bp)  # /api/analytics/track
    app.register_blueprint(user_prefs_bp)  # /api/user/chat-mode (NEW)
    app.register_blueprint(custom_persona_bp)  # /api/personas/* (NEW - Custom persona management)
    app.register_blueprint(achievements_bp)  # Already has url_prefix='/achievements' defined in blueprint
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp)  # Already has url_prefix='/admin' defined in blueprint
    app.register_blueprint(user_mgmt_bp)  # Already has url_prefix='/admin' defined in blueprint
    app.register_blueprint(wellness_bp, url_prefix='/wellness')
    app.register_blueprint(cbt_games_bp)

    # Onboarding middleware - redirect new users to onboarding
    @app.before_request
    def check_onboarding():
        from flask import request, redirect, url_for, session
        from flask_login import current_user
        from backend.services.onboarding_service import OnboardingService
        
        # Skip check for these routes
        skip_routes = [
            'static', 'onboarding', 'auth', 'admin_auth', 
            'health', 'api', '_debug_toolbar'
        ]
        
        # Skip if not logged in or route should be skipped
        if not current_user.is_authenticated:
            return
        
        if request.endpoint and any(request.endpoint.startswith(route) for route in skip_routes):
            return
        
        # Check if user needs onboarding
        try:
            if OnboardingService.needs_onboarding(current_user.id):
                # Allow access to logout
                if request.endpoint == 'user_auth.logout':
                    return
                # Redirect to onboarding
                return redirect(url_for('onboarding.onboarding_page'))
        except Exception as e:
            app.logger.error(f"Error checking onboarding status: {e}")
            # Don't block user on error
            return

    # Setup logging
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)

    return app, socketio