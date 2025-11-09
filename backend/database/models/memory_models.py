"""
Conversation Memory models for MyBella
Stores conversation history, summaries, and user preferences for personalized AI interactions
"""

from backend.database.models.models import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Text

class ConversationMemory(db.Model):
    """Store conversation summaries and context for personalized responses"""
    __tablename__ = 'conversation_memories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    persona = db.Column(db.String(50), nullable=False)  # Which persona was used (legacy)
    persona_id = db.Column(db.Integer, db.ForeignKey('persona_profiles.id'), nullable=True)  # New: persona reference
    
    # Conversation metadata
    session_id = db.Column(db.String(100))  # Group related conversations
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Memory content
    summary = db.Column(Text)  # AI-generated summary of conversation
    key_topics = db.Column(Text)  # Comma-separated topics discussed
    user_mood = db.Column(db.String(50))  # Detected mood during conversation
    important_facts = db.Column(Text)  # JSON string of important facts about user
    
    # Metadata
    message_count = db.Column(db.Integer, default=0)
    tokens_used = db.Column(db.Integer, default=0)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('conversation_memories', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ConversationMemory {self.user_id} - {self.persona} - {self.started_at}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'persona': self.persona,
            'session_id': self.session_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'summary': self.summary,
            'key_topics': self.key_topics.split(',') if self.key_topics else [],
            'user_mood': self.user_mood,
            'important_facts': self.important_facts,
            'message_count': self.message_count,
            'tokens_used': self.tokens_used
        }


class ChatMessage(db.Model):
    """Store individual chat messages for history and context"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    memory_id = db.Column(db.Integer, db.ForeignKey('conversation_memories.id'))
    persona_id = db.Column(db.Integer, db.ForeignKey('persona_profiles.id'), nullable=True)  # New: persona reference
    
    # Message content
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(Text, nullable=False)
    persona = db.Column(db.String(50))  # Legacy: kept for backward compatibility
    
    # Metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tokens = db.Column(db.Integer, default=0)
    model = db.Column(db.String(50))  # Which AI model was used
    
    # Context flags
    has_crisis_keywords = db.Column(db.Boolean, default=False)
    sentiment = db.Column(db.String(20))  # 'positive', 'negative', 'neutral'
    
    # Relationships
    user = db.relationship('User', backref=db.backref('chat_messages', lazy='dynamic'))
    memory = db.relationship('ConversationMemory', backref=db.backref('messages', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ChatMessage {self.role} - {self.timestamp}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'persona': self.persona,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'sentiment': self.sentiment
        }


class UserPreference(db.Model):
    """Track user preferences learned from conversations"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    persona_id = db.Column(db.Integer, db.ForeignKey('persona_profiles.id'), nullable=True)  # New: per-persona preferences
    
    # Preference details
    category = db.Column(db.String(50), nullable=False)  # 'topics', 'communication_style', 'interests', etc.
    key = db.Column(db.String(100), nullable=False)  # Specific preference key
    value = db.Column(Text)  # Preference value
    confidence = db.Column(db.Float, default=1.0)  # Confidence score (0-1)
    
    # Tracking
    learned_from = db.Column(db.String(100))  # Where this was learned (conversation, explicit setting)
    first_observed = db.Column(db.DateTime, default=datetime.utcnow)
    last_confirmed = db.Column(db.DateTime, default=datetime.utcnow)
    times_observed = db.Column(db.Integer, default=1)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('preferences', lazy='dynamic'))
    
    def __repr__(self):
        return f'<UserPreference {self.user_id} - {self.category}:{self.key}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'category': self.category,
            'key': self.key,
            'value': self.value,
            'confidence': self.confidence,
            'learned_from': self.learned_from,
            'times_observed': self.times_observed
        }
