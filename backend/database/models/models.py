"""
Database models for MyBella application
SQLAlchemy models for User, Chat, Message, and UserSettings
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

def init_db(app):
    """Initialize database with app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()

class User(UserMixin, db.Model):
    """User model with authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # 'user' or 'admin'
    gender = db.Column(db.String(20), nullable=True)  # 'male', 'female', 'other', 'prefer_not_to_say'
    profile_picture = db.Column(db.String(255), nullable=True)  # Path to profile picture
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    messages = db.relationship('Message', backref='user', lazy=True, cascade='all, delete-orphan')
    chats = db.relationship('Chat', backref='user', lazy=True, cascade='all, delete-orphan')
    settings = db.relationship('UserSettings', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def get_default_persona(self):
        """Get default persona based on user's gender"""
        if self.gender == 'female':
            return 'Alex'  # Female users get Alex as default
        elif self.gender == 'male':
            return 'Isabella'  # Male users get Isabella as default
        else:
            return 'Isabella'  # Default fallback for other/unspecified

    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.email}>'

class Chat(db.Model):
    """Chat session model"""
    __tablename__ = 'chats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    persona = db.Column(db.String(50), default='Isabella')
    mode = db.Column(db.String(50), default='Companion')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='chat', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Chat {self.id}: {self.title}>'

class Message(db.Model):
    """Individual message model"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=True)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'bot'
    content = db.Column(db.Text, nullable=False)
    persona = db.Column(db.String(50), default='Isabella')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message {self.id}: {self.role}>'

class UserSettings(db.Model):
    """User preferences and settings"""
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Chat preferences
    current_persona = db.Column(db.String(50), default='Isabella')  # Legacy: persona name
    current_persona_id = db.Column(db.Integer, db.ForeignKey('persona_profiles.id'), nullable=True)  # New: persona reference
    mode = db.Column(db.String(50), default='Companion')
    
    # Audio preferences
    tts_enabled = db.Column(db.Boolean, default=True)
    voice_override = db.Column(db.String(100), nullable=True)
    preferred_chat_mode = db.Column(db.String(20), default='chat')  # 'chat' or 'voice'
    
    # Privacy and safety
    age_confirmed = db.Column(db.Boolean, default=False)
    show_ads = db.Column(db.Boolean, default=True)
    
    # Onboarding
    onboarding_completed = db.Column(db.Boolean, default=False)
    onboarding_completed_at = db.Column(db.DateTime, nullable=True)
    personality_type = db.Column(db.String(50), nullable=True)  # balanced, introverted, extroverted
    communication_style = db.Column(db.String(50), default='friendly')  # friendly, professional, casual
    nickname = db.Column(db.String(100), nullable=True)
    pronouns = db.Column(db.String(50), nullable=True)
    support_focus = db.Column(db.String(50), nullable=True)
    support_topics = db.Column(db.Text, nullable=True)
    check_in_preference = db.Column(db.String(50), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserSettings for user {self.user_id}>'

class PersonaProfile(db.Model):
    """Persona profile information and avatars"""
    __tablename__ = 'persona_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # Persona name (Isabella, etc.)
    display_name = db.Column(db.String(100), nullable=True)  # Friendly display name
    description = db.Column(db.Text, nullable=True)  # Persona description
    profile_picture = db.Column(db.String(255), nullable=True)  # Path to persona avatar (keeping original column name)
    personality_traits = db.Column(db.Text, nullable=True)  # Personality description
    communication_style = db.Column(db.String(50), default='friendly')  # Conversational tone (friendly, professional, etc.)
    tagline = db.Column(db.String(150), nullable=True)  # Short persona tagline for UI displays
    voice_settings = db.Column(db.String(100), default='default')  # Voice configuration (legacy)
    voice_id = db.Column(db.String(100), nullable=True)  # ElevenLabs voice ID
    custom_voice_url = db.Column(db.Text, nullable=True)  # URL to custom voice file
    is_active = db.Column(db.Boolean, default=True)  # Whether persona is available (keeping original column name)
    is_custom = db.Column(db.Boolean, default=False)  # Whether this is a user-created persona
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Owner of custom persona
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Admin who created
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_personas')
    owner = db.relationship('User', foreign_keys=[user_id], backref='custom_personas')
    
    # Properties for backward compatibility
    @property
    def avatar_url(self):
        return self.profile_picture
    
    @avatar_url.setter
    def avatar_url(self, value):
        self.profile_picture = value
    
    @property
    def active(self):
        return self.is_active
    
    @active.setter
    def active(self, value):
        self.is_active = value

    def __repr__(self):
        return f'<PersonaProfile {self.name}>'

class UserSubscription(db.Model):
    """User subscription and voice call minutes tracking"""
    __tablename__ = 'user_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Subscription details
    subscription_type = db.Column(db.String(50), default='free')  # 'free', 'basic', 'premium'
    subscription_status = db.Column(db.String(20), default='active')  # 'active', 'expired', 'cancelled'
    subscription_start = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_end = db.Column(db.DateTime, nullable=True)
    subscription_amount = db.Column(db.Float, default=0.0)  # Monthly subscription amount
    
    # Voice call minutes
    total_minutes = db.Column(db.Integer, default=0)  # Total minutes allocated
    used_minutes = db.Column(db.Float, default=0.0)  # Minutes used (can be fractional)
    remaining_minutes = db.Column(db.Float, default=0.0)  # Minutes remaining
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='subscription')
    voice_calls = db.relationship('VoiceCall', backref='subscription', lazy=True, cascade='all, delete-orphan')

    def get_remaining_minutes(self):
        """Get remaining minutes as float"""
        return max(0.0, self.total_minutes - self.used_minutes)
    
    def has_minutes(self, required_minutes=0.1):
        """Check if user has enough minutes for a call"""
        return self.get_remaining_minutes() >= required_minutes
    
    def is_subscription_active(self):
        """Check if subscription is active and not expired"""
        if self.subscription_status != 'active':
            return False
        if self.subscription_end and self.subscription_end < datetime.utcnow():
            return False
        return True

    def __repr__(self):
        return f'<UserSubscription {self.user_id}: {self.subscription_type}>'

class VoiceCall(db.Model):
    """Voice call session tracking"""
    __tablename__ = 'voice_calls'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('user_subscriptions.id'), nullable=False)
    persona = db.Column(db.String(50), nullable=False)
    
    # Call details
    call_status = db.Column(db.String(20), default='initiated')  # 'initiated', 'active', 'ended', 'failed'
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Float, default=0.0)  # Actual call duration
    
    # Call quality and metadata
    call_quality = db.Column(db.String(20), nullable=True)  # 'excellent', 'good', 'fair', 'poor'
    user_rating = db.Column(db.Integer, nullable=True)  # 1-5 rating
    notes = db.Column(db.Text, nullable=True)  # Call notes or issues
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calculate_duration(self):
        """Calculate call duration in minutes"""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            return duration.total_seconds() / 60.0
        return 0.0

    def __repr__(self):
        return f'<VoiceCall {self.id}: {self.persona} ({self.duration_minutes}min)>'