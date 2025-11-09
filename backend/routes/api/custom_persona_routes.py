"""
Custom Persona API Routes
Handles user-created personas with voice customization
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from backend.database.models.models import db, PersonaProfile, UserSettings
from backend.database.utils.utils import allowed_image_file
import os
from datetime import datetime

custom_persona_bp = Blueprint('custom_persona', __name__, url_prefix='/api/personas')

# ElevenLabs voice presets (you can expand this list)
ELEVENLABS_VOICE_PRESETS = {
    'rachel': '21m00Tcm4TlvDq8ikWAM',  # Calm, soothing female
    'adam': 'pNInz6obpgDQGcFmaJgB',     # Deep, confident male
    'bella': 'EXAVITQu4vr4xnSDxMaL',    # Friendly female
    'antoni': 'ErXwobaYiN019PkySvjV',   # Well-rounded male
    'elli': 'MF3mGyEYCl7XYWbV9V6O',     # Emotional female
    'josh': 'TxGEqnHWrfWFTfGW9XjX',     # Young male
    'arnold': 'VR6AewLTigWG4xSOukaG',   # Crisp male
    'domi': 'AZnzlk1XvdvUeBnXmlld',     # Strong female
    'sam': 'yoZ06aMxZJJ28mfd3POQ'       # Raspy male
}

@custom_persona_bp.route('/available', methods=['GET'])
@login_required
def get_available_personas():
    """Get all personas available to the current user (system + their custom personas)"""
    try:
        # Get system personas (is_custom = False or NULL)
        system_personas = PersonaProfile.query.filter(
            (PersonaProfile.is_custom == False) | (PersonaProfile.is_custom == None),
            PersonaProfile.is_active == True
        ).all()
        
        # Get user's custom personas
        custom_personas = PersonaProfile.query.filter_by(
            user_id=current_user.id,
            is_custom=True,
            is_active=True
        ).all()
        
        all_personas = system_personas + custom_personas
        
        result = []
        for persona in all_personas:
            result.append({
                'id': persona.id,
                'name': persona.name,
                'display_name': persona.display_name or persona.name,
                'description': persona.description,
                'avatar': persona.profile_picture,
                'personality_traits': persona.personality_traits,
                'voice_id': persona.voice_id,
                'has_custom_voice': bool(persona.custom_voice_url),
                'is_custom': persona.is_custom or False,
                'is_current': current_user.settings.current_persona_id == persona.id if current_user.settings else False
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching personas: {str(e)}")
        return jsonify({'error': 'Failed to fetch personas'}), 500


@custom_persona_bp.route('/create', methods=['POST'])
@login_required
def create_custom_persona():
    """Create a new custom persona"""
    try:
        data = request.form if request.files else request.get_json()
        
        # Validate required fields
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'Persona name is required'}), 400
        
        # Check if persona name already exists for this user
        existing = PersonaProfile.query.filter_by(name=name, user_id=current_user.id).first()
        if existing:
            return jsonify({'error': 'You already have a persona with this name'}), 400
        
        # Handle avatar upload
        avatar_path = None
        if 'avatar' in request.files:
            avatar_file = request.files['avatar']
            if avatar_file and avatar_file.filename and allowed_image_file(avatar_file.filename):
                filename = secure_filename(f"custom_{current_user.id}_{int(datetime.utcnow().timestamp())}_{avatar_file.filename}")
                upload_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'backend/database/instances/uploads'), 'persona_pics')
                os.makedirs(upload_folder, exist_ok=True)
                avatar_file.save(os.path.join(upload_folder, filename))
                avatar_path = f"persona_pics/{filename}"
        
        # Create new persona
        new_persona = PersonaProfile(
            name=name,
            display_name=data.get('display_name', name),
            description=data.get('description', ''),
            personality_traits=data.get('personality_traits', ''),
            profile_picture=avatar_path,
            voice_id=data.get('voice_id'),
            is_custom=True,
            user_id=current_user.id,
            is_active=True
        )
        
        db.session.add(new_persona)
        db.session.commit()
        
        return jsonify({
            'message': 'Custom persona created successfully!',
            'persona': {
                'id': new_persona.id,
                'name': new_persona.name,
                'display_name': new_persona.display_name,
                'description': new_persona.description,
                'avatar': new_persona.profile_picture,
                'voice_id': new_persona.voice_id
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating custom persona: {str(e)}")
        return jsonify({'error': 'Failed to create custom persona'}), 500


@custom_persona_bp.route('/<int:persona_id>', methods=['PUT'])
@login_required
def update_custom_persona(persona_id):
    """Update a custom persona (only if owned by current user)"""
    try:
        persona = PersonaProfile.query.get_or_404(persona_id)
        
        # Check ownership
        if persona.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'error': 'You can only edit your own personas'}), 403
        
        data = request.form if request.files else request.get_json()
        
        # Update fields
        if 'name' in data:
            persona.name = data['name'].strip()
        if 'display_name' in data:
            persona.display_name = data['display_name'].strip()
        if 'description' in data:
            persona.description = data['description']
        if 'personality_traits' in data:
            persona.personality_traits = data['personality_traits']
        if 'voice_id' in data:
            persona.voice_id = data['voice_id']
        
        # Handle avatar upload
        if 'avatar' in request.files:
            avatar_file = request.files['avatar']
            if avatar_file and avatar_file.filename and allowed_image_file(avatar_file.filename):
                filename = secure_filename(f"custom_{current_user.id}_{int(datetime.utcnow().timestamp())}_{avatar_file.filename}")
                upload_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'backend/database/instances/uploads'), 'persona_pics')
                os.makedirs(upload_folder, exist_ok=True)
                avatar_file.save(os.path.join(upload_folder, filename))
                persona.profile_picture = f"persona_pics/{filename}"
        
        persona.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Persona updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating persona: {str(e)}")
        return jsonify({'error': 'Failed to update persona'}), 500


@custom_persona_bp.route('/<int:persona_id>', methods=['DELETE'])
@login_required
def delete_custom_persona(persona_id):
    """Delete a custom persona (only if owned by current user)"""
    try:
        persona = PersonaProfile.query.get_or_404(persona_id)
        
        # Check ownership
        if persona.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'error': 'You can only delete your own personas'}), 403
        
        # Don't allow deleting system personas
        if not persona.is_custom:
            return jsonify({'error': 'Cannot delete system personas'}), 400
        
        # Check if this is the user's current persona
        if current_user.settings and current_user.settings.current_persona_id == persona_id:
            # Switch to default persona
            default_persona = PersonaProfile.query.filter_by(name='Isabella').first()
            if default_persona:
                current_user.settings.current_persona_id = default_persona.id
        
        db.session.delete(persona)
        db.session.commit()
        
        return jsonify({'message': 'Persona deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting persona: {str(e)}")
        return jsonify({'error': 'Failed to delete persona'}), 500


@custom_persona_bp.route('/switch', methods=['POST'])
@login_required
def switch_persona():
    """Switch the user's current active persona"""
    try:
        data = request.get_json()
        persona_id = data.get('persona_id')
        
        if not persona_id:
            return jsonify({'error': 'persona_id is required'}), 400
        
        persona = PersonaProfile.query.get_or_404(persona_id)
        
        # Check if persona is accessible to user (system or owned by user)
        if persona.is_custom and persona.user_id != current_user.id:
            return jsonify({'error': 'Cannot access this persona'}), 403
        
        # Update user settings
        if not current_user.settings:
            current_user.settings = UserSettings(user_id=current_user.id)
            db.session.add(current_user.settings)
        
        current_user.settings.current_persona_id = persona_id
        current_user.settings.current_persona = persona.name  # Keep legacy field synced
        db.session.commit()
        
        return jsonify({
            'message': f'Switched to {persona.display_name or persona.name}',
            'persona': {
                'id': persona.id,
                'name': persona.name,
                'display_name': persona.display_name,
                'avatar': persona.profile_picture
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error switching persona: {str(e)}")
        return jsonify({'error': 'Failed to switch persona'}), 500


@custom_persona_bp.route('/voice-presets', methods=['GET'])
@login_required
def get_voice_presets():
    """Get available ElevenLabs voice presets"""
    presets = [
        {'id': voice_id, 'name': name.capitalize(), 'description': f'ElevenLabs {name.capitalize()} voice'}
        for name, voice_id in ELEVENLABS_VOICE_PRESETS.items()
    ]
    return jsonify(presets), 200


@custom_persona_bp.route('/<int:persona_id>/voice/upload', methods=['POST'])
@login_required
def upload_custom_voice(persona_id):
    """Upload a custom voice file for a persona"""
    try:
        persona = PersonaProfile.query.get_or_404(persona_id)
        
        # Check ownership
        if persona.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'error': 'You can only upload voices for your own personas'}), 403
        
        if 'voice_file' not in request.files:
            return jsonify({'error': 'No voice file provided'}), 400
        
        voice_file = request.files['voice_file']
        if not voice_file or not voice_file.filename:
            return jsonify({'error': 'Invalid voice file'}), 400
        
        # Allow audio files
        allowed_extensions = {'mp3', 'wav', 'ogg', 'm4a', 'flac'}
        if not any(voice_file.filename.lower().endswith(f'.{ext}') for ext in allowed_extensions):
            return jsonify({'error': 'Invalid file type. Allowed: mp3, wav, ogg, m4a, flac'}), 400
        
        # Save voice file
        filename = secure_filename(f"voice_{current_user.id}_{persona_id}_{int(datetime.utcnow().timestamp())}_{voice_file.filename}")
        upload_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'backend/database/instances/uploads'), 'voices')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        voice_file.save(file_path)
        
        # Update persona
        persona.custom_voice_url = f"voices/{filename}"
        persona.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Custom voice uploaded successfully!',
            'voice_url': persona.custom_voice_url
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error uploading custom voice: {str(e)}")
        return jsonify({'error': 'Failed to upload custom voice'}), 500
