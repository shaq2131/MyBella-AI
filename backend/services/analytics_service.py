"""
Analytics Service for MyBella
Aggregates data from mood tracking, exercises, conversations, and activities
"""

from backend.database.models.models import db
from backend.database.models.wellness_models import MoodEntry
from backend.database.models.exercise_models import ExerciseCompletion
from backend.database.models.memory_models import ChatMessage
from datetime import datetime, timedelta
from sqlalchemy import func, case
from collections import defaultdict


class AnalyticsService:
    """Service for aggregating and analyzing user data"""
    
    @staticmethod
    def get_mood_trends(user_id, days=30):
        """
        Get mood trends over time
        
        Args:
            user_id: User ID
            days: Number of days to analyze
        
        Returns:
            Dict with mood data for charts
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all mood entries in time period
        mood_entries = MoodEntry.query.filter(
            MoodEntry.user_id == user_id,
            MoodEntry.timestamp >= cutoff_date
        ).order_by(MoodEntry.timestamp).all()
        
        # Organize by date
        daily_moods = defaultdict(list)
        for entry in mood_entries:
            date_key = entry.timestamp.date().isoformat()
            daily_moods[date_key].append(entry.mood_level)
        
        # Calculate daily averages
        dates = []
        mood_values = []
        
        # Fill in all dates even if no entry
        current_date = (datetime.utcnow() - timedelta(days=days)).date()
        end_date = datetime.utcnow().date()
        
        while current_date <= end_date:
            date_str = current_date.isoformat()
            dates.append(date_str)
            
            if date_str in daily_moods:
                avg_mood = sum(daily_moods[date_str]) / len(daily_moods[date_str])
                mood_values.append(round(avg_mood, 1))
            else:
                mood_values.append(None)  # No data for this day
            
            current_date += timedelta(days=1)
        
        return {
            'labels': dates,
            'values': mood_values,
            'total_entries': len(mood_entries)
        }
    
    @staticmethod
    def get_emotion_distribution(user_id, days=30):
        """
        Get distribution of emotions over time period
        
        Args:
            user_id: User ID
            days: Number of days to analyze
        
        Returns:
            Dict with emotion counts
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        mood_entries = MoodEntry.query.filter(
            MoodEntry.user_id == user_id,
            MoodEntry.timestamp >= cutoff_date
        ).all()
        
        # Count emotions
        emotion_counts = defaultdict(int)
        for entry in mood_entries:
            if entry.emotions:
                emotions = entry.emotions.split(',')
                for emotion in emotions:
                    emotion = emotion.strip()
                    if emotion:
                        emotion_counts[emotion] += 1
        
        # Sort by frequency
        sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'labels': [e[0] for e in sorted_emotions[:10]],  # Top 10 emotions
            'values': [e[1] for e in sorted_emotions[:10]]
        }
    
    @staticmethod
    def get_exercise_stats(user_id, days=30):
        """
        Get exercise completion statistics
        
        Args:
            user_id: User ID
            days: Number of days to analyze
        
        Returns:
            Dict with exercise stats
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all completions
        completions = ExerciseCompletion.query.filter(
            ExerciseCompletion.user_id == user_id,
            ExerciseCompletion.completed_at >= cutoff_date
        ).all()
        
        # Count by type
        type_counts = defaultdict(int)
        total_minutes = 0
        
        for completion in completions:
            type_counts[completion.exercise_type] += 1
            if completion.duration_minutes:
                total_minutes += completion.duration_minutes
        
        # Get daily activity
        daily_activity = db.session.query(
            func.date(ExerciseCompletion.completed_at).label('date'),
            func.count(ExerciseCompletion.id).label('count')
        ).filter(
            ExerciseCompletion.user_id == user_id,
            ExerciseCompletion.completed_at >= cutoff_date
        ).group_by(
            func.date(ExerciseCompletion.completed_at)
        ).all()
        
        # Fill in all dates
        dates = []
        activity_counts = []
        
        current_date = (datetime.utcnow() - timedelta(days=days)).date()
        end_date = datetime.utcnow().date()
        
        activity_dict = {str(d): c for d, c in daily_activity}
        
        while current_date <= end_date:
            date_str = str(current_date)
            dates.append(date_str)
            activity_counts.append(activity_dict.get(date_str, 0))
            current_date += timedelta(days=1)
        
        return {
            'total_completions': len(completions),
            'total_minutes': total_minutes,
            'by_type': dict(type_counts),
            'daily_activity': {
                'labels': dates,
                'values': activity_counts
            }
        }
    
    @staticmethod
    def get_conversation_stats(user_id, days=30):
        """
        Get conversation activity statistics
        
        Args:
            user_id: User ID
            days: Number of days to analyze
        
        Returns:
            Dict with conversation stats
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all messages
        messages = ChatMessage.query.filter(
            ChatMessage.user_id == user_id,
            ChatMessage.timestamp >= cutoff_date
        ).all()
        
        # Count by persona
        persona_counts = defaultdict(int)
        user_messages = 0
        ai_messages = 0
        
        for message in messages:
            if message.role == 'user':
                user_messages += 1
            else:
                ai_messages += 1
                
            if message.persona:
                persona_counts[message.persona] += 1
        
        # Get daily message count
        daily_messages = db.session.query(
            func.date(ChatMessage.timestamp).label('date'),
            func.count(ChatMessage.id).label('count')
        ).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.timestamp >= cutoff_date
        ).group_by(
            func.date(ChatMessage.timestamp)
        ).all()
        
        # Fill in all dates
        dates = []
        message_counts = []
        
        current_date = (datetime.utcnow() - timedelta(days=days)).date()
        end_date = datetime.utcnow().date()
        
        messages_dict = {str(d): c for d, c in daily_messages}
        
        while current_date <= end_date:
            date_str = str(current_date)
            dates.append(date_str)
            message_counts.append(messages_dict.get(date_str, 0))
            current_date += timedelta(days=1)
        
        return {
            'total_messages': len(messages),
            'user_messages': user_messages,
            'ai_messages': ai_messages,
            'by_persona': dict(persona_counts),
            'daily_activity': {
                'labels': dates,
                'values': message_counts
            }
        }
    
    @staticmethod
    def get_wellness_overview(user_id, days=30):
        """
        Get comprehensive wellness overview
        
        Args:
            user_id: User ID
            days: Number of days to analyze
        
        Returns:
            Dict with all analytics data
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get counts
        mood_count = MoodEntry.query.filter(
            MoodEntry.user_id == user_id,
            MoodEntry.timestamp >= cutoff_date
        ).count()
        
        exercise_count = ExerciseCompletion.query.filter(
            ExerciseCompletion.user_id == user_id,
            ExerciseCompletion.completed_at >= cutoff_date
        ).count()
        
        message_count = ChatMessage.query.filter(
            ChatMessage.user_id == user_id,
            ChatMessage.timestamp >= cutoff_date,
            ChatMessage.role == 'user'
        ).count()
        
        # Calculate average mood
        avg_mood_result = db.session.query(
            func.avg(MoodEntry.mood_level)
        ).filter(
            MoodEntry.user_id == user_id,
            MoodEntry.timestamp >= cutoff_date
        ).scalar()
        
        avg_mood = round(avg_mood_result, 1) if avg_mood_result else 0
        
        # Get most active day
        most_active = db.session.query(
            func.date(MoodEntry.timestamp).label('date'),
            func.count(MoodEntry.id).label('count')
        ).filter(
            MoodEntry.user_id == user_id,
            MoodEntry.timestamp >= cutoff_date
        ).group_by(
            func.date(MoodEntry.timestamp)
        ).order_by(
            func.count(MoodEntry.id).desc()
        ).first()
        
        return {
            'mood_checkins': mood_count,
            'exercises_completed': exercise_count,
            'conversations': message_count,
            'average_mood': avg_mood,
            'most_active_day': str(most_active[0]) if most_active else None,
            'time_period_days': days
        }
    
    @staticmethod
    def get_weekly_report(user_id):
        """
        Generate weekly wellness report
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with weekly summary
        """
        mood_trends = AnalyticsService.get_mood_trends(user_id, days=7)
        exercise_stats = AnalyticsService.get_exercise_stats(user_id, days=7)
        conversation_stats = AnalyticsService.get_conversation_stats(user_id, days=7)
        emotions = AnalyticsService.get_emotion_distribution(user_id, days=7)
        
        # Calculate mood trend (improving/declining)
        mood_values = [v for v in mood_trends['values'] if v is not None]
        
        if len(mood_values) >= 2:
            first_half = mood_values[:len(mood_values)//2]
            second_half = mood_values[len(mood_values)//2:]
            
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)
            
            if avg_second > avg_first + 0.3:
                trend = 'improving'
            elif avg_second < avg_first - 0.3:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'week_ending': datetime.utcnow().date().isoformat(),
            'mood_trend': trend,
            'mood_data': mood_trends,
            'exercise_stats': exercise_stats,
            'conversation_stats': conversation_stats,
            'top_emotions': emotions,
            'summary': {
                'total_activities': (
                    mood_trends['total_entries'] +
                    exercise_stats['total_completions'] +
                    conversation_stats['user_messages']
                )
            }
        }
