import os

wellness_code = '''"""Cognitive Behavioral Therapy (CBT) Models for MyBella"""

from backend.database.models.models import db
from datetime import datetime, date
from sqlalchemy import Enum
import enum

class MoodScale(enum.Enum):
    VERY_LOW = 1
    LOW = 2
    SOMEWHAT_LOW = 3
    BELOW_AVERAGE = 4
    AVERAGE = 5
    SOMEWHAT_GOOD = 6
    GOOD = 7
    VERY_GOOD = 8
    EXCELLENT = 9
    OUTSTANDING = 10

class ThoughtPattern(enum.Enum):
    ALL_OR_NOTHING = "all_or_nothing"
    OVERGENERALIZATION = "overgeneralization"
    MENTAL_FILTER = "mental_filter"
    DISCOUNTING_POSITIVE = "discounting_positive"
    JUMPING_TO_CONCLUSIONS = "jumping_to_conclusions"
    MAGNIFICATION = "magnification"
    EMOTIONAL_REASONING = "emotional_reasoning"
    SHOULD_STATEMENTS = "should_statements"
    LABELING = "labeling"
    PERSONALIZATION = "personalization"


class CBTSession(db.Model):
    __tablename__ = 'cbt_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_type = db.Column(db.String(50), nullable=False)
    persona = db.Column(db.String(50), default='Maya')
    trigger_event = db.Column(db.Text, nullable=True)
    initial_mood = db.Column(db.Enum(MoodScale), nullable=True)
    final_mood = db.Column(db.Enum(MoodScale), nullable=True)
    automatic_thoughts = db.Column(db.Text, nullable=True)
    thought_patterns = db.Column(db.Text, nullable=True)
    evidence_for = db.Column(db.Text, nullable=True)
    evidence_against = db.Column(db.Text, nullable=True)
    balanced_thought = db.Column(db.Text, nullable=True)
    coping_strategies = db.Column(db.Text, nullable=True)
    action_plan = db.Column(db.Text, nullable=True)
    homework_assigned = db.Column(db.Text, nullable=True)
    duration_minutes = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref='cbt_sessions')


class MoodEntry(db.Model):
    __tablename__ = 'mood_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    overall_mood = db.Column(db.Enum(MoodScale), nullable=False)
    anxiety_level = db.Column(db.Enum(MoodScale), nullable=True)
    stress_level = db.Column(db.Enum(MoodScale), nullable=True)
    energy_level = db.Column(db.Enum(MoodScale), nullable=True)
    sleep_quality = db.Column(db.Enum(MoodScale), nullable=True)
    exercise_minutes = db.Column(db.Integer, default=0)
    water_glasses = db.Column(db.Integer, default=0)
    meditation_minutes = db.Column(db.Integer, default=0)
    social_interaction = db.Column(db.Boolean, default=False)
    gratitude_note = db.Column(db.Text, nullable=True)
    reflection_note = db.Column(db.Text, nullable=True)
    challenge_faced = db.Column(db.Text, nullable=True)
    entry_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='mood_entries')


class WellnessGoal(db.Model):
    __tablename__ = 'wellness_goals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), default='medium')
    target_value = db.Column(db.Float, nullable=True)
    current_value = db.Column(db.Float, default=0)
    unit = db.Column(db.String(50), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    target_date = db.Column(db.Date, nullable=True)
    completed_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='active')
    completion_percentage = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref='wellness_goals')


class FinanceEntry(db.Model):
    __tablename__ = 'finance_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    is_planned = db.Column(db.Boolean, default=False)
    budget_category = db.Column(db.String(50), nullable=True)
    spending_mood = db.Column(db.Enum(MoodScale), nullable=True)
    necessity_rating = db.Column(db.Integer, nullable=True)
    regret_level = db.Column(db.Integer, default=0)
    transaction_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='finance_entries')


class SocialConnection(db.Model):
    __tablename__ = 'social_connections'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    relationship_type = db.Column(db.String(50), nullable=False)
    contact_info = db.Column(db.String(200), nullable=True)
    closeness_level = db.Column(db.Integer, default=5)
    support_level = db.Column(db.Integer, default=5)
    interaction_frequency = db.Column(db.String(20), default='weekly')
    last_contact_date = db.Column(db.Date, nullable=True)
    last_contact_type = db.Column(db.String(50), nullable=True)
    next_planned_contact = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    birthday = db.Column(db.Date, nullable=True)
    important_dates = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref='social_connections')


class CopingStrategy(db.Model):
    __tablename__ = 'coping_strategies'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    difficulty_level = db.Column(db.Integer, default=1)
    times_used = db.Column(db.Integer, default=0)
    average_effectiveness = db.Column(db.Float, default=0)
    last_used_date = db.Column(db.Date, nullable=True)
    personal_notes = db.Column(db.Text, nullable=True)
    custom_modifications = db.Column(db.Text, nullable=True)
    trigger_situations = db.Column(db.Text, nullable=True)
    is_recommended = db.Column(db.Boolean, default=False)
    recommendation_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref='coping_strategies')


class WellnessInsight(db.Model):
    __tablename__ = 'wellness_insights'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    insight_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    recommended_actions = db.Column(db.Text, nullable=True)
    priority_level = db.Column(db.String(20), default='medium')
    data_points_analyzed = db.Column(db.Integer, default=0)
    confidence_score = db.Column(db.Float, default=0)
    time_period_analyzed = db.Column(db.String(50), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    is_helpful = db.Column(db.Boolean, nullable=True)
    user_notes = db.Column(db.Text, nullable=True)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    user = db.relationship('User', backref='wellness_insights')


class ThoughtReframe(db.Model):
    __tablename__ = 'thought_reframes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    negative_thought = db.Column(db.Text, nullable=False)
    cognitive_distortion = db.Column(db.String(50), nullable=True)
    user_reframe = db.Column(db.Text, nullable=True)
    ai_feedback = db.Column(db.Text, nullable=True)
    alternative_reframes = db.Column(db.Text, nullable=True)
    quality_score = db.Column(db.Integer, default=0)
    creativity_bonus = db.Column(db.Integer, default=0)
    total_points = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    time_spent_seconds = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='thought_reframes')


class EmotionMatch(db.Model):
    __tablename__ = 'emotion_matches'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_type = db.Column(db.String(50), default='emotion_coping')
    difficulty_level = db.Column(db.Integer, default=1)
    total_pairs = db.Column(db.Integer, default=8)
    matched_pairs = db.Column(db.Integer, default=0)
    failed_attempts = db.Column(db.Integer, default=0)
    time_seconds = db.Column(db.Integer, default=0)
    score = db.Column(db.Integer, default=0)
    accuracy_percentage = db.Column(db.Float, default=0)
    pairs_learned = db.Column(db.Text, nullable=True)
    favorite_strategies = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='emotion_matches')


class DailyNote(db.Model):
    __tablename__ = 'daily_notes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    note_type = db.Column(db.String(50), default='general')
    title = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)
    prompt_used = db.Column(db.Text, nullable=True)
    ai_response = db.Column(db.Text, nullable=True)
    mood_before = db.Column(db.Enum(MoodScale), nullable=True)
    mood_after = db.Column(db.Enum(MoodScale), nullable=True)
    tags = db.Column(db.Text, nullable=True)
    is_private = db.Column(db.Boolean, default=False)
    is_pinned = db.Column(db.Boolean, default=False)
    note_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref='daily_notes')


class LoveLetter(db.Model):
    __tablename__ = 'love_letters'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    persona = db.Column(db.String(50), nullable=False)
    direction = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)
    emotional_theme = db.Column(db.String(50), nullable=True)
    intensity_level = db.Column(db.Integer, default=5)
    ai_prompt_used = db.Column(db.Text, nullable=True)
    ai_suggestions = db.Column(db.Text, nullable=True)
    is_favorite = db.Column(db.Boolean, default=False)
    read_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='love_letters')


class WellnessRoutine(db.Model):
    __tablename__ = 'wellness_routines'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    routine_type = db.Column(db.String(20), nullable=False)
    time_of_day = db.Column(db.Time, nullable=True)
    days_of_week = db.Column(db.String(50), nullable=True)
    tasks = db.Column(db.Text, nullable=False)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    total_completions = db.Column(db.Integer, default=0)
    last_completed = db.Column(db.Date, nullable=True)
    reminder_enabled = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref='wellness_routines')


class RoutineCompletion(db.Model):
    __tablename__ = 'routine_completions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    routine_id = db.Column(db.Integer, db.ForeignKey('wellness_routines.id'), nullable=False)
    completion_date = db.Column(db.Date, nullable=False, default=date.today)
    completion_time = db.Column(db.Time, nullable=False, default=datetime.utcnow().time)
    tasks_completed = db.Column(db.Text, nullable=True)
    completion_percentage = db.Column(db.Float, default=100)
    mood_rating = db.Column(db.Enum(MoodScale), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='routine_completions')
    routine = db.relationship('WellnessRoutine', backref='completions')


class WellnessAchievement(db.Model):
    __tablename__ = 'wellness_achievements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    badge_name = db.Column(db.String(100), nullable=False)
    badge_description = db.Column(db.Text, nullable=False)
    badge_icon = db.Column(db.String(100), nullable=True)
    badge_tier = db.Column(db.String(20), default='bronze')
    required_count = db.Column(db.Integer, default=1)
    current_count = db.Column(db.Integer, default=0)
    is_unlocked = db.Column(db.Boolean, default=False)
    unlocked_at = db.Column(db.DateTime, nullable=True)
    points_awarded = db.Column(db.Integer, default=0)
    special_reward = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='wellness_achievements')


class CheckInEntry(db.Model):
    __tablename__ = 'checkin_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    checkin_type = db.Column(db.String(20), nullable=False)
    checkin_date = db.Column(db.Date, nullable=False, default=date.today)
    checkin_time = db.Column(db.Time, nullable=False, default=datetime.utcnow().time)
    sleep_quality = db.Column(db.Enum(MoodScale), nullable=True)
    morning_mood = db.Column(db.Enum(MoodScale), nullable=True)
    morning_intention = db.Column(db.Text, nullable=True)
    morning_affirmation = db.Column(db.Text, nullable=True)
    evening_mood = db.Column(db.Enum(MoodScale), nullable=True)
    gratitude_items = db.Column(db.Text, nullable=True)
    accomplishments = db.Column(db.Text, nullable=True)
    challenges_faced = db.Column(db.Text, nullable=True)
    tomorrow_preparation = db.Column(db.Text, nullable=True)
    persona_used = db.Column(db.String(50), default='Isabella')
    ai_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='checkin_entries')
'''

with open('backend/database/models/wellness_models.py', 'w', encoding='utf-8') as f:
    f.write(wellness_code)

print("wellness_models.py created successfully!")
