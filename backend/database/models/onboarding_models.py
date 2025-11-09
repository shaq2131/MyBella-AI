"""
Onboarding and User Profiling Models
Tracks user onboarding flow, preferences, and initial setup
"""

from backend.database.models.models import db
from datetime import datetime
import json


class OnboardingQuiz(db.Model):
    """First-run onboarding quiz responses"""
    __tablename__ = 'onboarding_quiz'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Q1: What brings you to MyBella?
    primary_goal = db.Column(db.String(50), nullable=True)  # 'companionship', 'mental_health', 'productivity', 'creativity'
    secondary_goals = db.Column(db.Text, nullable=True)  # JSON array of additional goals
    
    # Q2: How are you feeling right now?
    initial_mood = db.Column(db.Integer, nullable=True)  # 1-10 scale
    mood_description = db.Column(db.String(100), nullable=True)  # 'stressed', 'happy', 'anxious', 'motivated'
    
    # Q3: How would you like your AI companion to talk to you?
    preferred_tone = db.Column(db.String(50), nullable=True)  # 'friendly', 'professional', 'casual', 'supportive'
    personality_preference = db.Column(db.String(50), nullable=True)  # 'warm', 'direct', 'playful', 'calm'
    
    # Q4: When would you like daily check-ins?
    preferred_check_in_time = db.Column(db.String(20), nullable=True)  # 'morning', 'evening', 'both', 'none'
    check_in_hour_morning = db.Column(db.Integer, nullable=True)  # 0-23 hours
    check_in_hour_evening = db.Column(db.Integer, nullable=True)  # 0-23 hours
    
    # Q5: Choose your starting companion
    selected_persona_id = db.Column(db.Integer, db.ForeignKey('persona_profiles.id'), nullable=True)
    persona_selection_reason = db.Column(db.Text, nullable=True)  # Why they chose this persona
    
    # Additional context
    experience_level = db.Column(db.String(20), nullable=True)  # 'first_time', 'tried_ai_before', 'ai_enthusiast'
    privacy_comfort = db.Column(db.String(20), nullable=True)  # 'very_comfortable', 'comfortable', 'cautious'
    
    # Completion tracking
    completed = db.Column(db.Boolean, default=False)
    completion_percentage = db.Column(db.Integer, default=0)  # 0-100
    current_step = db.Column(db.Integer, default=1)  # Which question they're on
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='onboarding_quiz')
    selected_persona = db.relationship('PersonaProfile', backref='onboarded_users')
    
    def get_secondary_goals_list(self):
        """Parse secondary goals from JSON"""
        if self.secondary_goals:
            try:
                return json.loads(self.secondary_goals)
            except:
                return []
        return []
    
    def set_secondary_goals_list(self, goals_list):
        """Save secondary goals as JSON"""
        self.secondary_goals = json.dumps(goals_list)
    
    def calculate_completion(self):
        """Calculate completion percentage based on answered questions"""
        total_fields = 5  # 5 main questions
        completed_fields = 0
        
        if self.primary_goal:
            completed_fields += 1
        if self.initial_mood is not None:
            completed_fields += 1
        if self.preferred_tone:
            completed_fields += 1
        if self.preferred_check_in_time:
            completed_fields += 1
        if self.selected_persona_id:
            completed_fields += 1
        
        self.completion_percentage = int((completed_fields / total_fields) * 100)
        return self.completion_percentage
    
    def __repr__(self):
        return f'<OnboardingQuiz user={self.user_id} completed={self.completed}>'


class UserDisclaimerAcceptance(db.Model):
    """Track user acceptance of disclaimers and terms"""
    __tablename__ = 'user_disclaimer_acceptance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Disclaimer types
    disclaimer_type = db.Column(db.String(50), nullable=False)  # 'therapy', 'crisis', 'privacy', 'terms'
    disclaimer_version = db.Column(db.String(20), nullable=False)  # Version tracking for updates
    
    # Acceptance details
    accepted = db.Column(db.Boolean, default=False)
    acceptance_text = db.Column(db.Text, nullable=True)  # What they agreed to
    ip_address = db.Column(db.String(50), nullable=True)  # For legal records
    user_agent = db.Column(db.String(255), nullable=True)  # Device info
    
    # Timestamps
    accepted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='disclaimer_acceptances')
    
    def __repr__(self):
        return f'<DisclaimerAcceptance user={self.user_id} type={self.disclaimer_type}>'


