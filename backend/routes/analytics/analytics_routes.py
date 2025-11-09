"""
Analytics routes for MyBella
Comprehensive wellness analytics with Chart.js visualizations
"""

from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from backend.services.analytics_service import AnalyticsService
from datetime import datetime
import json
import io

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/')
@login_required
def dashboard():
    """Main analytics dashboard"""
    days = int(request.args.get('days', 30))
    
    # Get overview stats
    overview = AnalyticsService.get_wellness_overview(current_user.id, days=days)
    
    return render_template(
        'analytics/dashboard.html',
        overview=overview,
        selected_days=days
    )


@analytics_bp.route('/api/mood-trends')
@login_required
def api_mood_trends():
    """Get mood trends data for Chart.js"""
    days = int(request.args.get('days', 30))
    
    trends = AnalyticsService.get_mood_trends(current_user.id, days=days)
    
    return jsonify({
        'ok': True,
        'data': trends
    })


@analytics_bp.route('/api/emotions')
@login_required
def api_emotions():
    """Get emotion distribution for Chart.js"""
    days = int(request.args.get('days', 30))
    
    emotions = AnalyticsService.get_emotion_distribution(current_user.id, days=days)
    
    return jsonify({
        'ok': True,
        'data': emotions
    })


@analytics_bp.route('/api/exercises')
@login_required
def api_exercises():
    """Get exercise statistics"""
    days = int(request.args.get('days', 30))
    
    stats = AnalyticsService.get_exercise_stats(current_user.id, days=days)
    
    return jsonify({
        'ok': True,
        'data': stats
    })


@analytics_bp.route('/api/conversations')
@login_required
def api_conversations():
    """Get conversation statistics"""
    days = int(request.args.get('days', 30))
    
    stats = AnalyticsService.get_conversation_stats(current_user.id, days=days)
    
    return jsonify({
        'ok': True,
        'data': stats
    })


@analytics_bp.route('/weekly-report')
@login_required
def weekly_report():
    """Generate and display weekly wellness report"""
    report = AnalyticsService.get_weekly_report(current_user.id)
    
    return render_template(
        'analytics/weekly_report.html',
        report=report
    )


@analytics_bp.route('/export')
@login_required
def export_data():
    """Export all analytics data as JSON"""
    days = int(request.args.get('days', 90))
    
    export_data = {
        'user_id': current_user.id,
        'export_date': datetime.utcnow().isoformat(),
        'time_period_days': days,
        'mood_trends': AnalyticsService.get_mood_trends(current_user.id, days=days),
        'emotions': AnalyticsService.get_emotion_distribution(current_user.id, days=days),
        'exercises': AnalyticsService.get_exercise_stats(current_user.id, days=days),
        'conversations': AnalyticsService.get_conversation_stats(current_user.id, days=days),
        'overview': AnalyticsService.get_wellness_overview(current_user.id, days=days)
    }
    
    # Create JSON file
    json_data = json.dumps(export_data, indent=2)
    buffer = io.BytesIO(json_data.encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'mybella_analytics_{datetime.utcnow().strftime("%Y%m%d")}.json',
        mimetype='application/json'
    )
