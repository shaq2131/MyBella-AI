"""
Achievements Service for MyBella
Handles streak tracking, achievement unlocking, and leaderboard management
"""

from backend.database.models.models import db
from backend.database.models.wellness_models import MoodEntry
from backend.database.models.exercise_models import ExerciseCompletion
from backend.database.models.memory_models import ChatMessage
from backend.database.models.achievement_models import Achievement, UserAchievement, Streak, LeaderboardEntry
from datetime import datetime, timedelta
from sqlalchemy import func, distinct
from collections import defaultdict


class AchievementsService:
    """Service for managing achievements and streaks"""
    
    @staticmethod
    def get_or_create_streak(user_id):
        """Get or create streak record for user"""
        streak = Streak.query.filter_by(user_id=user_id).first()
        
        if not streak:
            streak = Streak(user_id=user_id)
            db.session.add(streak)
            db.session.commit()
        
        return streak
    
    @staticmethod
    def record_checkin(user_id):
        """
        Record a check-in for today
        Returns (streak_object, was_updated, newly_unlocked_achievements)
        """
        streak = AchievementsService.get_or_create_streak(user_id)
        
        # Attempt check-in
        was_updated = streak.check_in()
        db.session.commit()
        
        # Check for newly unlocked streak achievements
        newly_unlocked = []
        if was_updated:
            newly_unlocked = AchievementsService.check_streak_achievements(user_id, streak.current_streak)
        
        return streak, was_updated, newly_unlocked
    
    @staticmethod
    def check_streak_achievements(user_id, current_streak):
        """
        Check if user unlocked any streak-based achievements
        Returns list of newly unlocked achievements
        """
        # Get all streak achievements
        streak_achievements = Achievement.query.filter_by(
            category='streak',
            condition_type='streak_days',
            active=True
        ).all()
        
        newly_unlocked = []
        
        for achievement in streak_achievements:
            # Check if already unlocked
            already_unlocked = UserAchievement.query.filter_by(
                user_id=user_id,
                achievement_id=achievement.id
            ).first()
            
            if already_unlocked:
                continue
            
            # Check if condition met
            if current_streak >= achievement.condition_value:
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id,
                    progress_value=current_streak
                )
                db.session.add(user_achievement)
                newly_unlocked.append(achievement)
                
                # Update leaderboard
                AchievementsService.update_leaderboard_entry(user_id)
        
        if newly_unlocked:
            db.session.commit()
        
        return newly_unlocked
    
    @staticmethod
    def check_mood_achievements(user_id):
        """
        Check mood-based achievements
        Returns list of newly unlocked achievements
        """
        # Count total mood entries
        total_moods = MoodEntry.query.filter_by(user_id=user_id).count()
        
        # Get mood achievements
        mood_achievements = Achievement.query.filter_by(
            category='mood',
            condition_type='total_moods',
            active=True
        ).all()
        
        newly_unlocked = []
        
        for achievement in mood_achievements:
            # Check if already unlocked
            already_unlocked = UserAchievement.query.filter_by(
                user_id=user_id,
                achievement_id=achievement.id
            ).first()
            
            if already_unlocked:
                continue
            
            # Check if condition met
            if total_moods >= achievement.condition_value:
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id,
                    progress_value=total_moods
                )
                db.session.add(user_achievement)
                newly_unlocked.append(achievement)
                
                # Update leaderboard
                AchievementsService.update_leaderboard_entry(user_id)
        
        if newly_unlocked:
            db.session.commit()
        
        return newly_unlocked
    
    @staticmethod
    def check_exercise_achievements(user_id):
        """
        Check exercise-based achievements
        Returns list of newly unlocked achievements
        """
        # Count total exercises
        total_exercises = ExerciseCompletion.query.filter_by(user_id=user_id).count()
        
        # Get exercise achievements
        exercise_achievements = Achievement.query.filter_by(
            category='exercise',
            condition_type='total_exercises',
            active=True
        ).all()
        
        newly_unlocked = []
        
        for achievement in exercise_achievements:
            # Check if already unlocked
            already_unlocked = UserAchievement.query.filter_by(
                user_id=user_id,
                achievement_id=achievement.id
            ).first()
            
            if already_unlocked:
                continue
            
            # Check if condition met
            if total_exercises >= achievement.condition_value:
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id,
                    progress_value=total_exercises
                )
                db.session.add(user_achievement)
                newly_unlocked.append(achievement)
                
                # Update leaderboard
                AchievementsService.update_leaderboard_entry(user_id)
        
        if newly_unlocked:
            db.session.commit()
        
        return newly_unlocked
    
    @staticmethod
    def check_conversation_achievements(user_id):
        """
        Check conversation-based achievements
        Returns list of newly unlocked achievements
        """
        # Count distinct conversations (by date)
        conversations = db.session.query(
            func.date(ChatMessage.timestamp)
        ).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.role == 'user'
        ).distinct().count()
        
        # Get conversation achievements
        conversation_achievements = Achievement.query.filter_by(
            category='conversation',
            condition_type='total_conversations',
            active=True
        ).all()
        
        newly_unlocked = []
        
        for achievement in conversation_achievements:
            # Check if already unlocked
            already_unlocked = UserAchievement.query.filter_by(
                user_id=user_id,
                achievement_id=achievement.id
            ).first()
            
            if already_unlocked:
                continue
            
            # Check if condition met
            if conversations >= achievement.condition_value:
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id,
                    progress_value=conversations
                )
                db.session.add(user_achievement)
                newly_unlocked.append(achievement)
                
                # Update leaderboard
                AchievementsService.update_leaderboard_entry(user_id)
        
        if newly_unlocked:
            db.session.commit()
        
        return newly_unlocked
    
    @staticmethod
    def get_user_achievements(user_id, include_locked=True):
        """
        Get all achievements for user
        Returns dict with unlocked and locked achievements
        """
        # Get unlocked achievements
        unlocked = db.session.query(UserAchievement, Achievement).join(
            Achievement
        ).filter(
            UserAchievement.user_id == user_id
        ).order_by(UserAchievement.unlocked_at.desc()).all()
        
        unlocked_data = []
        unlocked_ids = set()
        
        for user_achievement, achievement in unlocked:
            unlocked_data.append({
                'achievement': achievement.to_dict(),
                'unlocked_at': user_achievement.unlocked_at.isoformat(),
                'progress_value': user_achievement.progress_value,
                'viewed': user_achievement.viewed
            })
            unlocked_ids.add(achievement.id)
        
        result = {'unlocked': unlocked_data}
        
        if include_locked:
            # Get locked achievements (not secret)
            all_achievements = Achievement.query.filter_by(active=True).all()
            
            locked_data = []
            for achievement in all_achievements:
                if achievement.id not in unlocked_ids and not achievement.is_secret:
                    # Calculate progress
                    progress = AchievementsService.calculate_achievement_progress(
                        user_id, achievement
                    )
                    
                    locked_data.append({
                        'achievement': achievement.to_dict(),
                        'progress': progress,
                        'progress_percentage': min(100, (progress / achievement.condition_value) * 100)
                    })
            
            result['locked'] = locked_data
        
        return result
    
    @staticmethod
    def calculate_achievement_progress(user_id, achievement):
        """Calculate current progress towards an achievement"""
        if achievement.condition_type == 'streak_days':
            streak = Streak.query.filter_by(user_id=user_id).first()
            return streak.current_streak if streak else 0
        
        elif achievement.condition_type == 'total_moods':
            return MoodEntry.query.filter_by(user_id=user_id).count()
        
        elif achievement.condition_type == 'total_exercises':
            return ExerciseCompletion.query.filter_by(user_id=user_id).count()
        
        elif achievement.condition_type == 'total_conversations':
            return db.session.query(
                func.date(ChatMessage.timestamp)
            ).filter(
                ChatMessage.user_id == user_id,
                ChatMessage.role == 'user'
            ).distinct().count()
        
        elif achievement.condition_type == 'total_points':
            entry = LeaderboardEntry.query.filter_by(user_id=user_id).first()
            return entry.total_points if entry else 0
        
        return 0
    
    @staticmethod
    def mark_achievements_viewed(user_id, achievement_ids):
        """Mark achievements as viewed"""
        UserAchievement.query.filter(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id.in_(achievement_ids)
        ).update({'viewed': True}, synchronize_session=False)
        
        db.session.commit()
    
    @staticmethod
    def get_user_stats(user_id):
        """Get comprehensive user statistics"""
        streak = AchievementsService.get_or_create_streak(user_id)
        
        # Count achievements
        total_achievements = UserAchievement.query.filter_by(user_id=user_id).count()
        available_achievements = Achievement.query.filter_by(active=True).count()
        
        # Get total points
        leaderboard_entry = LeaderboardEntry.query.filter_by(user_id=user_id).first()
        total_points = leaderboard_entry.total_points if leaderboard_entry else 0
        
        # Count activities
        total_moods = MoodEntry.query.filter_by(user_id=user_id).count()
        total_exercises = ExerciseCompletion.query.filter_by(user_id=user_id).count()
        total_conversations = db.session.query(
            func.date(ChatMessage.timestamp)
        ).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.role == 'user'
        ).distinct().count()
        
        return {
            'streak': streak.to_dict(),
            'achievements': {
                'unlocked': total_achievements,
                'total': available_achievements,
                'percentage': (total_achievements / available_achievements * 100) if available_achievements > 0 else 0
            },
            'total_points': total_points,
            'activities': {
                'moods': total_moods,
                'exercises': total_exercises,
                'conversations': total_conversations
            }
        }
    
    @staticmethod
    def update_leaderboard_entry(user_id):
        """Update or create leaderboard entry for user"""
        from backend.database.models.models import User
        
        # Get or create entry
        entry = LeaderboardEntry.query.filter_by(user_id=user_id).first()
        
        if not entry:
            user = User.query.get(user_id)
            entry = LeaderboardEntry(
                user_id=user_id,
                display_name=user.name if user else 'Anonymous'
            )
            db.session.add(entry)
        
        # Calculate total points
        user_achievements = db.session.query(UserAchievement, Achievement).join(
            Achievement
        ).filter(UserAchievement.user_id == user_id).all()
        
        total_points = sum(achievement.points for _, achievement in user_achievements)
        
        # Get streak data
        streak = Streak.query.filter_by(user_id=user_id).first()
        
        # Update entry
        entry.total_points = total_points
        entry.total_achievements = len(user_achievements)
        entry.current_streak = streak.current_streak if streak else 0
        entry.longest_streak = streak.longest_streak if streak else 0
        
        db.session.commit()
        
        # Recalculate ranks
        AchievementsService.recalculate_ranks()
    
    @staticmethod
    def recalculate_ranks():
        """Recalculate leaderboard ranks"""
        # Get all entries ordered by points (desc), then streak (desc)
        entries = LeaderboardEntry.query.order_by(
            LeaderboardEntry.total_points.desc(),
            LeaderboardEntry.current_streak.desc()
        ).all()
        
        # Assign ranks
        for rank, entry in enumerate(entries, start=1):
            entry.rank = rank
        
        db.session.commit()
    
    @staticmethod
    def get_leaderboard(limit=50, opt_in_only=True):
        """
        Get leaderboard rankings
        """
        query = LeaderboardEntry.query
        
        if opt_in_only:
            query = query.filter_by(opt_in=True)
        
        entries = query.order_by(
            LeaderboardEntry.rank
        ).limit(limit).all()
        
        return [entry.to_dict() for entry in entries]
    
    @staticmethod
    def toggle_leaderboard_opt_in(user_id):
        """Toggle user's leaderboard opt-in status"""
        entry = LeaderboardEntry.query.filter_by(user_id=user_id).first()
        
        if not entry:
            # Create entry with opt-in
            from backend.database.models.models import User
            user = User.query.get(user_id)
            entry = LeaderboardEntry(
                user_id=user_id,
                display_name=user.name if user else 'Anonymous',
                opt_in=True
            )
            db.session.add(entry)
        else:
            # Toggle opt-in
            entry.opt_in = not entry.opt_in
        
        db.session.commit()
        
        return entry.opt_in
    
    @staticmethod
    def get_new_achievements_count(user_id):
        """Get count of unviewed achievements"""
        return UserAchievement.query.filter_by(
            user_id=user_id,
            viewed=False
        ).count()