class CrisisResource(db.Model):
    """Crisis hotlines and resources by region"""
    __tablename__ = 'crisis_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Location
    country_code = db.Column(db.String(2), nullable=False, index=True)  # ISO 3166-1 alpha-2
    country_name = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=True)  # State/province for large countries
    
    # Resource details
    resource_type = db.Column(db.String(50), nullable=False)  # 'suicide', 'mental_health', 'domestic_violence', 'substance_abuse'
    organization_name = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(50), nullable=True)
    sms_number = db.Column(db.String(50), nullable=True)
    website_url = db.Column(db.String(255), nullable=True)
    chat_url = db.Column(db.String(255), nullable=True)
    
    # Availability
    available_24_7 = db.Column(db.Boolean, default=True)
    availability_hours = db.Column(db.String(100), nullable=True)  # "9AM-5PM Mon-Fri"
    languages = db.Column(db.Text, nullable=True)  # JSON array of language codes
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=1)  # Display order (1=highest)
    description = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_languages_list(self):
        """Parse languages from JSON"""
        if self.languages:
            try:
                return json.loads(self.languages)
            except:
                return []
        return []
    
    def __repr__(self):
        return f'<CrisisResource {self.country_code} {self.resource_type}>'


class UserMemoryControl(db.Model):
    """User control over conversation memories and data"""
    __tablename__ = 'user_memory_control'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Memory preferences
    memory_retention_days = db.Column(db.Integer, default=365)  # How long to keep memories
    auto_cleanup_enabled = db.Column(db.Boolean, default=False)  # Auto-delete old memories
    
    # Per-persona memory settings
    persona_memory_enabled = db.Column(db.Boolean, default=True)  # Allow persona memory collection
    cross_persona_sharing = db.Column(db.Boolean, default=False)  # Share context between personas
    
    # Privacy controls
    sensitive_topics_stored = db.Column(db.Boolean, default=True)  # Store health/personal topics
    location_data_stored = db.Column(db.Boolean, default=False)  # Store location mentions
    
    # Export tracking
    last_export_at = db.Column(db.DateTime, nullable=True)
    export_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='memory_control')
    
    def __repr__(self):
        return f'<UserMemoryControl user={self.user_id}>'


class ContentModerationLog(db.Model):
    """Log of content moderation actions"""
    __tablename__ = 'content_moderation_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for system events
    
    # Content details
    content_type = db.Column(db.String(50), nullable=False)  # 'message', 'profile', 'persona_creation'
    content_id = db.Column(db.Integer, nullable=True)  # Reference to actual content
    content_excerpt = db.Column(db.Text, nullable=True)  # First 500 chars
    
    # Moderation result
    flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.String(100), nullable=True)  # 'sexual_content', 'violence', 'harassment', 'underage'
    severity = db.Column(db.String(20), nullable=True)  # 'low', 'medium', 'high', 'critical'
    
    # Action taken
    action = db.Column(db.String(50), nullable=True)  # 'blocked', 'warned', 'logged_only', 'filtered'
    automated = db.Column(db.Boolean, default=True)  # Was this auto-moderated or human review?
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Admin who reviewed
    
    # Metadata
    moderation_engine = db.Column(db.String(50), nullable=True)  # 'regex', 'openai_moderation', 'custom_model'
    confidence_score = db.Column(db.Float, nullable=True)  # 0.0-1.0 confidence
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='moderation_logs')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='moderation_reviews')
    
    def __repr__(self):
        return f'<ModerationLog user={self.user_id} flagged={self.flagged}>'
