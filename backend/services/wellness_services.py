"""
CBT and Wellness Service Functions
Core business logic for cognitive behavioral therapy and wellness features
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date, timedelta
from flask import current_app
from backend.database.models.models import db, User
from backend.database.models.wellness_models import (
    CBTSession, MoodEntry, WellnessGoal, FinanceEntry, 
    SocialConnection, CopingStrategy, WellnessInsight,
    MoodScale, ThoughtPattern
)
import json
import statistics
from sqlalchemy import func, and_

class CBTService:
    """Cognitive Behavioral Therapy service functions"""
    
    @staticmethod
    def start_cbt_session(user_id: int, session_type: str, trigger_event: str = None) -> CBTSession:
        """Start a new CBT session"""
        try:
            session = CBTSession()
            session.user_id = user_id
            session.session_type = session_type
            session.trigger_event = trigger_event
            session.persona = 'Maya'  # Wellness-focused persona
            
            db.session.add(session)
            db.session.commit()
            
            current_app.logger.info(f"Started CBT session {session.id} for user {user_id}")
            return session
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error starting CBT session: {e}")
            raise
    
    @staticmethod
    def record_thought_analysis(session_id: int, automatic_thoughts: str, 
                               thought_patterns: List[str], evidence_for: str, 
                               evidence_against: str, balanced_thought: str) -> bool:
        """Record thought analysis in CBT session"""
        try:
            session = CBTSession.query.get(session_id)
            if not session:
                return False
            
            session.automatic_thoughts = automatic_thoughts
            session.thought_patterns = json.dumps(thought_patterns)
            session.evidence_for = evidence_for
            session.evidence_against = evidence_against
            session.balanced_thought = balanced_thought
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error recording thought analysis: {e}")
            return False
    
    @staticmethod
    def complete_cbt_session(session_id: int, final_mood: MoodScale, 
                            coping_strategies: str, action_plan: str) -> bool:
        """Complete a CBT session"""
        try:
            session = CBTSession.query.get(session_id)
            if not session:
                return False
            
            session.final_mood = final_mood
            session.coping_strategies = coping_strategies
            session.action_plan = action_plan
            session.completed = True
            session.duration_minutes = int((datetime.utcnow() - session.created_at).total_seconds() / 60)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error completing CBT session: {e}")
            return False
    
    @staticmethod
    def get_user_cbt_progress(user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get user's CBT progress analytics"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            sessions = CBTSession.query.filter(
                CBTSession.user_id == user_id,
                CBTSession.created_at >= start_date
            ).all()
            
            completed_sessions = [s for s in sessions if s.completed]
            
            progress = {
                'total_sessions': len(sessions),
                'completed_sessions': len(completed_sessions),
                'completion_rate': len(completed_sessions) / len(sessions) if sessions else 0,
                'average_duration': statistics.mean([s.duration_minutes for s in completed_sessions]) if completed_sessions else 0,
                'mood_improvement': CBTService._calculate_mood_improvement(completed_sessions),
                'common_patterns': CBTService._analyze_thought_patterns(completed_sessions),
                'recent_sessions': [CBTService._session_to_dict(s) for s in sessions[-5:]]
            }
            
            return progress
            
        except Exception as e:
            current_app.logger.error(f"Error getting CBT progress: {e}")
            return {}
    
    @staticmethod
    def _calculate_mood_improvement(sessions: List[CBTSession]) -> float:
        """Calculate average mood improvement across sessions"""
        improvements = []
        for session in sessions:
            if session.initial_mood and session.final_mood:
                improvement = session.final_mood.value - session.initial_mood.value
                improvements.append(improvement)
        
        return statistics.mean(improvements) if improvements else 0
    
    @staticmethod
    def _analyze_thought_patterns(sessions: List[CBTSession]) -> Dict[str, int]:
        """Analyze common thought patterns"""
        pattern_counts = {}
        for session in sessions:
            if session.thought_patterns:
                try:
                    patterns = json.loads(session.thought_patterns)
                    for pattern in patterns:
                        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
                except:
                    continue
        
        return pattern_counts
    
    @staticmethod
    def _session_to_dict(session: CBTSession) -> Dict[str, Any]:
        """Convert CBT session to dictionary"""
        return {
            'id': session.id,
            'session_type': session.session_type,
            'trigger_event': session.trigger_event,
            'initial_mood': session.initial_mood.value if session.initial_mood else None,
            'final_mood': session.final_mood.value if session.final_mood else None,
            'completed': session.completed,
            'created_at': session.created_at.isoformat(),
            'duration_minutes': session.duration_minutes
        }

class MoodTrackingService:
    """Mood and wellness tracking service"""
    
    @staticmethod
    def log_daily_mood(user_id: int, entry_date: date, overall_mood: MoodScale,
                      anxiety_level: MoodScale = None, stress_level: MoodScale = None,
                      energy_level: MoodScale = None, sleep_quality: MoodScale = None,
                      exercise_minutes: int = 0, water_glasses: int = 0,
                      meditation_minutes: int = 0, social_interaction: bool = False,
                      gratitude_note: str = None, reflection_note: str = None) -> MoodEntry:
        """Log daily mood and wellness data"""
        try:
            # Check if entry already exists for this date
            existing_entry = MoodEntry.query.filter(
                MoodEntry.user_id == user_id,
                MoodEntry.entry_date == entry_date
            ).first()
            
            if existing_entry:
                # Update existing entry
                entry = existing_entry
            else:
                # Create new entry
                entry = MoodEntry()
                entry.user_id = user_id
                entry.entry_date = entry_date
                db.session.add(entry)
            
            # Update fields
            entry.overall_mood = overall_mood
            entry.anxiety_level = anxiety_level
            entry.stress_level = stress_level
            entry.energy_level = energy_level
            entry.sleep_quality = sleep_quality
            entry.exercise_minutes = exercise_minutes
            entry.water_glasses = water_glasses
            entry.meditation_minutes = meditation_minutes
            entry.social_interaction = social_interaction
            entry.gratitude_note = gratitude_note
            entry.reflection_note = reflection_note
            
            db.session.commit()
            return entry
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error logging mood entry: {e}")
            raise
    
    @staticmethod
    def get_mood_trends(user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get mood trends and analytics"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            entries = MoodEntry.query.filter(
                MoodEntry.user_id == user_id,
                MoodEntry.entry_date >= start_date,
                MoodEntry.entry_date <= end_date
            ).order_by(MoodEntry.entry_date).all()
            
            if not entries:
                return {'error': 'No mood data found'}
            
            # Calculate trends
            mood_values = [entry.overall_mood.value for entry in entries]
            anxiety_values = [entry.anxiety_level.value for entry in entries if entry.anxiety_level]
            stress_values = [entry.stress_level.value for entry in entries if entry.stress_level]
            energy_values = [entry.energy_level.value for entry in entries if entry.energy_level]
            
            trends = {
                'period_days': days,
                'total_entries': len(entries),
                'average_mood': statistics.mean(mood_values),
                'mood_trend': MoodTrackingService._calculate_trend(mood_values),
                'mood_stability': statistics.stdev(mood_values) if len(mood_values) > 1 else 0,
                'best_day': {
                    'date': max(entries, key=lambda x: x.overall_mood.value).entry_date.isoformat(),
                    'mood': max(mood_values)
                },
                'worst_day': {
                    'date': min(entries, key=lambda x: x.overall_mood.value).entry_date.isoformat(),
                    'mood': min(mood_values)
                },
                'wellness_metrics': {
                    'average_anxiety': statistics.mean(anxiety_values) if anxiety_values else None,
                    'average_stress': statistics.mean(stress_values) if stress_values else None,
                    'average_energy': statistics.mean(energy_values) if energy_values else None,
                    'total_exercise_minutes': sum(entry.exercise_minutes for entry in entries),
                    'total_meditation_minutes': sum(entry.meditation_minutes for entry in entries),
                    'social_interaction_days': sum(1 for entry in entries if entry.social_interaction)
                },
                'correlations': MoodTrackingService._calculate_correlations(entries),
                'daily_data': [MoodTrackingService._entry_to_dict(entry) for entry in entries]
            }
            
            return trends
            
        except Exception as e:
            current_app.logger.error(f"Error getting mood trends: {e}")
            return {'error': 'Failed to analyze mood trends'}
    
    @staticmethod
    def _calculate_trend(values: List[float]) -> str:
        """Calculate if mood is improving, declining, or stable"""
        if len(values) < 3:
            return 'insufficient_data'
        
        # Calculate linear regression slope
        x = list(range(len(values)))
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.1:
            return 'improving'
        elif slope < -0.1:
            return 'declining'
        else:
            return 'stable'
    
    @staticmethod
    def _calculate_correlations(entries: List[MoodEntry]) -> Dict[str, float]:
        """Calculate correlations between mood and wellness factors"""
        correlations = {}
        
        mood_values = [entry.overall_mood.value for entry in entries]
        
        # Exercise correlation
        exercise_values = [entry.exercise_minutes for entry in entries]
        if any(exercise_values):
            correlations['exercise'] = MoodTrackingService._correlation(mood_values, exercise_values)
        
        # Sleep correlation
        sleep_values = [entry.sleep_quality.value for entry in entries if entry.sleep_quality]
        if len(sleep_values) == len(mood_values):
            correlations['sleep'] = MoodTrackingService._correlation(mood_values, sleep_values)
        
        # Meditation correlation
        meditation_values = [entry.meditation_minutes for entry in entries]
        if any(meditation_values):
            correlations['meditation'] = MoodTrackingService._correlation(mood_values, meditation_values)
        
        return correlations
    
    @staticmethod
    def _correlation(x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(xi ** 2 for xi in x)
        sum_y2 = sum(yi ** 2 for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
        
        return numerator / denominator if denominator != 0 else 0
    
    @staticmethod
    def _entry_to_dict(entry: MoodEntry) -> Dict[str, Any]:
        """Convert mood entry to dictionary"""
        return {
            'date': entry.entry_date.isoformat(),
            'overall_mood': entry.overall_mood.value,
            'anxiety_level': entry.anxiety_level.value if entry.anxiety_level else None,
            'stress_level': entry.stress_level.value if entry.stress_level else None,
            'energy_level': entry.energy_level.value if entry.energy_level else None,
            'sleep_quality': entry.sleep_quality.value if entry.sleep_quality else None,
            'exercise_minutes': entry.exercise_minutes,
            'water_glasses': entry.water_glasses,
            'meditation_minutes': entry.meditation_minutes,
            'social_interaction': entry.social_interaction,
            'gratitude_note': entry.gratitude_note,
            'reflection_note': entry.reflection_note
        }

class GoalTrackingService:
    """Wellness and life goal tracking service"""
    
    @staticmethod
    def create_goal(user_id: int, title: str, description: str, category: str,
                   target_value: float = None, unit: str = None, 
                   target_date: date = None, priority: str = 'medium') -> WellnessGoal:
        """Create a new wellness goal"""
        try:
            goal = WellnessGoal()
            goal.user_id = user_id
            goal.title = title
            goal.description = description
            goal.category = category
            goal.target_value = target_value
            goal.unit = unit
            goal.target_date = target_date
            goal.priority = priority
            goal.start_date = date.today()
            
            db.session.add(goal)
            db.session.commit()
            
            current_app.logger.info(f"Created goal {goal.id} for user {user_id}")
            return goal
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating goal: {e}")
            raise
    
    @staticmethod
    def update_goal_progress(goal_id: int, progress_value: float, notes: str = None) -> bool:
        """Update progress on a goal"""
        try:
            goal = WellnessGoal.query.get(goal_id)
            if not goal:
                return False
            
            goal.current_value = progress_value
            
            # Calculate completion percentage
            if goal.target_value:
                goal.completion_percentage = min(100, (progress_value / goal.target_value) * 100)
            
            # Check if goal is completed
            if goal.completion_percentage >= 100 and goal.status == 'active':
                goal.status = 'completed'
                goal.completed_date = date.today()
            
            goal.updated_at = datetime.utcnow()
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating goal progress: {e}")
            return False
    
    @staticmethod
    def get_user_goals(user_id: int, status: str = None) -> List[Dict[str, Any]]:
        """Get user's goals with optional status filter"""
        try:
            query = WellnessGoal.query.filter(WellnessGoal.user_id == user_id)
            
            if status:
                query = query.filter(WellnessGoal.status == status)
            
            goals = query.order_by(WellnessGoal.created_at.desc()).all()
            
            return [GoalTrackingService._goal_to_dict(goal) for goal in goals]
            
        except Exception as e:
            current_app.logger.error(f"Error getting user goals: {e}")
            return []
    
    @staticmethod
    def _goal_to_dict(goal: WellnessGoal) -> Dict[str, Any]:
        """Convert goal to dictionary"""
        return {
            'id': goal.id,
            'title': goal.title,
            'description': goal.description,
            'category': goal.category,
            'priority': goal.priority,
            'target_value': goal.target_value,
            'current_value': goal.current_value,
            'unit': goal.unit,
            'completion_percentage': goal.completion_percentage,
            'status': goal.status,
            'start_date': goal.start_date.isoformat(),
            'target_date': goal.target_date.isoformat() if goal.target_date else None,
            'completed_date': goal.completed_date.isoformat() if goal.completed_date else None,
            'created_at': goal.created_at.isoformat(),
            'updated_at': goal.updated_at.isoformat()
        }

