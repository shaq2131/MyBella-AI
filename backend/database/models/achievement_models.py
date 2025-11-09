"""
Achievement and Streak Models for MyBella
Gamification system with badges, milestones, and streak tracking
"""

from backend.database.models.models import db
from datetime import datetime, timedelta
from sqlalchemy import func


class Achievement(db.Model):
    """
    Achievement definitions (badges, milestones)
    """
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    
    # Achievement category
    category = db.Column(db.String(50), nullable=False)
    # Categories: 'streak', 'milestone', 'exercise', 'mood', 'conversation', 'wellness'
    
    # Achievement tier (bronze, silver, gold, platinum)
    tier = db.Column(db.String(20), default='bronze')
    
    # Unlock condition
    condition_type = db.Column(db.String(50), nullable=False)
    # Types: 'streak_days', 'total_moods', 'total_exercises', 'total_conversations', etc.
    
    condition_value = db.Column(db.Integer, nullable=False)
    # e.g., 7 for 7-day streak, 50 for 50 total mood entries
    
    # Visual representation
    icon = db.Column(db.String(50), default='🏆')
    color = db.Column(db.String(20), default='#FFD700')
    
    # Points awarded
    points = db.Column(db.Integer, default=10)
    
    # Hidden until unlocked?
    is_secret = db.Column(db.Boolean, default=False)
    
    # Active/inactive
    active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_achievements = db.relationship('UserAchievement', back_populates='achievement', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Achievement {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'tier': self.tier,
            'condition_type': self.condition_type,
            'condition_value': self.condition_value,
            'icon': self.icon,
            'color': self.color,
            'points': self.points,
            'is_secret': self.is_secret
        }


class UserAchievement(db.Model):
    """
    User's unlocked achievements
    """
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id', ondelete='CASCADE'), nullable=False)
    
    # Unlock timestamp
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Progress when unlocked
    progress_value = db.Column(db.Integer, default=0)
    
    # Notification sent?
    notified = db.Column(db.Boolean, default=False)
    
    # Viewed by user?
    viewed = db.Column(db.Boolean, default=False)
    
    # Relationships
    achievement = db.relationship('Achievement', back_populates='user_achievements')
    
    # Composite unique constraint (user can't unlock same achievement twice)
    __table_args__ = (
        db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),
    )
    
    def __repr__(self):
        return f'<UserAchievement user={self.user_id} achievement={self.achievement_id}>'
    
    def to_dict(self):
        """Convert to dictionary with achievement details"""
        return {
            'id': self.id,
            'achievement': self.achievement.to_dict() if self.achievement else None,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
            'progress_value': self.progress_value,
            'notified': self.notified,
            'viewed': self.viewed
        }


class Streak(db.Model):
    """
    User streak tracking (daily check-ins)
    """
    __tablename__ = 'streaks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Current streak
    current_streak = db.Column(db.Integer, default=0)
    
    # Longest streak ever
    longest_streak = db.Column(db.Integer, default=0)
    
    # Last check-in date (date only, no time)
    last_checkin_date = db.Column(db.Date, nullable=True)
    
    # Total check-in days (lifetime)
    total_checkins = db.Column(db.Integer, default=0)
    
    # Streak started date
    streak_start_date = db.Column(db.Date, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Streak user={self.user_id} current={self.current_streak}>'
    
    def check_in(self):
        """
        Record a check-in for today
        Updates streak counter intelligently
        """
        today = datetime.utcnow().date()
        
        # First check-in ever
        if self.last_checkin_date is None:
            self.current_streak = 1
            self.longest_streak = 1
            self.last_checkin_date = today
            self.streak_start_date = today
            self.total_checkins = 1
            return True
        
        # Already checked in today
        if self.last_checkin_date == today:
            return False
        
        # Check-in yesterday (continue streak)
        yesterday = today - timedelta(days=1)
        if self.last_checkin_date == yesterday:
            self.current_streak += 1
            self.last_checkin_date = today
            self.total_checkins += 1
            
            # Update longest streak
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
            
            return True
        
        # Missed days (reset streak)
        self.current_streak = 1
        self.last_checkin_date = today
        self.streak_start_date = today
        self.total_checkins += 1
        
        return True
    
    def get_streak_calendar(self, days=30):
        """
        Get calendar data for last N days
        Returns list of dates with check-in status
        """
        today = datetime.utcnow().date()
        calendar_data = []
        
        for i in range(days):
            date = today - timedelta(days=days - i - 1)
            
            # Determine if user checked in on this date
            # This requires querying actual activity (mood entries, exercises, etc.)
            # For now, we'll mark dates within current streak as checked in
            
            is_checkin = False
            if self.last_checkin_date and self.streak_start_date:
                if self.streak_start_date <= date <= self.last_checkin_date:
                    is_checkin = True
            
            calendar_data.append({
                'date': date.isoformat(),
                'checked_in': is_checkin,
                'is_today': date == today
            })
        
        return calendar_data
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_checkin_date': self.last_checkin_date.isoformat() if self.last_checkin_date else None,
            'total_checkins': self.total_checkins,
            'streak_start_date': self.streak_start_date.isoformat() if self.streak_start_date else None
        }


class LeaderboardEntry(db.Model):
    """
    Leaderboard rankings (cached for performance)
    """
    __tablename__ = 'leaderboard_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Total points from achievements
    total_points = db.Column(db.Integer, default=0)
    
    # Current rank
    rank = db.Column(db.Integer, nullable=True)
    
    # Total achievements unlocked
    total_achievements = db.Column(db.Integer, default=0)
    
    # Current streak (denormalized for sorting)
    current_streak = db.Column(db.Integer, default=0)
    
    # Longest streak (denormalized)
    longest_streak = db.Column(db.Integer, default=0)
    
    # Display name (for privacy)
    display_name = db.Column(db.String(100), nullable=True)
    
    # Opt-in to leaderboard
    opt_in = db.Column(db.Boolean, default=False)
    
    # Last updated
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<LeaderboardEntry user={self.user_id} points={self.total_points} rank={self.rank}>'
    
    def to_dict(self, include_user_id=False):
        """Convert to dictionary"""
        data = {
            'rank': self.rank,
            'display_name': self.display_name or 'Anonymous',
            'total_points': self.total_points,
            'total_achievements': self.total_achievements,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak
        }
        
        if include_user_id:
            data['user_id'] = self.user_id
        
        return data
