"""
Exercise tracking models for MyBella
Tracks user completion of breathing exercises, meditation, and journaling
"""

from backend.database.models.models import db
from datetime import datetime

class ExerciseCompletion(db.Model):
    """Track user completion of guided exercises"""
    __tablename__ = 'exercise_completions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exercise_type = db.Column(db.String(50), nullable=False)  # 'breathing', 'meditation', 'journaling'
    exercise_name = db.Column(db.String(100), nullable=False)  # '4-7-8 Breathing', 'Box Breathing', etc.
    duration_minutes = db.Column(db.Integer)  # For meditation sessions
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notes = db.Column(db.Text)  # Optional user notes
    mood_before = db.Column(db.Integer)  # 1-5 rating before exercise
    mood_after = db.Column(db.Integer)  # 1-5 rating after exercise
    
    # Relationship
    user = db.relationship('User', backref=db.backref('exercise_completions', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ExerciseCompletion {self.user_id} - {self.exercise_name}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exercise_type': self.exercise_type,
            'exercise_name': self.exercise_name,
            'duration_minutes': self.duration_minutes,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes,
            'mood_before': self.mood_before,
            'mood_after': self.mood_after
        }


class JournalingPrompt(db.Model):
    """Database of journaling prompts for guided reflection"""
    __tablename__ = 'journaling_prompts'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # 'gratitude', 'reflection', 'goals', 'anxiety', 'relationships'
    prompt = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20))  # 'beginner', 'intermediate', 'advanced'
    tags = db.Column(db.String(200))  # Comma-separated tags
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<JournalingPrompt {self.category} - {self.prompt[:50]}...>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'category': self.category,
            'prompt': self.prompt,
            'difficulty': self.difficulty,
            'tags': self.tags.split(',') if self.tags else []
        }
