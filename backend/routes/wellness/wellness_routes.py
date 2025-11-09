"""
Wellness and CBT Routes for MyBella
API endpoints for mental health, finance, and wellness features
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from backend.database.models.wellness_models import (
    CBTSession, MoodEntry, WellnessGoal, FinanceEntry, 
    SocialConnection, CopingStrategy, WellnessInsight, MoodScale
)
from backend.services.wellness_services import (
    CBTService, MoodTrackingService, GoalTrackingService, FinanceWellnessService
)
from backend.database.models.models import db
import json

wellness_bp = Blueprint('wellness', __name__, url_prefix='/wellness')

# =============================================================================
# Main Wellness Dashboard Route
# =============================================================================

@wellness_bp.route('/')
@wellness_bp.route('/wellness-dashboard')  # Alias for dashboard compatibility
@login_required
def wellness_dashboard():
    """Main wellness dashboard with overview of all wellness modules"""
    try:
        # Get wellness summary data
        cbt_progress = CBTService.get_user_cbt_progress(current_user.id)
        mood_trends = MoodTrackingService.get_mood_trends(current_user.id)
        user_goals = GoalTrackingService.get_user_goals(current_user.id)
        financial_summary = FinanceWellnessService.get_financial_summary(current_user.id)
        
        return render_template('wellness/wellness_dashboard.html',
                             cbt_progress=cbt_progress,
                             mood_trends=mood_trends,
                             user_goals=user_goals,
                             financial_summary=financial_summary)
    except Exception as e:
        flash(f'Error loading wellness dashboard: {str(e)}', 'error')
        return redirect(url_for('user_views.dashboard'))

# =============================================================================
# CBT (Cognitive Behavioral Therapy) Routes
# =============================================================================

@wellness_bp.route('/cbt')
@wellness_bp.route('/cbt-dashboard')  # Alias for dashboard compatibility
@login_required
def cbt_dashboard():
    """CBT dashboard and session overview"""
    try:
        progress = CBTService.get_user_cbt_progress(current_user.id)
        return render_template('wellness/cbt_dashboard.html', 
                             title='CBT Sessions', 
                             progress=progress)
    except Exception as e:
        flash('Error loading CBT dashboard.', 'error')
        return redirect(url_for('user_views.dashboard'))

@wellness_bp.route('/cbt/start', methods=['POST'])
@login_required
def start_cbt_session():
    """Start a new CBT session"""
    try:
        data = request.get_json()
        session_type = data.get('session_type', 'thought_record')
        trigger_event = data.get('trigger_event', '')
        
        session = CBTService.start_cbt_session(
            user_id=current_user.id,
            session_type=session_type,
            trigger_event=trigger_event
        )
        
        return jsonify({
            'success': True,
            'session_id': session.id,
            'message': 'CBT session started successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@wellness_bp.route('/cbt/session/<int:session_id>')
@login_required
def cbt_session_detail(session_id):
    """CBT session detail and interaction page"""
    try:
        session = CBTSession.query.filter(
            CBTSession.id == session_id,
            CBTSession.user_id == current_user.id
        ).first()
        
        if not session:
            flash('CBT session not found.', 'error')
            return redirect(url_for('wellness.cbt_dashboard'))
        
        return render_template('wellness/cbt_session.html', 
                             title='CBT Session', 
                             session=session)
        
    except Exception as e:
        flash('Error loading CBT session.', 'error')
        return redirect(url_for('wellness.cbt_dashboard'))

@wellness_bp.route('/cbt/session/<int:session_id>/thought-analysis', methods=['POST'])
@login_required
def record_thought_analysis(session_id):
    """Record thought analysis in CBT session"""
    try:
        data = request.get_json()
        
        success = CBTService.record_thought_analysis(
            session_id=session_id,
            automatic_thoughts=data.get('automatic_thoughts', ''),
            thought_patterns=data.get('thought_patterns', []),
            evidence_for=data.get('evidence_for', ''),
            evidence_against=data.get('evidence_against', ''),
            balanced_thought=data.get('balanced_thought', '')
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Thought analysis recorded'})
        else:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@wellness_bp.route('/cbt/session/<int:session_id>/complete', methods=['POST'])
@login_required
def complete_cbt_session(session_id):
    """Complete a CBT session"""
    try:
        data = request.get_json()
        
        final_mood = MoodScale(int(data.get('final_mood', 5)))
        
        success = CBTService.complete_cbt_session(
            session_id=session_id,
            final_mood=final_mood,
            coping_strategies=data.get('coping_strategies', ''),
            action_plan=data.get('action_plan', '')
        )
        
        if success:
            return jsonify({'success': True, 'message': 'CBT session completed'})
        else:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# Mood Tracking Routes
# =============================================================================

@wellness_bp.route('/mood')
@wellness_bp.route('/mood-dashboard')  # Alias for dashboard compatibility
@login_required
def mood_dashboard():
    """Mood tracking dashboard"""
    try:
        trends = MoodTrackingService.get_mood_trends(current_user.id, days=30)
        today_entry = MoodEntry.query.filter(
            MoodEntry.user_id == current_user.id,
            MoodEntry.entry_date == date.today()
        ).first()
        
        return render_template('wellness/mood_tracking.html',
                             title='Mood Tracking',
                             trends=trends,
                             today_entry=today_entry)
                             
    except Exception as e:
        flash('Error loading mood dashboard.', 'error')
        return redirect(url_for('user_views.dashboard'))

@wellness_bp.route('/mood/log', methods=['GET', 'POST'])
@login_required
def log_mood():
    """Log daily mood entry"""
    if request.method == 'GET':
        return render_template('wellness/mood_log.html', title='Log Mood')
    
    try:
        data = request.get_json() if request.is_json else request.form
        
        entry = MoodTrackingService.log_daily_mood(
            user_id=current_user.id,
            entry_date=datetime.strptime(data.get('entry_date', str(date.today())), '%Y-%m-%d').date(),
            overall_mood=MoodScale(int(data.get('overall_mood'))),
            anxiety_level=MoodScale(int(data.get('anxiety_level'))) if data.get('anxiety_level') else None,
            stress_level=MoodScale(int(data.get('stress_level'))) if data.get('stress_level') else None,
            energy_level=MoodScale(int(data.get('energy_level'))) if data.get('energy_level') else None,
            sleep_quality=MoodScale(int(data.get('sleep_quality'))) if data.get('sleep_quality') else None,
            exercise_minutes=int(data.get('exercise_minutes', 0)),
            water_glasses=int(data.get('water_glasses', 0)),
            meditation_minutes=int(data.get('meditation_minutes', 0)),
            social_interaction=bool(data.get('social_interaction', False)),
            gratitude_note=data.get('gratitude_note', ''),
            reflection_note=data.get('reflection_note', '')
        )
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Mood logged successfully'})
        else:
            flash('Mood logged successfully!', 'success')
            return redirect(url_for('wellness.mood_dashboard'))
            
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash('Error logging mood. Please try again.', 'error')
            return render_template('wellness/mood_log.html', title='Log Mood')

@wellness_bp.route('/mood/trends')
@login_required
def mood_trends_api():
    """API endpoint for mood trends data"""
    try:
        days = request.args.get('days', 30, type=int)
        trends = MoodTrackingService.get_mood_trends(current_user.id, days)
        return jsonify(trends)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# Goal Tracking Routes
# =============================================================================

@wellness_bp.route('/goals')
@wellness_bp.route('/goals-dashboard')  # Alias for dashboard compatibility
@login_required
def goals_dashboard():
    """Goals tracking dashboard"""
    try:
        active_goals = GoalTrackingService.get_user_goals(current_user.id, status='active')
        completed_goals = GoalTrackingService.get_user_goals(current_user.id, status='completed')
        
        return render_template('wellness/goals_dashboard.html',
                             title='Goals & Progress',
                             active_goals=active_goals,
                             completed_goals=completed_goals)
                             
    except Exception as e:
        flash('Error loading goals dashboard.', 'error')
        return redirect(url_for('user_views.dashboard'))

@wellness_bp.route('/goals/create', methods=['POST'])
@login_required
def create_goal():
    """Create a new wellness goal"""
    try:
        data = request.get_json()
        
        target_date = None
        if data.get('target_date'):
            target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
        
        goal = GoalTrackingService.create_goal(
            user_id=current_user.id,
            title=data['title'],
            description=data.get('description', ''),
            category=data['category'],
            target_value=float(data['target_value']) if data.get('target_value') else None,
            unit=data.get('unit'),
            target_date=target_date,
            priority=data.get('priority', 'medium')
        )
        
        return jsonify({
            'success': True,
            'goal_id': goal.id,
            'message': 'Goal created successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@wellness_bp.route('/goals/<int:goal_id>/progress', methods=['POST'])
@login_required
def update_goal_progress(goal_id):
    """Update progress on a goal"""
    try:
        data = request.get_json()
        progress_value = float(data['progress_value'])
        
        success = GoalTrackingService.update_goal_progress(goal_id, progress_value)
        
        if success:
            return jsonify({'success': True, 'message': 'Progress updated'})
        else:
            return jsonify({'success': False, 'error': 'Goal not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# Finance Wellness Routes
# =============================================================================

@wellness_bp.route('/finance')
@wellness_bp.route('/finance-dashboard')  # Alias for dashboard compatibility
@login_required
def finance_dashboard():
    """Financial wellness dashboard"""
    try:
        summary = FinanceWellnessService.get_financial_summary(current_user.id, days=30)
        return render_template('wellness/financial_wellness.html',
                             title='Financial Wellness',
                             summary=summary)
                             
    except Exception as e:
        flash('Error loading finance dashboard.', 'error')
        return redirect(url_for('user_views.dashboard'))

@wellness_bp.route('/finance/transaction', methods=['POST'])
@login_required
def log_transaction():
    """Log a financial transaction"""
    try:
        data = request.get_json()
        
        transaction_date = None
        if data.get('transaction_date'):
            transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date()
        
        spending_mood = None
        if data.get('spending_mood'):
            spending_mood = MoodScale(int(data['spending_mood']))
        
        entry = FinanceWellnessService.log_transaction(
            user_id=current_user.id,
            transaction_type=data['transaction_type'],
            category=data['category'],
            amount=float(data['amount']),
            description=data.get('description'),
            transaction_date=transaction_date,
            spending_mood=spending_mood,
            necessity_rating=int(data['necessity_rating']) if data.get('necessity_rating') else None
        )
        
        return jsonify({
            'success': True,
            'transaction_id': entry.id,
            'message': 'Transaction logged successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@wellness_bp.route('/finance/summary')
@login_required
def finance_summary_api():
    """API endpoint for financial summary"""
    try:
        days = request.args.get('days', 30, type=int)
        summary = FinanceWellnessService.get_financial_summary(current_user.id, days)
        return jsonify(summary)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# Wellness Insights Routes
# =============================================================================

@wellness_bp.route('/insights')
@wellness_bp.route('/wellness-insights')  # Alias for dashboard compatibility
@login_required
def wellness_insights():
    """Wellness insights and recommendations"""
    try:
        insights = WellnessInsight.query.filter(
            WellnessInsight.user_id == current_user.id,
            WellnessInsight.is_read == False
        ).order_by(WellnessInsight.generated_at.desc()).limit(10).all()
        
        return render_template('wellness/insights.html',
                             title='Wellness Insights',
                             insights=insights)
                             
    except Exception as e:
        flash('Error loading insights.', 'error')
        return redirect(url_for('user_views.dashboard'))

@wellness_bp.route('/insights/<int:insight_id>/read', methods=['POST'])
@login_required
def mark_insight_read(insight_id):
    """Mark an insight as read"""
    try:
        insight = WellnessInsight.query.filter(
            WellnessInsight.id == insight_id,
            WellnessInsight.user_id == current_user.id
        ).first()
        
        if insight:
            insight.is_read = True
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Insight not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# Social Wellness Routes  
# =============================================================================

@wellness_bp.route('/social')
@wellness_bp.route('/social-dashboard')  # Alias for dashboard compatibility
@login_required
def social_dashboard():
    """Social connections and relationships dashboard"""
    try:
        connections = SocialConnection.query.filter(
            SocialConnection.user_id == current_user.id,
            SocialConnection.is_active == True
        ).order_by(SocialConnection.last_contact_date.desc()).all()
        
        return render_template('wellness/social_dashboard.html',
                             title='Social Wellness',
                             connections=connections)
                             
    except Exception as e:
        flash('Error loading social dashboard.', 'error')
        return redirect(url_for('user_views.dashboard'))

@wellness_bp.route('/social/connection', methods=['POST'])
@login_required
def add_social_connection():
    """Add a new social connection"""
    try:
        data = request.get_json()
        
        connection = SocialConnection()
        connection.user_id = current_user.id
        connection.name = data['name']
        connection.relationship_type = data['relationship_type']
        connection.contact_info = data.get('contact_info', '')
        connection.closeness_level = int(data.get('closeness_level', 5))
        connection.support_level = int(data.get('support_level', 5))
        connection.interaction_frequency = data.get('interaction_frequency', 'weekly')
        connection.notes = data.get('notes', '')
        
        if data.get('birthday'):
            connection.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
        
        db.session.add(connection)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'connection_id': connection.id,
            'message': 'Social connection added successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# Coping Strategies Routes
# =============================================================================

@wellness_bp.route('/coping')
@login_required
def coping_strategies():
    """Coping strategies and techniques"""
    try:
        user_strategies = CopingStrategy.query.filter(
            CopingStrategy.user_id == current_user.id
        ).order_by(CopingStrategy.average_effectiveness.desc()).all()
        
        recommended_strategies = CopingStrategy.query.filter(
            CopingStrategy.is_recommended == True
        ).limit(5).all()
        
        return render_template('wellness/coping_strategies.html',
                             title='Coping Strategies',
                             user_strategies=user_strategies,
                             recommended_strategies=recommended_strategies)
                             
    except Exception as e:
        flash('Error loading coping strategies.', 'error')
        return redirect(url_for('user_views.dashboard'))

@wellness_bp.route('/coping/use/<int:strategy_id>', methods=['POST'])
@login_required
def use_coping_strategy(strategy_id):
    """Record usage of a coping strategy"""
    try:
        data = request.get_json()
        effectiveness_rating = float(data.get('effectiveness_rating', 5))
        
        strategy = CopingStrategy.query.filter(
            CopingStrategy.id == strategy_id,
            CopingStrategy.user_id == current_user.id
        ).first()
        
        if strategy:
            # Update usage statistics
            strategy.times_used += 1
            strategy.last_used_date = date.today()
            
            # Update average effectiveness
            current_total = strategy.average_effectiveness * (strategy.times_used - 1)
            new_average = (current_total + effectiveness_rating) / strategy.times_used
            strategy.average_effectiveness = new_average
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Coping strategy usage recorded',
                'new_average_effectiveness': new_average
            })
        else:
            return jsonify({'success': False, 'error': 'Strategy not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# Quick Access API Routes
# =============================================================================

@wellness_bp.route('/api/mood/quick', methods=['POST'])
@login_required
def quick_mood_checkin():
    """Quick mood check-in API"""
    try:
        data = request.get_json()
        mood = MoodScale(int(data['mood']))
        
        entry = MoodTrackingService.log_daily_mood(
            user_id=current_user.id,
            entry_date=date.today(),
            overall_mood=mood
        )
        
        return jsonify({
            'success': True,
            'message': f'Mood logged: {mood.name}',
            'mood_value': mood.value
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@wellness_bp.route('/api/wellness/summary')
@login_required
def wellness_summary_api():
    """Get comprehensive wellness summary for dashboard"""
    try:
        # Get recent data
        mood_trends = MoodTrackingService.get_mood_trends(current_user.id, days=7)
        active_goals = GoalTrackingService.get_user_goals(current_user.id, status='active')
        finance_summary = FinanceWellnessService.get_financial_summary(current_user.id, days=7)
        cbt_progress = CBTService.get_user_cbt_progress(current_user.id, days=7)
        
        summary = {
            'mood': {
                'current_average': mood_trends.get('average_mood', 5),
                'trend': mood_trends.get('mood_trend', 'stable'),
                'last_entry': mood_trends.get('daily_data', [])[-1] if mood_trends.get('daily_data') else None
            },
            'goals': {
                'total_active': len(active_goals),
                'completion_rate': sum(g['completion_percentage'] for g in active_goals) / len(active_goals) if active_goals else 0
            },
            'finance': {
                'wellness_score': finance_summary.get('financial_wellness_score', {}),
                'net_income': finance_summary.get('net_income', 0),
                'savings_rate': finance_summary.get('savings_rate', 0)
            },
            'cbt': {
                'total_sessions': cbt_progress.get('total_sessions', 0),
                'completion_rate': cbt_progress.get('completion_rate', 0),
                'mood_improvement': cbt_progress.get('mood_improvement', 0)
            }
        }
        
        return jsonify(summary)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# CBT Game View Routes
# =============================================================================

@wellness_bp.route('/hub')
@login_required
def wellness_hub():
    """Wellness Hub - Central access to all wellness tools"""
    return render_template('wellness/hub.html')


@wellness_bp.route('/games/reframe-puzzle')
@login_required
def reframe_puzzle_view():
    """View for the Reframe Puzzle game"""
    return render_template('wellness/reframe_puzzle.html')


@wellness_bp.route('/games/memory-match')
@login_required
def memory_match_view():
    """View for the Memory Match game"""
    return render_template('wellness/memory_match.html')


@wellness_bp.route('/games/daily-notes')
@login_required
def daily_notes_view():
    """View for Daily Notes and reflections"""
    return render_template('wellness/daily_notes.html')


@wellness_bp.route('/games/checkin')
@login_required
def checkin_view():
    """View for Morning/Evening Check-ins"""
    return render_template('wellness/checkin.html')


@wellness_bp.route('/games/achievements')
@login_required
def achievements_view():
    """View for Achievements and badges"""
    return render_template('wellness/achievements.html')