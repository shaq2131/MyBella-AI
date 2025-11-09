"""
Voice Upload and Management Routes for MyBella
Provides UI for voice cloning and persona voice assignment
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from backend.database.models.models import db, PersonaProfile
from backend.database.utils.utils import get_user_id, get_persona_voice_id

voice_bp = Blueprint('voice', __name__, url_prefix='/voice')


@voice_bp.route('/upload')
@login_required
def upload():
    """Voice upload page with drag-drop and microphone recording"""
    # Get all available personas
    personas = PersonaProfile.query.all()
    
    # Get user's current voice assignments
    user_id = get_user_id()
    voice_assignments = {}
    
    for persona in personas:
        voice_id = get_persona_voice_id(user_id, persona.name)
        if voice_id:
            voice_assignments[persona.name.lower()] = voice_id
    
    return render_template(
        'voice/upload.html',
        personas=personas,
        voice_assignments=voice_assignments
    )


@voice_bp.route('/manage')
@login_required
def manage():
    """Voice management dashboard - view, test, and manage uploaded voices"""
    personas = PersonaProfile.query.all()
    user_id = get_user_id()
    
    # Build voice data for each persona
    voice_data = []
    for persona in personas:
        custom_voice_id = get_persona_voice_id(user_id, persona.name)
        voice_data.append({
            'persona_name': persona.name,
            'persona_avatar': persona.profile_pic,
            'voice_id': custom_voice_id if custom_voice_id else persona.voice_id,
            'has_custom_voice': bool(custom_voice_id),
            'default_voice': persona.voice_id or 'Default'
        })
    
    return render_template(
        'voice/manage.html',
        voice_data=voice_data,
        personas=personas
    )


@voice_bp.route('/test', methods=['POST'])
@login_required
def test_voice():
    """Test a voice with sample text"""
    data = request.get_json()
    voice_id = data.get('voice_id')
    text = data.get('text', 'Hello! This is a test of your custom voice.')
    
    if not voice_id:
        return jsonify({'error': 'No voice_id provided'}), 400
    
    # Use existing TTS service
    from backend.services.elevenlabs.tts_service import generate_speech
    
    result = generate_speech(
        text=text,
        persona='Custom',  # Doesn't matter for direct voice_id
        user_id=get_user_id(),
        voice_id=voice_id
    )
    
    return jsonify(result)


@voice_bp.route('/delete', methods=['POST'])
@login_required
def delete_voice():
    """Remove custom voice assignment from a persona"""
    data = request.get_json()
    persona = data.get('persona')
    
    if not persona:
        return jsonify({'error': 'No persona specified'}), 400
    
    user_id = get_user_id()
    
    # Clear voice assignment from database
    from backend.database.utils.utils import set_persona_voice_id
    set_persona_voice_id(user_id, persona, None)
    
    return jsonify({
        'ok': True,
        'message': f'Custom voice removed from {persona}'
    })


@voice_bp.route('/status')
@login_required
def voice_status():
    """Get voice upload status for all personas (API endpoint)"""
    personas = PersonaProfile.query.all()
    user_id = get_user_id()
    
    status = {}
    for persona in personas:
        voice_id = get_persona_voice_id(user_id, persona.name)
        status[persona.name.lower()] = {
            'has_custom_voice': bool(voice_id),
            'voice_id': voice_id,
            'default_voice': persona.voice or 'Default'
        }
    
    return jsonify(status)
