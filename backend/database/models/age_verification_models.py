"""
Age Verification & Feature Access Models
Handles age-gated content compliance (COPPA, GDPR-K, App Store policies)
"""

from datetime import datetime, date
from backend.database.models.models import db


class UserAgeVerification(db.Model):
    """
    Stores user age verification information
    Required for COPPA/GDPR-K compliance
    """
    __tablename__ = 'user_age_verification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Age Information
    date_of_birth = db.Column(db.Date, nullable=False)
    age_verified_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Calculated Fields
    is_teen = db.Column(db.Boolean, default=False)  # 16-17 years old
    is_adult = db.Column(db.Boolean, default=True)  # 18+ years old
    is_minor = db.Column(db.Boolean, default=False)  # Under 16 (blocked)
    
    # Verification Metadata
    verification_method = db.Column(db.String(50), default='dob_entry')  # dob_entry, id_verification, etc.
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    
    # Age Tier (for feature access logic)
    age_tier = db.Column(db.String(20))  # 'minor', 'teen', 'adult'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('age_verification', uselist=False))
    
    def calculate_age(self):
        """Calculate current age from date of birth"""
        today = date.today()
        age = today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
        return age
    
    def update_age_tier(self):
        """Update age tier and flags based on current age"""
        age = self.calculate_age()
        
        if age < 16:
            self.age_tier = 'minor'
            self.is_minor = True
            self.is_teen = False
            self.is_adult = False
        elif 16 <= age <= 17:
            self.age_tier = 'teen'
            self.is_minor = False
            self.is_teen = True
            self.is_adult = False
        else:  # 18+
            self.age_tier = 'adult'
            self.is_minor = False
            self.is_teen = False
            self.is_adult = True
        
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<UserAgeVerification user_id={self.user_id} tier={self.age_tier}>'


class FeatureAccess(db.Model):
    """
    Controls which features are accessible based on age tier
    Supports age-gated content compliance
    """
    __tablename__ = 'feature_access'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Feature Information
    feature_key = db.Column(db.String(100), unique=True, nullable=False)  # e.g., 'intimacy_mode', 'whisper_talk'
    feature_name = db.Column(db.String(200), nullable=False)
    feature_description = db.Column(db.Text)
    feature_category = db.Column(db.String(50))  # 'romantic', 'wellness', 'social', 'premium'
    
    # Age Restrictions
    min_age_required = db.Column(db.Integer, default=16)  # Minimum age to access
    teen_accessible = db.Column(db.Boolean, default=True)  # 16-17 can access
    adult_only = db.Column(db.Boolean, default=False)  # 18+ only
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    requires_verification = db.Column(db.Boolean, default=False)  # Extra verification needed
    
    # Compliance Notes
    compliance_reason = db.Column(db.Text)  # Why restricted (e.g., "COPPA compliance")
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_accessible_for_age(self, age: int) -> bool:
        """Check if feature is accessible for given age"""
        if not self.is_active:
            return False
        
        if age < self.min_age_required:
            return False
        
        if self.adult_only and age < 18:
            return False
        
        if 16 <= age <= 17 and not self.teen_accessible:
            return False
        
        return True
    
    def __repr__(self):
        return f'<FeatureAccess {self.feature_key} min_age={self.min_age_required}>'


class UserFeatureOverride(db.Model):
    """
    Manual overrides for specific users (e.g., parental consent)
    """
    __tablename__ = 'user_feature_override'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    feature_key = db.Column(db.String(100), nullable=False)
    
    # Override Details
    override_type = db.Column(db.String(50))  # 'grant', 'deny'
    reason = db.Column(db.Text)
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Admin who granted
    
    # Consent Information (for minors with parental consent)
    parental_consent = db.Column(db.Boolean, default=False)
    consent_document_url = db.Column(db.String(500))
    
    # Expiry
    expires_at = db.Column(db.DateTime)  # Optional expiration
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='feature_overrides')
    admin = db.relationship('User', foreign_keys=[granted_by])
    
    def is_active(self):
        """Check if override is still active"""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def __repr__(self):
        return f'<UserFeatureOverride user={self.user_id} feature={self.feature_key}>'


class PersonaAgeRestriction(db.Model):
    """
    Age-appropriate behavior settings for each persona
    Controls tone, topics, and interaction style based on user age
    """
    __tablename__ = 'persona_age_restriction'
    
    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey('persona_profiles.id'), nullable=False)
    
    # Teen Mode Settings (16-17)
    teen_mode_enabled = db.Column(db.Boolean, default=True)
    teen_tone = db.Column(db.String(100))  # 'supportive_sister', 'brotherly_coach', 'maternal_guide'
    teen_system_prompt = db.Column(db.Text)  # Custom system prompt for teen interactions
    teen_forbidden_topics = db.Column(db.Text)  # JSON array of blocked topics
    
    # Adult Mode Settings (18+)
    adult_tone = db.Column(db.String(100))  # Original persona tone
    adult_system_prompt = db.Column(db.Text)  # Custom system prompt for adult interactions
    
    # Behavior Flags
    allow_romantic_dialogue = db.Column(db.Boolean, default=False)  # Teen: False, Adult: True
    allow_flirty_responses = db.Column(db.Boolean, default=False)
    allow_intimacy_content = db.Column(db.Boolean, default=False)
    wellness_focus_only = db.Column(db.Boolean, default=False)  # Teen: True
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    persona = db.relationship('PersonaProfile', backref='age_restrictions')
    
    def get_system_prompt_for_age(self, age: int) -> str:
        """Get appropriate system prompt based on user age"""
        if 16 <= age <= 17:
            return self.teen_system_prompt or "You are a supportive, wellness-focused companion."
        else:
            return self.adult_system_prompt or ""
    
    def __repr__(self):
        return f'<PersonaAgeRestriction persona={self.persona_id}>'
