"""
Onboarding Routes
Handles 60-second personalization quiz flow
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from flask_login import login_required, current_user

from backend.services.onboarding_service import OnboardingService
from backend.database.models.models import PersonaProfile


onboarding_bp = Blueprint('onboarding', __name__)


@onboarding_bp.route('/onboarding')
@onboarding_bp.route('/onboarding/quiz')  # Alias for dashboard compatibility
@login_required
def onboarding_page():
    """
    Display onboarding quiz page
    
    If user has already completed onboarding, redirect to chat
    """
    # Check if user has completed onboarding
    if not OnboardingService.needs_onboarding(current_user.id):
        return redirect(url_for('chat.chat_page'))
    
    # Get all personas for selection
    personas = OnboardingService.get_all_personas_for_selection()
    
    # Get current quiz status (in case user is resuming)
    quiz_status = OnboardingService.get_quiz_status(current_user.id)
    
    return render_template(
        'onboarding/quiz.html',
        personas=personas,
        quiz_status=quiz_status
    )


@onboarding_bp.route('/api/onboarding/status', methods=['GET'])
@login_required
def get_onboarding_status():
    """
    Get user's onboarding completion status
    
    Returns:
        JSON with completion status and data
    """
    try:
        status = OnboardingService.get_quiz_status(current_user.id)
        return jsonify({
            'success': True,
            **status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@onboarding_bp.route('/api/onboarding/start', methods=['POST'])
@login_required
def start_onboarding():
    """
    Initialize onboarding quiz for user
    
    Returns:
        JSON with quiz ID and initial status
    """
    try:
        quiz = OnboardingService.get_or_create_quiz(current_user.id)
        
        return jsonify({
            'success': True,
            'quiz_id': quiz.id,
            'completion_percentage': quiz.calculate_completion(),
            'message': 'Onboarding started successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@onboarding_bp.route('/api/onboarding/update', methods=['PATCH', 'POST'])
@login_required
def update_onboarding():
    """
    Update quiz with user's answer to a question
    
    Request Body:
        {
            "primary_goal": "mental_health",  // Optional
            "secondary_goals": ["companionship"],  // Optional
            "initial_mood": 7,  // Optional
            "preferred_tone": "supportive",  // Optional
            "personality_preference": "empathetic",  // Optional
            "preferred_check_in_time": "morning",  // Optional
            "selected_persona_id": 3  // Optional
        }
    
    Returns:
        JSON with updated quiz status
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Update quiz with provided data
        quiz = OnboardingService.update_quiz_response(current_user.id, data)
        
        return jsonify({
            'success': True,
            'completion_percentage': quiz.calculate_completion(),
            'message': 'Quiz updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@onboarding_bp.route('/api/onboarding/complete', methods=['POST'])
@login_required
def complete_onboarding():
    """
    Complete onboarding and apply preferences
    
    Request Body:
        {
            "primary_goal": "mental_health",
            "secondary_goals": ["companionship", "productivity"],
            "initial_mood": 7,
            "mood_description": "happy",
            "preferred_tone": "supportive",
            "personality_preference": "empathetic",
            "preferred_check_in_time": "morning",
            "selected_persona_id": 3
        }
    
    Returns:
        JSON with success status and applied settings
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        if 'selected_persona_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Persona selection is required'
            }), 400
        
        # Complete onboarding
        result = OnboardingService.complete_onboarding(current_user.id, data)
        
        # Set session flag for welcome message
        session['onboarding_just_completed'] = True
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@onboarding_bp.route('/api/onboarding/skip', methods=['POST'])
@login_required
def skip_onboarding():
    """
    Allow user to skip onboarding with default settings
    
    Returns:
        JSON with success status
    """
    try:
        result = OnboardingService.skip_onboarding(current_user.id)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@onboarding_bp.route('/api/onboarding/personas', methods=['GET'])
@login_required
def get_personas():
    """
    Get all active personas for selection
    
    Returns:
        JSON list of personas
    """
    try:
        personas = OnboardingService.get_all_personas_for_selection()
        
        return jsonify({
            'success': True,
            'personas': personas
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@onboarding_bp.route('/api/onboarding/recommend-persona', methods=['POST'])
@login_required
def recommend_persona():
    """
    Get persona recommendation based on quiz responses
    
    Request Body:
        {
            "primary_goal": "mental_health",
            "preferred_tone": "supportive",
            "initial_mood": 7
        }
    
    Returns:
        JSON with recommended persona
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No quiz data provided'
            }), 400
        
        # Get recommendation
        persona = OnboardingService.get_recommended_persona(data)
        
        if not persona:
            return jsonify({
                'success': False,
                'error': 'No matching persona found'
            }), 404
        
        return jsonify({
            'success': True,
            'recommended_persona': {
                'id': persona.id,
                'name': persona.name,
                'description': persona.description,
                'personality_traits': persona.personality_traits,
                'communication_style': persona.communication_style,
                'profile_picture': persona.profile_picture
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@onboarding_bp.route('/api/onboarding/needs-onboarding', methods=['GET'])
@login_required
def check_needs_onboarding():
    """
    Check if current user needs onboarding
    
    Returns:
        JSON with boolean indicating if onboarding is needed
    """
    try:
        needs_onboarding = OnboardingService.needs_onboarding(current_user.id)
        
        return jsonify({
            'success': True,
            'needs_onboarding': needs_onboarding
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