class FinanceWellnessService:
    """Financial wellness and management service"""
    
    @staticmethod
    def log_transaction(user_id: int, transaction_type: str, category: str,
                       amount: float, description: str = None, 
                       transaction_date: date = None, spending_mood: MoodScale = None,
                       necessity_rating: int = None) -> FinanceEntry:
        """Log a financial transaction"""
        try:
            entry = FinanceEntry()
            entry.user_id = user_id
            entry.transaction_type = transaction_type
            entry.category = category
            entry.amount = amount
            entry.description = description
            entry.transaction_date = transaction_date or date.today()
            entry.spending_mood = spending_mood
            entry.necessity_rating = necessity_rating
            
            db.session.add(entry)
            db.session.commit()
            
            return entry
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error logging transaction: {e}")
            raise
    
    @staticmethod
    def get_financial_summary(user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive financial summary and wellness insights"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            entries = FinanceEntry.query.filter(
                FinanceEntry.user_id == user_id,
                FinanceEntry.transaction_date >= start_date,
                FinanceEntry.transaction_date <= end_date
            ).all()
            
            if not entries:
                return {'error': 'No financial data found'}
            
            # Calculate totals by type
            income = sum(e.amount for e in entries if e.transaction_type == 'income')
            expenses = sum(e.amount for e in entries if e.transaction_type == 'expense')
            savings = sum(e.amount for e in entries if e.transaction_type == 'savings')
            investments = sum(e.amount for e in entries if e.transaction_type == 'investment')
            
            # Category breakdown
            expense_by_category = {}
            for entry in entries:
                if entry.transaction_type == 'expense':
                    expense_by_category[entry.category] = expense_by_category.get(entry.category, 0) + entry.amount
            
            # Emotional spending analysis
            emotional_spending = [e for e in entries if e.spending_mood and e.transaction_type == 'expense']
            mood_spending_correlation = FinanceWellnessService._analyze_mood_spending(emotional_spending)
            
            summary = {
                'period_days': days,
                'income': income,
                'expenses': expenses,
                'savings': savings,
                'investments': investments,
                'net_income': income - expenses,
                'savings_rate': (savings / income * 100) if income > 0 else 0,
                'expense_by_category': expense_by_category,
                'largest_expense': max(entries, key=lambda x: x.amount if x.transaction_type == 'expense' else 0).amount if entries else 0,
                'average_daily_spending': expenses / days,
                'emotional_spending_analysis': mood_spending_correlation,
                'financial_wellness_score': FinanceWellnessService._calculate_wellness_score(income, expenses, savings),
                'recommendations': FinanceWellnessService._generate_financial_recommendations(income, expenses, savings, expense_by_category)
            }
            
            return summary
            
        except Exception as e:
            current_app.logger.error(f"Error getting financial summary: {e}")
            return {'error': 'Failed to analyze financial data'}
    
    @staticmethod
    def _analyze_mood_spending(emotional_entries: List[FinanceEntry]) -> Dict[str, Any]:
        """Analyze relationship between mood and spending"""
        if not emotional_entries:
            return {'error': 'No emotional spending data'}
        
        mood_totals = {}
        mood_counts = {}
        
        for entry in emotional_entries:
            mood = entry.spending_mood.value
            mood_totals[mood] = mood_totals.get(mood, 0) + entry.amount
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        mood_averages = {mood: mood_totals[mood] / mood_counts[mood] for mood in mood_totals}
        
        return {
            'spending_by_mood': mood_totals,
            'average_spending_by_mood': mood_averages,
            'highest_spending_mood': max(mood_averages, key=mood_averages.get),
            'pattern_analysis': FinanceWellnessService._identify_spending_patterns(emotional_entries)
        }
    
    @staticmethod
    def _identify_spending_patterns(entries: List[FinanceEntry]) -> List[str]:
        """Identify concerning spending patterns"""
        patterns = []
        
        # High spending when mood is low
        low_mood_spending = [e for e in entries if e.spending_mood.value <= 4]
        if low_mood_spending and len(low_mood_spending) / len(entries) > 0.3:
            patterns.append("Tendency to spend more when feeling down")
        
        # Impulse buying (low necessity ratings)
        impulse_purchases = [e for e in entries if e.necessity_rating and e.necessity_rating <= 2]
        if impulse_purchases and len(impulse_purchases) / len(entries) > 0.2:
            patterns.append("Frequent impulse purchases")
        
        # High regret spending
        regret_purchases = [e for e in entries if e.regret_level and e.regret_level >= 3]
        if regret_purchases and len(regret_purchases) / len(entries) > 0.15:
            patterns.append("High regret about purchases")
        
        return patterns
    
    @staticmethod
    def _calculate_wellness_score(income: float, expenses: float, savings: float) -> Dict[str, Any]:
        """Calculate financial wellness score"""
        if income <= 0:
            return {'score': 0, 'level': 'critical', 'message': 'No income recorded'}
        
        savings_ratio = savings / income
        expense_ratio = expenses / income
        
        score = 0
        
        # Savings rate scoring (40% of total)
        if savings_ratio >= 0.2:
            score += 40
        elif savings_ratio >= 0.1:
            score += 30
        elif savings_ratio >= 0.05:
            score += 20
        else:
            score += 10
        
        # Expense control scoring (40% of total)
        if expense_ratio <= 0.7:
            score += 40
        elif expense_ratio <= 0.8:
            score += 30
        elif expense_ratio <= 0.9:
            score += 20
        else:
            score += 10
        
        # Net positive income (20% of total)
        if income > expenses:
            score += 20
        
        # Determine level
        if score >= 80:
            level = 'excellent'
        elif score >= 60:
            level = 'good'
        elif score >= 40:
            level = 'fair'
        else:
            level = 'needs_improvement'
        
        return {
            'score': score,
            'level': level,
            'savings_ratio': savings_ratio * 100,
            'expense_ratio': expense_ratio * 100
        }
    
    @staticmethod
    def _generate_financial_recommendations(income: float, expenses: float, 
                                         savings: float, expense_categories: Dict[str, float]) -> List[str]:
        """Generate personalized financial recommendations"""
        recommendations = []
        
        if income <= 0:
            recommendations.append("Focus on establishing a steady income source")
            return recommendations
        
        savings_ratio = savings / income
        expense_ratio = expenses / income
        
        # Savings recommendations
        if savings_ratio < 0.1:
            recommendations.append("Try to save at least 10% of your income")
        elif savings_ratio < 0.2:
            recommendations.append("Great start! Consider increasing savings to 20% for better financial security")
        
        # Expense recommendations
        if expense_ratio > 0.9:
            recommendations.append("Your expenses are very high. Look for areas to cut back")
            
            # Identify highest expense categories
            if expense_categories:
                highest_category = max(expense_categories, key=expense_categories.get)
                recommendations.append(f"Consider reducing spending in '{highest_category}' category")
        
        # Emergency fund
        monthly_expenses = expenses
        if savings < (monthly_expenses * 3):
            recommendations.append("Build an emergency fund covering 3-6 months of expenses")
        
        # Investment suggestions
        if savings_ratio >= 0.2:
            recommendations.append("You're saving well! Consider investing some savings for long-term growth")
        
        return recommendations