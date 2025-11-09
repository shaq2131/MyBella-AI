"""
Crisis Support Routes for MyBella AI Wellness Companion
Provides immediate access to crisis resources and professional help
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from backend.services.crisis_detection import (
    detect_crisis, 
    get_crisis_response, 
    get_all_crisis_resources,
    log_crisis_event
)

crisis_bp = Blueprint('crisis', __name__, url_prefix='/crisis')


@crisis_bp.route('/support')
def support():
    """
    Crisis support page with immediate help resources.
    This page is intentionally NOT login required - anyone should be able to access it.
    """
    resources = get_all_crisis_resources()
    return render_template('crisis/support.html', resources=resources)


@crisis_bp.route('/check', methods=['POST'])
@login_required
def check_message():
    """
    API endpoint to check if a message contains crisis indicators.
    Used by chat interface to detect and respond to crisis situations.
    """
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Detect crisis
    is_crisis, severity, matched_keywords = detect_crisis(message)
    
    # Log if crisis detected
    if is_crisis:
        log_crisis_event(
            user_id=current_user.id,
            message=message,
            severity=severity,
            matched_keywords=matched_keywords
        )
    
    # Get appropriate response
    response_data = {
        'is_crisis': is_crisis,
        'severity': severity,
        'crisis_response': get_crisis_response(severity) if is_crisis else None,
        'resources': get_all_crisis_resources() if is_crisis else None
    }
    
    return jsonify(response_data)


@crisis_bp.route('/resources')
def resources():
    """
    Get crisis resources as JSON (for API access or mobile apps).
    Public endpoint - no login required.
    """
    return jsonify(get_all_crisis_resources())


@crisis_bp.route('/immediate-help')
def immediate_help():
    """
    Simplified page for immediate crisis intervention.
    Large buttons, clear text, easy to use in crisis situations.
    """
    return render_template('crisis/immediate_help.html')


@crisis_bp.route('/safety-plan')
@login_required
def safety_plan():
    """
    Personal safety plan creation and management.
    Helps users prepare coping strategies for crisis moments.
    """
    # TODO: Implement safety plan storage in database
    return render_template('crisis/safety_plan.html')


@crisis_bp.route('/hotlines')
def hotlines():
    """
    Comprehensive list of crisis hotlines and text services.
    Categorized by type (suicide, domestic violence, substance abuse, etc.)
    """
    resources = get_all_crisis_resources()
    return render_template('crisis/hotlines.html', hotlines=resources['hotlines'])
